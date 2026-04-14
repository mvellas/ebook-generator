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
