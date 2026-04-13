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
