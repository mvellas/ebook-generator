from unittest.mock import patch, MagicMock
from research.perplexity import research_topic


def test_research_topic_returns_string():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "AI is transforming industries in 2026."

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
