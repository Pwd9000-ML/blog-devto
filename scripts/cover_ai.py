#!/usr/bin/env python3
"""Create topic-specific DEV.to covers using Cloudflare Workers AI."""

from __future__ import annotations

import argparse
import base64
import io
import json
import os
import random
import re
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from PIL import Image, ImageDraw, ImageFont, ImageOps

WIDTH, HEIGHT = 1000, 420
FONT_CANDIDATES = (
    r'C:\Windows\Fonts\segoeuib.ttf',
    r'C:\Windows\Fonts\seguisb.ttf',
    r'C:\Windows\Fonts\arialbd.ttf',
    r'C:\Windows\Fonts\consola.ttf',
)
ENV_FILE = Path(__file__).resolve().parent.parent / '.env'
ENV_KEYS = ('CLOUDFLARE_ACCOUNT_ID', 'CLOUDFLARE_API_TOKEN')
CLOUDFLARE_DEFAULT_MODEL = '@cf/leonardo/lucid-origin'
ART_DIRECTIONS = {
    'cinematic-diorama': 'A tactile miniature diorama with dramatic studio lighting and shallow depth of field.',
    'editorial-collage': 'An original layered editorial collage with cut-paper and material textures.',
    'isometric-world': 'A detailed 3D isometric world with a few meaningful, connected objects.',
    'paper-sculpture': 'An intricate sculpted-paper scene with dimensional shadows and bold shapes.',
    'macro-materials': 'A striking close-up of physical objects in glass, ceramic, and brushed metal.',
    'neon-night': 'A moody night scene with soft volumetric light, glowing edges, and reflective surfaces.',
    'technical-illustration': 'A sophisticated conceptual illustration with precise shapes and rich texture.',
}
PALETTES = (
    'deep navy, electric cyan, and restrained coral accents',
    'charcoal, warm amber, and violet highlights',
    'midnight indigo, mint, and soft rose',
    'near-black, teal, and warm orange glow',
    'graphite, lime, and muted teal',
    'dark slate, magenta, and sky blue',
)
# Opt-in GitHub-inspired key art (brand.github.com). Logos and mascots are trademarked: never request them.
GITHUB_DIRECTION = (
    'A detailed 3D isometric landscape built from contribution-graph cubes floating in a dark night sky, '
    'some cubes solid, some transparent glass, some glowing, with subtle dithered pixel textures, '
    'soft rim lighting, and a few tiny stars. No animal mascots or characters.'
)
GITHUB_THEMES = {
    'core': 'near-black #101411 and charcoal neutrals with glowing GitHub green #0FBF3E accents',
    'security': (
        'near-black #101411 and charcoal neutrals with GitHub green #0FBF3E and '
        'security blue #3094FF glowing accents'
    ),
    'copilot': (
        'near-black #101411 and charcoal neutrals with GitHub green #0FBF3E and '
        'Copilot purple #8534F3 glowing accents'
    ),
}


@dataclass(frozen=True)
class ArtBrief:
    title: str
    subtitle: str
    topic: str
    seed: int
    art_direction: str
    palette: str
    prompt: str
    output: str
    source: str = 'brief-only'
    model: str | None = None


def validate_output(output: str) -> None:
    if (
        Path(output).name != output or '\\' in output or '/' in output
        or ':' in output or Path(output).suffix.lower() != '.png'
    ):
        raise ValueError('The output must be a PNG filename without directories.')


def create_brief(
    title: str,
    topic: str,
    subtitle: str,
    output: str,
    seed: int | None = None,
    github_theme: str | None = None,
    art_direction: str | None = None,
) -> ArtBrief:
    if not title.strip() or not topic.strip():
        raise ValueError('The title and public visual concept must not be empty.')
    validate_output(output)
    if github_theme is not None and github_theme not in GITHUB_THEMES:
        raise ValueError(f'Unknown GitHub theme. Choose from: {", ".join(GITHUB_THEMES)}.')
    if art_direction is not None and art_direction not in ART_DIRECTIONS:
        raise ValueError(f'Unknown art direction. Choose from: {", ".join(ART_DIRECTIONS)}.')
    actual_seed = random.SystemRandom().randrange(2**63) if seed is None else seed
    rnd = random.Random(actual_seed)
    direction = art_direction or rnd.choice(tuple(ART_DIRECTIONS))
    description = ART_DIRECTIONS[direction]
    palette = rnd.choice(PALETTES)
    if github_theme is not None:
        direction, description, palette = 'github-key-art', GITHUB_DIRECTION, GITHUB_THEMES[github_theme]
    # Omit the title: diffusion models tend to paint any quoted words into the artwork.
    prompt = (
        'A purely visual, wordless editorial illustration. '
        f'Scene: {topic.strip()}. '
        'Interpret that concept with one concrete, topic-relevant visual metaphor. '
        f'Art direction: {description} Palette: {palette}. '
        'Make an actual illustration, not a poster, title slide, or generic AI brain or robot. '
        'Wide horizontal banner composition. Place the main subject on the right third; '
        'the left half is plain, dark, empty background with nothing in it. '
        'Keep all important objects in the middle 55 percent of the image height so '
        'the artwork can be centre-cropped to a 1000 by 420 pixel banner. '
        'Every surface is blank and unmarked: no typography, lettering, signage, labels, code, '
        'logos, watermarks, or user-interface screenshots. '
        'Do not imitate another author or artist. Render original objects and composition.'
    )
    return ArtBrief(
        title.strip(), subtitle.strip(), topic.strip(), actual_seed,
        direction, palette, prompt, output,
    )


def load_brief(path: Path) -> ArtBrief:
    data = json.loads(path.read_text(encoding='utf-8'))
    text_fields = ('title', 'subtitle', 'topic', 'art_direction', 'palette', 'prompt', 'output', 'source')
    if not isinstance(data, dict) or any(
        not isinstance(data.get(field), str) for field in text_fields
    ):
        raise ValueError(f'Invalid cover brief: {path}')
    if type(data.get('seed')) is not int or (
        data.get('model') is not None and not isinstance(data['model'], str)
    ):
        raise ValueError(f'Invalid seed or model in cover brief: {path}')
    brief = ArtBrief(**data)
    if not brief.title.strip() or not brief.topic.strip() or not brief.prompt.strip():
        raise ValueError('The brief needs a non-empty title, topic, and image prompt.')
    validate_output(brief.output)
    return brief


def save_brief(path: Path, brief: ArtBrief) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(brief), indent=2) + '\n', encoding='utf-8')


def load_credentials_from_env_file(path: Path | None = None) -> None:
    path = ENV_FILE if path is None else path
    if not path.is_file():
        return
    for line in path.read_text(encoding='utf-8-sig').splitlines():
        name, separator, value = line.strip().partition('=')
        name = name.strip()
        if not separator or name not in ENV_KEYS or os.environ.get(name, '').strip():
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in '"\'':
            value = value[1:-1].strip()
        if value:
            os.environ[name] = value


def api_error_reason(error: HTTPError) -> str:
    # Never print provider messages, which could contain credentials or prompt content.
    with error:
        body = error.read()
    try:
        data = json.loads(body or b'{}')
    except ValueError:
        return ''
    errors = data.get('errors') if isinstance(data, dict) else None
    if not isinstance(errors, list):
        return ''
    codes = [
        str(item['code']) for item in errors
        if isinstance(item, dict) and type(item.get('code')) is int
    ]
    return f": {', '.join(dict.fromkeys(codes))}" if codes else ''


def generate_artwork_cloudflare(prompt: str) -> Image.Image:
    account = os.environ.get('CLOUDFLARE_ACCOUNT_ID', '').strip()
    token = os.environ.get('CLOUDFLARE_API_TOKEN', '').strip()
    if not account or not token:
        raise ValueError(
            'CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN must be set. No image request was made.'
        )
    if not re.fullmatch(r'[0-9a-fA-F]{32}', account):
        raise ValueError('CLOUDFLARE_ACCOUNT_ID must be the 32-character account ID. No request was made.')
    if not prompt.strip():
        raise ValueError('The image prompt must not be empty. No image request was made.')
    request = Request(
        f'https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/{CLOUDFLARE_DEFAULT_MODEL}',
        data=json.dumps({'prompt': prompt, 'width': 1344, 'height': 576}).encode('utf-8'),
        headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'},
        method='POST',
    )
    try:
        with urlopen(request, timeout=180) as response:
            content_type = response.headers.get('Content-Type', '')
            body = response.read()
    except HTTPError as error:
        raise RuntimeError(
            f'Image generation failed (HTTP {error.code}{api_error_reason(error)}). '
            'Check the account ID, Workers AI token permissions, and the daily free allocation. '
            'No automatic retry.'
        ) from error
    except URLError as error:
        raise RuntimeError('Image generation could not reach Cloudflare. No automatic retry.') from error
    if content_type.startswith('image/'):
        image_bytes = body
    else:
        data = json.loads(body)
        result = data.get('result') if isinstance(data, dict) else None
        if (
            not isinstance(data, dict) or data.get('success') is False
            or not isinstance(result, dict) or not isinstance(result.get('image'), str)
        ):
            raise ValueError('Workers AI response did not contain a base64 image.')
        image_bytes = base64.b64decode(result['image'], validate=True)
    with Image.open(io.BytesIO(image_bytes)) as image:
        artwork = ImageOps.exif_transpose(image).convert('RGBA')
    if artwork.width < WIDTH or artwork.height < HEIGHT:
        raise ValueError(f'Workers AI artwork must be at least {WIDTH}x{HEIGHT} pixels.')
    return artwork


def find_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in FONT_CANDIDATES:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default(size=size)


def measure(
    draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
) -> tuple[int, int]:
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    return int(right - left), int(bottom - top)


def wrap_text(
    draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    max_width: int,
) -> list[str]:
    lines: list[str] = []
    current: list[str] = []
    for word in text.split():
        candidate = ' '.join(current + [word])
        if measure(draw, candidate, font)[0] <= max_width or not current:
            current.append(word)
        else:
            lines.append(' '.join(current))
            current = [word]
    if current:
        lines.append(' '.join(current))
    return lines


def fit_text(
    draw: ImageDraw.ImageDraw, text: str, width: int, height: int, maximum_size: int,
) -> tuple[ImageFont.FreeTypeFont | ImageFont.ImageFont, list[str], int]:
    for size in range(maximum_size, 17, -2):
        font = find_font(size)
        lines = wrap_text(draw, text, font, width)
        line_height = measure(draw, 'Ag', font)[1] + 10
        if (
            all(measure(draw, line, font)[0] <= width for line in lines)
            and len(lines) * line_height <= height
        ):
            return font, lines, line_height
    raise ValueError('Cover text does not fit. Use a shorter headline or subtitle.')


def compose_cover(artwork: Image.Image, title: str, subtitle: str = '') -> Image.Image:
    if artwork.width < WIDTH or artwork.height < HEIGHT:
        raise ValueError(f'Artwork must be at least {WIDTH}x{HEIGHT} pixels.')
    image = Image.new('RGBA', (WIDTH, HEIGHT), (8, 12, 24, 255))
    image.alpha_composite(
        ImageOps.fit(artwork.convert('RGBA'), (WIDTH, HEIGHT), centering=(0.5, 0.5))
    )
    shade = Image.new('RGBA', image.size)
    shade_draw = ImageDraw.Draw(shade)
    for x in range(WIDTH):
        opacity = round(235 * max(0.0, min(1.0, (740 - x) / 300)))
        shade_draw.line((x, 0, x, HEIGHT), fill=(5, 9, 20, opacity))
    image.alpha_composite(shade)
    draw = ImageDraw.Draw(image)
    subtitle_font, subtitle_lines, subtitle_step = fit_text(draw, subtitle, 440, 72, 22)
    subtitle_height = len(subtitle_lines) * subtitle_step if subtitle else 0
    gap = 16 if subtitle_height else 0
    title_font, title_lines, title_step = fit_text(
        draw, title, 440, 332 - subtitle_height - gap, 52,
    )
    y = (HEIGHT - len(title_lines) * title_step - gap - subtitle_height) // 2
    for line in title_lines:
        draw.text((40, y), line, font=title_font, fill=(255, 255, 255))
        y += title_step
    y += gap
    if subtitle:
        for line in subtitle_lines:
            draw.text((40, y), line, font=subtitle_font, fill=(211, 226, 240))
            y += subtitle_step
    return image.convert('RGB')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    plan = commands.add_parser('brief', help='Write a randomised, topic-specific art brief; no image is generated.')
    plan.add_argument('--title', required=True)
    plan.add_argument('--topic', required=True, help='Public topic or visual metaphor, not private article text.')
    plan.add_argument('--subtitle', default='')
    plan.add_argument('--output', required=True, type=Path, help='Final PNG cover path.')
    plan.add_argument('--seed', type=int, help='Repeat the art direction and palette, not the model image pixels.')
    plan.add_argument('--art-direction', choices=tuple(ART_DIRECTIONS), help='Override the random art direction.')
    plan.add_argument(
        '--github-theme', choices=tuple(GITHUB_THEMES),
        help='Optional GitHub-inspired isometric key art with this accent theme (no logos or mascots).',
    )
    render = commands.add_parser('render', help='Make one Cloudflare Workers AI request and compose a cover.')
    render.add_argument('--brief', required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.command == 'brief':
            path = args.output.with_name(f'{args.output.stem}-cover.json')
            save_brief(path, create_brief(
                args.title, args.topic, args.subtitle, args.output.name, args.seed,
                args.github_theme, args.art_direction,
            ))
            print(f'Art brief saved: {path}. No image generated; existing cover unchanged.')
        else:
            brief = load_brief(args.brief)
            load_credentials_from_env_file()
            artwork = generate_artwork_cloudflare(brief.prompt)
            cover = compose_cover(artwork, brief.title, brief.subtitle)
            output = args.brief.parent / brief.output
            artwork.save(output.with_name(f'{output.stem}-art.png'), 'PNG')
            cover.save(output, 'PNG')
            save_brief(args.brief, replace(
                brief, source='cloudflare-workers-ai', model=CLOUDFLARE_DEFAULT_MODEL,
            ))
            print(f'Cover saved: {output} ({WIDTH}x{HEIGHT}); source=cloudflare-workers-ai. Review before publication.')
    except (OSError, ValueError, TypeError, RuntimeError) as error:
        parser.exit(1, f'Cover creation failed: {error}\n')


if __name__ == '__main__':
    main()
