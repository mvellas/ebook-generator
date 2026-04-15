PYTHON := .venv/bin/python
PIP    := .venv/bin/pip
LOG_DIR := logs

.PHONY: help install start test lint clean logs setup check

# ─── Default ────────────────────────────────────────────────────────────────

help:
	@echo ""
	@echo "  E-BOOK GENERATOR"
	@echo ""
	@echo "  make install   Install dependencies into .venv"
	@echo "  make start     Run the ebook generator CLI"
	@echo "  make test      Run the full test suite"
	@echo "  make lint      Check code style (ruff)"
	@echo "  make logs      Show the latest run log"
	@echo "  make clean     Remove .venv, __pycache__, .docx outputs"
	@echo "  make setup     First-time setup (venv + deps + .env)"
	@echo "  make check     Verify API keys are set in .env"
	@echo ""

# ─── Setup ──────────────────────────────────────────────────────────────────

setup: install
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "  .env created — fill in your API keys before running make start"; \
	else \
		echo "  .env already exists"; \
	fi

install:
	@echo "Installing dependencies..."
	@python3 -m venv .venv
	@$(PIP) install --quiet --upgrade pip
	@$(PIP) install --quiet -e ".[dev]"
	@echo "Done."

# ─── Run ────────────────────────────────────────────────────────────────────

start: check
	@mkdir -p $(LOG_DIR)
	@$(PYTHON) main.py 2>&1 | tee $(LOG_DIR)/run-$$(date +%Y%m%d-%H%M%S).log

# ─── Quality ────────────────────────────────────────────────────────────────

test:
	@$(PYTHON) -m pytest -v

lint:
	@$(PYTHON) -m ruff check . || true

# ─── Logs ───────────────────────────────────────────────────────────────────

logs:
	@if ls $(LOG_DIR)/*.log 1>/dev/null 2>&1; then \
		cat $$(ls -t $(LOG_DIR)/*.log | head -1); \
	else \
		echo "No logs found. Run 'make start' first."; \
	fi

# ─── Maintenance ────────────────────────────────────────────────────────────

clean:
	@echo "Cleaning..."
	@rm -rf .venv __pycache__ *.egg-info
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; true
	@find . -name "*.pyc" -delete
	@find . -maxdepth 1 -name "*.docx" ! -path "./docs/*" -delete
	@echo "Done."

check:
	@if [ ! -f .env ]; then \
		echo "ERROR: .env not found. Run 'make setup' first."; exit 1; \
	fi
	@$(PYTHON) -c "\
import os; from dotenv import load_dotenv; load_dotenv(); \
keys = ['ANTHROPIC_API_KEY','OPENAI_API_KEY','PERPLEXITY_API_KEY']; \
missing = [k for k in keys if not os.getenv(k)]; \
[print(f'ERROR: {k} not set in .env') for k in missing]; \
exit(1) if missing else print('API keys OK')"
