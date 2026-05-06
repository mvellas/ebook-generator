# Ebook Generator

Ebook Generator is a Python CLI for producing Kindle-ready nonfiction ebooks with AI. It researches a topic, creates an editable outline, writes each chapter, generates chapter illustrations from `[IMAGE: ...]` markers, and exports a formatted `.docx` manuscript.

## Features

- Interactive command-line flow for book theme, title, author, target page range, and language.
- Current-topic research through Perplexity.
- AI-generated outline with an approval/edit/rewrite loop before chapter writing begins.
- Chapter drafting with Anthropic models.
- Optional AI illustrations generated from inline image placeholders.
- Kindle-style `.docx` export with title page, copyright, front matter, table of contents, chapters, about-the-author section, and optional references.
- Run logs and raw chapter debug files for easier review.

## Requirements

- Python 3.12 or newer
- API keys for:
  - Anthropic
  - OpenAI
  - Perplexity
- Optional Kindle `.docx` template, configured with `KINDLE_TEMPLATE_PATH`

## Installation

Clone the repository and enter the project directory:

```bash
git clone <repository-url>
cd ebook-generator
```

Run the first-time setup:

```bash
make setup
```

This creates a local virtual environment in `.venv`, installs the project with development dependencies, and creates `.env` from `.env.example` if it does not already exist.

If you prefer to install manually:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
cp .env.example .env
```

## Environment Configuration

Edit `.env` and add your API keys:

```env
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
PERPLEXITY_API_KEY=pplx-...
KINDLE_TEMPLATE_PATH=~/Desktop/5 x 8 in.docx
```

Required variables:

- `ANTHROPIC_API_KEY`: used for outline generation, chapter writing, about-the-author text, and citation formatting.
- `OPENAI_API_KEY`: used for image generation.
- `PERPLEXITY_API_KEY`: used for research.

Optional variables:

- `GEMINI_API_KEY`: reserved for future writer/model support. It is present in `.env.example` but is not required by the current pipeline.
- `KINDLE_TEMPLATE_PATH`: path to a Kindle `.docx` template. If the file is missing or invalid, the app falls back to built-in 5 x 8 inch page defaults.

You can verify the required keys with:

```bash
make check
```

## Usage

Start the generator:

```bash
make start
```

Or run the CLI directly:

```bash
source .venv/bin/activate
python main.py
```

The CLI asks for:

- Book theme
- Book title
- Author name
- Target page range, for example `100-120`
- Language, for example `English` or `Portuguese`

After research completes, the generator creates an outline and asks you to choose:

- `A`: approve the outline
- `E`: edit the outline by describing requested changes
- `R`: rewrite the outline from scratch

Once approved, the app writes each chapter, generates images where useful, and exports a `.docx` file in the repository root. The filename is based on the generated book title.

## How It Works

The pipeline runs in five main phases:

1. Research: `research/perplexity.py` queries Perplexity for current context, trends, data, and expert perspectives about the selected theme.
2. Outline: `agents/planner.py` asks Anthropic to produce a structured JSON outline, then lets you approve, edit, or regenerate it.
3. Writing: `agents/writer.py` writes each chapter from the outline and research context.
4. Images: `images/generator.py` extracts `[IMAGE: description]` markers from chapter text and generates print-friendly illustrations.
5. Export: `export/docx_builder.py` assembles the final manuscript as a `.docx`, using page dimensions from `KINDLE_TEMPLATE_PATH` when available.

## Outputs

Generated files are written locally:

- `<book-title>.docx`: final manuscript in the repository root.
- `debug/chapter_XX_raw.txt`: raw chapter drafts saved during generation.
- `logs/run-YYYYMMDD-HHMMSS.log`: full run logs when using `make start`.

Generated `.docx` files and secrets are ignored by Git through `.gitignore`.

## Make Commands

```bash
make help      # Show available commands
make setup     # Create .venv, install dependencies, and create .env
make install   # Create .venv and install dependencies
make check     # Verify required API keys are set
make start     # Run the interactive ebook generator
make test      # Run the test suite
make lint      # Run ruff checks if available
make logs      # Print the latest run log
make clean     # Remove local environment, caches, egg-info, and root .docx outputs
```

## Project Structure

```text
.
+-- agents/              # Book data models, outline planner, chapter writer
+-- cli/                 # Interactive CLI prompts
+-- export/              # Template reader and DOCX builder
+-- images/              # Image marker extraction and OpenAI image generation
+-- pipeline/            # End-to-end orchestration
+-- research/            # Perplexity research and citation formatting
+-- tests/               # Pytest test suite
+-- main.py              # CLI entrypoint
+-- Makefile             # Setup, run, test, and maintenance commands
+-- pyproject.toml       # Python package metadata and dependencies
`-- .env.example         # Environment variable template
```

## Testing

Run all tests with:

```bash
make test
```

Or directly:

```bash
source .venv/bin/activate
python -m pytest -v
```

## Troubleshooting

### `.env not found`

Run:

```bash
make setup
```

Then edit `.env` with your real API keys.

### Missing API key errors

Run:

```bash
make check
```

Make sure `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, and `PERPLEXITY_API_KEY` are present and non-empty in `.env`.

### Kindle template warning

If `KINDLE_TEMPLATE_PATH` points to a missing, invalid, or non-`.docx` file, the app prints a warning and uses built-in 5 x 8 inch defaults. Set the variable to a valid `.docx` template if you want custom page dimensions.

### Image generation skipped

Image generation errors are non-fatal. If OpenAI returns an error for an image prompt, the app logs the warning and continues building the ebook.

## Security Notes

Never commit `.env` or real API keys. The repository ignores `.env` by default, and `.env.example` should contain placeholders only.
