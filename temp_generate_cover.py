from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path

assets_path = Path('posts/2025/DevOps-md2mermaid/assets')
width, height = 1000, 420

base = Image.new('RGBA', (width, height))
pixels = base.load()
start = (11, 17, 32)
end = (24, 121, 201)
for x in range(width):
    blend = x / (width - 1)
    r = int(start[0] + (end[0] - start[0]) * blend)
    g = int(start[1] + (end[1] - start[1]) * blend)
    b = int(start[2] + (end[2] - start[2]) * blend)
    for y in range(height):
        pixels[x, y] = (r, g, b, 255)

overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
draw_overlay = ImageDraw.Draw(overlay)
for i in range(-height, width, 60):
    draw_overlay.line([(i, 0), (i + height, height)], fill=(255, 255, 255, 25), width=2)
overlay = overlay.filter(ImageFilter.GaussianBlur(6))
base = Image.alpha_composite(base, overlay)

spot = Image.new('RGBA', (width, height), (0, 0, 0, 0))
draw_spot = ImageDraw.Draw(spot)
spot_radius = 200
spot_center = (int(width * 0.72), int(height * 0.5))
draw_spot.ellipse([
    spot_center[0] - spot_radius,
    spot_center[1] - spot_radius,
    spot_center[0] + spot_radius,
    spot_center[1] + spot_radius
], fill=(255, 255, 255, 80))
spot = spot.filter(ImageFilter.GaussianBlur(80))
base = Image.alpha_composite(base, spot)

logo = Image.open(assets_path / 'MD2MMD.png').convert('RGBA')
max_logo_height = 260
scale = max_logo_height / logo.height
logo_size = (int(logo.width * scale), max_logo_height)
logo = logo.resize(logo_size, Image.Resampling.LANCZOS)

logo_x = width - logo_size[0] - 80
logo_y = (height - logo_size[1]) // 2
base.paste(logo, (logo_x, logo_y), logo)

font_path_bold = Path('C:/Windows/Fonts/segoeuib.ttf')
font_path_regular = Path('C:/Windows/Fonts/SegoeUI.ttf')
if not font_path_regular.exists():
    font_path_regular = font_path_bold

title_font = ImageFont.truetype(str(font_path_bold), 60)
subtitle_font = ImageFont.truetype(str(font_path_regular), 32)
small_font = ImageFont.truetype(str(font_path_regular), 24)

text_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
draw = ImageDraw.Draw(text_layer)

left_margin = 70
top_margin = 120

draw.text((left_margin, top_margin), 'Convert 2 Mermaid API', font=title_font, fill=(236, 247, 255, 255))
draw.text((left_margin, top_margin + 80), 'From Markdown outlines to polished diagrams', font=subtitle_font, fill=(205, 227, 255, 255))

badge_y = top_margin + 140
badge_text = 'Automate documentation visuals in seconds'
badge_padding = (24, 14)
text_bbox = draw.textbbox((0, 0), badge_text, font=small_font)
badge_width = (text_bbox[2] - text_bbox[0]) + badge_padding[0] * 2
badge_height = (text_bbox[3] - text_bbox[1]) + badge_padding[1] * 2
badge_rect = [left_margin, badge_y, left_margin + badge_width, badge_y + badge_height]
draw.rounded_rectangle(badge_rect, radius=22, fill=(12, 176, 205, 180))
draw.text((left_margin + badge_padding[0], badge_y + badge_padding[1] - 4), badge_text, font=small_font, fill=(6, 20, 34, 255))

accent = ImageDraw.Draw(text_layer)
accent_radius = 8
accent_positions = [
    (left_margin, top_margin - 40),
    (left_margin + 180, top_margin - 60),
    (left_margin + 360, top_margin - 20)
]
for cx, cy in accent_positions:
    accent.ellipse([cx - accent_radius, cy - accent_radius, cx + accent_radius, cy + accent_radius], fill=(76, 213, 255, 160))

base = Image.alpha_composite(base, text_layer)

output_png = assets_path / 'main.png'
base.convert('RGB').save(output_png, format='PNG', optimize=True)

print(f'Saved {output_png} ({width}x{height})')
