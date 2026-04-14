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
