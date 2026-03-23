#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
PRINTABLES = ROOT / "images" / "printables"
LOGO = ROOT / "images" / "logo-small.png"
FONT_SERIF = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
FONT_SANS = "/System/Library/Fonts/Supplemental/GillSans.ttc"
SIZE = (1200, 1500)


PRODUCTS = [
    {
        "slug": "family-meal-planner",
        "category": "MEAL PLANNING",
        "title": ["Family Meals", "& Lunches"],
        "subtitle": "calm weekly system",
        "accent": "#cb7e62",
        "accent_soft": "#f0d8d2",
        "glow": "#dccfc3",
        "preview_main": "preview-weekly-planner.png",
        "preview_back": "preview-overview.png",
    },
    {
        "slug": "kids-routine-chart",
        "category": "ROUTINES",
        "title": ["Kids Routines", "& Responsibilities"],
        "subtitle": "clearer daily flow",
        "accent": "#71816d",
        "accent_soft": "#dce5da",
        "glow": "#d8ddd2",
        "preview_main": "preview-morning-flow.png",
        "preview_back": "preview-overview.png",
    },
    {
        "slug": "playroom-organization-labels",
        "category": "ORGANIZATION",
        "title": ["Playroom Labels", "+ Rotation"],
        "subtitle": "simpler cleanup",
        "accent": "#c6a06a",
        "accent_soft": "#efe0c8",
        "glow": "#e5dbc8",
        "preview_main": "preview-category-grid.png",
        "preview_back": "preview-overview.png",
    },
    {
        "slug": "lunchbox-notes",
        "category": "LUNCHBOX NOTES",
        "title": ["Lunchbox Notes", "+ Joke Cards"],
        "subtitle": "warmer school lunches",
        "accent": "#c77063",
        "accent_soft": "#f4ddd8",
        "glow": "#e6d7d0",
        "preview_main": "preview-encouragement-notes.png",
        "preview_back": "preview-overview.png",
    },
    {
        "slug": "baby-registry-planner",
        "category": "NEW BABY",
        "title": ["Baby Registry", "+ First Week"],
        "subtitle": "calmer priorities",
        "accent": "#9a8c78",
        "accent_soft": "#ede4da",
        "glow": "#e6ddd3",
        "preview_main": "preview-priorities.png",
        "preview_back": "preview-overview.png",
    },
]


def hex_to_rgba(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size)


def fit_preview(path: Path, size: tuple[int, int]) -> Image.Image:
    image = Image.open(path).convert("RGBA")
    return ImageOps.contain(image, size, Image.Resampling.LANCZOS)


def add_shadow(base: Image.Image, rect: tuple[int, int, int, int], radius: int, opacity: int = 46) -> Image.Image:
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)
    draw.rounded_rectangle(rect, radius=radius, fill=(34, 30, 25, opacity))
    shadow = shadow.filter(ImageFilter.GaussianBlur(28))
    return Image.alpha_composite(base, shadow)


def draw_preview_card(canvas: Image.Image, preview: Image.Image, box: tuple[int, int, int, int], radius: int, rotate: float = 0) -> None:
    x0, y0, x1, y1 = box
    card = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)
    draw.rounded_rectangle((0, 0, card.width, card.height), radius=radius, fill=(255, 255, 255, 245), outline=(228, 219, 207, 255), width=2)

    inner = Image.new("RGBA", (card.width, card.height), (0, 0, 0, 0))
    px = (card.width - preview.width) // 2
    py = (card.height - preview.height) // 2
    inner.alpha_composite(preview, (px, py))
    card = Image.alpha_composite(card, inner)

    if rotate:
        card = card.rotate(rotate, resample=Image.Resampling.BICUBIC, expand=True)
    ox = x0 - (card.width - (x1 - x0)) // 2
    oy = y0 - (card.height - (y1 - y0)) // 2
    canvas.alpha_composite(card, (ox, oy))


def build_thumb(config: dict[str, str]) -> None:
    folder = PRINTABLES / config["slug"]
    thumb_path = folder / "thumb.png"
    main_preview = fit_preview(folder / config["preview_main"], (430, 560))
    back_preview = fit_preview(folder / config["preview_back"], (320, 430))

    canvas = Image.new("RGBA", SIZE, hex_to_rgba("#f7f1ea"))
    glow = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse((-120, 980, 660, 1760), fill=hex_to_rgba(config["accent_soft"], 120))
    gdraw.ellipse((730, -80, 1460, 620), fill=hex_to_rgba(config["glow"], 120))
    gdraw.ellipse((860, 1050, 1380, 1530), fill=hex_to_rgba(config["accent"], 40))
    glow = glow.filter(ImageFilter.GaussianBlur(48))
    canvas = Image.alpha_composite(canvas, glow)

    frame = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    fdraw = ImageDraw.Draw(frame)
    fdraw.rounded_rectangle((34, 34, SIZE[0] - 34, SIZE[1] - 34), radius=46, outline=(230, 221, 209, 255), width=3)
    canvas = Image.alpha_composite(canvas, frame)

    serif_big = load_font(FONT_SERIF, 106)
    serif_small = load_font(FONT_SERIF, 58)
    sans_label = load_font(FONT_SANS, 34)
    sans_chip = load_font(FONT_SANS, 28)

    draw = ImageDraw.Draw(canvas)

    logo = Image.open(LOGO).convert("RGBA").resize((72, 72), Image.Resampling.LANCZOS)
    logo_back = Image.new("RGBA", (96, 96), (0, 0, 0, 0))
    ldraw = ImageDraw.Draw(logo_back)
    ldraw.rounded_rectangle((0, 0, 96, 96), radius=28, fill=(255, 255, 255, 238), outline=(232, 223, 212, 255), width=2)
    logo_back.alpha_composite(logo, ((96 - 72) // 2, (96 - 72) // 2))
    canvas.alpha_composite(logo_back, (86, 84))

    chip_w = 250
    chip_h = 56
    chip_x = 196
    chip_y = 106
    draw.rounded_rectangle((chip_x, chip_y, chip_x + chip_w, chip_y + chip_h), radius=28, fill=hex_to_rgba(config["accent_soft"]), outline=hex_to_rgba(config["accent"], 45), width=2)
    draw.text((chip_x + 26, chip_y + 10), config["category"], fill=hex_to_rgba(config["accent"]), font=sans_label)

    y = 218
    for idx, line in enumerate(config["title"]):
        font = serif_big if idx == 0 else serif_small
        draw.text((96, y), line, fill=hex_to_rgba("#233039"), font=font)
        y += 108 if idx == 0 else 78

    sub_w = 360
    sub_h = 66
    draw.rounded_rectangle((96, y + 8, 96 + sub_w, y + 8 + sub_h), radius=30, fill=(255, 255, 255, 220), outline=(231, 221, 209, 255), width=2)
    draw.text((122, y + 24), config["subtitle"].upper(), fill=hex_to_rgba("#62707a"), font=sans_chip)

    card_area = (630, 208, 1090, 1248)
    canvas = add_shadow(canvas, (700, 300, 1070, 1240), radius=40, opacity=55)
    canvas = add_shadow(canvas, (610, 218, 920, 650), radius=36, opacity=35)
    draw_preview_card(canvas, back_preview, (620, 238, 930, 650), radius=34, rotate=-7)
    draw_preview_card(canvas, main_preview, (700, 308, 1088, 1240), radius=40)

    footer_y = 1328
    footer_w = 318
    footer_h = 74
    draw.rounded_rectangle((96, footer_y, 96 + footer_w, footer_y + footer_h), radius=34, fill=hex_to_rgba(config["accent"]), outline=None)
    draw.text((126, footer_y + 20), "8 PAGES  •  DIGITAL PDF", fill=(255, 255, 255, 245), font=sans_chip)

    thumb_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(thumb_path, quality=95)


def main() -> None:
    for product in PRODUCTS:
        build_thumb(product)


if __name__ == "__main__":
    main()
