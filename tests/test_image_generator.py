import pytest
import base64
from unittest.mock import MagicMock, patch
import openai
from images.generator import extract_image_markers, ImageMarker, generate_images_for_chapter


def test_extract_image_markers_finds_single():
    text = "Some text.\n[IMAGE: A diagram showing neural network layers]\nMore text."
    markers = extract_image_markers(text)
    assert len(markers) == 1
    assert markers[0].description == "A diagram showing neural network layers"


def test_extract_image_markers_finds_multiple():
    text = (
        "Intro.\n[IMAGE: Chart of AI growth 2010-2026]\n"
        "Middle.\n[IMAGE: Photo of a robot arm in a factory]\nEnd."
    )
    markers = extract_image_markers(text)
    assert len(markers) == 2
    assert "Chart of AI growth" in markers[0].description
    assert "robot arm" in markers[1].description


def test_extract_image_markers_returns_empty_when_none():
    text = "No images here. Just plain text."
    markers = extract_image_markers(text)
    assert markers == []


def test_extract_image_markers_captures_position():
    text = "Before.\n[IMAGE: Test image]\nAfter."
    markers = extract_image_markers(text)
    assert markers[0].full_match == "[IMAGE: Test image]"


def test_generate_images_for_chapter_returns_empty_when_no_markers():
    result = generate_images_for_chapter("No markers here.", api_key="test-key")
    assert result == []


def test_generate_images_for_chapter_returns_generated_images():
    text = "Some text.\n[IMAGE: A neural network diagram]\nMore text."

    fake_bytes = b"fake-png-data"
    fake_b64 = base64.b64encode(fake_bytes).decode()

    mock_response = MagicMock()
    mock_response.data = [MagicMock(b64_json=fake_b64)]

    mock_client = MagicMock()
    mock_client.images.generate.return_value = mock_response

    with patch("images.generator.openai.OpenAI", return_value=mock_client):
        result = generate_images_for_chapter(text, api_key="test-key")

    assert len(result) == 1
    assert result[0].image_bytes == fake_bytes
    assert result[0].marker.description == "A neural network diagram"
