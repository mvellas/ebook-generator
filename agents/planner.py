from __future__ import annotations
import json
import re
import anthropic
from agents.models import BookParams, Outline, Chapter, Section

PLANNER_MODEL = "claude-opus-4-5"

SYSTEM_PROMPT = """You are an expert book editor and author. Your task is to create a comprehensive,
well-structured book outline based on the provided parameters.

You MUST respond ONLY with a valid JSON object matching this exact structure:
{
  "book_title": "string",
  "author": "string",
  "language": "string",
  "front_matter": ["Dedication", "Acknowledgments"],
  "chapters": [
    {
      "number": 1,
      "title": "Chapter Title",
      "sections": [
        {"title": "Section Title", "estimated_pages": 3.5}
      ],
      "estimated_pages": 12.0
    }
  ],
  "back_matter": ["About the Author"],
  "total_estimated_pages": 120
}

Guidelines:
- Create 8-12 chapters unless the page range suggests otherwise
- Each chapter should have 3-5 sections
- Distribute pages evenly based on the target page range
- Make chapter titles compelling and specific
- Front matter always includes Dedication and Acknowledgments
- Back matter always includes About the Author
- Respond in the same language specified in the parameters
"""


def parse_outline_json(text: str) -> Outline:
    """Parse outline from a JSON string, stripping markdown code fences if present."""
    # Strip markdown code fences
    clean = re.sub(r"```(?:json)?\s*", "", text).strip()
    # Find first { ... } block
    match = re.search(r"\{.*\}", clean, re.DOTALL)
    if not match:
        raise ValueError(f"Could not parse outline — no JSON object found in response")
    try:
        data = json.loads(match.group())
    except json.JSONDecodeError as e:
        raise ValueError(f"Could not parse outline — invalid JSON: {e}")

    try:
        chapters = [
            Chapter(
                number=ch["number"],
                title=ch["title"],
                sections=[
                    Section(title=s["title"], estimated_pages=s["estimated_pages"])
                    for s in ch.get("sections", [])
                ],
                estimated_pages=ch["estimated_pages"],
            )
            for ch in data["chapters"]
        ]

        return Outline(
            book_title=data["book_title"],
            author=data["author"],
            language=data["language"],
            front_matter=data.get("front_matter", ["Dedication", "Acknowledgments"]),
            chapters=chapters,
            back_matter=data.get("back_matter", ["About the Author"]),
            total_estimated_pages=data["total_estimated_pages"],
        )
    except (KeyError, TypeError) as e:
        raise ValueError(f"Could not parse outline — missing field: {e}")


def _format_outline_for_display(outline: Outline) -> str:
    lines = [
        f"\n{'='*60}",
        f"  📖 {outline.book_title}",
        f"  ✍️  {outline.author}  |  🌐 {outline.language}",
        f"  📄 ~{outline.total_estimated_pages} pages",
        f"{'='*60}",
        "",
        "FRONT MATTER",
    ]
    for item in outline.front_matter:
        lines.append(f"  • {item}")
    lines.append("")

    for ch in outline.chapters:
        lines.append(f"CHAPTER {ch.number}: {ch.title}  (~{ch.estimated_pages:.0f} pages)")
        for sec in ch.sections:
            lines.append(f"    └─ {sec.title}  (~{sec.estimated_pages:.1f} pages)")
        lines.append("")

    lines.append("BACK MATTER")
    for item in outline.back_matter:
        lines.append(f"  • {item}")
    lines.append(f"{'='*60}\n")
    return "\n".join(lines)


def generate_outline(params: BookParams, research_context: str, api_key: str) -> Outline:
    """Generate and interactively refine a book outline using Opus."""
    client = anthropic.Anthropic(api_key=api_key)

    user_prompt = (
        f"Create a book outline with these parameters:\n"
        f"- Theme: {params.theme}\n"
        f"- Title: {params.title}\n"
        f"- Author: {params.author}\n"
        f"- Target page range: {params.page_range}\n"
        f"- Language: {params.language}\n\n"
        f"Research context (use this to make the outline current and well-informed):\n"
        f"{research_context}"
    )

    messages = [{"role": "user", "content": user_prompt}]

    while True:
        print("\n⏳ Generating outline with Opus...")
        response = client.messages.create(
            model=PLANNER_MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=messages,
        )
        raw = response.content[0].text
        try:
            outline = parse_outline_json(raw)
        except ValueError as e:
            print(f"\n⚠  Could not parse outline: {e}\nRetrying...\n")
            continue

        print(_format_outline_for_display(outline))

        print("What would you like to do?")
        print("  [A] Approve this outline")
        print("  [E] Edit — describe what to change")
        print("  [R] Rewrite from scratch")
        choice = input("\nYour choice (A/E/R): ").strip().upper()

        if choice == "A":
            print("\n✅ Outline approved!\n")
            return outline
        elif choice == "R":
            messages = [{"role": "user", "content": user_prompt}]
            print("\n🔄 Rewriting outline from scratch...\n")
        elif choice == "E":
            edit_instruction = input("Describe your changes: ").strip()
            messages = [
                *messages,
                {"role": "assistant", "content": raw},
                {
                    "role": "user",
                    "content": (
                        f"Please revise the outline with these changes: {edit_instruction}\n"
                        f"Return the complete revised JSON outline."
                    ),
                },
            ]
            print("\n✏️  Refining outline...\n")
        else:
            print("Please enter A, E, or R.")
