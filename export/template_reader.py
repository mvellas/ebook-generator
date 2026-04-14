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
        print(f"  Warning: Template not found at {path}, using built-in defaults.")
        return _DEFAULTS

    try:
        doc = Document(str(path))
        section = doc.sections[0]

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
