#!/usr/bin/env python3

from __future__ import annotations

import io
import json
import re
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "pinterest_backlog.json"

HEADLINE_FONT_PATHS = [
    Path("/System/Library/Fonts/Supplemental/Georgia Bold.ttf"),
    Path("/System/Library/Fonts/Supplemental/Georgia.ttf"),
    Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
]
LABEL_FONT_PATHS = [
    Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
]

CARD_FILL = (251, 247, 242, 235)
SHADOW_FILL = (24, 29, 33, 70)
TEXT_FILL = (53, 45, 39, 255)
LABEL_FILL = (231, 78, 97, 255)


def load_posts() -> list[dict[str, Any]]:
    with DATA_PATH.open() as handle:
        return json.load(handle)


def load_font(paths: list[Path], size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in paths:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def image_path(relative_path: str) -> Path:
    return ROOT / relative_path.lstrip("/")


def resolve_source_image(post: dict[str, Any]) -> Path:
    relative = post.get("source_image")
    if relative:
        return image_path(relative)
    output_path = image_path(post["image"])
    return output_path.parent / "source" / output_path.name


def normalize_title(text: str) -> str:
    title = re.sub(r"\s*\((?:19|20)\d{2}\)\s*$", "", text).strip()
    title = re.sub(r"\s+in\s+(?:19|20)\d{2}\b", "", title).strip()
    title = title.replace(" & ", " and ")
    return re.sub(r"\s+", " ", title).strip()


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]

    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        candidate_box = draw.textbbox((0, 0), candidate, font=font)
        if candidate_box[2] <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def fit_headline(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
) -> tuple[ImageFont.ImageFont, list[str], int]:
    for size in range(84, 44, -2):
        font = load_font(HEADLINE_FONT_PATHS, size)
        lines = wrap_text(draw, text, font, max_width)
        if len(lines) > 3:
            continue

        spacing = max(8, size // 5)
        text_box = draw.multiline_textbbox((0, 0), "\n".join(lines), font=font, spacing=spacing)
        if text_box[2] <= max_width and text_box[3] <= 330:
            return font, lines, spacing

    font = load_font(HEADLINE_FONT_PATHS, 44)
    lines = wrap_text(draw, text, font, max_width)
    return font, lines[:3], 10


def draw_overlay(post: dict[str, Any]) -> bool:
    source_path = resolve_source_image(post)
    output_path = image_path(post["image"])
    if not source_path.exists():
        raise FileNotFoundError(f"Missing source image for {post['path']}: {source_path}")

    pin_title = normalize_title(post.get("pin_title") or post["title"])

    with Image.open(source_path) as image:
        canvas = image.convert("RGBA")

    width, height = canvas.size
    label_font = load_font(LABEL_FONT_PATHS, 26)
    scratch = Image.new("RGBA", (width, height))
    scratch_draw = ImageDraw.Draw(scratch)

    card_width = int(width * 0.82)
    padding_x = 54
    padding_top = 42
    padding_bottom = 46
    max_text_width = card_width - (padding_x * 2)

    headline_font, title_lines, line_spacing = fit_headline(scratch_draw, pin_title, max_text_width)
    label_box = scratch_draw.textbbox((0, 0), "THE TINY CART", font=label_font)
    title_box = scratch_draw.multiline_textbbox(
        (0, 0),
        "\n".join(title_lines),
        font=headline_font,
        spacing=line_spacing,
    )

    label_height = label_box[3] - label_box[1]
    title_height = title_box[3] - title_box[1]
    card_height = padding_top + label_height + 18 + title_height + padding_bottom
    card_x = int(width * 0.08)
    card_y = height - card_height - int(height * 0.075)
    card_bounds = (card_x, card_y, card_x + card_width, card_y + card_height)
    radius = 38

    shadow_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)
    shadow_bounds = (
        card_bounds[0] + 8,
        card_bounds[1] + 12,
        card_bounds[2] + 8,
        card_bounds[3] + 12,
    )
    shadow_draw.rounded_rectangle(shadow_bounds, radius=radius, fill=SHADOW_FILL)
    canvas = Image.alpha_composite(canvas, shadow_layer.filter(ImageFilter.GaussianBlur(18)))

    card_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    card_draw = ImageDraw.Draw(card_layer)
    card_draw.rounded_rectangle(card_bounds, radius=radius, fill=CARD_FILL)
    card_draw.rounded_rectangle(
        (card_x + padding_x, card_y + 30, card_x + padding_x + 110, card_y + 42),
        radius=6,
        fill=(231, 78, 97, 70),
    )

    text_x = card_x + padding_x
    label_y = card_y + padding_top
    card_draw.text(
        (text_x, label_y),
        "THE TINY CART",
        font=label_font,
        fill=LABEL_FILL,
    )
    title_y = label_y + label_height + 18
    card_draw.multiline_text(
        (text_x, title_y),
        "\n".join(title_lines),
        font=headline_font,
        fill=TEXT_FILL,
        spacing=line_spacing,
    )

    merged = Image.alpha_composite(canvas, card_layer).convert("RGB")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    buffer = io.BytesIO()
    merged.save(buffer, format="PNG", optimize=True)
    new_bytes = buffer.getvalue()
    old_bytes = output_path.read_bytes() if output_path.exists() else None
    if old_bytes == new_bytes:
        return False

    output_path.write_bytes(new_bytes)
    return True


def main() -> None:
    posts = load_posts()
    changed_count = 0
    for post in posts:
        if draw_overlay(post):
            changed_count += 1
    print(f"Rendered {len(posts)} Pinterest pin images ({changed_count} changed).")


if __name__ == "__main__":
    main()
