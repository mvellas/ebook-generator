import pytest
from unittest.mock import patch, MagicMock
from requests.exceptions import HTTPError
from research.perplexity import research_topic


def test_research_topic_returns_string():
    with patch("research.perplexity.requests.post") as mock_post:
        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": "AI is transforming industries in 2026."}}]
        }
        mock_post.return_value.raise_for_status = MagicMock()
        result = research_topic("artificial intelligence", api_key="test-key")

    assert isinstance(result, str)
    assert len(result) > 0


def test_research_topic_includes_theme_in_query():
    with patch("research.perplexity.requests.post") as mock_post:
        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": "Some research content."}}]
        }
        mock_post.return_value.raise_for_status = MagicMock()
        research_topic("quantum computing", api_key="test-key")

    call_args = mock_post.call_args
    body = call_args[1]["json"]
    assert any("quantum computing" in str(m.get("content", "")) for m in body["messages"])


def test_empty_theme_raises_value_error():
    with pytest.raises(ValueError, match="theme must be a non-empty string"):
        research_topic("", api_key="test-key")


def test_whitespace_only_theme_raises_value_error():
    with pytest.raises(ValueError, match="theme must be a non-empty string"):
        research_topic("   ", api_key="test-key")


def test_empty_api_key_raises_value_error():
    with pytest.raises(ValueError, match="api_key must be a non-empty string"):
        research_topic("artificial intelligence", api_key="")


def test_whitespace_only_api_key_raises_value_error():
    with pytest.raises(ValueError, match="api_key must be a non-empty string"):
        research_topic("artificial intelligence", api_key="   ")


def test_http_error_propagates():
    with patch("research.perplexity.requests.post") as mock_post:
        mock_post.return_value.raise_for_status.side_effect = HTTPError("401 Unauthorized")

        with pytest.raises(HTTPError, match="401 Unauthorized"):
            research_topic("artificial intelligence", api_key="test-key")


def test_missing_choices_key_raises_value_error():
    with patch("research.perplexity.requests.post") as mock_post:
        mock_post.return_value.json.return_value = {}
        mock_post.return_value.raise_for_status = MagicMock()

        with pytest.raises(ValueError, match="API response missing 'choices' key or empty choices list"):
            research_topic("artificial intelligence", api_key="test-key")


def test_empty_choices_list_raises_value_error():
    with patch("research.perplexity.requests.post") as mock_post:
        mock_post.return_value.json.return_value = {"choices": []}
        mock_post.return_value.raise_for_status = MagicMock()

        with pytest.raises(ValueError, match="API response missing 'choices' key or empty choices list"):
            research_topic("artificial intelligence", api_key="test-key")
