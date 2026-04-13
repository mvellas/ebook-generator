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
