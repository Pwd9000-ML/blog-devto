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
    CLOUDFLARE_DEFAULT_MODEL,
    compose_cover,
    create_brief,
    generate_artwork,
    generate_artwork_cloudflare,
    load_brief,
    load_credentials_from_env_file,
    main,
    save_brief,
)

CF_ACCOUNT = '0123456789abcdef0123456789abcdef'
CF_ENV = {'CLOUDFLARE_ACCOUNT_ID': CF_ACCOUNT, 'CLOUDFLARE_API_TOKEN': 'cf-test-token'}


def png_bytes(size: tuple[int, int]) -> bytes:
    buffer = io.BytesIO()
    Image.new('RGB', size, 'navy').save(buffer, 'PNG')
    return buffer.getvalue()


def cloudflare_json(size: tuple[int, int] = (1024, 1024)) -> io.BytesIO:
    return io.BytesIO(json.dumps({
        'result': {'image': base64.b64encode(png_bytes(size)).decode('ascii')},
        'success': True, 'errors': [], 'messages': [],
    }).encode('utf-8'))


class BinaryImageResponse(io.BytesIO):
    headers = {'Content-Type': 'image/png'}


class CoverAITests(unittest.TestCase):
    def test_env_file_loads_only_allowlisted_keys_and_existing_environment_wins(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / '.env'
            env_file.write_text(
                '# comment\nOTHER_SECRET=ignored\nOPENAI_API_KEY="file-placeholder"\n'
                f'CLOUDFLARE_ACCOUNT_ID={CF_ACCOUNT}\nCLOUDFLARE_API_TOKEN=\'file-token\'\n',
                encoding='utf-8',
            )
            with patch.dict('os.environ', {}, clear=True):
                load_credentials_from_env_file(env_file)
                self.assertEqual(os.environ.get('OPENAI_API_KEY'), 'file-placeholder')
                self.assertEqual(os.environ.get('CLOUDFLARE_ACCOUNT_ID'), CF_ACCOUNT)
                self.assertEqual(os.environ.get('CLOUDFLARE_API_TOKEN'), 'file-token')
                self.assertNotIn('OTHER_SECRET', os.environ)
            with patch.dict('os.environ', {'CLOUDFLARE_API_TOKEN': 'process-token'}, clear=True):
                load_credentials_from_env_file(env_file)
                self.assertEqual(os.environ['CLOUDFLARE_API_TOKEN'], 'process-token')
            with patch.dict('os.environ', {}, clear=True):
                load_credentials_from_env_file(Path(directory) / 'missing.env')
                self.assertNotIn('OPENAI_API_KEY', os.environ)

    def test_cloudflare_missing_or_invalid_settings_never_make_request(self) -> None:
        with patch('cover_ai.urlopen') as request:
            with patch.dict('os.environ', {}, clear=True):
                with self.assertRaisesRegex(ValueError, 'CLOUDFLARE_ACCOUNT_ID'):
                    generate_artwork_cloudflare('Public prompt')
            with patch.dict('os.environ', {**CF_ENV, 'CLOUDFLARE_ACCOUNT_ID': '../x'}, clear=True):
                with self.assertRaisesRegex(ValueError, '32-character'):
                    generate_artwork_cloudflare('Public prompt')
            with patch.dict('os.environ', CF_ENV, clear=True):
                with self.assertRaisesRegex(ValueError, 'Workers AI model'):
                    generate_artwork_cloudflare('Public prompt', '@cf/../../evil')
                with self.assertRaisesRegex(ValueError, '2048'):
                    generate_artwork_cloudflare('x' * 2049)
            request.assert_not_called()

    def test_cloudflare_contract_decodes_json_image_and_upscales_small_output(self) -> None:
        with (
            patch.dict('os.environ', CF_ENV, clear=True),
            patch('cover_ai.urlopen', return_value=cloudflare_json((512, 512))) as call,
        ):
            image = generate_artwork_cloudflare('Public prompt')
            call.assert_called_once()
            request = call.call_args.args[0]
            self.assertEqual(
                request.full_url,
                f'https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}/ai/run/{CLOUDFLARE_DEFAULT_MODEL}',
            )
            self.assertEqual(request.get_method(), 'POST')
            self.assertEqual(request.get_header('Authorization'), 'Bearer ' + 'cf-test-token')
            self.assertEqual(json.loads(request.data), {'prompt': 'Public prompt', 'steps': 8})
        self.assertGreaterEqual(image.width, 1000)
        self.assertGreaterEqual(image.height, 420)

    def test_cloudflare_lucid_origin_requests_wide_image_and_accepts_binary_response(self) -> None:
        response = BinaryImageResponse(png_bytes((1344, 576)))
        with (
            patch.dict('os.environ', CF_ENV, clear=True),
            patch('cover_ai.urlopen', return_value=response) as call,
        ):
            image = generate_artwork_cloudflare('Public prompt', '@cf/leonardo/lucid-origin')
            self.assertEqual(json.loads(call.call_args.args[0].data), {
                'prompt': 'Public prompt', 'width': 1344, 'height': 576,
            })
        self.assertEqual(image.size, (1344, 576))

    def test_cloudflare_error_reports_codes_without_secrets_or_retry(self) -> None:
        body = io.BytesIO(
            b'{"success": false, "errors": [{"code": 3036, "message": "cf-test-token detail"}]}'
        )
        error = HTTPError('https://api.cloudflare.com/', 429, 'Too Many', {}, body)
        with (
            patch.dict('os.environ', CF_ENV, clear=True),
            patch('cover_ai.urlopen', side_effect=error) as call,
        ):
            with self.assertRaisesRegex(RuntimeError, r'HTTP 429: 3036\)') as caught:
                generate_artwork_cloudflare('Public prompt')
            self.assertNotIn('cf-test-token', str(caught.exception))
            self.assertNotIn(CF_ACCOUNT, str(caught.exception))
            call.assert_called_once()
        with (
            patch.dict('os.environ', CF_ENV, clear=True),
            patch('cover_ai.urlopen', return_value=io.BytesIO(b'{"success": false, "result": null}')),
        ):
            with self.assertRaisesRegex(ValueError, 'base64 image'):
                generate_artwork_cloudflare('Public prompt')

    def test_cli_cloudflare_render_records_provider_and_model(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            brief_path = Path(directory) / 'main-cover.json'
            save_brief(brief_path, create_brief('Lock What Runs', 'Public topic', 'Sub', 'main.png', 7))
            with (
                patch.dict('os.environ', CF_ENV, clear=True),
                patch('cover_ai.ENV_FILE', Path(directory) / 'none.env'),
                patch('cover_ai.urlopen', return_value=cloudflare_json()) as call,
                patch('sys.argv', [
                    'cover_ai.py', 'render', '--brief', str(brief_path), '--provider', 'cloudflare',
                ]),
            ):
                main()
                call.assert_called_once()
            rendered = load_brief(brief_path)
            self.assertEqual(rendered.source, 'cloudflare-workers-ai')
            self.assertEqual(rendered.model, CLOUDFLARE_DEFAULT_MODEL)
            with Image.open(Path(directory) / 'main.png') as image:
                self.assertEqual((image.size, image.mode), ((1000, 420), 'RGB'))
            self.assertTrue((Path(directory) / 'main-art.png').is_file())

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

    def test_api_error_reports_only_safe_error_code(self) -> None:
        body = io.BytesIO(
            b'{"error": {"code": "insufficient_quota", "type": "insufficient_quota",'
            b' "message": "secret-ish detail sk-test"}}'
        )
        error = HTTPError('https://api.openai.com/v1/images/generations', 429, 'Too Many', {}, body)
        with (
            patch.dict('os.environ', {'OPENAI_API_KEY': 'unit-test-placeholder'}),
            patch('cover_ai.urlopen', side_effect=error),
        ):
            with self.assertRaisesRegex(RuntimeError, r'HTTP 429: insufficient_quota\)') as caught:
                generate_artwork('Public prompt', 'chosen-image-model')
            self.assertNotIn('sk-test', str(caught.exception))
            self.assertNotIn('unit-test-placeholder', str(caught.exception))

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
