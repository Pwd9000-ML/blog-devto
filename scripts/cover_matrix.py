#!/usr/bin/env python3
"""Generate an advanced Matrix/cyberpunk style cover image with modern effects."""

from __future__ import annotations

import math
import random
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
except ImportError:
    print("Pillow is required: python -m pip install pillow")
    exit(1)

WIDTH, HEIGHT = 1000, 420
FONT_CANDIDATES = (
    r"C:\Windows\Fonts\consola.ttf",  # Consolas - great for code/tech
    r"C:\Windows\Fonts\cascadiamono.ttf",
    r"C:\Windows\Fonts\seguisb.ttf",
    r"C:\Windows\Fonts\segoeuib.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
)


def find_font(size: int, mono: bool = False) -> ImageFont.FreeTypeFont:
    """Find a suitable font, preferring monospace for code aesthetics."""
    candidates = FONT_CANDIDATES if not mono else FONT_CANDIDATES[:2] + FONT_CANDIDATES[2:]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size)
            except OSError:
                continue
    return ImageFont.load_default()


def measure(draw: ImageDraw.ImageDraw, text: str, font) -> tuple[int, int]:
    """Measure text dimensions."""
    if hasattr(draw, "textbbox"):
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        return right - left, bottom - top
    return draw.textsize(text, font=font)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    """Wrap text to fit within max_width."""
    words = text.split()
    if not words:
        return []
    lines = []
    current = []
    for word in words:
        candidate = " ".join(current + [word]) if current else word
        width, _ = measure(draw, candidate, font)
        if width <= max_width or not current:
            current.append(word)
        else:
            lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def create_gradient_background(width: int, height: int) -> Image.Image:
    """Create a deep cyberpunk gradient background."""
    img = Image.new("RGBA", (width, height))
    draw = ImageDraw.Draw(img)
    
    # Deep purple to dark blue gradient with slight green tint
    for y in range(height):
        t = y / max(height - 1, 1)
        # Start: dark purple, End: near black with slight blue
        r = int(12 * (1 - t) + 2 * t)
        g = int(8 * (1 - t) + 12 * t)
        b = int(24 * (1 - t) + 8 * t)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
    
    return img


def draw_matrix_rain(img: Image.Image, density: int = 80, seed: int = 42) -> None:
    """Draw Matrix-style falling code characters."""
    draw = ImageDraw.Draw(img, "RGBA")
    rnd = random.Random(seed)
    
    # Matrix characters (katakana-inspired + tech symbols)
    chars = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン01{}[]<>/\\|#$%&@"
    
    mono_font = find_font(14, mono=True)
    
    for _ in range(density):
        x = rnd.randint(0, WIDTH)
        # Create vertical streams
        stream_length = rnd.randint(3, 12)
        start_y = rnd.randint(-100, HEIGHT)
        
        for i in range(stream_length):
            y = start_y + i * 18
            if 0 <= y < HEIGHT:
                char = rnd.choice(chars)
                # Fade effect: brighter at the head, dimmer at tail
                brightness = max(40, 255 - (i * 25))
                # Green tint with varying intensity
                if i == 0:
                    # Head of stream - bright white/green
                    color = (200, 255, 200, min(255, brightness + 50))
                else:
                    color = (0, brightness, int(brightness * 0.4), brightness)
                draw.text((x, y), char, font=mono_font, fill=color)


def draw_circuit_lines(img: Image.Image, seed: int = 123) -> None:
    """Draw subtle circuit board traces."""
    draw = ImageDraw.Draw(img, "RGBA")
    rnd = random.Random(seed)
    
    for _ in range(25):
        # Start point
        x = rnd.randint(0, WIDTH)
        y = rnd.randint(0, HEIGHT)
        
        # Draw connected segments
        points = [(x, y)]
        for _ in range(rnd.randint(2, 5)):
            # Move horizontally or vertically
            if rnd.choice([True, False]):
                x += rnd.choice([-1, 1]) * rnd.randint(30, 120)
            else:
                y += rnd.choice([-1, 1]) * rnd.randint(20, 80)
            x = max(0, min(WIDTH, x))
            y = max(0, min(HEIGHT, y))
            points.append((x, y))
        
        # Draw the trace
        color = rnd.choice([
            (0, 180, 100, 40),
            (0, 120, 180, 35),
            (100, 200, 150, 30),
        ])
        if len(points) >= 2:
            draw.line(points, fill=color, width=1)
            # Add nodes at junctions
            for px, py in points:
                draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(0, 200, 120, 60))


def draw_hex_grid(img: Image.Image, opacity: int = 20) -> None:
    """Draw a subtle hexagonal grid pattern."""
    draw = ImageDraw.Draw(img, "RGBA")
    
    hex_size = 40
    h = hex_size * math.sqrt(3)
    
    for row in range(-1, int(HEIGHT / h) + 2):
        for col in range(-1, int(WIDTH / (hex_size * 1.5)) + 2):
            cx = col * hex_size * 1.5
            cy = row * h + (col % 2) * (h / 2)
            
            # Calculate hexagon points
            points = []
            for i in range(6):
                angle = math.pi / 3 * i + math.pi / 6
                px = cx + hex_size * 0.8 * math.cos(angle)
                py = cy + hex_size * 0.8 * math.sin(angle)
                points.append((px, py))
            
            draw.polygon(points, outline=(0, 200, 150, opacity))


def draw_glow_orbs(img: Image.Image, seed: int = 456) -> None:
    """Add floating glow orbs for depth."""
    rnd = random.Random(seed)
    
    for _ in range(8):
        # Create a separate layer for each orb
        orb = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        odraw = ImageDraw.Draw(orb, "RGBA")
        
        cx = rnd.randint(50, WIDTH - 50)
        cy = rnd.randint(50, HEIGHT - 50)
        radius = rnd.randint(20, 60)
        
        # Color variations
        color = rnd.choice([
            (0, 255, 150),   # Cyan-green
            (0, 200, 255),   # Cyan
            (150, 100, 255), # Purple
            (0, 255, 200),   # Teal
        ])
        
        # Draw concentric circles with decreasing opacity
        for r in range(radius, 0, -2):
            alpha = int(30 * (r / radius))
            odraw.ellipse(
                [cx - r, cy - r, cx + r, cy + r],
                fill=(color[0], color[1], color[2], alpha)
            )
        
        # Blur the orb
        orb = orb.filter(ImageFilter.GaussianBlur(radius // 3))
        img.alpha_composite(orb)


def draw_scanlines(img: Image.Image, intensity: int = 15) -> None:
    """Add CRT-style scanlines."""
    draw = ImageDraw.Draw(img, "RGBA")
    
    for y in range(0, HEIGHT, 3):
        draw.line([(0, y), (WIDTH, y)], fill=(0, 0, 0, intensity))


def draw_vignette(img: Image.Image, strength: float = 0.4) -> Image.Image:
    """Apply a vignette effect to darken edges."""
    vignette = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(vignette, "RGBA")
    
    cx, cy = WIDTH // 2, HEIGHT // 2
    max_dist = math.sqrt(cx ** 2 + cy ** 2)
    
    # Draw radial gradient
    for ring in range(int(max_dist), 0, -2):
        dist_ratio = ring / max_dist
        if dist_ratio > 0.5:
            alpha = int(255 * strength * ((dist_ratio - 0.5) / 0.5) ** 1.5)
            vdraw.ellipse(
                [cx - ring, cy - ring, cx + ring, cy + ring],
                outline=(0, 0, 0, min(255, alpha)),
                width=3
            )
    
    vignette = vignette.filter(ImageFilter.GaussianBlur(30))
    img.alpha_composite(vignette)
    return img


def draw_title_with_glow(
    img: Image.Image,
    title: str,
    subtitle: str,
    title_font,
    subtitle_font,
) -> None:
    """Draw title and subtitle with neon glow effect."""
    draw = ImageDraw.Draw(img, "RGBA")
    
    # Calculate text positioning
    max_width = int(WIDTH * 0.85)
    title_lines = wrap_text(draw, title, title_font, max_width)
    subtitle_lines = wrap_text(draw, subtitle, subtitle_font, max_width)
    
    # Measure total height
    line_spacing = 8
    title_height = sum(measure(draw, line, title_font)[1] for line in title_lines)
    title_height += (len(title_lines) - 1) * line_spacing
    
    subtitle_height = sum(measure(draw, line, subtitle_font)[1] for line in subtitle_lines)
    subtitle_height += (len(subtitle_lines) - 1) * (line_spacing - 2)
    
    gap = 20
    total_height = title_height + gap + subtitle_height
    start_y = (HEIGHT - total_height) // 2
    
    # Draw title with glow
    y = start_y
    for line in title_lines:
        w, h = measure(draw, line, title_font)
        x = (WIDTH - w) // 2
        
        # Create glow layer
        glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow, "RGBA")
        
        # Draw multiple layers of glow
        glow_color = (0, 255, 180)  # Cyan-green glow
        for offset in range(12, 0, -2):
            alpha = int(40 - offset * 3)
            gdraw.text((x, y), line, font=title_font, fill=(glow_color[0], glow_color[1], glow_color[2], alpha))
        
        glow = glow.filter(ImageFilter.GaussianBlur(8))
        img.alpha_composite(glow)
        
        # Draw main text with slight shadow
        draw.text((x + 2, y + 2), line, font=title_font, fill=(0, 40, 30, 150))
        draw.text((x, y), line, font=title_font, fill=(255, 255, 255, 255))
        
        y += h + line_spacing
    
    # Draw subtitle
    y += gap - line_spacing
    for line in subtitle_lines:
        w, h = measure(draw, line, subtitle_font)
        x = (WIDTH - w) // 2
        
        # Subtle glow for subtitle
        glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow, "RGBA")
        gdraw.text((x, y), line, font=subtitle_font, fill=(0, 200, 150, 50))
        glow = glow.filter(ImageFilter.GaussianBlur(4))
        img.alpha_composite(glow)
        
        # Main subtitle text
        draw.text((x + 1, y + 1), line, font=subtitle_font, fill=(0, 20, 15, 100))
        draw.text((x, y), line, font=subtitle_font, fill=(180, 220, 210, 255))
        
        y += h + line_spacing - 2


def draw_corner_accents(img: Image.Image) -> None:
    """Draw tech-style corner brackets."""
    draw = ImageDraw.Draw(img, "RGBA")
    
    accent_color = (0, 255, 180, 180)
    length = 40
    thickness = 2
    margin = 25
    
    # Top-left
    draw.line([(margin, margin), (margin + length, margin)], fill=accent_color, width=thickness)
    draw.line([(margin, margin), (margin, margin + length)], fill=accent_color, width=thickness)
    
    # Top-right
    draw.line([(WIDTH - margin - length, margin), (WIDTH - margin, margin)], fill=accent_color, width=thickness)
    draw.line([(WIDTH - margin, margin), (WIDTH - margin, margin + length)], fill=accent_color, width=thickness)
    
    # Bottom-left
    draw.line([(margin, HEIGHT - margin), (margin + length, HEIGHT - margin)], fill=accent_color, width=thickness)
    draw.line([(margin, HEIGHT - margin - length), (margin, HEIGHT - margin)], fill=accent_color, width=thickness)
    
    # Bottom-right
    draw.line([(WIDTH - margin - length, HEIGHT - margin), (WIDTH - margin, HEIGHT - margin)], fill=accent_color, width=thickness)
    draw.line([(WIDTH - margin, HEIGHT - margin - length), (WIDTH - margin, HEIGHT - margin)], fill=accent_color, width=thickness)


def add_chromatic_aberration(img: Image.Image, offset: int = 2) -> Image.Image:
    """Add subtle chromatic aberration effect."""
    r, g, b, a = img.split()
    
    # Offset red channel slightly
    r = r.transform(r.size, Image.AFFINE, (1, 0, offset, 0, 1, 0))
    # Offset blue channel in opposite direction
    b = b.transform(b.size, Image.AFFINE, (1, 0, -offset, 0, 1, 0))
    
    return Image.merge("RGBA", (r, g, b, a))


def add_noise(img: Image.Image, amount: float = 0.03) -> Image.Image:
    """Add subtle film grain noise."""
    import random
    
    pixels = img.load()
    width, height = img.size
    
    rnd = random.Random(789)
    for y in range(height):
        for x in range(width):
            if rnd.random() < amount:
                r, g, b, a = pixels[x, y]
                noise = rnd.randint(-15, 15)
                pixels[x, y] = (
                    max(0, min(255, r + noise)),
                    max(0, min(255, g + noise)),
                    max(0, min(255, b + noise)),
                    a
                )
    
    return img


def generate_matrix_cover(
    title: str,
    subtitle: str,
    output_path: Path,
) -> None:
    """Generate the complete Matrix-style cover image."""
    
    # Create base with gradient
    img = create_gradient_background(WIDTH, HEIGHT)
    
    # Add background effects (layered from back to front)
    draw_hex_grid(img, opacity=15)
    draw_circuit_lines(img, seed=123)
    draw_matrix_rain(img, density=100, seed=42)
    draw_glow_orbs(img, seed=456)
    
    # Add scanlines for CRT effect
    draw_scanlines(img, intensity=12)
    
    # Draw text with glow
    title_font = find_font(52)
    subtitle_font = find_font(22)
    draw_title_with_glow(img, title, subtitle, title_font, subtitle_font)
    
    # Add corner accents
    draw_corner_accents(img)
    
    # Apply vignette
    img = draw_vignette(img, strength=0.5)
    
    # Post-processing effects
    img = add_chromatic_aberration(img, offset=1)
    img = add_noise(img, amount=0.02)
    
    # Slight contrast boost
    enhancer = ImageEnhance.Contrast(img.convert("RGB"))
    final = enhancer.enhance(1.1)
    
    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final.save(output_path, "PNG")
    print(f"Saved Matrix-style cover -> {output_path} ({WIDTH}x{HEIGHT})")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate Matrix/cyberpunk style cover")
    parser.add_argument("--title", required=True, help="Title text")
    parser.add_argument("--subtitle", required=True, help="Subtitle/description text")
    parser.add_argument("--output", required=True, help="Output path for the image")
    
    args = parser.parse_args()
    
    generate_matrix_cover(
        title=args.title,
        subtitle=args.subtitle,
        output_path=Path(args.output),
    )


if __name__ == "__main__":
    main()
