#!/usr/bin/env python3
# main.py
from __future__ import annotations
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    from cli.prompts import collect_book_params
    from pipeline.orchestrator import run

    try:
        params = collect_book_params()
        output_path = run(params)
        print(f"\n🎉 Done! Your book is ready: {output_path}\n")
    except KeyboardInterrupt:
        print("\n\n⛔ Cancelled by user.")
        sys.exit(0)
    except KeyError as e:
        print(f"\n❌ Missing environment variable: {e}")
        print("   Copy .env.example to .env and fill in your API keys.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
