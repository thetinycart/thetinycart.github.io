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
        "label": "MEAL PLANNER",
        "accent": "#cb7e62",
        "accent_soft": "#f0d8d2",
        "glow": "#dccfc3",
        "preview_main": "preview-weekly-planner.png",
        "preview_back": "preview-overview.png",
        "layout": "right",
    },
    {
        "slug": "kids-routine-chart",
        "label": "ROUTINES",
        "accent": "#71816d",
        "accent_soft": "#dce5da",
        "glow": "#d8ddd2",
        "preview_main": "preview-morning-flow.png",
        "preview_back": "preview-overview.png",
        "layout": "left",
    },
    {
        "slug": "playroom-organization-labels",
        "label": "ORGANIZE",
        "accent": "#c6a06a",
        "accent_soft": "#efe0c8",
        "glow": "#e5dbc8",
        "preview_main": "preview-category-grid.png",
        "preview_back": "preview-overview.png",
        "layout": "center",
    },
    {
        "slug": "lunchbox-notes",
        "label": "NOTES",
        "accent": "#c77063",
        "accent_soft": "#f4ddd8",
        "glow": "#e6d7d0",
        "preview_main": "preview-encouragement-notes.png",
        "preview_back": "preview-overview.png",
        "layout": "right",
    },
    {
        "slug": "baby-registry-planner",
        "label": "NEW BABY",
        "accent": "#9a8c78",
        "accent_soft": "#ede4da",
        "glow": "#e6ddd3",
        "preview_main": "preview-priorities.png",
        "preview_back": "preview-overview.png",
        "layout": "left",
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
    main_preview = fit_preview(folder / config["preview_main"], (520, 770))
    back_preview = fit_preview(folder / config["preview_back"], (340, 500))

    canvas = Image.new("RGBA", SIZE, hex_to_rgba("#f7f1ea"))
    glow = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    if config["layout"] == "left":
        gdraw.ellipse((-120, 140, 740, 980), fill=hex_to_rgba(config["accent_soft"], 135))
        gdraw.ellipse((620, 900, 1380, 1650), fill=hex_to_rgba(config["glow"], 120))
    elif config["layout"] == "right":
        gdraw.ellipse((500, 120, 1360, 980), fill=hex_to_rgba(config["accent_soft"], 135))
        gdraw.ellipse((-80, 960, 760, 1650), fill=hex_to_rgba(config["glow"], 120))
    else:
        gdraw.ellipse((-120, 980, 660, 1760), fill=hex_to_rgba(config["accent_soft"], 120))
        gdraw.ellipse((730, -80, 1460, 620), fill=hex_to_rgba(config["glow"], 120))
    gdraw.ellipse((820, 1120, 1380, 1570), fill=hex_to_rgba(config["accent"], 35))
    glow = glow.filter(ImageFilter.GaussianBlur(48))
    canvas = Image.alpha_composite(canvas, glow)

    frame = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    fdraw = ImageDraw.Draw(frame)
    fdraw.rounded_rectangle((34, 34, SIZE[0] - 34, SIZE[1] - 34), radius=46, outline=(230, 221, 209, 255), width=3)
    fdraw.rounded_rectangle((72, 72, SIZE[0] - 72, SIZE[1] - 72), radius=40, outline=(237, 230, 219, 255), width=2)
    canvas = Image.alpha_composite(canvas, frame)

    sans_label = load_font(FONT_SANS, 34)
    sans_chip = load_font(FONT_SANS, 26)

    draw = ImageDraw.Draw(canvas)

    logo = Image.open(LOGO).convert("RGBA").resize((72, 72), Image.Resampling.LANCZOS)
    logo_back = Image.new("RGBA", (96, 96), (0, 0, 0, 0))
    ldraw = ImageDraw.Draw(logo_back)
    ldraw.rounded_rectangle((0, 0, 96, 96), radius=28, fill=(255, 255, 255, 238), outline=(232, 223, 212, 255), width=2)
    logo_back.alpha_composite(logo, ((96 - 72) // 2, (96 - 72) // 2))
    canvas.alpha_composite(logo_back, (86, 84))

    chip_w = 220
    chip_h = 56
    chip_x = 196
    chip_y = 106
    draw.rounded_rectangle((chip_x, chip_y, chip_x + chip_w, chip_y + chip_h), radius=28, fill=hex_to_rgba(config["accent_soft"]), outline=hex_to_rgba(config["accent"], 45), width=2)
    draw.text((chip_x + 24, chip_y + 10), config["label"], fill=hex_to_rgba(config["accent"]), font=sans_label)

    mat_x0, mat_y0, mat_x1, mat_y1 = 86, 190, 1114, 1380
    mat = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    mdraw = ImageDraw.Draw(mat)
    mdraw.rounded_rectangle((mat_x0, mat_y0, mat_x1, mat_y1), radius=38, fill=(255, 252, 247, 130), outline=(235, 227, 217, 220), width=2)
    mat = mat.filter(ImageFilter.GaussianBlur(0.5))
    canvas = Image.alpha_composite(canvas, mat)

    layout = config["layout"]
    if layout == "left":
        back_box = (560, 310, 900, 810)
        main_box = (170, 420, 710, 1220)
        main_rotate = -2
        back_rotate = 8
    elif layout == "right":
        back_box = (290, 290, 630, 790)
        main_box = (520, 410, 1060, 1210)
        main_rotate = 2
        back_rotate = -8
    else:
        back_box = (220, 300, 560, 800)
        main_box = (360, 380, 900, 1180)
        main_rotate = 0
        back_rotate = -6

    canvas = add_shadow(canvas, (back_box[0], back_box[1], back_box[2], back_box[3]), radius=34, opacity=28)
    canvas = add_shadow(canvas, (main_box[0], main_box[1], main_box[2], main_box[3]), radius=38, opacity=44)
    draw_preview_card(canvas, back_preview, back_box, radius=32, rotate=back_rotate)
    draw_preview_card(canvas, main_preview, main_box, radius=38, rotate=main_rotate)

    footer_y = 1308
    footer_w = 168
    footer_h = 62
    footer_x = SIZE[0] - 86 - footer_w
    draw.rounded_rectangle((footer_x, footer_y, footer_x + footer_w, footer_y + footer_h), radius=28, fill=(255, 255, 255, 220), outline=(231, 221, 209, 255), width=2)
    draw.text((footer_x + 28, footer_y + 18), "DIGITAL PDF", fill=hex_to_rgba("#5b6972"), font=sans_chip)

    thumb_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(thumb_path, quality=95)


def main() -> None:
    for product in PRODUCTS:
        build_thumb(product)


if __name__ == "__main__":
    main()
