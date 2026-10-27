#!/usr/bin/env python3
"""Plan topic-specific cover art, then render it with generated or imported artwork."""

from __future__ import annotations

import argparse
import base64
import io
import json
import os
import random
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from PIL import Image, ImageDraw, ImageFont, ImageOps

from cover_creative import HEIGHT, WIDTH, find_font, measure, wrap_text

ART_DIRECTIONS = {
    'cinematic-diorama': 'A tactile miniature scene with dramatic studio lighting and depth.',
    'editorial-collage': 'An original layered editorial collage with cut-paper and material textures.',
    'isometric-world': 'A detailed isometric world with a few meaningful connected objects.',
    'paper-sculpture': 'An intricate sculpted-paper scene with dimensional shadows and bold shapes.',
    'macro-materials': 'A striking close-up of physical objects in glass, ceramic, and brushed metal.',
    'technical-illustration': 'A sophisticated conceptual illustration with precise shapes and rich texture.',
}
PALETTES = (
    'deep navy, electric cyan, and restrained coral accents',
    'charcoal, warm amber, and violet highlights',
    'midnight indigo, mint, and soft rose',
    'cobalt, burnt orange, and warm ivory',
    'graphite, lime, and muted teal',
)


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


def create_brief(
    title: str,
    topic: str,
    subtitle: str,
    output: str,
    seed: int | None = None,
    previous_direction: str | None = None,
) -> ArtBrief:
    if not title.strip() or not topic.strip():
        raise ValueError('The title and public visual concept must not be empty.')
    if Path(output).name != output or '\\' in output or Path(output).suffix.lower() != '.png':
        raise ValueError('The output filename must be a PNG filename without directories.')
    actual_seed = random.SystemRandom().randrange(2**63) if seed is None else seed
    rnd = random.Random(actual_seed)
    choices = [
        direction for direction in ART_DIRECTIONS
        if seed is not None or direction != previous_direction
    ]
    direction = rnd.choice(choices)
    palette = rnd.choice(PALETTES)
    prompt = (
        f'Create original editorial artwork for this technical article: {title.strip()}. '
        f'Public visual concept: {topic.strip()}. '
        'Interpret that concept with one concrete, topic-relevant visual metaphor. '
        f'Art direction: {ART_DIRECTIONS[direction]} Palette: {palette}. '
        'Make an actual illustration, not a title slide or a generic AI brain or robot. '
        'Use a wide horizontal composition. Put the main subject on the right half; '
        'leave the left half dark, quiet, and uncluttered for a separately added headline. '
        'Keep all important objects in the middle 55 percent of the image height so '
        'the artwork can be centre-cropped to a 1000 by 420 pixel banner. '
        'No words, letters, code, logos, watermarks, or fabricated user-interface screenshots. '
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
    if (
        Path(brief.output).name != brief.output
        or '\\' in brief.output
        or Path(brief.output).suffix.lower() != '.png'
    ):
        raise ValueError('The brief output must be a PNG filename without directories.')
    return brief


def save_brief(path: Path, brief: ArtBrief) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(brief), indent=2) + '\n', encoding='utf-8')


def generate_artwork(prompt: str, model: str) -> Image.Image:
    key = os.environ.get('OPENAI_API_KEY', '').strip()
    if not key:
        raise ValueError('OPENAI_API_KEY is not set. No image request was made.')
    if not model.strip():
        raise ValueError('Choose an image model available to your API account.')
    request = Request(
        'https://api.openai.com/v1/images/generations',
        data=json.dumps({'model': model, 'prompt': prompt, 'n': 1}).encode('utf-8'),
        headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'},
        method='POST',
    )
    try:
        with urlopen(request, timeout=180) as response:
            data = json.load(response)
    except HTTPError as error:
        raise RuntimeError(
            f'Image generation failed (HTTP {error.code}). '
            'Check model access, account verification, and API billing. No automatic retry.'
        ) from error
    except URLError as error:
        raise RuntimeError('Image generation could not reach the API. No automatic retry.') from error
    entries = data.get('data') if isinstance(data, dict) else None
    if (
        not isinstance(entries, list) or len(entries) != 1
        or not isinstance(entries[0], dict)
        or not isinstance(entries[0].get('b64_json'), str)
    ):
        raise ValueError('Image API response did not contain exactly one base64 image.')
    image_bytes = base64.b64decode(entries[0]['b64_json'], validate=True)
    with Image.open(io.BytesIO(image_bytes)) as image:
        return ImageOps.exif_transpose(image).convert('RGBA')


def fit_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    width: int,
    height: int,
    maximum_size: int,
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
    plan = commands.add_parser('brief', help='Write a random art brief; do not generate an image.')
    plan.add_argument('--title', required=True)
    plan.add_argument('--topic', required=True, help='Public topic or visual metaphor, not private article text.')
    plan.add_argument('--subtitle', default='')
    plan.add_argument('--output', required=True, type=Path, help='Final PNG cover path.')
    plan.add_argument('--seed', type=int, help='Repeat the art direction, not the model image pixels.')
    render = commands.add_parser('render', help='Render one saved brief using AI or imported artwork.')
    render.add_argument('--brief', required=True, type=Path)
    source = render.add_mutually_exclusive_group(required=True)
    source.add_argument('--model', help='Explicitly make one paid OpenAI Images API request.')
    source.add_argument('--background', type=Path, help='Import artwork instead; no API call.')
    args = parser.parse_args()
    try:
        if args.command == 'brief':
            path = args.output.with_name(f'{args.output.stem}-cover.json')
            previous = load_brief(path).art_direction if path.exists() and args.seed is None else None
            brief = create_brief(
                args.title, args.topic, args.subtitle, args.output.name, args.seed, previous,
            )
            save_brief(path, brief)
            print(f'Art brief saved: {path}. No image generated; existing cover unchanged.')
        else:
            brief = load_brief(args.brief)
            if args.background is not None:
                with Image.open(args.background) as imported:
                    artwork = ImageOps.exif_transpose(imported).convert('RGBA')
                brief = replace(brief, source='imported', model=None)
            else:
                artwork = generate_artwork(brief.prompt, args.model)
                brief = replace(brief, source='openai', model=args.model)
            cover = compose_cover(artwork, brief.title, brief.subtitle)
            output = args.brief.parent / brief.output
            artwork.save(output.with_name(f'{output.stem}-art.png'), 'PNG')
            cover.save(output, 'PNG')
            save_brief(args.brief, brief)
            print(f'Cover saved: {output} ({WIDTH}x{HEIGHT}); source={brief.source}. Review before publication.')
    except (OSError, ValueError, TypeError, RuntimeError) as error:
        parser.exit(1, f'Cover creation failed: {error}\n')


if __name__ == '__main__':
    main()
