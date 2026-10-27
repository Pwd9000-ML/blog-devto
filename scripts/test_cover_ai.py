from __future__ import annotations

import base64
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

from PIL import Image

from cover_ai import (
    ART_DIRECTIONS,
    compose_cover,
    create_brief,
    generate_artwork,
    load_api_key_from_env_file,
    load_brief,
    main,
    save_brief,
)


class CoverAITests(unittest.TestCase):
    def test_env_file_loads_only_api_key_and_existing_environment_wins(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / '.env'
            env_file.write_text(
                '# comment\nOTHER_SECRET=ignored\nOPENAI_API_KEY="file-placeholder"\n', encoding='utf-8',
            )
            with patch.dict('os.environ', {}, clear=True):
                load_api_key_from_env_file(env_file)
                self.assertEqual(os.environ.get('OPENAI_API_KEY'), 'file-placeholder')
                self.assertNotIn('OTHER_SECRET', os.environ)
            with patch.dict('os.environ', {'OPENAI_API_KEY': 'process-placeholder'}, clear=True):
                load_api_key_from_env_file(env_file)
                self.assertEqual(os.environ['OPENAI_API_KEY'], 'process-placeholder')
            with patch.dict('os.environ', {}, clear=True):
                load_api_key_from_env_file(Path(directory) / 'missing.env')
                self.assertNotIn('OPENAI_API_KEY', os.environ)

    def test_seed_repeats_prompt_and_public_topic_is_present(self) -> None:
        first = create_brief('Lock What Runs', 'An immutable CI dependency chain', '', 'main.png', 42)
        second = create_brief('Lock What Runs', 'An immutable CI dependency chain', '', 'main.png', 42)
        self.assertEqual(first, second)
        self.assertIn('An immutable CI dependency chain', first.prompt)
        self.assertIn('No words', first.prompt)

    def test_random_brief_avoids_previous_direction(self) -> None:
        for previous in ART_DIRECTIONS:
            brief = create_brief('Cover', 'Public topic', '', 'main.png', previous_direction=previous)
            self.assertNotEqual(brief.art_direction, previous)

    def test_brief_round_trip_and_invalid_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'main-cover.json'
            brief = create_brief('Cover', 'Public topic', '', 'main.png', 1)
            save_brief(path, brief)
            self.assertEqual(load_brief(path), brief)
            data = json.loads(path.read_text(encoding='utf-8'))
            for output in ('../outside.png', '..\\outside.png', 'main.jpg'):
                data['output'] = output
                path.write_text(json.dumps(data), encoding='utf-8')
                with self.assertRaises(ValueError):
                    load_brief(path)

    def test_cover_is_rgb_png_at_required_dimensions(self) -> None:
        artwork = Image.new('RGBA', (1536, 1024), (30, 180, 220, 255))
        original = artwork.tobytes()
        cover = compose_cover(
            artwork, 'GitHub Actions Workflow Lockfiles: Pin What Actually Runs',
            'Review the code your pipeline runs.',
        )
        self.assertEqual(cover.size, (1000, 420))
        self.assertEqual(cover.mode, 'RGB')
        self.assertEqual(artwork.tobytes(), original)
        self.assertLess(cover.getpixel((0, 0))[1], cover.getpixel((900, 0))[1])
        encoded = io.BytesIO()
        cover.save(encoded, 'PNG')
        encoded.seek(0)
        with Image.open(encoded) as image:
            self.assertEqual(image.format, 'PNG')
            self.assertEqual(image.size, (1000, 420))

    def test_rejects_small_artwork_and_text_that_would_clip(self) -> None:
        with self.assertRaisesRegex(ValueError, 'at least'):
            compose_cover(Image.new('RGB', (100, 100)), 'Cover')
        with self.assertRaisesRegex(ValueError, 'does not fit'):
            compose_cover(Image.new('RGB', (1000, 420)), 'W' * 1000)

    def test_missing_api_key_never_makes_request(self) -> None:
        with patch.dict('os.environ', {}, clear=True), patch('cover_ai.urlopen') as request:
            with self.assertRaisesRegex(ValueError, 'OPENAI_API_KEY'):
                generate_artwork('Public prompt', 'chosen-image-model')
            request.assert_not_called()

    def test_api_contract_uses_one_request_and_decodes_image(self) -> None:
        png = io.BytesIO()
        Image.new('RGB', (1024, 1024)).save(png, 'PNG')
        response = io.BytesIO(json.dumps({
            'data': [{'b64_json': base64.b64encode(png.getvalue()).decode('ascii')}],
        }).encode('utf-8'))
        with (
            patch.dict('os.environ', {'OPENAI_API_KEY': 'unit-test-placeholder'}),
            patch('cover_ai.urlopen', return_value=response) as call,
        ):
            image = generate_artwork('Public prompt', 'chosen-image-model')
            self.assertEqual(image.size, (1024, 1024))
            call.assert_called_once()
            request = call.call_args.args[0]
            self.assertEqual(request.full_url, 'https://api.openai.com/v1/images/generations')
            self.assertEqual(request.get_header('Authorization'), 'Bearer unit-test-placeholder')
            self.assertEqual(request.get_header('Content-type'), 'application/json')
            self.assertEqual(json.loads(request.data), {
                'model': 'chosen-image-model', 'prompt': 'Public prompt', 'n': 1,
            })

    def test_api_failure_is_visible_without_retry_or_secret(self) -> None:
        error = HTTPError('https://api.openai.com/v1/images/generations', 403, 'Forbidden', {}, None)
        with (
            patch.dict('os.environ', {'OPENAI_API_KEY': 'unit-test-placeholder'}),
            patch('cover_ai.urlopen', side_effect=error) as call,
        ):
            with self.assertRaisesRegex(RuntimeError, 'HTTP 403') as caught:
                generate_artwork('Public prompt', 'chosen-image-model')
            self.assertNotIn('unit-test-placeholder', str(caught.exception))
            call.assert_called_once()

    def test_rejects_missing_image_in_api_response(self) -> None:
        with (
            patch.dict('os.environ', {'OPENAI_API_KEY': 'unit-test-placeholder'}),
            patch('cover_ai.urlopen', return_value=io.BytesIO(b'{"data": []}')),
        ):
            with self.assertRaisesRegex(ValueError, 'exactly one'):
                generate_artwork('Public prompt', 'chosen-image-model')

    def test_cli_brief_preserves_cover_then_import_renders(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'main.png'
            artwork = Path(directory) / 'input.png'
            Image.new('RGB', (1536, 1024), 'teal').save(artwork)
            output.write_bytes(b'existing cover')
            with patch('sys.argv', [
                'cover_ai.py', 'brief', '--title', 'Lock What Runs',
                '--topic', 'Immutable pipeline dependencies', '--output', str(output),
            ]):
                main()
            self.assertEqual(output.read_bytes(), b'existing cover')
            brief_path = Path(directory) / 'main-cover.json'
            first = load_brief(brief_path)
            with patch('sys.argv', [
                'cover_ai.py', 'render', '--brief', str(brief_path), '--background', str(artwork),
            ]), patch('cover_ai.urlopen') as request:
                main()
                request.assert_not_called()
            with Image.open(output) as image:
                self.assertEqual(image.size, (1000, 420))
            rendered = load_brief(brief_path)
            self.assertEqual(rendered.seed, first.seed)
            self.assertEqual(rendered.prompt, first.prompt)
            self.assertEqual(rendered.source, 'imported')
            self.assertTrue((Path(directory) / 'main-art.png').is_file())


if __name__ == '__main__':
    unittest.main()
