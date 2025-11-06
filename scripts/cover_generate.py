#!/usr/bin/env python3
"""Generate a standardised 1000x420 cover image for any article."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Dict, Tuple
from urllib.request import urlopen

try:
    from PIL import Image, ImageDraw, ImageFont
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
        help="HTTP(S) URL to a PNG logo to place on the accent panel (overrides --github-logo if provided)",
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

    output_path = Path(args.output) if args.output else article_dir / "assets" / "main.png"
    if not output_path.is_absolute():
        output_path = (repo_root / output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists() and not args.no_backup:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = output_path.with_suffix(output_path.suffix + f".bak-{timestamp}")
        output_path.replace(backup_path)
        print(f"Existing cover moved to backup: {backup_path.relative_to(repo_root)}")

    # Attempt to fetch a logo image if URL provided
    logo_img = None
    if args.logo_url:
        try:
            with urlopen(args.logo_url, timeout=10) as resp:
                data = resp.read()
            logo_img = Image.open(BytesIO(data))
        except Exception as e:
            print(f"Warning: failed to fetch logo from URL: {e}")
            logo_img = None

    image = draw_cover(
        title=title,
        subtitle=subtitle,
        tagline=tagline,
        accent_label=args.label,
        github_logo=args.github_logo,
        logo_image=logo_img,
    )
    image.save(output_path)
    try:
        rel = output_path.relative_to(repo_root)
    except ValueError:
        rel = output_path
    print(f"Saved new cover image -> {rel} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
