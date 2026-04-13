from unittest.mock import patch
import pytest
from cli.prompts import collect_book_params
from agents.models import BookParams


def test_collect_book_params_returns_book_params():
    inputs = ["AI Ethics", "Ethics in the Machine", "John Smith", "100-120", "English"]
    with patch("builtins.input", side_effect=inputs):
        result = collect_book_params()
    assert isinstance(result, BookParams)
    assert result.theme == "AI Ethics"
    assert result.title == "Ethics in the Machine"
    assert result.author == "John Smith"
    assert result.page_range == "100-120"
    assert result.language == "English"


def test_collect_book_params_retries_empty_theme():
    inputs = ["", "AI Ethics", "Ethics in the Machine", "John Smith", "100-120", "English"]
    with patch("builtins.input", side_effect=inputs):
        result = collect_book_params()
    assert result.theme == "AI Ethics"


def test_collect_book_params_retries_empty_title():
    inputs = ["AI Ethics", "", "Ethics in the Machine", "John Smith", "100-120", "English"]
    with patch("builtins.input", side_effect=inputs):
        result = collect_book_params()
    assert result.title == "Ethics in the Machine"
