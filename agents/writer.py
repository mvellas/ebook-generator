from __future__ import annotations
import anthropic
from agents.models import Chapter, Outline

WRITER_MODEL = "claude-haiku-4-5-20251001"
WORDS_PER_PAGE = 250

SYSTEM_PROMPT_TEMPLATE = """You are a professional book author writing in {language}.

Your task is to write a complete, engaging book chapter. Follow these rules:
1. Write in {language} — every word, heading, and sentence
2. Write ~{estimated_pages} pages of content (approximately {word_count} words)
3. Use clear, engaging prose suitable for a general educated audience
4. Include section headings that match the outline exactly
5. Where a visual would genuinely help understanding, insert a placeholder on its own line:
   [IMAGE: detailed description of what the image should show, style, and purpose]
   Use at most 2 images per chapter, only where truly valuable.
6. Start each section directly — no meta-commentary about what you're about to write
7. Do not include a chapter number heading — the title formatting is handled separately
"""


def build_chapter_prompt(chapter: Chapter, outline: Outline, research_context: str) -> str:
    sections_list = "\n".join(
        f"  {i+1}. {s.title} (~{s.estimated_pages:.1f} pages)"
        for i, s in enumerate(chapter.sections)
    )
    word_count = int(chapter.estimated_pages * WORDS_PER_PAGE)

    return (
        f"Write Chapter {chapter.number}: \"{chapter.title}\"\n\n"
        f"Book: \"{outline.book_title}\" by {outline.author}\n"
        f"Language: {outline.language}\n"
        f"Target length: ~{chapter.estimated_pages:.0f} pages (~{word_count} words)\n\n"
        f"Sections to cover:\n{sections_list}\n\n"
        f"Research context to draw from:\n{research_context}\n\n"
        f"Where visuals would help: Use [IMAGE: description] placeholders on their own lines.\n\n"
        f"Write the full chapter now, in {outline.language}."
    )


def write_chapter(
    chapter: Chapter,
    outline: Outline,
    research_context: str,
    api_key: str,
) -> str:
    """Write a single chapter using Haiku with streaming output."""
    client = anthropic.Anthropic(api_key=api_key)

    system = SYSTEM_PROMPT_TEMPLATE.format(
        language=outline.language,
        estimated_pages=chapter.estimated_pages,
        word_count=int(chapter.estimated_pages * WORDS_PER_PAGE),
    )
    user_prompt = build_chapter_prompt(chapter, outline, research_context)

    print(f"\n✍️  Writing Chapter {chapter.number}: {chapter.title}...")
    print("-" * 50)

    full_text = []
    try:
        with client.messages.stream(
            model=WRITER_MODEL,
            max_tokens=8192,
            system=system,
            messages=[{"role": "user", "content": user_prompt}],
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
                full_text.append(text)
    except anthropic.APIError as e:
        raise RuntimeError(f"Failed to write chapter {chapter.number}: {e}") from e

    print("\n" + "-" * 50)
    return "".join(full_text)
