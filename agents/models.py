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
