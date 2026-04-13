# E-book Generator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python CLI that collects 5 book parameters, uses Opus to plan an outline, Haiku to write content, gpt-image-1 to generate embedded images, and outputs a Kindle-ready .docx file.

**Architecture:** Modular pipeline with dedicated modules per responsibility: `cli/` (input), `pipeline/` (orchestration), `agents/` (Opus planner + Haiku writer), `research/` (Perplexity), `images/` (gpt-image-1), `export/` (docx assembly). Each module has a single clear interface and can be tested independently.

**Tech Stack:** Python 3.12+, anthropic SDK, openai SDK, python-docx, Pillow, python-dotenv, requests, pytest

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `pyproject.toml` | Create | Project metadata + dependencies |
| `.env.example` | Create | API key template |
| `.gitignore` | Create | Ignore .env, __pycache__, *.docx output |
| `main.py` | Create | Entrypoint: wires CLI → pipeline |
| `cli/__init__.py` | Create | Package marker |
| `cli/prompts.py` | Create | Collect 5 fields, return BookParams |
| `pipeline/__init__.py` | Create | Package marker |
| `pipeline/orchestrator.py` | Create | Sequence phases, manage state |
| `agents/__init__.py` | Create | Package marker |
| `agents/models.py` | Create | BookParams, Section, Chapter, Outline dataclasses |
| `agents/planner.py` | Create | Opus: generate + refine outline |
| `agents/writer.py` | Create | Haiku: write one chapter with streaming |
| `research/__init__.py` | Create | Package marker |
| `research/perplexity.py` | Create | Perplexity sonar-pro web research |
| `images/__init__.py` | Create | Package marker |
| `images/generator.py` | Create | gpt-image-1: extract markers + generate images |
| `export/__init__.py` | Create | Package marker |
| `export/template_reader.py` | Create | Extract styles from Kindle .docx template |
| `export/docx_builder.py` | Create | Assemble final .docx with all content + images |
| `tests/__init__.py` | Create | Package marker |
| `tests/test_models.py` | Create | Tests for dataclasses |
| `tests/test_cli.py` | Create | Tests for input validation |
| `tests/test_perplexity.py` | Create | Tests for research module (mocked) |
| `tests/test_planner.py` | Create | Tests for planner (mocked Anthropic) |
| `tests/test_writer.py` | Create | Tests for writer (mocked Anthropic) |
| `tests/test_image_generator.py` | Create | Tests for image extraction + generation (mocked) |
| `tests/test_template_reader.py` | Create | Tests for template parsing |
| `tests/test_docx_builder.py` | Create | Tests for document assembly |

---

## Task 1: Project Scaffold

**Files:**
- Create: `pyproject.toml`
- Create: `.env.example`
- Create: `.gitignore`

- [ ] **Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["setuptools>=70"]
build-backend = "setuptools.build_meta"

[project]
name = "ebook-generator"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "anthropic>=0.91.0",
    "openai>=1.30.0",
    "google-generativeai>=0.5.0",
    "requests>=2.31.0",
    "python-docx>=1.1.0",
    "python-dotenv>=1.0.0",
    "pillow>=10.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-mock>=3.12.0",
]

[tool.setuptools.packages.find]
where = ["."]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--tb=short -q"
```

- [ ] **Step 2: Create .env.example**

```env
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
PERPLEXITY_API_KEY=pplx-...
KINDLE_TEMPLATE_PATH=~/Desktop/5 x 8 in.docx
```

- [ ] **Step 3: Create .gitignore**

```gitignore
.env
__pycache__/
*.pyc
*.egg-info/
.venv/
dist/
*.docx
!docs/**/*.docx
```

- [ ] **Step 4: Install dependencies**

```bash
cd "/Users/mvellasquez/Claude Projects/ebook-generator"
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Expected: all packages install without error.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml .env.example .gitignore
git commit -m "chore: project scaffold"
```

---

## Task 2: Data Models

**Files:**
- Create: `agents/__init__.py`
- Create: `agents/models.py`
- Create: `tests/__init__.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: Write failing tests**

Create `tests/__init__.py` (empty) and `tests/test_models.py`:

```python
from agents.models import BookParams, Section, Chapter, Outline


def test_book_params_fields():
    p = BookParams(
        theme="artificial intelligence",
        title="The AI Age",
        author="Jane Doe",
        page_range="100-120",
        language="English",
    )
    assert p.theme == "artificial intelligence"
    assert p.title == "The AI Age"
    assert p.author == "Jane Doe"
    assert p.page_range == "100-120"
    assert p.language == "English"


def test_section_fields():
    s = Section(title="Introduction to ML", estimated_pages=3.5)
    assert s.title == "Introduction to ML"
    assert s.estimated_pages == 3.5


def test_chapter_fields():
    s = Section(title="Overview", estimated_pages=2.0)
    c = Chapter(number=1, title="Getting Started", sections=[s], estimated_pages=10.0)
    assert c.number == 1
    assert c.title == "Getting Started"
    assert len(c.sections) == 1
    assert c.estimated_pages == 10.0


def test_outline_fields():
    s = Section(title="Overview", estimated_pages=2.0)
    c = Chapter(number=1, title="Chapter One", sections=[s], estimated_pages=10.0)
    o = Outline(
        book_title="My Book",
        author="Jane Doe",
        language="English",
        front_matter=["Dedication", "Acknowledgments"],
        chapters=[c],
        back_matter=["About the Author"],
        total_estimated_pages=120,
    )
    assert o.book_title == "My Book"
    assert len(o.chapters) == 1
    assert o.total_estimated_pages == 120
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_models.py -v
```

Expected: `ModuleNotFoundError: No module named 'agents'`

- [ ] **Step 3: Create agents/\_\_init\_\_.py (empty) and agents/models.py**

```python
# agents/__init__.py
```

```python
# agents/models.py
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class BookParams:
    theme: str
    title: str
    author: str
    page_range: str
    language: str


@dataclass
class Section:
    title: str
    estimated_pages: float


@dataclass
class Chapter:
    number: int
    title: str
    sections: list[Section]
    estimated_pages: float


@dataclass
class Outline:
    book_title: str
    author: str
    language: str
    front_matter: list[str]
    chapters: list[Chapter]
    back_matter: list[str]
    total_estimated_pages: int
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_models.py -v
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add agents/ tests/
git commit -m "feat(models): add BookParams, Section, Chapter, Outline dataclasses"
```

---

## Task 3: CLI Input Collection

**Files:**
- Create: `cli/__init__.py`
- Create: `cli/prompts.py`
- Create: `tests/test_cli.py`

- [ ] **Step 1: Write failing tests**

Create `cli/__init__.py` (empty) and `tests/test_cli.py`:

```python
from unittest.mock import patch
import pytest
from cli.prompts import collect_book_params
from agents.models import BookParams


def test_collect_book_params_returns_book_params():
    inputs = ["AI Ethics", "Ethics in the Machine", "John Smith", "100-120", "English"]
    with patch("builtins.input", side_effect=inputs):
        result = collect_book_params()
    assert isinstance(result, BookParams)
    assert result.theme == "AI Ethics"
    assert result.title == "Ethics in the Machine"
    assert result.author == "John Smith"
    assert result.page_range == "100-120"
    assert result.language == "English"


def test_collect_book_params_retries_empty_theme():
    inputs = ["", "AI Ethics", "Ethics in the Machine", "John Smith", "100-120", "English"]
    with patch("builtins.input", side_effect=inputs):
        result = collect_book_params()
    assert result.theme == "AI Ethics"


def test_collect_book_params_retries_empty_title():
    inputs = ["AI Ethics", "", "Ethics in the Machine", "John Smith", "100-120", "English"]
    with patch("builtins.input", side_effect=inputs):
        result = collect_book_params()
    assert result.title == "Ethics in the Machine"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_cli.py -v
```

Expected: `ModuleNotFoundError: No module named 'cli'`

- [ ] **Step 3: Implement cli/prompts.py**

```python
# cli/prompts.py
from agents.models import BookParams

BANNER = """
╔══════════════════════════════════════╗
║        E-BOOK GENERATOR  📚          ║
║   Kindle-Ready Books with AI         ║
╚══════════════════════════════════════╝
"""


def _ask(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("  ⚠  This field is required. Please try again.")


def collect_book_params() -> BookParams:
    print(BANNER)
    theme = _ask("📌 Theme (what is the book about?): ")
    title = _ask("📖 Title: ")
    author = _ask("✍️  Author name: ")
    page_range = _ask("📄 Target page range (e.g. 100-120): ")
    language = _ask("🌐 Language (e.g. English, Português): ")
    return BookParams(
        theme=theme,
        title=title,
        author=author,
        page_range=page_range,
        language=language,
    )
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_cli.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add cli/ tests/test_cli.py
git commit -m "feat(cli): add interactive book parameter collection"
```

---

## Task 4: Perplexity Research

**Files:**
- Create: `research/__init__.py`
- Create: `research/perplexity.py`
- Create: `tests/test_perplexity.py`

- [ ] **Step 1: Write failing tests**

Create `research/__init__.py` (empty) and `tests/test_perplexity.py`:

```python
from unittest.mock import patch, MagicMock
from research.perplexity import research_topic


def test_research_topic_returns_string():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "AI is transforming industries in 2026."

    with patch("research.perplexity.requests.post") as mock_post:
        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": "AI is transforming industries in 2026."}}]
        }
        mock_post.return_value.raise_for_status = MagicMock()
        result = research_topic("artificial intelligence", api_key="test-key")

    assert isinstance(result, str)
    assert len(result) > 0


def test_research_topic_includes_theme_in_query():
    with patch("research.perplexity.requests.post") as mock_post:
        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": "Some research content."}}]
        }
        mock_post.return_value.raise_for_status = MagicMock()
        research_topic("quantum computing", api_key="test-key")

    call_args = mock_post.call_args
    body = call_args[1]["json"]
    assert any("quantum computing" in str(m.get("content", "")) for m in body["messages"])
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_perplexity.py -v
```

Expected: `ModuleNotFoundError: No module named 'research'`

- [ ] **Step 3: Implement research/perplexity.py**

```python
# research/perplexity.py
from __future__ import annotations
import requests
from datetime import datetime


PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"


def research_topic(theme: str, api_key: str) -> str:
    """Query Perplexity sonar-pro for current context on the given theme."""
    year = datetime.now().year
    query = (
        f"{theme} — current context, key trends, recent data, and expert perspectives as of {year}. "
        f"Provide a comprehensive synthesis suitable for informing a book chapter."
    )

    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a research assistant. Provide a well-structured synthesis of current "
                    "knowledge on the given topic. Focus on facts, trends, and insights. "
                    "Do not include raw URLs or citations lists — integrate the information naturally."
                ),
            },
            {"role": "user", "content": query},
        ],
        "max_tokens": 2000,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    response = requests.post(PERPLEXITY_API_URL, json=payload, headers=headers, timeout=60)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_perplexity.py -v
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add research/ tests/test_perplexity.py
git commit -m "feat(research): add Perplexity sonar-pro web research"
```

---

## Task 5: Outline Planner (Opus)

**Files:**
- Create: `agents/planner.py`
- Create: `tests/test_planner.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_planner.py`:

```python
import json
from unittest.mock import MagicMock, patch
from agents.models import BookParams, Outline, Chapter, Section
from agents.planner import parse_outline_json, generate_outline


SAMPLE_OUTLINE_JSON = json.dumps({
    "book_title": "The AI Age",
    "author": "Jane Doe",
    "language": "English",
    "front_matter": ["Dedication", "Acknowledgments"],
    "chapters": [
        {
            "number": 1,
            "title": "The Dawn of AI",
            "sections": [
                {"title": "What is AI?", "estimated_pages": 3.0},
                {"title": "Brief History", "estimated_pages": 4.0},
            ],
            "estimated_pages": 10.0,
        }
    ],
    "back_matter": ["About the Author"],
    "total_estimated_pages": 110,
})


def test_parse_outline_json_returns_outline():
    outline = parse_outline_json(SAMPLE_OUTLINE_JSON)
    assert isinstance(outline, Outline)
    assert outline.book_title == "The AI Age"
    assert len(outline.chapters) == 1
    assert outline.chapters[0].number == 1
    assert len(outline.chapters[0].sections) == 2
    assert outline.total_estimated_pages == 110


def test_parse_outline_json_handles_json_in_markdown_block():
    wrapped = f"```json\n{SAMPLE_OUTLINE_JSON}\n```"
    outline = parse_outline_json(wrapped)
    assert outline.book_title == "The AI Age"


def test_parse_outline_json_raises_on_invalid():
    import pytest
    with pytest.raises(ValueError, match="Could not parse outline"):
        parse_outline_json("this is not json")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_planner.py -v
```

Expected: `ModuleNotFoundError: No module named 'agents.planner'`

- [ ] **Step 3: Implement agents/planner.py**

```python
# agents/planner.py
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
        outline = parse_outline_json(raw)

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
            messages.append({"role": "assistant", "content": raw})
            messages.append({
                "role": "user",
                "content": (
                    f"Please revise the outline with these changes: {edit_instruction}\n"
                    f"Return the complete revised JSON outline."
                ),
            })
            print("\n✏️  Refining outline...\n")
        else:
            print("Please enter A, E, or R.")
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_planner.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add agents/planner.py tests/test_planner.py
git commit -m "feat(agents): add Opus outline planner with interactive approval loop"
```

---

## Task 6: Chapter Writer (Haiku)

**Files:**
- Create: `agents/writer.py`
- Create: `tests/test_writer.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_writer.py`:

```python
from unittest.mock import MagicMock, patch
from agents.models import Chapter, Section, Outline, BookParams
from agents.writer import write_chapter, build_chapter_prompt


def _make_outline() -> Outline:
    sections = [
        Section(title="What is AI?", estimated_pages=3.0),
        Section(title="History of AI", estimated_pages=4.0),
    ]
    chapter = Chapter(number=1, title="The Dawn of AI", sections=sections, estimated_pages=10.0)
    return Outline(
        book_title="The AI Age",
        author="Jane Doe",
        language="English",
        front_matter=["Dedication"],
        chapters=[chapter],
        back_matter=["About the Author"],
        total_estimated_pages=110,
    )


def test_build_chapter_prompt_contains_chapter_title():
    outline = _make_outline()
    chapter = outline.chapters[0]
    prompt = build_chapter_prompt(chapter, outline, "Some research context")
    assert "The Dawn of AI" in prompt
    assert "What is AI?" in prompt
    assert "History of AI" in prompt


def test_build_chapter_prompt_contains_language():
    outline = _make_outline()
    chapter = outline.chapters[0]
    prompt = build_chapter_prompt(chapter, outline, "research")
    assert "English" in prompt


def test_build_chapter_prompt_contains_image_instruction():
    outline = _make_outline()
    chapter = outline.chapters[0]
    prompt = build_chapter_prompt(chapter, outline, "research")
    assert "[IMAGE:" in prompt
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_writer.py -v
```

Expected: `ModuleNotFoundError: No module named 'agents.writer'`

- [ ] **Step 3: Implement agents/writer.py**

```python
# agents/writer.py
from __future__ import annotations
import anthropic
from agents.models import Chapter, Outline

WRITER_MODEL = "claude-haiku-4-5-20251001"

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
    word_count = int(chapter.estimated_pages * 250)  # ~250 words per page

    return (
        f"Write Chapter {chapter.number}: \"{chapter.title}\"\n\n"
        f"Book: \"{outline.book_title}\" by {outline.author}\n"
        f"Language: {outline.language}\n"
        f"Target length: ~{chapter.estimated_pages:.0f} pages (~{word_count} words)\n\n"
        f"Sections to cover:\n{sections_list}\n\n"
        f"Research context to draw from:\n{research_context}\n\n"
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
        word_count=int(chapter.estimated_pages * 250),
    )
    user_prompt = build_chapter_prompt(chapter, outline, research_context)

    print(f"\n✍️  Writing Chapter {chapter.number}: {chapter.title}...")
    print("-" * 50)

    full_text = []
    with client.messages.stream(
        model=WRITER_MODEL,
        max_tokens=8192,
        system=system,
        messages=[{"role": "user", "content": user_prompt}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_text.append(text)

    print("\n" + "-" * 50)
    return "".join(full_text)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_writer.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add agents/writer.py tests/test_writer.py
git commit -m "feat(agents): add Haiku chapter writer with streaming"
```

---

## Task 7: Image Generator (gpt-image-1)

**Files:**
- Create: `images/__init__.py`
- Create: `images/generator.py`
- Create: `tests/test_image_generator.py`

- [ ] **Step 1: Write failing tests**

Create `images/__init__.py` (empty) and `tests/test_image_generator.py`:

```python
import pytest
from images.generator import extract_image_markers, ImageMarker


def test_extract_image_markers_finds_single():
    text = "Some text.\n[IMAGE: A diagram showing neural network layers]\nMore text."
    markers = extract_image_markers(text)
    assert len(markers) == 1
    assert markers[0].description == "A diagram showing neural network layers"


def test_extract_image_markers_finds_multiple():
    text = (
        "Intro.\n[IMAGE: Chart of AI growth 2010-2026]\n"
        "Middle.\n[IMAGE: Photo of a robot arm in a factory]\nEnd."
    )
    markers = extract_image_markers(text)
    assert len(markers) == 2
    assert "Chart of AI growth" in markers[0].description
    assert "robot arm" in markers[1].description


def test_extract_image_markers_returns_empty_when_none():
    text = "No images here. Just plain text."
    markers = extract_image_markers(text)
    assert markers == []


def test_extract_image_markers_captures_position():
    text = "Before.\n[IMAGE: Test image]\nAfter."
    markers = extract_image_markers(text)
    assert markers[0].full_match == "[IMAGE: Test image]"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_image_generator.py -v
```

Expected: `ModuleNotFoundError: No module named 'images'`

- [ ] **Step 3: Implement images/generator.py**

```python
# images/generator.py
from __future__ import annotations
import re
import base64
from dataclasses import dataclass
import openai

IMAGE_MODEL = "gpt-image-1"
IMAGE_SIZE = "1024x1024"


@dataclass
class ImageMarker:
    full_match: str
    description: str


@dataclass
class GeneratedImage:
    marker: ImageMarker
    image_bytes: bytes


def extract_image_markers(text: str) -> list[ImageMarker]:
    """Find all [IMAGE: description] markers in text."""
    pattern = re.compile(r"\[IMAGE:\s*([^\]]+)\]")
    return [
        ImageMarker(full_match=m.group(0), description=m.group(1).strip())
        for m in pattern.finditer(text)
    ]


def _build_image_prompt(description: str) -> str:
    return (
        f"Book illustration for a professional non-fiction publication. "
        f"Style: clean, editorial, high quality. "
        f"Subject: {description}. "
        f"No text overlays. Suitable for print at 300 DPI."
    )


def generate_images_for_chapter(
    chapter_text: str,
    api_key: str,
) -> list[GeneratedImage]:
    """Generate images for all [IMAGE: ...] markers found in chapter_text."""
    markers = extract_image_markers(chapter_text)
    if not markers:
        return []

    client = openai.OpenAI(api_key=api_key)
    results = []

    for marker in markers:
        print(f"\n🎨 Generating image: {marker.description[:60]}...")
        prompt = _build_image_prompt(marker.description)

        response = client.images.generate(
            model=IMAGE_MODEL,
            prompt=prompt,
            size=IMAGE_SIZE,
            quality="standard",
            n=1,
            response_format="b64_json",
        )

        image_b64 = response.data[0].b64_json
        image_bytes = base64.b64decode(image_b64)
        results.append(GeneratedImage(marker=marker, image_bytes=image_bytes))
        print(f"  ✅ Image generated ({len(image_bytes) // 1024} KB)")

    return results
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_image_generator.py -v
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add images/ tests/test_image_generator.py
git commit -m "feat(images): add gpt-image-1 image generation with marker extraction"
```

---

## Task 8: Template Reader

**Files:**
- Create: `export/__init__.py`
- Create: `export/template_reader.py`
- Create: `tests/test_template_reader.py`

- [ ] **Step 1: Write failing tests**

Create `export/__init__.py` (empty) and `tests/test_template_reader.py`:

```python
import pytest
from unittest.mock import MagicMock, patch
from export.template_reader import load_template_styles, TemplateStyles


def test_template_styles_has_required_fields():
    styles = TemplateStyles(
        chapter_title="CSP - Chapter Title",
        body_text="CSP - Chapter Body Text",
        first_paragraph="CSP - Chapter Body Text - First Paragraph",
        front_matter_body="CSP - Front Matter Body Text",
        page_width_inches=5.0,
        page_height_inches=8.0,
        margin_top_inches=0.76,
        margin_bottom_inches=0.76,
        margin_left_inches=0.76,
        margin_right_inches=0.60,
    )
    assert styles.chapter_title == "CSP - Chapter Title"
    assert styles.page_width_inches == 5.0
    assert styles.margin_right_inches == 0.60


def test_load_template_styles_returns_template_styles(tmp_path):
    # Create a minimal .docx to test file loading
    from docx import Document
    doc = Document()
    doc_path = tmp_path / "template.docx"
    doc.save(str(doc_path))

    # Should not raise even with a minimal docx (falls back to defaults)
    styles = load_template_styles(str(doc_path))
    assert isinstance(styles, TemplateStyles)
    assert styles.page_width_inches > 0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_template_reader.py -v
```

Expected: `ModuleNotFoundError: No module named 'export'`

- [ ] **Step 3: Implement export/template_reader.py**

```python
# export/template_reader.py
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from docx import Document
from docx.shared import Inches


@dataclass
class TemplateStyles:
    chapter_title: str
    body_text: str
    first_paragraph: str
    front_matter_body: str
    page_width_inches: float
    page_height_inches: float
    margin_top_inches: float
    margin_bottom_inches: float
    margin_left_inches: float
    margin_right_inches: float


# Kindle template defaults extracted from "5 x 8 in.docx"
_DEFAULTS = TemplateStyles(
    chapter_title="CSP - Chapter Title",
    body_text="CSP - Chapter Body Text",
    first_paragraph="CSP - Chapter Body Text - First Paragraph",
    front_matter_body="CSP - Front Matter Body Text",
    page_width_inches=5.0,
    page_height_inches=8.0,
    margin_top_inches=0.76,
    margin_bottom_inches=0.76,
    margin_left_inches=0.76,
    margin_right_inches=0.60,
)

_KNOWN_STYLE_NAMES = {
    "chapter_title": "CSP - Chapter Title",
    "body_text": "CSP - Chapter Body Text",
    "first_paragraph": "CSP - Chapter Body Text - First Paragraph",
    "front_matter_body": "CSP - Front Matter Body Text",
}


def load_template_styles(template_path: str) -> TemplateStyles:
    """Load page dimensions from the Kindle .docx template, falling back to known defaults."""
    path = Path(template_path).expanduser()
    if not path.exists():
        print(f"  ⚠  Template not found at {path}, using built-in defaults.")
        return _DEFAULTS

    doc = Document(str(path))
    section = doc.sections[0]

    try:
        width = section.page_width.inches
        height = section.page_height.inches
        top = section.top_margin.inches
        bottom = section.bottom_margin.inches
        left = section.left_margin.inches
        right = section.right_margin.inches
    except Exception:
        return _DEFAULTS

    return TemplateStyles(
        chapter_title=_KNOWN_STYLE_NAMES["chapter_title"],
        body_text=_KNOWN_STYLE_NAMES["body_text"],
        first_paragraph=_KNOWN_STYLE_NAMES["first_paragraph"],
        front_matter_body=_KNOWN_STYLE_NAMES["front_matter_body"],
        page_width_inches=width,
        page_height_inches=height,
        margin_top_inches=top,
        margin_bottom_inches=bottom,
        margin_left_inches=left,
        margin_right_inches=right,
    )
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_template_reader.py -v
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add export/template_reader.py export/__init__.py tests/test_template_reader.py
git commit -m "feat(export): add Kindle template style reader"
```

---

## Task 9: Docx Builder

**Files:**
- Create: `export/docx_builder.py`
- Create: `tests/test_docx_builder.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_docx_builder.py`:

```python
import io
import pytest
from docx import Document
from agents.models import BookParams, Outline, Chapter, Section
from export.template_reader import TemplateStyles, _DEFAULTS
from export.docx_builder import DocxBuilder


def _make_outline() -> Outline:
    sections = [Section(title="Overview", estimated_pages=3.0)]
    chapter = Chapter(number=1, title="The Beginning", sections=sections, estimated_pages=8.0)
    return Outline(
        book_title="Test Book",
        author="Test Author",
        language="English",
        front_matter=["Dedication", "Acknowledgments"],
        chapters=[chapter],
        back_matter=["About the Author"],
        total_estimated_pages=100,
    )


def test_build_creates_docx_bytes():
    outline = _make_outline()
    chapter_texts = {1: "This is chapter one content. It has some text."}
    chapter_images = {1: []}

    builder = DocxBuilder(styles=_DEFAULTS)
    result = builder.build(
        outline=outline,
        chapter_texts=chapter_texts,
        chapter_images=chapter_images,
        about_author="Test author bio.",
    )

    assert isinstance(result, bytes)
    assert len(result) > 0
    # Verify it's a valid docx
    doc = Document(io.BytesIO(result))
    assert doc is not None


def test_build_includes_title_and_author():
    outline = _make_outline()
    builder = DocxBuilder(styles=_DEFAULTS)
    result = builder.build(
        outline=outline,
        chapter_texts={1: "Chapter content here."},
        chapter_images={1: []},
        about_author="Bio text.",
    )
    doc = Document(io.BytesIO(result))
    all_text = "\n".join(p.text for p in doc.paragraphs)
    assert "Test Book" in all_text
    assert "Test Author" in all_text


def test_build_includes_chapter_title():
    outline = _make_outline()
    builder = DocxBuilder(styles=_DEFAULTS)
    result = builder.build(
        outline=outline,
        chapter_texts={1: "Chapter content here."},
        chapter_images={1: []},
        about_author="Bio.",
    )
    doc = Document(io.BytesIO(result))
    all_text = "\n".join(p.text for p in doc.paragraphs)
    assert "The Beginning" in all_text
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_docx_builder.py -v
```

Expected: `ModuleNotFoundError: No module named 'export.docx_builder'`

- [ ] **Step 3: Implement export/docx_builder.py**

```python
# export/docx_builder.py
from __future__ import annotations
import io
import re
from dataclasses import dataclass
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from agents.models import Outline
from export.template_reader import TemplateStyles
from images.generator import GeneratedImage


def _add_page_break(doc: Document) -> None:
    para = doc.add_paragraph()
    run = para.add_run()
    run.add_break(docx_break_type=None)
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    br = OxmlElement("w:br")
    br.set(qn("w:type"), "page")
    run._r.append(br)


def _set_run_font(run, name: str, size_pt: float, bold: bool = False) -> None:
    run.font.name = name
    run.font.size = Pt(size_pt)
    run.font.bold = bold


def _add_styled_paragraph(doc: Document, text: str, style_name: str) -> None:
    """Add paragraph with a named style, falling back to Normal if style missing."""
    try:
        para = doc.add_paragraph(text, style=style_name)
    except KeyError:
        para = doc.add_paragraph(text)
    return para


@dataclass
class DocxBuilder:
    styles: TemplateStyles

    def build(
        self,
        outline: Outline,
        chapter_texts: dict[int, str],
        chapter_images: dict[int, list[GeneratedImage]],
        about_author: str,
    ) -> bytes:
        doc = Document()

        # Page setup
        for section in doc.sections:
            section.page_width = Inches(self.styles.page_width_inches)
            section.page_height = Inches(self.styles.page_height_inches)
            section.top_margin = Inches(self.styles.margin_top_inches)
            section.bottom_margin = Inches(self.styles.margin_bottom_inches)
            section.left_margin = Inches(self.styles.margin_left_inches)
            section.right_margin = Inches(self.styles.margin_right_inches)

        self._add_title_page(doc, outline)
        _add_page_break(doc)
        self._add_copyright(doc, outline)
        _add_page_break(doc)
        self._add_front_matter_section(doc, "DEDICATION", "For all curious minds.")
        _add_page_break(doc)
        self._add_front_matter_section(doc, "ACKNOWLEDGMENTS", "")
        _add_page_break(doc)
        self._add_contents(doc, outline)
        _add_page_break(doc)

        for chapter in outline.chapters:
            text = chapter_texts.get(chapter.number, "")
            images = chapter_images.get(chapter.number, [])
            self._add_chapter(doc, chapter, text, images)
            _add_page_break(doc)

        self._add_about_author(doc, about_author)

        buf = io.BytesIO()
        doc.save(buf)
        return buf.getvalue()

    def _add_title_page(self, doc: Document, outline: Outline) -> None:
        # Book title
        title_para = doc.add_paragraph()
        title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = title_para.add_run(outline.book_title)
        _set_run_font(run, "Garamond", 36, bold=False)

        doc.add_paragraph()

        # Author
        author_para = doc.add_paragraph()
        author_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = author_para.add_run(outline.author)
        _set_run_font(run, "Garamond", 18)

    def _add_copyright(self, doc: Document, outline: Outline) -> None:
        from datetime import datetime
        year = datetime.now().year
        lines = [
            f"Copyright © {year} {outline.author}",
            "All rights reserved.",
            "",
            "No part of this publication may be reproduced, distributed, or transmitted "
            "in any form or by any means without the prior written permission of the author.",
        ]
        for line in lines:
            para = doc.add_paragraph()
            run = para.add_run(line)
            _set_run_font(run, "Garamond", 10)

    def _add_front_matter_section(self, doc: Document, heading: str, body: str) -> None:
        try:
            doc.add_paragraph(heading, style=self.styles.chapter_title)
        except KeyError:
            p = doc.add_paragraph(heading)
            p.runs[0].font.size = Pt(14)

        doc.add_paragraph()
        if body:
            try:
                doc.add_paragraph(body, style=self.styles.front_matter_body)
            except KeyError:
                doc.add_paragraph(body)

    def _add_contents(self, doc: Document, outline: Outline) -> None:
        try:
            doc.add_paragraph("CONTENTS", style=self.styles.chapter_title)
        except KeyError:
            doc.add_paragraph("CONTENTS")

        doc.add_paragraph()
        for ch in outline.chapters:
            p = doc.add_paragraph()
            run = p.add_run(f"{ch.number}. {ch.title}")
            _set_run_font(run, "Garamond", 11)

    def _add_chapter(
        self,
        doc: Document,
        chapter,
        text: str,
        images: list[GeneratedImage],
    ) -> None:
        # Chapter title
        try:
            doc.add_paragraph(
                f"{chapter.number}  {chapter.title.upper()}",
                style=self.styles.chapter_title,
            )
        except KeyError:
            p = doc.add_paragraph(f"{chapter.number}  {chapter.title.upper()}")
            p.runs[0].font.size = Pt(14)

        doc.add_paragraph()

        # Build image lookup by full match string
        image_map: dict[str, GeneratedImage] = {img.marker.full_match: img for img in images}

        # Split text on [IMAGE: ...] markers and interleave images
        image_pattern = re.compile(r"(\[IMAGE:[^\]]+\])")
        parts = image_pattern.split(text)

        is_first_para = True
        for i, part in enumerate(parts):
            if image_pattern.match(part):
                # Insert image
                img = image_map.get(part)
                if img:
                    self._embed_image(doc, img)
                else:
                    # No generated image — insert italic placeholder
                    p = doc.add_paragraph()
                    run = p.add_run(part)
                    run.italic = True
                    _set_run_font(run, "Garamond", 10)
            else:
                # Split into paragraphs
                paragraphs = [p.strip() for p in part.split("\n\n") if p.strip()]
                for para_text in paragraphs:
                    if is_first_para:
                        try:
                            doc.add_paragraph(para_text, style=self.styles.first_paragraph)
                        except KeyError:
                            doc.add_paragraph(para_text)
                        is_first_para = False
                    else:
                        try:
                            doc.add_paragraph(para_text, style=self.styles.body_text)
                        except KeyError:
                            doc.add_paragraph(para_text)

    def _embed_image(self, doc: Document, img: GeneratedImage) -> None:
        import io as _io
        from PIL import Image as PILImage

        buf = _io.BytesIO(img.image_bytes)
        # Resize to max 4x4 inches for Kindle print
        pil_img = PILImage.open(buf)
        buf_out = _io.BytesIO()
        pil_img.save(buf_out, format="PNG")
        buf_out.seek(0)

        para = doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = para.add_run()
        run.add_picture(buf_out, width=Inches(4.0))

        # Caption
        caption_para = doc.add_paragraph()
        caption_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        caption_run = caption_para.add_run(img.marker.description)
        caption_run.italic = True
        _set_run_font(caption_run, "Garamond", 9)

    def _add_about_author(self, doc: Document, bio: str) -> None:
        try:
            doc.add_paragraph("ABOUT THE AUTHOR", style=self.styles.chapter_title)
        except KeyError:
            doc.add_paragraph("ABOUT THE AUTHOR")

        doc.add_paragraph()
        try:
            doc.add_paragraph(bio, style=self.styles.front_matter_body)
        except KeyError:
            doc.add_paragraph(bio)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_docx_builder.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add export/docx_builder.py tests/test_docx_builder.py
git commit -m "feat(export): add DocxBuilder — assembles Kindle-ready .docx with embedded images"
```

---

## Task 10: Pipeline Orchestrator

**Files:**
- Create: `pipeline/__init__.py`
- Create: `pipeline/orchestrator.py`

- [ ] **Step 1: Implement pipeline/orchestrator.py**

No unit test for orchestrator (it's a pure integration coordinator — its correctness is validated end-to-end in Task 11).

```python
# pipeline/orchestrator.py
from __future__ import annotations
import os
import re
from pathlib import Path
from agents.models import BookParams, Outline
from agents.planner import generate_outline
from agents.writer import write_chapter
from research.perplexity import research_topic
from images.generator import generate_images_for_chapter
from export.template_reader import load_template_styles
from export.docx_builder import DocxBuilder


def _sanitize_filename(title: str) -> str:
    return re.sub(r"[^\w\s-]", "", title).strip().replace(" ", "-").lower()


def run(params: BookParams) -> Path:
    """Execute all 5 pipeline phases and return path to the generated .docx."""
    anthropic_key = os.environ["ANTHROPIC_API_KEY"]
    openai_key = os.environ["OPENAI_API_KEY"]
    perplexity_key = os.environ["PERPLEXITY_API_KEY"]
    template_path = os.environ.get(
        "KINDLE_TEMPLATE_PATH", str(Path.home() / "Desktop" / "5 x 8 in.docx")
    )

    # Phase 1 — Research
    print("\n[1/5] 🔍 Researching topic with Perplexity...")
    research = research_topic(params.theme, api_key=perplexity_key)
    print(f"  ✅ Research complete ({len(research)} chars)")

    # Phase 2 — Outline
    print("\n[2/5] 🧠 Generating outline with Opus...")
    outline: Outline = generate_outline(params, research, api_key=anthropic_key)

    # Phase 3 + 4 — Write + generate images per chapter
    chapter_texts: dict[int, str] = {}
    chapter_images: dict[int, list] = {}
    total = len(outline.chapters)

    for i, chapter in enumerate(outline.chapters, 1):
        print(f"\n[3/5] ✍️  Writing chapter {i}/{total}...")
        text = write_chapter(chapter, outline, research, api_key=anthropic_key)
        chapter_texts[chapter.number] = text

        print(f"\n[4/5] 🎨 Generating images for chapter {i}/{total}...")
        images = generate_images_for_chapter(text, api_key=openai_key)
        chapter_images[chapter.number] = images

    # About the author (brief, generated by Haiku)
    from anthropic import Anthropic
    client = Anthropic(api_key=anthropic_key)
    print("\n  ✍️  Writing 'About the Author' section...")
    about_resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": (
                f"Write a short 'About the Author' bio (2-3 sentences) for "
                f"{outline.author}, author of '{outline.book_title}'. "
                f"Write in {outline.language}. Professional and engaging."
            ),
        }],
    )
    about_author = about_resp.content[0].text

    # Phase 5 — Export
    print("\n[5/5] 📄 Assembling .docx...")
    styles = load_template_styles(template_path)
    builder = DocxBuilder(styles=styles)
    docx_bytes = builder.build(
        outline=outline,
        chapter_texts=chapter_texts,
        chapter_images=chapter_images,
        about_author=about_author,
    )

    filename = f"{_sanitize_filename(outline.book_title)}.docx"
    output_path = Path.cwd() / filename
    output_path.write_bytes(docx_bytes)

    print(f"\n✅ Book saved: {output_path}")
    return output_path
```

- [ ] **Step 2: Create pipeline/\_\_init\_\_.py (empty)**

- [ ] **Step 3: Commit**

```bash
git add pipeline/ 
git commit -m "feat(pipeline): add orchestrator — sequences all 5 phases"
```

---

## Task 11: Entrypoint + Final Integration

**Files:**
- Create: `main.py`

- [ ] **Step 1: Create main.py**

```python
#!/usr/bin/env python3
# main.py
from __future__ import annotations
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    from cli.prompts import collect_book_params
    from pipeline.orchestrator import run

    try:
        params = collect_book_params()
        output_path = run(params)
        print(f"\n🎉 Done! Your book is ready: {output_path}\n")
    except KeyboardInterrupt:
        print("\n\n⛔ Cancelled by user.")
        sys.exit(0)
    except KeyError as e:
        print(f"\n❌ Missing environment variable: {e}")
        print("   Copy .env.example to .env and fill in your API keys.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run full test suite**

```bash
pytest -v
```

Expected: all tests pass.

- [ ] **Step 3: Smoke test with real API keys**

Copy `.env.example` to `.env`, fill in real keys, then:

```bash
python main.py
```

Enter sample values:
- Theme: `artificial intelligence in healthcare`
- Title: `AI Heals`  
- Author: `Your Name`
- Page range: `80-100`
- Language: `English`

Expected: CLI shows progress through all 5 phases, outputs `ai-heals.docx` in current directory.

- [ ] **Step 4: Commit**

```bash
git add main.py
git commit -m "feat: add main entrypoint — e-book generator CLI complete"
```

---

## Self-Review

**Spec coverage check:**
- ✅ 5-field CLI input (Task 3)
- ✅ Perplexity sonar-pro research (Task 4)
- ✅ Opus outline generation with A/E/R loop (Task 5)
- ✅ Haiku chapter writing with streaming (Task 6)
- ✅ gpt-image-1 image generation + extraction (Task 7)
- ✅ Template style reader from `5 x 8 in.docx` (Task 8)
- ✅ DocxBuilder with full document structure (Task 9)
- ✅ Pipeline orchestrator sequencing all phases (Task 10)
- ✅ Entrypoint with env loading + error handling (Task 11)
- ✅ All API keys: ANTHROPIC, OPENAI, GEMINI (reserved), PERPLEXITY (Task 1)
- ✅ KINDLE_TEMPLATE_PATH env var with default (Task 8)

**Type consistency:**
- `BookParams`, `Outline`, `Chapter`, `Section` defined in Task 2, used consistently through Tasks 5–10
- `ImageMarker`, `GeneratedImage` defined in Task 7, used in Task 9
- `TemplateStyles` defined in Task 8, used in Task 9–10
- `DocxBuilder` takes `styles: TemplateStyles` — consistent across Tasks 9 and 10
- `chapter_texts: dict[int, str]` and `chapter_images: dict[int, list[GeneratedImage]]` keyed by `chapter.number` — consistent in Tasks 10 and 9

**No placeholders found.** All steps have concrete code.
