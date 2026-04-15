# images/generator.py
from __future__ import annotations
import re
import base64
from dataclasses import dataclass
import requests
import openai

IMAGE_MODEL = "gpt-image-1"
IMAGE_SIZE = "1024x1024"
IMAGE_QUALITY = "medium"


@dataclass
class ImageMarker:
    full_match: str
    description: str


@dataclass
class GeneratedImage:
    marker: ImageMarker
    image_bytes: bytes


def extract_image_markers(text: str) -> list[ImageMarker]:
    """Find all [IMAGE: description] markers in text."""
    pattern = re.compile(r"\[IMAGE:\s*([^\]]+)\]")
    return [
        ImageMarker(full_match=m.group(0), description=m.group(1).strip())
        for m in pattern.finditer(text)
    ]


def _build_image_prompt(description: str) -> str:
    return (
        f"Book illustration for a professional non-fiction publication. "
        f"Style: clean, editorial, high quality. "
        f"Subject: {description}. "
        f"No text overlays. Suitable for print at 300 DPI."
    )


def generate_images_for_chapter(
    chapter_text: str,
    api_key: str,
) -> list[GeneratedImage]:
    """Generate images for all [IMAGE: ...] markers found in chapter_text."""
    markers = extract_image_markers(chapter_text)
    if not markers:
        return []

    client = openai.OpenAI(api_key=api_key)
    results = []

    for marker in markers:
        print(f"\n🎨 Generating image: {marker.description[:60]}...")
        prompt = _build_image_prompt(marker.description)

        try:
            response = client.images.generate(
                model=IMAGE_MODEL,
                prompt=prompt,
                size=IMAGE_SIZE,
                quality=IMAGE_QUALITY,
                n=1,
            )

            data = response.data[0]
            if data.b64_json:
                image_bytes = base64.b64decode(data.b64_json)
            elif data.url:
                image_bytes = requests.get(data.url, timeout=30).content
            else:
                raise ValueError("API returned no image data (no b64_json or url)")
            results.append(GeneratedImage(marker=marker, image_bytes=image_bytes))
            print(f"  ✅ Image generated ({len(image_bytes) // 1024} KB)")
        except openai.OpenAIError as e:
            print(f"  ⚠  Skipping image for '{marker.description[:40]}...': {e}")

    return results
