#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai",
#     "pillow",
# ]
# ///
"""
Generate images using Google's Gemini image models.

Usage:
    uv run image.py --prompt "A colorful abstract pattern" --output "./hero.png"
    uv run image.py --prompt "Minimalist icon" --output "./icon.png" --aspect landscape
    uv run image.py --prompt "Wide banner" --output "./banner.png" --aspect 21:9
    uv run image.py --prompt "Instagram post" --output "./post.png" --aspect 4:5
    uv run image.py --prompt "Similar style image" --output "./new.png" --reference "./existing.png"
    uv run image.py --prompt "High quality art" --output "./art.png" --model pro --size 2K

Supported aspect ratios:
    Aliases: square (1:1), landscape (16:9), portrait (9:16), wide (21:9), photo (4:3), photo-portrait (3:4)
    Direct:  1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9
"""

import argparse
import os
import sys

from google import genai
from google.genai import types
from PIL import Image

MODEL_IDS = {
    "flash": "gemini-2.5-flash-image",
    "pro": "gemini-3-pro-image-preview",
}

# API 지원 종횡비 전체 + 편의 별칭
ASPECT_RATIOS = {
    # 별칭 (편의용)
    "square": "1:1",
    "landscape": "16:9",
    "portrait": "9:16",
    "wide": "21:9",
    "photo": "4:3",
    "photo-portrait": "3:4",
    # 직접 비율 값
    "1:1": "1:1",
    "2:3": "2:3",
    "3:2": "3:2",
    "3:4": "3:4",
    "4:3": "4:3",
    "4:5": "4:5",
    "5:4": "5:4",
    "9:16": "9:16",
    "16:9": "16:9",
    "21:9": "21:9",
}

ASPECT_CHOICES = list(ASPECT_RATIOS.keys())


def get_aspect_instruction(aspect: str) -> str:
    """Return aspect ratio instruction for the prompt."""
    ratio = ASPECT_RATIOS.get(aspect, "1:1")
    return f"Generate an image with {ratio} aspect ratio."


def generate_image(
    prompt: str,
    output_path: str,
    aspect: str = "square",
    reference: str | None = None,
    model: str = "flash",
    size: str = "1K",
) -> None:
    """Generate an image using Gemini and save to output_path."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    aspect_instruction = get_aspect_instruction(aspect)
    full_prompt = f"{aspect_instruction} {prompt}"

    # Build contents with optional reference image
    contents: list = []
    if reference:
        if not os.path.exists(reference):
            print(f"Error: Reference image not found: {reference}", file=sys.stderr)
            sys.exit(1)
        ref_image = Image.open(reference)
        contents.append(ref_image)
        full_prompt = f"{full_prompt} Use the provided image as a reference for style, composition, or content."
    contents.append(full_prompt)

    model_id = MODEL_IDS[model]

    # Pro model supports additional config for resolution
    if model == "pro":
        config = types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio=ASPECT_RATIOS.get(aspect, "1:1"),
                image_size=size,
            ),
        )
        response = client.models.generate_content(
            model=model_id,
            contents=contents,
            config=config,
        )
    else:
        response = client.models.generate_content(
            model=model_id,
            contents=contents,
        )

    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Extract image from response
    for part in response.parts:
        if part.text is not None:
            print(f"Model response: {part.text}")
        elif part.inline_data is not None:
            image = part.as_image()
            image.save(output_path)
            print(f"Image saved to: {output_path}")
            return

    print("Error: No image data in response", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Generate images using Gemini (Flash or Pro)"
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help="Description of the image to generate",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output file path (PNG format)",
    )
    parser.add_argument(
        "--aspect",
        choices=ASPECT_CHOICES,
        default="square",
        help="Aspect ratio: square, landscape, portrait, wide, photo, photo-portrait, or direct ratios like 1:1, 16:9, 9:16, 4:3, 3:4, 3:2, 2:3, 5:4, 4:5, 21:9 (default: square)",
    )
    parser.add_argument(
        "--reference",
        help="Path to a reference image for style/composition guidance (optional)",
    )
    parser.add_argument(
        "--model",
        choices=["flash", "pro"],
        default="flash",
        help="Model: flash (fast, 1024px) or pro (high-quality, up to 4K) (default: flash)",
    )
    parser.add_argument(
        "--size",
        choices=["1K", "2K", "4K"],
        default="1K",
        help="Image resolution for pro model (default: 1K, ignored for flash)",
    )

    args = parser.parse_args()
    generate_image(args.prompt, args.output, args.aspect, args.reference, args.model, args.size)


if __name__ == "__main__":
    main()
