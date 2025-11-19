from PIL import Image, ImageDraw, ImageFont
import os
import requests
from io import BytesIO

# Generates a 1000x420 cover image using a public Book of News image as background.
OUT = os.path.join('posts', '2025', 'Ignite-2025-DevOps', 'assets')
os.makedirs(OUT, exist_ok=True)
PATH = os.path.join(OUT, 'main.png')
W, H = 1000, 420

# Public Book of News main image (press asset)
BG_URL = 'https://msftstories.thesourcemediaassets.com/sites/739/2025/11/ignite-2025-book-of-news-main-1024x576.jpg'

def download_image(url):
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return Image.open(BytesIO(resp.content)).convert('RGBA')

bg = None
try:
    bg = download_image(BG_URL)
except Exception:
    bg = Image.new('RGBA', (W, H), '#0f1724')

# Resize/crop background to fill 1000x420 while preserving aspect ratio
bg_w, bg_h = bg.size
scale = max(W / bg_w, H / bg_h)
new_size = (int(bg_w * scale), int(bg_h * scale))
bg = bg.resize(new_size, Image.LANCZOS)
# center crop
left = (bg.width - W) // 2
top = (bg.height - H) // 2
bg = bg.crop((left, top, left + W, top + H)).convert('RGB')

img = Image.new('RGB', (W, H))
img.paste(bg)
draw = ImageDraw.Draw(img)

# overlay for better contrast
overlay = Image.new('RGBA', (W, H), (6, 11, 20, 140))
img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
draw = ImageDraw.Draw(img)

try:
    font = ImageFont.truetype('arial.ttf', 48)
    font_small = ImageFont.truetype('arial.ttf', 20)
except Exception:
    font = ImageFont.load_default()
    font_small = ImageFont.load_default()

# Title using hyphen instead of em dash
title = 'Ignite 2025 - Devs & DevOps'
bbox = draw.textbbox((0, 0), title, font=font)
tw = bbox[2] - bbox[0]
th = bbox[3] - bbox[1]
draw.text(((W - tw) / 2, 110), title, font=font, fill='white')

subtitle = 'Top announcements, tools and practical guidance for developers & DevOps'
bbox2 = draw.textbbox((0, 0), subtitle, font=font_small)
sw = bbox2[2] - bbox2[0]
draw.text(((W - sw) / 2, 110 + th + 14), subtitle, font=font_small, fill='#e6eef8')

# footer note
draw.text((20, H - 30), 'Pwd9000 - Microsoft Ignite 2025 highlights', font=font_small, fill='#cbd6e6')

img.save(PATH)
print('Wrote', PATH)
