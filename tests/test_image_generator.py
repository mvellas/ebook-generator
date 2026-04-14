import pytest
from images.generator import extract_image_markers, ImageMarker


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
