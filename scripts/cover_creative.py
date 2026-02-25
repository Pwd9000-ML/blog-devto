#!/usr/bin/env python3
"""Generate creative DEV.to cover images with random style selection.

Default behaviour picks a random style each run so covers are not repetitive.
You can also pin a specific style with --style.
"""

from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
except ImportError:
    print('Pillow is required: python -m pip install pillow')
    raise SystemExit(1)

WIDTH, HEIGHT = 1000, 420

FONT_CANDIDATES = (
    r'C:\Windows\Fonts\segoeuib.ttf',
    r'C:\Windows\Fonts\seguisb.ttf',
    r'C:\Windows\Fonts\arialbd.ttf',
    r'C:\Windows\Fonts\consola.ttf',
)

STYLES = (
    'mesh-gradient',
    'blueprint',
    'duotone-noise',
    'sunset-waves',
    'minimal-paper',
    'neon-grid',
    'aurora-mist',
    'retro-terminal',
    'geometric-collage',
)

RANDOM_STYLE_WEIGHTS = {
    'mesh-gradient': 1.0,
    'blueprint': 1.0,
    'duotone-noise': 1.0,
    'sunset-waves': 1.0,
    'minimal-paper': 1.0,
    'neon-grid': 1.0,
    'aurora-mist': 1.0,
    'retro-terminal': 1.0,
    'geometric-collage': 1.0,
}


def pick_weighted_style(rnd: random.Random) -> str:
    styles = list(STYLES)
    weights = [RANDOM_STYLE_WEIGHTS.get(style, 1.0) for style in styles]
    return rnd.choices(styles, weights=weights, k=1)[0]


def find_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in FONT_CANDIDATES:
        path = Path(candidate)
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size)
            except OSError:
                continue
    return ImageFont.load_default()


def measure(draw: ImageDraw.ImageDraw, text: str, font) -> tuple[int, int]:
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    return int(right - left), int(bottom - top)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    words = text.split()
    if not words:
        return []
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = ' '.join(current + [word]) if current else word
        width, _ = measure(draw, candidate, font)
        if width <= max_width or not current:
            current.append(word)
        else:
            lines.append(' '.join(current))
            current = [word]
    if current:
        lines.append(' '.join(current))
    return lines


def draw_centered_text(
    img: Image.Image,
    title: str,
    subtitle: str,
    title_fill: tuple[int, int, int, int],
    subtitle_fill: tuple[int, int, int, int],
    glow_fill: tuple[int, int, int, int] | None = None,
) -> None:
    draw = ImageDraw.Draw(img, 'RGBA')
    title_font = find_font(52)
    subtitle_font = find_font(22)
    max_width = int(WIDTH * 0.84)

    title_lines = wrap_text(draw, title, title_font, max_width)
    subtitle_lines = wrap_text(draw, subtitle, subtitle_font, max_width)

    title_height = sum(measure(draw, line, title_font)[1] for line in title_lines) + (
        max(0, len(title_lines) - 1) * 8
    )
    subtitle_height = sum(measure(draw, line, subtitle_font)[1] for line in subtitle_lines) + (
        max(0, len(subtitle_lines) - 1) * 6
    )

    total_height = title_height + 18 + subtitle_height
    y = (HEIGHT - total_height) // 2

    for line in title_lines:
        width, line_height = measure(draw, line, title_font)
        x = (WIDTH - width) // 2

        if glow_fill is not None:
            glow = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
            gdraw = ImageDraw.Draw(glow, 'RGBA')
            gdraw.text((x, y), line, font=title_font, fill=glow_fill)
            glow = glow.filter(ImageFilter.GaussianBlur(8))
            img.alpha_composite(glow)

        draw.text((x + 2, y + 2), line, font=title_font, fill=(0, 0, 0, 120))
        draw.text((x, y), line, font=title_font, fill=title_fill)
        y += line_height + 8

    y += 10
    for line in subtitle_lines:
        width, line_height = measure(draw, line, subtitle_font)
        x = (WIDTH - width) // 2
        draw.text((x + 1, y + 1), line, font=subtitle_font, fill=(0, 0, 0, 90))
        draw.text((x, y), line, font=subtitle_font, fill=subtitle_fill)
        y += line_height + 6


def style_mesh_gradient(title: str, subtitle: str, output_path: Path, rnd: random.Random) -> None:
    img = Image.new('RGBA', (WIDTH, HEIGHT), (18, 20, 45, 255))

    palette = [
        (80, 120, 255),
        (150, 90, 240),
        (35, 210, 210),
        (255, 120, 90),
        (110, 240, 160),
    ]

    for _ in range(9):
        layer = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer, 'RGBA')
        cx = rnd.randint(80, WIDTH - 80)
        cy = rnd.randint(60, HEIGHT - 60)
        radius = rnd.randint(90, 220)
        colour = rnd.choice(palette)
        for r in range(radius, 8, -6):
            alpha = max(0, int(130 * (r / radius) ** 1.7))
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(*colour, alpha))
        layer = layer.filter(ImageFilter.GaussianBlur(28))
        img.alpha_composite(layer)

    grid = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(grid, 'RGBA')
    for x in range(0, WIDTH, 32):
        gdraw.line([(x, 0), (x, HEIGHT)], fill=(255, 255, 255, 18), width=1)
    for y in range(0, HEIGHT, 32):
        gdraw.line([(0, y), (WIDTH, y)], fill=(255, 255, 255, 18), width=1)
    img.alpha_composite(grid)

    draw_centered_text(
        img,
        title,
        subtitle,
        title_fill=(255, 255, 255, 255),
        subtitle_fill=(224, 236, 255, 245),
        glow_fill=(210, 230, 255, 120),
    )

    img = ImageEnhance.Contrast(img).enhance(1.08)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, 'PNG')


def style_blueprint(title: str, subtitle: str, output_path: Path, rnd: random.Random) -> None:
    img = Image.new('RGBA', (WIDTH, HEIGHT), (12, 36, 74, 255))
    draw = ImageDraw.Draw(img, 'RGBA')

    for x in range(0, WIDTH, 25):
        alpha = 24 if x % 100 else 45
        draw.line([(x, 0), (x, HEIGHT)], fill=(160, 205, 255, alpha), width=1)
    for y in range(0, HEIGHT, 25):
        alpha = 24 if y % 100 else 45
        draw.line([(0, y), (WIDTH, y)], fill=(160, 205, 255, alpha), width=1)

    for _ in range(12):
        x1 = rnd.randint(50, WIDTH - 220)
        y1 = rnd.randint(40, HEIGHT - 120)
        x2 = x1 + rnd.randint(80, 220)
        y2 = y1 + rnd.randint(30, 120)
        draw.rectangle((x1, y1, x2, y2), outline=(200, 230, 255, 70), width=2)

    draw.rectangle((26, 26, WIDTH - 26, HEIGHT - 26), outline=(220, 240, 255, 120), width=3)

    draw_centered_text(
        img,
        title,
        subtitle,
        title_fill=(240, 248, 255, 255),
        subtitle_fill=(198, 226, 255, 245),
        glow_fill=(120, 185, 255, 80),
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, 'PNG')


def style_duotone_noise(title: str, subtitle: str, output_path: Path, rnd: random.Random) -> None:
    img = Image.new('RGBA', (WIDTH, HEIGHT), (26, 16, 34, 255))
    draw = ImageDraw.Draw(img, 'RGBA')

    for y in range(HEIGHT):
        t = y / max(HEIGHT - 1, 1)
        r = int(35 + (130 - 35) * t)
        g = int(15 + (45 - 15) * t)
        b = int(50 + (165 - 50) * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255), width=1)

    noise_layer = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    ndraw = ImageDraw.Draw(noise_layer, 'RGBA')
    for _ in range(14000):
        x = rnd.randint(0, WIDTH - 1)
        y = rnd.randint(0, HEIGHT - 1)
        shade = rnd.randint(160, 255)
        alpha = rnd.randint(10, 38)
        ndraw.point((x, y), fill=(shade, shade, shade, alpha))
    img.alpha_composite(noise_layer)

    for _ in range(22):
        y = rnd.randint(0, HEIGHT - 1)
        draw.line([(0, y), (WIDTH, y)], fill=(255, 255, 255, rnd.randint(8, 22)), width=1)

    draw_centered_text(
        img,
        title,
        subtitle,
        title_fill=(255, 244, 252, 255),
        subtitle_fill=(238, 215, 240, 245),
        glow_fill=(255, 190, 228, 100),
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, 'PNG')


def style_sunset_waves(title: str, subtitle: str, output_path: Path, rnd: random.Random) -> None:
    img = Image.new('RGBA', (WIDTH, HEIGHT), (14, 21, 56, 255))
    draw = ImageDraw.Draw(img, 'RGBA')

    for y in range(HEIGHT):
        t = y / max(HEIGHT - 1, 1)
        r = int(20 + (250 - 20) * t)
        g = int(40 + (120 - 40) * t)
        b = int(95 + (90 - 95) * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255), width=1)

    for i in range(8):
        layer = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
        ldraw = ImageDraw.Draw(layer, 'RGBA')
        base_y = 40 + i * 50
        amp = rnd.randint(10, 22)
        freq = rnd.uniform(0.007, 0.017)
        points = []
        for x in range(0, WIDTH + 10, 10):
            y = int(base_y + amp * math.sin(x * freq + i * 0.8))
            points.append((x, y))
        points.extend([(WIDTH, HEIGHT), (0, HEIGHT)])
        colour = (255, 180 - i * 12, 120 + i * 10, max(28, 90 - i * 7))
        ldraw.polygon(points, fill=colour)
        layer = layer.filter(ImageFilter.GaussianBlur(6))
        img.alpha_composite(layer)

    draw_centered_text(
        img,
        title,
        subtitle,
        title_fill=(255, 252, 245, 255),
        subtitle_fill=(255, 232, 210, 245),
        glow_fill=(255, 210, 170, 120),
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, 'PNG')


def style_minimal_paper(title: str, subtitle: str, output_path: Path, rnd: random.Random) -> None:
    img = Image.new('RGBA', (WIDTH, HEIGHT), (242, 235, 223, 255))
    draw = ImageDraw.Draw(img, 'RGBA')

    for y in range(HEIGHT):
        alpha = rnd.randint(8, 18)
        draw.line([(0, y), (WIDTH, y)], fill=(140, 125, 108, alpha), width=1)

    accents = [(185, 120, 90, 110), (108, 130, 154, 100), (128, 145, 108, 100)]
    for _ in range(6):
        x1 = rnd.randint(-80, WIDTH - 120)
        y1 = rnd.randint(-40, HEIGHT - 80)
        x2 = x1 + rnd.randint(160, 300)
        y2 = y1 + rnd.randint(80, 180)
        draw.ellipse((x1, y1, x2, y2), fill=rnd.choice(accents))

    draw_centered_text(
        img,
        title,
        subtitle,
        title_fill=(55, 44, 36, 255),
        subtitle_fill=(88, 74, 62, 245),
        glow_fill=None,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, 'PNG')


def style_neon_grid(title: str, subtitle: str, output_path: Path, rnd: random.Random) -> None:
    img = Image.new('RGBA', (WIDTH, HEIGHT), (8, 10, 24, 255))
    draw = ImageDraw.Draw(img, 'RGBA')

    for y in range(HEIGHT):
        t = y / max(HEIGHT - 1, 1)
        draw.line(
            [(0, y), (WIDTH, y)],
            fill=(int(10 + 35 * t), int(12 + 20 * t), int(35 + 80 * t), 255),
            width=1,
        )

    for x in range(0, WIDTH, 32):
        draw.line([(x, 0), (x, HEIGHT)], fill=(50, 235, 255, 42), width=1)
    for y in range(0, HEIGHT, 32):
        draw.line([(0, y), (WIDTH, y)], fill=(220, 75, 255, 32), width=1)

    for _ in range(20):
        x1 = rnd.randint(0, WIDTH - 1)
        y1 = rnd.randint(0, HEIGHT - 1)
        x2 = x1 + rnd.randint(-220, 220)
        y2 = y1 + rnd.randint(-120, 120)
        draw.line([(x1, y1), (x2, y2)], fill=(120, 255, 220, 50), width=2)

    draw_centered_text(
        img,
        title,
        subtitle,
        title_fill=(248, 253, 255, 255),
        subtitle_fill=(190, 235, 255, 245),
        glow_fill=(75, 240, 255, 140),
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, 'PNG')


def style_aurora_mist(title: str, subtitle: str, output_path: Path, rnd: random.Random) -> None:
    img = Image.new('RGBA', (WIDTH, HEIGHT), (8, 20, 32, 255))

    bands = [
        (70, 245, 190),
        (110, 190, 255),
        (170, 120, 255),
        (110, 255, 150),
    ]

    for i in range(8):
        layer = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer, 'RGBA')
        colour = bands[i % len(bands)]
        base = 40 + i * 45
        amp = rnd.randint(18, 40)
        freq = rnd.uniform(0.006, 0.012)
        points = []
        for x in range(0, WIDTH + 12, 12):
            y = int(base + amp * math.sin(x * freq + i * 0.9))
            points.append((x, y))
        points.extend([(WIDTH, HEIGHT), (0, HEIGHT)])
        draw.polygon(points, fill=(*colour, 55))
        layer = layer.filter(ImageFilter.GaussianBlur(18))
        img.alpha_composite(layer)

    draw_centered_text(
        img,
        title,
        subtitle,
        title_fill=(244, 255, 252, 255),
        subtitle_fill=(205, 235, 255, 245),
        glow_fill=(150, 255, 225, 120),
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, 'PNG')


def style_retro_terminal(title: str, subtitle: str, output_path: Path, rnd: random.Random) -> None:
    img = Image.new('RGBA', (WIDTH, HEIGHT), (10, 20, 10, 255))
    draw = ImageDraw.Draw(img, 'RGBA')

    for y in range(HEIGHT):
        t = y / max(HEIGHT - 1, 1)
        draw.line([(0, y), (WIDTH, y)], fill=(int(8 + 20 * t), int(30 + 60 * t), int(8 + 18 * t), 255), width=1)

    for y in range(0, HEIGHT, 3):
        draw.line([(0, y), (WIDTH, y)], fill=(0, 0, 0, 26), width=1)

    mono_font = find_font(16)
    snippets = ['> build', '> deploy', '> test --all', '> analyse logs', '> status ok']
    for i in range(9):
        draw.text((24, 18 + i * 22), rnd.choice(snippets), font=mono_font, fill=(120, 255, 140, 80))

    draw_centered_text(
        img,
        title,
        subtitle,
        title_fill=(205, 255, 195, 255),
        subtitle_fill=(165, 225, 160, 245),
        glow_fill=(120, 255, 130, 95),
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, 'PNG')


def style_geometric_collage(title: str, subtitle: str, output_path: Path, rnd: random.Random) -> None:
    img = Image.new('RGBA', (WIDTH, HEIGHT), (22, 25, 34, 255))
    draw = ImageDraw.Draw(img, 'RGBA')

    palette = [
        (255, 110, 90, 120),
        (95, 180, 255, 120),
        (255, 205, 90, 110),
        (145, 115, 255, 120),
        (90, 220, 180, 110),
    ]

    for _ in range(28):
        shape = rnd.choice(['rect', 'tri', 'circle'])
        colour = rnd.choice(palette)
        x = rnd.randint(-80, WIDTH)
        y = rnd.randint(-80, HEIGHT)
        size = rnd.randint(50, 180)

        if shape == 'rect':
            draw.rectangle((x, y, x + size, y + int(size * rnd.uniform(0.4, 1.1))), fill=colour)
        elif shape == 'circle':
            draw.ellipse((x, y, x + size, y + size), fill=colour)
        else:
            points = [(x, y), (x + size, y + rnd.randint(0, size)), (x + rnd.randint(0, size), y + size)]
            draw.polygon(points, fill=colour)

    overlay = Image.new('RGBA', (WIDTH, HEIGHT), (255, 255, 255, 0))
    odraw = ImageDraw.Draw(overlay, 'RGBA')
    for _ in range(12):
        odraw.line(
            [(rnd.randint(0, WIDTH), rnd.randint(0, HEIGHT)), (rnd.randint(0, WIDTH), rnd.randint(0, HEIGHT))],
            fill=(255, 255, 255, 35),
            width=rnd.randint(1, 4),
        )
    img.alpha_composite(overlay)

    draw_centered_text(
        img,
        title,
        subtitle,
        title_fill=(255, 255, 255, 255),
        subtitle_fill=(230, 235, 248, 245),
        glow_fill=(255, 255, 255, 70),
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, 'PNG')


def generate_cover(title: str, subtitle: str, output_path: Path, style: str, seed: int | None) -> str:
    rnd = random.Random(seed)
    selected_style = style
    if selected_style == 'random':
        selected_style = pick_weighted_style(rnd)

    generators = {
        'mesh-gradient': style_mesh_gradient,
        'blueprint': style_blueprint,
        'duotone-noise': style_duotone_noise,
        'sunset-waves': style_sunset_waves,
        'minimal-paper': style_minimal_paper,
        'neon-grid': style_neon_grid,
        'aurora-mist': style_aurora_mist,
        'retro-terminal': style_retro_terminal,
        'geometric-collage': style_geometric_collage,
    }

    if selected_style not in generators:
        raise ValueError(f'Unknown style: {selected_style}')

    generators[selected_style](title, subtitle, output_path, rnd)
    return selected_style


def main() -> None:
    parser = argparse.ArgumentParser(description='Generate creative cover image with random style by default')
    parser.add_argument('--title', required=True, help='Title text')
    parser.add_argument('--subtitle', default='', help='Subtitle text')
    parser.add_argument('--output', required=True, help='Output path for the image')
    parser.add_argument(
        '--style',
        default='random',
        choices=('random',) + STYLES,
        help='Cover style. Defaults to random.',
    )
    parser.add_argument('--seed', type=int, default=None, help='Optional random seed for repeatable output')

    args = parser.parse_args()
    output_path = Path(args.output)
    used_style = generate_cover(args.title, args.subtitle, output_path, args.style, args.seed)
    print(f'Saved creative cover -> {output_path} ({WIDTH}x{HEIGHT}), style={used_style}')


if __name__ == '__main__':
    main()
