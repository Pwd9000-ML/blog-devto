#!/usr/bin/env python3
"""Generate a standardised 1000x420 cover image for any article."""

from __future__ import annotations

import argparse
import random
import sys
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Dict, Tuple
from urllib.request import urlopen

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
except ImportError:  # pragma: no cover - runtime dependency check
    print("Pillow is required: python -m pip install pillow", file=sys.stderr)
    sys.exit(1)

WIDTH, HEIGHT = 1000, 420
ACCENT_WIDTH = 280
FONT_CANDIDATES = (
    r"C:\\Windows\\Fonts\\segoeui.ttf",
    r"C:\\Windows\\Fonts\\seguisb.ttf",
    r"C:\\Windows\\Fonts\\segoeuib.ttf",
    r"C:\\Windows\\Fonts\\arialbd.ttf",
    r"C:\\Windows\\Fonts\\arial.ttf",
)


def resolve_repo_root(current: Path) -> Path:
    return current.resolve().parents[1]


def resolve_article(article_arg: str, repo_root: Path) -> Tuple[Path, Path | None]:
    target = Path(article_arg)
    if not target.is_absolute():
        target = (repo_root / target).resolve()

    if target.is_file():
        return target.parent, target
    if target.is_dir():
        markdown_files = sorted(p for p in target.iterdir() if p.suffix.lower() == ".md")
        preferred = target / f"{target.name}.md"
        if preferred.exists():
            return target, preferred
        return target, markdown_files[0] if markdown_files else None

    raise FileNotFoundError(f"Article path not found: {article_arg}")


def parse_front_matter(markdown_path: Path | None) -> Dict[str, str]:
    if not markdown_path or not markdown_path.exists():
        return {}
    text = markdown_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    fm_lines: list[str] = []
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            fm_lines = lines[1:idx]
            break
    data: Dict[str, str] = {}
    for raw in fm_lines:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        cleaned = value.strip().strip("'\"")
        data[key.strip()] = cleaned
    return data


def fallback_title(slug: str) -> str:
    words = slug.replace("_", " ").replace("-", " ").split()
    return " ".join(w.capitalize() for w in words) if words else slug


def find_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in FONT_CANDIDATES:
        path = Path(candidate)
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size)
            except OSError:
                continue
    return ImageFont.load_default()


def measure(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> Tuple[int, int]:
    if hasattr(draw, "textbbox"):
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        return right - left, bottom - top
    return draw.textsize(text, font=font)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    if not words:
        return []
    lines = []
    current: list[str] = []
    for word in words:
        candidate = " ".join(current + [word]) if current else word
        width, _ = measure(draw, candidate, font)
        if width <= max_width or not current:
            current.append(word)
            continue
        lines.append(" ".join(current))
        current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def ellipsize_to_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> str:
    if not text:
        return text
    w, _ = measure(draw, text, font)
    if w <= max_width:
        return text
    # Reserve space for ellipsis
    ell = "…"
    ew, _ = measure(draw, ell, font)
    # Greedy shrink
    s = text
    while s and measure(draw, s, font)[0] + ew > max_width:
        s = s[:-1]
    return (s + ell) if s else ell


def layout_text_block(
    draw: ImageDraw.ImageDraw,
    title: str,
    subtitle: str | None,
    title_font: ImageFont.ImageFont,
    subtitle_font: ImageFont.ImageFont,
    x: int,
    top_y: int,
    max_width: int,
    bottom_limit: int,
    line_spacing: int = 6,
) -> Tuple[int, list[str], list[str]]:
    # Wrap lines
    t_lines = wrap_text(draw, title, title_font, max_width)
    s_lines = wrap_text(draw, subtitle or "", subtitle_font, max_width) if subtitle else []

    # Measure total height
    def block_height(lines, font):
        h = 0
        for i, ln in enumerate(lines):
            _, lh = measure(draw, ln, font)
            h += lh
            if i < len(lines) - 1:
                h += line_spacing
        return h

    total = block_height(t_lines, title_font) + (16 if s_lines else 0) + block_height(s_lines, subtitle_font)

    # If overflow, drop subtitle lines first
    while s_lines and top_y + total > bottom_limit:
        s_lines.pop()
        total = block_height(t_lines, title_font) + (16 if s_lines else 0) + block_height(s_lines, subtitle_font)

    # If still overflow, truncate last title line with ellipsis
    while top_y + total > bottom_limit and t_lines:
        last = t_lines[-1]
        t_lines[-1] = ellipsize_to_width(draw, last, title_font, max_width)
        # After ellipsizing, recompute but prevent infinite loop
        new_total = block_height(t_lines, title_font) + (16 if s_lines else 0) + block_height(s_lines, subtitle_font)
        if new_total >= total:
            break
        total = new_total

    # Draw
    y = top_y
    for i, ln in enumerate(t_lines):
        draw.text((x, y), ln, font=title_font, fill=(255, 255, 255))
        _, lh = measure(draw, ln, title_font)
        y += lh + (line_spacing if i < len(t_lines) - 1 else 0)
    if s_lines:
        y += 16
        for i, ln in enumerate(s_lines):
            draw.text((x, y), ln, font=subtitle_font, fill=(220, 230, 250))
            _, lh = measure(draw, ln, subtitle_font)
            y += lh + (line_spacing if i < len(s_lines) - 1 else 0)
    return y, t_lines, s_lines


def friendly_date(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = value.strip()
    if cleaned.endswith("Z"):
        cleaned = cleaned[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(cleaned)
    except ValueError:
        return value
    return parsed.strftime("%d %b %Y")


def compute_text_block(
    draw: ImageDraw.ImageDraw,
    title: str,
    title_font: ImageFont.ImageFont,
    subtitle: str | None,
    subtitle_font: ImageFont.ImageFont,
    max_width: int,
) -> Tuple[list[str], list[str], int]:
    title_lines = wrap_text(draw, title, title_font, max_width)
    subtitle_lines: list[str] = []
    if subtitle:
        subtitle_lines = wrap_text(draw, subtitle, subtitle_font, max_width)
    total_height = 0
    line_spacing = 6
    for idx, line in enumerate(title_lines):
        _, h = measure(draw, line, title_font)
        total_height += h
        if idx < len(title_lines) - 1:
            total_height += line_spacing
    if subtitle_lines:
        total_height += 16
        for idx, line in enumerate(subtitle_lines):
            _, h = measure(draw, line, subtitle_font)
            total_height += h
            if idx < len(subtitle_lines) - 1:
                total_height += line_spacing
    return title_lines, subtitle_lines, total_height


def draw_octocat(canvas: Image.Image, center: Tuple[int, int]) -> None:
    draw = ImageDraw.Draw(canvas, "RGBA")
    head_radius = 88
    draw.ellipse(
        [
            center[0] - head_radius,
            center[1] - head_radius,
            center[0] + head_radius,
            center[1] + head_radius,
        ],
        fill=(6, 8, 14, 255),
        outline=(255, 255, 255, 40),
        width=3,
    )

    ear_height = 58
    ear_width = 60
    left_ear = [
        (center[0] - head_radius + 26, center[1] - head_radius + 20),
        (center[0] - head_radius - 22, center[1] - head_radius - ear_height + 16),
        (center[0] - head_radius + ear_width, center[1] - head_radius - 6),
    ]
    right_ear = [
        (center[0] + head_radius - 26, center[1] - head_radius + 20),
        (center[0] + head_radius + 22, center[1] - head_radius - ear_height + 16),
        (center[0] + head_radius - ear_width, center[1] - head_radius - 6),
    ]
    draw.polygon(left_ear, fill=(6, 8, 14, 255), outline=(255, 255, 255, 40))
    draw.polygon(right_ear, fill=(6, 8, 14, 255), outline=(255, 255, 255, 40))

    eye_y = center[1] - 16
    eye_offset = 46
    for dx in (-eye_offset, eye_offset):
        draw.ellipse(
            [
                center[0] + dx - 16,
                eye_y - 14,
                center[0] + dx + 16,
                eye_y + 14,
            ],
            fill=(245, 249, 255, 235),
        )
        draw.ellipse(
            [
                center[0] + dx - 5,
                eye_y - 6,
                center[0] + dx + 5,
                eye_y + 6,
            ],
            fill=(6, 8, 14, 255),
        )

    draw.ellipse(
        [
            center[0] - 8,
            center[1] + 12,
            center[0] + 8,
            center[1] + 26,
        ],
        fill=(235, 240, 255, 190),
    )

    whisker_data = [(-84, -8, -12, -22), (-84, 12, -12, 26)]
    for start_dx, start_dy, end_dx, end_dy in whisker_data:
        draw.line(
            [
                (center[0] + start_dx, center[1] + start_dy),
                (center[0] + end_dx, center[1] + end_dy),
            ],
            fill=(200, 215, 255, 120),
            width=3,
        )
        draw.line(
            [
                (center[0] - start_dx, center[1] + start_dy),
                (center[0] - end_dx, center[1] + end_dy),
            ],
            fill=(200, 215, 255, 120),
            width=3,
        )


def draw_cover(
    title: str,
    subtitle: str | None,
    tagline: str | None,
    accent_label: str,
    github_logo: bool,
    logo_image: Image.Image | None,
) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), "#0a1428")
    draw = ImageDraw.Draw(img)

    for y in range(HEIGHT):
        ratio = y / max(HEIGHT - 1, 1)
        r = int(12 + ratio * 30)
        g = int(34 + ratio * 60)
        b = int(68 + ratio * 80)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    draw.rectangle([(0, 0), (ACCENT_WIDTH, HEIGHT)], fill=(28, 90, 180))
    accent_layer = Image.new("RGBA", (ACCENT_WIDTH, HEIGHT))
    accent_draw = ImageDraw.Draw(accent_layer)
    for y in range(HEIGHT):
        opacity = int(160 - (160 * y / max(HEIGHT - 1, 1)))
        accent_draw.line([(0, y), (ACCENT_WIDTH, y)], fill=(40, 140, 255, max(opacity, 40)))

    # Prefer pasted logo image if provided; otherwise fall back to vector logo
    if logo_image is not None:
        max_w = int(ACCENT_WIDTH * 0.62)
        max_h = int(HEIGHT * 0.5)
        w, h = logo_image.size
        scale = min(max_w / max(w, 1), max_h / max(h, 1))
        new_size = (max(1, int(w * scale)), max(1, int(h * scale)))
        resample = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS
        logo_rgba = logo_image.convert("RGBA").resize(new_size, resample)
        pos = ((ACCENT_WIDTH - new_size[0]) // 2, (HEIGHT - new_size[1]) // 2)
        accent_layer.paste(logo_rgba, pos, logo_rgba)
    elif github_logo:
        draw_octocat(accent_layer, (ACCENT_WIDTH // 2, HEIGHT // 2))

    img.paste(accent_layer, (0, 0), accent_layer)

    title_font = find_font(46)
    subtitle_font = find_font(22)
    tagline_font = find_font(18)
    label_font = find_font(20)

    text_x = ACCENT_WIDTH + 48
    text_width = WIDTH - text_x - 48

    title_lines, subtitle_lines, block_height = compute_text_block(
        draw, title, title_font, subtitle, subtitle_font, text_width
    )

    start_y = (HEIGHT - block_height) // 2
    current_y = start_y
    for line in title_lines:
        draw.text((text_x, current_y), line, font=title_font, fill=(255, 255, 255))
        _, h = measure(draw, line, title_font)
        current_y += h + 6

    if subtitle_lines:
        current_y += 10
        for line in subtitle_lines:
            draw.text((text_x, current_y), line, font=subtitle_font, fill=(220, 230, 250))
            _, h = measure(draw, line, subtitle_font)
            current_y += h + 6

    if tagline:
        tag_width, tag_height = measure(draw, tagline, tagline_font)
        draw.rounded_rectangle(
            [
                text_x,
                HEIGHT - tag_height - 40,
                text_x + tag_width + 30,
                HEIGHT - 24,
            ],
            radius=16,
            fill=(36, 110, 210),
        )
        draw.text((text_x + 16, HEIGHT - tag_height - 32), tagline, font=tagline_font, fill=(255, 255, 255))

    label_text = accent_label.upper()
    label_width, label_height = measure(draw, label_text, label_font)
    draw.text(
        ((ACCENT_WIDTH - label_width) / 2, HEIGHT - label_height - 28),
        label_text,
        font=label_font,
        fill=(255, 255, 255, 220),
    )
    return img


def draw_cover_template(
    title: str,
    subtitle: str | None,
    caption: str | None,
    label_text: str,
    logo_image: Image.Image | None,
) -> Image.Image:
    img = Image.new("RGBA", (WIDTH, HEIGHT), (27, 15, 59, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Background gradient (approximate template #2B1E5B -> #1B0F3B)
    start = (43, 30, 91)
    end = (27, 15, 59)
    for y in range(HEIGHT):
        t = y / max(HEIGHT - 1, 1)
        r = int(start[0] * (1 - t) + end[0] * t)
        g = int(start[1] * (1 - t) + end[1] * t)
        b = int(start[2] * (1 - t) + end[2] * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Accent blob (soft, translucent)
    blob = Image.new("RGBA", (WIDTH, HEIGHT))
    bdraw = ImageDraw.Draw(blob, "RGBA")
    bdraw.ellipse([600, -160, 1020, 280], fill=(124, 92, 255, 46))
    bdraw.ellipse([540, -120, 960, 300], fill=(98, 213, 255, 40))
    img.alpha_composite(blob)

    # Pill label background
    pill_x, pill_y, pill_w, pill_h = 64, 64, 146, 46
    draw.rounded_rectangle(
        [pill_x, pill_y, pill_x + pill_w, pill_y + pill_h],
        radius=12,
        fill=(60, 46, 107, 204),  # #3C2E6B with ~0.8 opacity
    )
    label_font = find_font(18)
    label = label_text.upper()
    lw, lh = measure(draw, label, label_font)
    draw.text((pill_x + 16, pill_y + (pill_h - lh) // 2), label, font=label_font, fill=(179, 200, 255))

    # Title, subtitle, caption
    title_font = find_font(54)
    subtitle_font = find_font(26)
    caption_font = find_font(20)

    text_x = 64
    max_w = 600
    top_y = 170
    # Keep at least 80px bottom margin for aesthetics and potential caption
    bottom_limit = HEIGHT - 90
    y, _, _ = layout_text_block(draw, title, subtitle, title_font, subtitle_font, text_x, top_y, max_w, bottom_limit)

    if caption:
        # Place caption after text, but ensure it doesn't exceed bottom
        _, ch = measure(draw, caption, caption_font)
        y = min(max(y + 12, 270), HEIGHT - ch - 24)
        draw.text((text_x, y), caption, font=caption_font, fill=(196, 215, 255))

    # Accent underline
    draw.line([(64, 305), (420, 305)], fill=(124, 92, 255, 153), width=4)

    # Right side icon cards
    def rounded_rect_outline(x, y, w, h, radius, outline, width=3, fill=None):
        draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, outline=outline, width=width, fill=fill)

    # Card 1
    c1x, c1y = 720, 120
    rounded_rect_outline(c1x, c1y, 100, 100, 20, outline=(124, 92, 255), width=3, fill=(60, 46, 107))
    # Paste logo if provided, centered in card 1
    if logo_image is not None:
        max_w_logo, max_h_logo = 72, 72
        w, h = logo_image.size
        scale = min(max_w_logo / max(w, 1), max_h_logo / max(h, 1))
        new_size = (max(1, int(w * scale)), max(1, int(h * scale)))
        resample = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS
        logo = logo_image.convert("RGBA").resize(new_size, resample)
        lx = c1x + (100 - new_size[0]) // 2
        ly = c1y + (100 - new_size[1]) // 2
        img.paste(logo, (lx, ly), logo)
    else:
        cx = c1x + 50
        cy = c1y + 58
        draw.text((cx, cy), "Icon 1", anchor="mm", font=caption_font, fill=(196, 215, 255))

    # Card 2
    c2x, c2y = 850, 208
    rounded_rect_outline(c2x, c2y, 100, 100, 20, outline=(98, 213, 255), width=3, fill=(60, 46, 107))
    cx2 = c2x + 50
    cy2 = c2y + 58
    draw.text((cx2, cy2), "Icon 2", anchor="mm", font=caption_font, fill=(196, 215, 255))

    return img.convert("RGB")


def _pixelate(image: Image.Image, factor: float = 0.25) -> Image.Image:
    factor = max(0.05, min(0.5, factor))
    w, h = image.size
    down = (max(1, int(w * factor)), max(1, int(h * factor)))
    resample = Image.Resampling.NEAREST if hasattr(Image, "Resampling") else Image.NEAREST
    small = image.resize(down, resample)
    return small.resize((w, h), resample)


def draw_cover_pixel(
    title: str,
    subtitle: str | None,
    caption: str | None,
    label_text: str,
    logo_images: list[Image.Image] | None,
) -> Image.Image:
    # Build background on a separate layer to pixelate selectively
    bg = Image.new("RGBA", (WIDTH, HEIGHT), (10, 12, 22, 255))
    bdraw = ImageDraw.Draw(bg, "RGBA")

    # Retro gradient
    start = (16, 20, 40)
    end = (6, 8, 18)
    for y in range(HEIGHT):
        t = y / max(HEIGHT - 1, 1)
        r = int(start[0] * (1 - t) + end[0] * t)
        g = int(start[1] * (1 - t) + end[1] * t)
        b = int(start[2] * (1 - t) + end[2] * t)
        bdraw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Pixel grid overlay (subtle)
    grid = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(grid, "RGBA")
    step = 10
    grid_color = (255, 255, 255, 18)
    for x in range(0, WIDTH, step):
        gdraw.line([(x, 0), (x, HEIGHT)], fill=grid_color)
    for y in range(0, HEIGHT, step):
        gdraw.line([(0, y), (WIDTH, y)], fill=grid_color)
    bg.alpha_composite(grid)

    # Stars as 1-2px squares
    rnd = random.Random(42)
    for _ in range(120):
        x = rnd.randrange(0, WIDTH)
        y = rnd.randrange(0, HEIGHT)
        size = rnd.choice([1, 2])
        c = rnd.choice([(220, 230, 255, 180), (170, 190, 255, 150), (255, 255, 255, 200)])
        bdraw.rectangle([x, y, x + size, y + size], fill=c)

    # Ground/platform blocks
    for i in range(8):
        bx = 40 + i * 52
        by = HEIGHT - 80 - (i % 3) * 8
        bdraw.rectangle([bx, by, bx + 40, by + 14], fill=(40, 80, 160, 200), outline=(120, 180, 255, 220))
        bdraw.rectangle([bx + 8, by - 10, bx + 20, by + 2], fill=(100, 160, 255, 200))

    # Label badge (blocky)
    label = label_text.upper()
    label_font = find_font(18)
    lw, lh = measure(bdraw, label, label_font)
    lx, ly = 64, 50
    pad = 14
    bdraw.rectangle([lx, ly, lx + lw + pad * 2, ly + lh + pad], fill=(30, 30, 60, 200), outline=(150, 200, 255, 220), width=4)
    bdraw.text((lx + pad, ly + (pad // 2)), label, font=label_font, fill=(180, 210, 255, 255))

    # Title + subtitle onto BG layer
    title_font = find_font(46)
    subtitle_font = find_font(22)
    caption_font = find_font(18)
    text_x = 64
    max_w = 600
    ty = 140
    for line in wrap_text(bdraw, title, title_font, max_w):
        # Pixel-style shadow
        bdraw.text((text_x + 4, ty + 4), line, font=title_font, fill=(0, 0, 0, 120))
        bdraw.text((text_x, ty), line, font=title_font, fill=(255, 255, 255, 255))
        _, th = measure(bdraw, line, title_font)
        ty += th + 6

    if subtitle:
        ty += 6
        for line in wrap_text(bdraw, subtitle, subtitle_font, max_w):
            bdraw.text((text_x + 3, ty + 3), line, font=subtitle_font, fill=(0, 0, 0, 90))
            bdraw.text((text_x, ty), line, font=subtitle_font, fill=(220, 230, 250, 255))
            _, sh = measure(bdraw, line, subtitle_font)
            ty += sh + 4

    if caption:
        cy = HEIGHT - 54
        cw, ch = measure(bdraw, caption, caption_font)
        bdraw.rectangle([text_x - 8, cy - 6, text_x + cw + 14, cy + ch + 6], fill=(30, 70, 140, 200), outline=(140, 200, 255, 220), width=3)
        bdraw.text((text_x, cy), caption, font=caption_font, fill=(255, 255, 255, 255))

    # Pixelate the background layer
    bg_pix = _pixelate(bg, factor=0.2)

    # Compose final image and add crisp logos as sprites
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    img.alpha_composite(bg_pix)

    if logo_images:
        resample = Image.Resampling.NEAREST if hasattr(Image, "Resampling") else Image.NEAREST
        slots = [(760, 100), (860, 140), (820, 220)]
        for (lx, ly), logo in zip(slots, logo_images[:3]):
            w, h = logo.size
            scale = min(64 / max(w, 1), 64 / max(h, 1))
            new_size = (max(1, int(w * scale)), max(1, int(h * scale)))
            sprite = logo.convert("RGBA").resize(new_size, resample)
            # Add a simple pixel shadow
            shadow = Image.new("RGBA", sprite.size, (0, 0, 0, 0))
            sdraw = ImageDraw.Draw(shadow)
            sdraw.rectangle([2, 2, new_size[0], new_size[1]], fill=(0, 0, 0, 100))
            img.paste(shadow, (lx + 3, ly + 3), shadow)
            img.paste(sprite, (lx, ly), sprite)

    return img.convert("RGB")


def _draw_glow_blob(base: Image.Image, center: tuple[int, int], radius: int, color: tuple[int, int, int], alpha: int = 80, blur: int = 28) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ldraw = ImageDraw.Draw(layer, "RGBA")
    cx, cy = center
    ldraw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(color[0], color[1], color[2], alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(layer)


def draw_cover_glass(
    title: str,
    subtitle: str | None,
    caption: str | None,
    label_text: str,
    logo_images: list[Image.Image] | None,
) -> Image.Image:
    img = Image.new("RGBA", (WIDTH, HEIGHT), (12, 18, 36, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Vertical gradient background
    top, bottom = (15, 22, 48), (8, 10, 22)
    for y in range(HEIGHT):
        t = y / max(HEIGHT - 1, 1)
        r = int(top[0] * (1 - t) + bottom[0] * t)
        g = int(top[1] * (1 - t) + bottom[1] * t)
        b = int(top[2] * (1 - t) + bottom[2] * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Aurora streaks (blurred diagonal shapes)
    streak = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(streak, "RGBA")
    sdraw.polygon([(0, 200), (380, 80), (420, 140), (40, 260)], fill=(124, 92, 255, 70))
    sdraw.polygon([(280, 280), (720, 140), (760, 200), (320, 340)], fill=(98, 213, 255, 60))
    streak = streak.filter(ImageFilter.GaussianBlur(30))
    img.alpha_composite(streak)

    # Glass panel behind text
    panel = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    pdraw = ImageDraw.Draw(panel, "RGBA")
    px, py, pw, ph = 56 + ACCENT_WIDTH - 30, 90, WIDTH - (56 + ACCENT_WIDTH - 30) - 56, 220
    pdraw.rounded_rectangle([px, py, px + pw, py + ph], radius=22, fill=(255, 255, 255, 26), outline=(255, 255, 255, 40), width=2)
    panel = panel.filter(ImageFilter.GaussianBlur(0))
    img.alpha_composite(panel)

    # Label pill
    label_font = find_font(18)
    label = label_text.upper()
    lw, lh = measure(draw, label, label_font)
    lx, ly = 64, 56
    draw.rounded_rectangle([lx, ly, lx + lw + 28, ly + lh + 16], radius=12, fill=(60, 46, 107, 200))
    draw.text((lx + 14, ly + 8), label, font=label_font, fill=(179, 200, 255))

    # Text
    title_font = find_font(48)
    subtitle_font = find_font(22)
    caption_font = find_font(18)
    text_x = ACCENT_WIDTH + 48
    max_w = WIDTH - text_x - 48
    top_y = 110
    # Leave room at the bottom for a chip/tagline if present
    chip_h = 30 if caption else 0
    bottom_limit = HEIGHT - (chip_h + 40)
    ty, _, _ = layout_text_block(draw, title, subtitle, title_font, subtitle_font, text_x, top_y, max_w, bottom_limit)
    if caption:
        cw, ch = measure(draw, caption, caption_font)
        chip_y = min(HEIGHT - ch - 26, max(ty + 10, HEIGHT - ch - 38))
        draw.rounded_rectangle([text_x, chip_y, text_x + cw + 24, chip_y + ch + 16], radius=12, fill=(36, 110, 210, 220))
        draw.text((text_x + 12, chip_y + 8), caption, font=caption_font, fill=(255, 255, 255))

    # Logos with subtle glow (support up to two logos for glass style)
    if logo_images:
        resample = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS
        primary_center = (210, 140)
        _draw_glow_blob(img, (primary_center[0], primary_center[1] + 40), 70, (124, 92, 255), alpha=60, blur=22)
        primary = logo_images[0].convert("RGBA")
        pw, ph = primary.size
        pscale = min(120 / max(pw, 1), 120 / max(ph, 1))
        primary = primary.resize((max(1, int(pw * pscale)), max(1, int(ph * pscale))), resample)
        img.paste(primary, (primary_center[0] - primary.size[0] // 2, primary_center[1] - primary.size[1] // 2), primary)

        # Optional secondary logo (e.g. additional GitHub Octocat) placed to the right
        if len(logo_images) > 1:
            secondary_center = (primary_center[0] + 150, primary_center[1] + 10)
            _draw_glow_blob(img, (secondary_center[0], secondary_center[1] + 20), 50, (98, 213, 255), alpha=55, blur=18)
            secondary = logo_images[1].convert("RGBA")
            sw, sh = secondary.size
            sscale = min(88 / max(sw, 1), 88 / max(sh, 1))
            secondary = secondary.resize((max(1, int(sw * sscale)), max(1, int(sh * sscale))), resample)
            img.paste(
                secondary,
                (secondary_center[0] - secondary.size[0] // 2, secondary_center[1] - secondary.size[1] // 2),
                secondary,
            )

    return img.convert("RGB")


def draw_cover_flow(
    title: str,
    subtitle: str | None,
    caption: str | None,
    label_text: str,
    logo_images: list[Image.Image] | None,
) -> Image.Image:
    img = Image.new("RGBA", (WIDTH, HEIGHT), (10, 12, 24, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Background gradient
    for y in range(HEIGHT):
        t = y / max(HEIGHT - 1, 1)
        r = int(14 * (1 - t) + 6 * t)
        g = int(20 * (1 - t) + 10 * t)
        b = int(44 * (1 - t) + 24 * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Flow paths (smoothed by blurring a bright thin line layer)
    path_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    pdraw = ImageDraw.Draw(path_layer, "RGBA")
    colors = [(98, 213, 255, 130), (124, 92, 255, 130), (120, 200, 255, 110)]
    rnd = random.Random()
    for i, col in enumerate(colors):
        y0 = 60 + i * 80
        points = []
        for x in range(-40, WIDTH + 40, 40):
            jitter = rnd.randint(-20, 20)
            points.append((x, y0 + jitter))
        pdraw.line(points, fill=col, width=3)
    path_layer = path_layer.filter(ImageFilter.GaussianBlur(2))
    img.alpha_composite(path_layer)

    # Nodes
    for i in range(5):
        nx = 200 + i * 140
        ny = 90 + (i % 3) * 60
        _draw_glow_blob(img, (nx, ny), 16, (120, 200, 255), alpha=80, blur=10)
        draw.ellipse([nx - 8, ny - 8, nx + 8, ny + 8], fill=(220, 240, 255, 255))

    # Label
    label_font = find_font(18)
    label = label_text.upper()
    lw, lh = measure(draw, label, label_font)
    draw.rounded_rectangle([64, 56, 64 + lw + 28, 56 + lh + 16], radius=12, fill=(30, 40, 80, 210))
    draw.text((64 + 14, 56 + 8), label, font=label_font, fill=(179, 200, 255))

    # Text
    title_font = find_font(48)
    subtitle_font = find_font(22)
    caption_font = find_font(18)
    text_x = 64
    max_w = 560
    top_y = 120
    chip_h = 30 if caption else 0
    bottom_limit = HEIGHT - (chip_h + 40)
    ty, _, _ = layout_text_block(draw, title, subtitle, title_font, subtitle_font, text_x, top_y, max_w, bottom_limit)
    if caption:
        cw, ch = measure(draw, caption, caption_font)
        chip_y = min(HEIGHT - ch - 26, max(ty + 10, HEIGHT - ch - 38))
        draw.rounded_rectangle([text_x, chip_y, text_x + cw + 24, chip_y + ch + 16], radius=12, fill=(36, 110, 210, 220))
        draw.text((text_x + 12, chip_y + 8), caption, font=caption_font, fill=(255, 255, 255))

    # Logo in a highlighted node area (right side)
    if logo_images:
        cx, cy = WIDTH - 140, 120
        _draw_glow_blob(img, (cx, cy + 20), 60, (124, 92, 255), alpha=70, blur=18)
        resample = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS
        logo = logo_images[0].convert("RGBA")
        w, h = logo.size
        scale = min(108 / max(w, 1), 108 / max(h, 1))
        logo = logo.resize((max(1, int(w * scale)), max(1, int(h * scale))), resample)
        img.paste(logo, (cx - logo.size[0] // 2, cy - logo.size[1] // 2), logo)

    return img.convert("RGB")


def draw_cover_fun(
    title: str,
    label_text: str,
    logo_images: list[Image.Image] | None,
) -> Image.Image:
    """Playful style with vibrant gradient, confetti, and careful logo placement.

    Ensures: only title text rendered; logos do not overlap title; title does not overlap.
    Logos are pasted unmodified to respect brand guidelines.
    """
    img = Image.new("RGBA", (WIDTH, HEIGHT), (18, 22, 44, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Colorful diagonal gradient
    for y in range(HEIGHT):
        t = y / max(HEIGHT - 1, 1)
        r = int(30 + 80 * (1 - t))
        g = int(50 + 90 * (t))
        b = int(100 + 40 * (0.5 - abs(0.5 - t)))
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Soft spotlight circles
    spot = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(spot, "RGBA")
    sdraw.ellipse([120, -80, 520, 320], fill=(255, 200, 120, 60))
    sdraw.ellipse([580, 120, 1040, 520], fill=(98, 213, 255, 70))
    spot = spot.filter(ImageFilter.GaussianBlur(36))
    img.alpha_composite(spot)

    # Title block
    title_font = find_font(54)
    max_title_width = int(WIDTH * 0.78)
    tdraw = ImageDraw.Draw(img, "RGBA")
    lines = wrap_text(tdraw, title, title_font, max_title_width)
    spacing = 8
    total_h = 0
    for i, ln in enumerate(lines):
        _, h = measure(tdraw, ln, title_font)
        total_h += h + (spacing if i < len(lines) - 1 else 0)
    top = (HEIGHT - total_h) // 2
    bbox = [WIDTH, HEIGHT, 0, 0]
    y = top
    for ln in lines:
        w, h = measure(tdraw, ln, title_font)
        x = (WIDTH - w) // 2
        # subtle shadow
        tdraw.text((x + 3, y + 3), ln, font=title_font, fill=(0, 0, 0, 120))
        tdraw.text((x, y), ln, font=title_font, fill=(255, 255, 255, 255))
        bbox[0] = min(bbox[0], x)
        bbox[1] = min(bbox[1], y)
        bbox[2] = max(bbox[2], x + w)
        bbox[3] = max(bbox[3], y + h)
        y += h + spacing

    # Confetti shapes (avoid title bbox)
    import random as _rand
    rnd = _rand.Random(31415)
    for _ in range(140):
        cx = rnd.randrange(0, WIDTH)
        cy = rnd.randrange(0, HEIGHT)
        if bbox[0] - 12 <= cx <= bbox[2] + 12 and bbox[1] - 12 <= cy <= bbox[3] + 12:
            continue
        size = rnd.choice([3, 4, 5, 6])
        col = rnd.choice([
            (255, 255, 255, 180),
            (124, 92, 255, 170),
            (98, 213, 255, 170),
            (255, 160, 160, 170),
            (180, 255, 180, 170),
        ])
        shape = rnd.choice(["rect", "circle", "diamond"])
        if shape == "rect":
            draw.rectangle([cx, cy, cx + size, cy + size], fill=col)
        elif shape == "circle":
            draw.ellipse([cx, cy, cx + size, cy + size], fill=col)
        else:
            draw.polygon([(cx, cy + size), (cx + size, cy), (cx + size * 2, cy + size), (cx + size, cy + size * 2)], fill=col)

    # Label pill
    label_font = find_font(18)
    label = label_text.upper()
    lw, lh = measure(draw, label, label_font)
    draw.rounded_rectangle([40, 34, 40 + lw + 26, 34 + lh + 18], radius=12, fill=(0, 0, 0, 90))
    draw.text((40 + 13, 34 + 9), label, font=label_font, fill=(200, 220, 255, 255))

    # Logos: choose corners, nudge to avoid title bbox
    if logo_images:
        resample = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS
        slots = [(WIDTH - 150, 36), (WIDTH - 160, HEIGHT - 160), (60, HEIGHT - 150)]
        for (lx, ly), logo in zip(slots, logo_images[:3]):
            logo_rgba = logo.convert("RGBA")
            w, h = logo_rgba.size
            scale = min(104 / max(w, 1), 104 / max(h, 1))
            logo_resized = logo_rgba.resize((max(1, int(w * scale)), max(1, int(h * scale))), resample)
            bx1, by1 = lx, ly
            bx2, by2 = lx + logo_resized.size[0], ly + logo_resized.size[1]
            # If overlapping title, push away vertically
            if not (bx2 < bbox[0] or bx1 > bbox[2] or by2 < bbox[1] or by1 > bbox[3]):
                if ly < HEIGHT / 2:
                    ly = max(16, bbox[1] - logo_resized.size[1] - 20)
                else:
                    ly = min(HEIGHT - logo_resized.size[1] - 16, bbox[3] + 20)
            img.paste(logo_resized, (lx, ly), logo_resized)

    return img.convert("RGB")


def build_tagline(metadata: Dict[str, str], explicit: str | None) -> str | None:
    if explicit:
        return explicit
    friendly = friendly_date(metadata.get("date"))
    if friendly:
        return f"Published {friendly}"
    series = metadata.get("series")
    if series:
        return series
    tags = metadata.get("tags")
    if tags:
        return tags.split(",")[0].strip()
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Regenerate a cover image for any article.")
    parser.add_argument("--article", required=True, help="Relative path to an article folder or markdown file")
    parser.add_argument("--title", help="Override the title text displayed on the cover")
    parser.add_argument("--subtitle", help="Optional subtitle text")
    parser.add_argument("--tagline", help="Optional tagline chip text")
    parser.add_argument("--label", default="pwd9000.dev", help="Accent strip label text")
    parser.add_argument("--output", help="Override output image path")
    parser.add_argument("--no-backup", action="store_true", help="Skip writing a .bak copy of the existing image")
    parser.add_argument(
        "--github-logo",
        action="store_true",
        help="Render a stylised GitHub Octocat badge on the accent panel",
    )
    parser.add_argument(
        "--logo-url",
        action="append",
        help="HTTP(S) PNG logo URL. Repeat to add multiple logos (used especially by --style pixel)",
    )
    parser.add_argument(
        "--style",
        choices=["default", "template", "pixel", "glass", "flow", "fun", "random"],
        default="default",
        help="Choose a style: default, template, pixel (background only), glass, flow, fun, or random",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Use shorter, catchier text (auto-compacts title/subtitle/tagline)",
    )
    args = parser.parse_args()

    repo_root = resolve_repo_root(Path(__file__))
    try:
        article_dir, markdown_path = resolve_article(args.article, repo_root)
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)

    metadata = parse_front_matter(markdown_path)
    title = args.title or metadata.get("title") or fallback_title(article_dir.name)
    subtitle = args.subtitle or metadata.get("description")
    tagline = build_tagline(metadata, args.tagline)

    # Optional: compact the text into a catchy, minimal variant
    if args.compact:
        def compact_text(title_in: str, subtitle_in: str | None, tagline_in: str | None) -> tuple[str, str | None, str | None]:
            low = title_in.lower()
            keywords = []
            def add(k, label):
                if k not in keywords:
                    keywords.append(label)

            # Heuristic keyword extraction
            if "vs code" in low or "vscode" in low:
                add("vscode", "VS Code")
            if "copilot" in low:
                add("copilot", "Copilot")
            if "model context protocol" in low or "mcp" in low:
                add("mcp", "MCP")
            if "github" in low:
                add("github", "GitHub")
            if "azure" in low:
                add("azure", "Azure")
            if "terraform" in low:
                add("terraform", "Terraform")
            if "agent" in low:
                add("agent", "Agent Mode")
            if "ai" in low and "copilot" not in low:
                add("ai", "AI")

            compact_title = " + ".join(keywords[:3]) if keywords else None

            # Fallback: take the first segment before dash/colon and compress to 3-5 words
            if not compact_title:
                import re
                base = re.split(r"[\-|:\u2013\u2014]", title_in)[0].strip()
                words = [w for w in re.findall(r"[A-Za-z0-9+]+", base) if len(w) > 1]
                compact_title = " ".join(words[:4]) if words else title_in[:24]

            # Subtitle: keep very short or drop
            compact_sub = None
            if subtitle_in:
                sub_low = subtitle_in.lower()
                if any(tok in sub_low for tok in ["quick", "easy", "setup", "guide", "start"]):
                    compact_sub = "Quick Setup"
                elif "agent" in sub_low:
                    compact_sub = "Agent Mode Ready"
                else:
                    # pick 2-4 words
                    import re
                    sw = set(["the","for","and","with","using","your","in","to","of","a","an"])
                    toks = [t for t in re.findall(r"[A-Za-z0-9+]+", subtitle_in) if t.lower() not in sw]
                    compact_sub = " ".join(toks[:3]) if toks else None

            # Tagline: prefer very short chip
            compact_tag = None
            if tagline_in:
                if len(tagline_in) <= 18:
                    compact_tag = tagline_in
                else:
                    compact_tag = "Quick Start"
            else:
                compact_tag = "Quick Start"

            return compact_title, compact_sub, compact_tag

        title, subtitle, tagline = compact_text(title, subtitle, tagline)

    output_path = Path(args.output) if args.output else article_dir / "assets" / "main.png"
    if not output_path.is_absolute():
        output_path = (repo_root / output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists() and not args.no_backup:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = output_path.with_suffix(output_path.suffix + f".bak-{timestamp}")
        output_path.replace(backup_path)
        print(f"Existing cover moved to backup: {backup_path.relative_to(repo_root)}")

    # Attempt to fetch logo image(s) if URL(s) provided
    logo_imgs: list[Image.Image] = []
    if args.logo_url:
        for url in args.logo_url:
            try:
                with urlopen(url, timeout=12) as resp:
                    data = resp.read()
                logo_imgs.append(Image.open(BytesIO(data)))
            except Exception as e:
                print(f"Warning: failed to fetch logo from URL '{url}': {e}")

    # Style registry and random selection (exclude 'pixel' from random by default)
    style_funcs = {
        "default": lambda: draw_cover(
            title=title,
            subtitle=subtitle,
            tagline=tagline,
            accent_label=args.label,
            github_logo=args.github_logo,
            logo_image=logo_imgs[0] if logo_imgs else None,
        ),
        "template": lambda: draw_cover_template(
            title=title,
            subtitle=subtitle,
            caption=tagline,
            label_text=args.label,
            logo_image=logo_imgs[0] if logo_imgs else None,
        ),
        "pixel": lambda: draw_cover_pixel(
            title=title,
            subtitle=subtitle,
            caption=tagline,
            label_text=args.label,
            logo_images=logo_imgs,
        ),
        "glass": lambda: draw_cover_glass(
            title=title,
            subtitle=subtitle,
            caption=tagline,
            label_text=args.label,
            logo_images=logo_imgs,
        ),
        "flow": lambda: draw_cover_flow(
            title=title,
            subtitle=subtitle,
            caption=tagline,
            label_text=args.label,
            logo_images=logo_imgs,
        ),
        "fun": lambda: draw_cover_fun(
            title=title,
            label_text=args.label,
            logo_images=logo_imgs,
        ),
    }

    if args.style == "random":
        candidates = ["default", "template", "glass", "flow", "fun"]
        choice = random.choice(candidates)
        image = style_funcs[choice]()
    elif args.style == "template":
        image = draw_cover_template(
            title=title,
            subtitle=subtitle,
            caption=tagline,
            label_text=args.label,
            logo_image=logo_imgs[0] if logo_imgs else None,
        )
    elif args.style == "pixel":
        image = draw_cover_pixel(
            title=title,
            subtitle=subtitle,
            caption=tagline,
            label_text=args.label,
            logo_images=logo_imgs,
        )
    elif args.style == "glass":
        image = draw_cover_glass(
            title=title,
            subtitle=subtitle,
            caption=tagline,
            label_text=args.label,
            logo_images=logo_imgs,
        )
    elif args.style == "flow":
        image = draw_cover_flow(
            title=title,
            subtitle=subtitle,
            caption=tagline,
            label_text=args.label,
            logo_images=logo_imgs,
        )
    elif args.style == "fun":
        image = draw_cover_fun(
            title=title,
            label_text=args.label,
            logo_images=logo_imgs,
        )
    else:
        image = draw_cover(
            title=title,
            subtitle=subtitle,
            tagline=tagline,
            accent_label=args.label,
            github_logo=args.github_logo,
            logo_image=logo_imgs[0] if logo_imgs else None,
        )
    image.save(output_path)
    try:
        rel = output_path.relative_to(repo_root)
    except ValueError:
        rel = output_path
    print(f"Saved new cover image -> {rel} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
