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
