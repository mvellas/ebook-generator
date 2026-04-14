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
    br = OxmlElement("w:br")
    br.set(qn("w:type"), "page")
    run._r.append(br)


def _set_run_font(run, name: str, size_pt: float, bold: bool = False) -> None:
    run.font.name = name
    run.font.size = Pt(size_pt)
    run.font.bold = bold


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
        title_para = doc.add_paragraph()
        title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = title_para.add_run(outline.book_title)
        _set_run_font(run, "Garamond", 36, bold=False)

        doc.add_paragraph()

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
        try:
            doc.add_paragraph(
                f"{chapter.number}  {chapter.title.upper()}",
                style=self.styles.chapter_title,
            )
        except KeyError:
            p = doc.add_paragraph(f"{chapter.number}  {chapter.title.upper()}")
            p.runs[0].font.size = Pt(14)

        doc.add_paragraph()

        image_map: dict[str, GeneratedImage] = {img.marker.full_match: img for img in images}

        image_pattern = re.compile(r"(\[IMAGE:[^\]]+\])")
        parts = image_pattern.split(text)

        is_first_para = True
        for part in parts:
            if image_pattern.match(part):
                img = image_map.get(part)
                if img:
                    self._embed_image(doc, img)
                else:
                    p = doc.add_paragraph()
                    run = p.add_run(part)
                    run.italic = True
                    _set_run_font(run, "Garamond", 10)
            else:
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
        pil_img = PILImage.open(buf)
        buf_out = _io.BytesIO()
        pil_img.save(buf_out, format="PNG")
        buf_out.seek(0)

        para = doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = para.add_run()
        run.add_picture(buf_out, width=Inches(4.0))

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
