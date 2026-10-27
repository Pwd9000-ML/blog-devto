from __future__ import annotations

import base64
import io
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from PIL import Image

from cover_ai import (
    ART_DIRECTIONS,
    CLOUDFLARE_DEFAULT_MODEL,
    PALETTES,
    compose_cover,
    create_brief,
    generate_artwork_cloudflare,
    load_brief,
    load_credentials_from_env_file,
    main,
    save_brief,
)

CF_ACCOUNT = '0123456789abcdef0123456789abcdef'
CF_ENV = {'CLOUDFLARE_ACCOUNT_ID': CF_ACCOUNT, 'CLOUDFLARE_API_TOKEN': 'test-token'}


def png_bytes(size: tuple[int, int] = (1344, 576)) -> bytes:
    buffer = io.BytesIO()
    Image.new('RGB', size, 'navy').save(buffer, 'PNG')
    return buffer.getvalue()


class APIResponse(io.BytesIO):
    headers = {'Content-Type': 'application/json'}


class BinaryImageResponse(APIResponse):
    headers = {'Content-Type': 'image/png'}


def cloudflare_response(image: bytes | None = None) -> APIResponse:
    return APIResponse(json.dumps({
        'result': {'image': base64.b64encode(png_bytes() if image is None else image).decode('ascii')},
        'success': True, 'errors': [], 'messages': [],
    }).encode('utf-8'))


class CoverAITests(unittest.TestCase):
    def test_credentials_read_only_cloudflare_and_preserve_environment(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / '.env'
            path.write_text(
                '# comment\nOTHER_SECRET=ignored\nLEGACY_KEY=ignored\n'
                f'CLOUDFLARE_ACCOUNT_ID="{CF_ACCOUNT}"\nCLOUDFLARE_API_TOKEN=\'file-token\'\n',
                encoding='utf-8-sig',
            )
            with patch.dict('os.environ', {}, clear=True):
                load_credentials_from_env_file(path)
                self.assertEqual(dict(os.environ), {
                    'CLOUDFLARE_ACCOUNT_ID': CF_ACCOUNT, 'CLOUDFLARE_API_TOKEN': 'file-token',
                })
            with patch.dict('os.environ', CF_ENV, clear=True):
                load_credentials_from_env_file(path)
                self.assertEqual(os.environ['CLOUDFLARE_API_TOKEN'], 'test-token')
            with patch.dict('os.environ', {}, clear=True):
                load_credentials_from_env_file(Path(directory) / 'missing.env')
                self.assertEqual(dict(os.environ), {})

    def test_default_model_and_general_randomised_style(self) -> None:
        self.assertEqual(CLOUDFLARE_DEFAULT_MODEL, '@cf/leonardo/lucid-origin')
        first = create_brief('Lock What Runs', 'Immutable pipeline cubes', '', 'main.png', 42)
        self.assertEqual(first, create_brief('Lock What Runs', 'Immutable pipeline cubes', '', 'main.png', 42))
        self.assertIn(first.art_direction, ART_DIRECTIONS)
        self.assertIn(first.palette, PALETTES)
        self.assertIn('Immutable pipeline cubes', first.prompt)
        self.assertIn('wordless', first.prompt)
        self.assertNotIn('Lock What Runs', first.prompt)
        directions = {create_brief('A', 'B', '', 'main.png', seed).art_direction for seed in range(60)}
        self.assertGreater(len(directions), 3)
        chosen = create_brief('A', 'B', '', 'main.png', 1, art_direction='paper-sculpture')
        self.assertEqual(chosen.art_direction, 'paper-sculpture')
        self.assertIn(ART_DIRECTIONS['paper-sculpture'], chosen.prompt)
        github = create_brief('A', 'B', '', 'main.png', 1, github_theme='core')
        self.assertEqual(github.art_direction, 'github-key-art')
        self.assertIn('contribution-graph cubes', github.prompt)

    def test_themes_and_invalid_briefs(self) -> None:
        for theme, colour in [('core', '#0FBF3E'), ('security', '#3094FF'), ('copilot', '#8534F3')]:
            with self.subTest(theme=theme):
                self.assertIn(colour, create_brief('A', 'B', '', 'main.png', github_theme=theme).palette)
        for arguments in [
            ('', 'B', '', 'main.png'), ('A', '', '', 'main.png'),
            ('A', 'B', '', '../main.png'), ('A', 'B', '', '..\\main.png'),
            ('A', 'B', '', 'main.jpg'), ('A', 'B', '', 'C:main.png'),
        ]:
            with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                create_brief(*arguments)
        with self.assertRaisesRegex(ValueError, 'Unknown GitHub theme'):
            create_brief('A', 'B', '', 'main.png', github_theme='invalid')
        with self.assertRaisesRegex(ValueError, 'Unknown art direction'):
            create_brief('A', 'B', '', 'main.png', art_direction='invalid')

    def test_saved_approved_metadata_remains_loadable(self) -> None:
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

    def test_invalid_credentials_or_prompt_never_make_request(self) -> None:
        with patch('cover_ai.urlopen') as request:
            for values, prompt in [({}, 'Public'), ({**CF_ENV, 'CLOUDFLARE_ACCOUNT_ID': '../x'}, 'Public'), (CF_ENV, '')]:
                with patch.dict('os.environ', values, clear=True), self.assertRaises(ValueError):
                    generate_artwork_cloudflare(prompt)
            request.assert_not_called()

    def test_request_contract_and_base64_image(self) -> None:
        with (
            patch.dict('os.environ', CF_ENV, clear=True),
            patch('cover_ai.urlopen', return_value=cloudflare_response()) as call,
        ):
            image = generate_artwork_cloudflare('Public prompt')
            call.assert_called_once()
            request = call.call_args.args[0]
            self.assertEqual(request.full_url,
                             f'https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}/ai/run/{CLOUDFLARE_DEFAULT_MODEL}')
            self.assertEqual(request.get_method(), 'POST')
            self.assertEqual(request.get_header('Authorization'), 'Bearer test-token')
            self.assertEqual(request.get_header('Content-type'), 'application/json')
            self.assertEqual(json.loads(request.data), {
                'prompt': 'Public prompt', 'width': 1344, 'height': 576,
            })
            self.assertEqual(call.call_args.kwargs, {'timeout': 180})
            self.assertEqual((image.size, image.mode), ((1344, 576), 'RGBA'))

    def test_binary_response(self) -> None:
        with (
            patch.dict('os.environ', CF_ENV, clear=True),
            patch('cover_ai.urlopen', return_value=BinaryImageResponse(png_bytes())),
        ):
            self.assertEqual(generate_artwork_cloudflare('Public prompt').size, (1344, 576))

    def test_provider_errors_are_visible_without_secrets_or_retry(self) -> None:
        error = HTTPError('https://api.cloudflare.com/', 429, 'Too Many', {}, io.BytesIO(
            b'{"success": false, "errors": [{"code": 3036, "message": "test-token private detail"}]}'
        ))
        with (
            patch.dict('os.environ', CF_ENV, clear=True),
            patch('cover_ai.urlopen', side_effect=error) as call,
        ):
            with self.assertRaisesRegex(RuntimeError, r'HTTP 429: 3036\)') as caught:
                generate_artwork_cloudflare('Public prompt')
            self.assertNotIn('test-token', str(caught.exception))
            self.assertNotIn(CF_ACCOUNT, str(caught.exception))
            call.assert_called_once()
            self.assertTrue(error.closed)
        with (
            patch.dict('os.environ', CF_ENV, clear=True),
            patch('cover_ai.urlopen', side_effect=URLError('private transport details')) as call,
        ):
            with self.assertRaisesRegex(RuntimeError, 'could not reach Cloudflare'):
                generate_artwork_cloudflare('Public prompt')
            call.assert_called_once()

    def test_malformed_provider_responses_fail_explicitly(self) -> None:
        bodies = [
            b'{"success": false, "result": null}',
            b'{"success": true, "result": {"image": "not-base64!"}}',
            b'not-json',
        ]
        for body in bodies:
            with (
                self.subTest(body=body),
                patch.dict('os.environ', CF_ENV, clear=True),
                patch('cover_ai.urlopen', return_value=APIResponse(body)),
                self.assertRaises(ValueError),
            ):
                generate_artwork_cloudflare('Public prompt')
        for image in [png_bytes((512, 512)), b'not an image']:
            with (
                patch.dict('os.environ', CF_ENV, clear=True),
                patch('cover_ai.urlopen', return_value=cloudflare_response(image)),
                self.assertRaises((ValueError, OSError)),
            ):
                generate_artwork_cloudflare('Public prompt')

    def test_composition_is_rgb_and_does_not_mutate_source(self) -> None:
        artwork = Image.new('RGBA', (1344, 576), (30, 180, 220, 255))
        original = artwork.tobytes()
        cover = compose_cover(artwork, 'Lock What Runs', 'GitHub Actions workflow lockfiles')
        self.assertEqual((cover.size, cover.mode), ((1000, 420), 'RGB'))
        self.assertEqual(artwork.tobytes(), original)
        self.assertLess(cover.getpixel((0, 0))[1], cover.getpixel((900, 0))[1])
        with self.assertRaisesRegex(ValueError, 'at least'):
            compose_cover(Image.new('RGB', (100, 100)), 'Cover')
        with self.assertRaisesRegex(ValueError, 'does not fit'):
            compose_cover(artwork, 'W' * 1000)

    def test_cli_brief_preserves_cover_and_render_records_cloudflare(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'main.png'
            output.write_bytes(b'existing cover')
            brief_path = Path(directory) / 'main-cover.json'
            with patch('sys.argv', [
                'cover_ai.py', 'brief', '--title', 'Lock What Runs', '--topic', 'Immutable pipeline cubes',
                '--github-theme', 'security', '--output', str(output),
            ]), patch('cover_ai.urlopen') as request:
                main()
                request.assert_not_called()
            self.assertEqual(output.read_bytes(), b'existing cover')
            with (
                patch.dict('os.environ', CF_ENV, clear=True),
                patch('cover_ai.ENV_FILE', Path(directory) / 'missing.env'),
                patch('cover_ai.urlopen', return_value=cloudflare_response()) as call,
                patch('sys.argv', ['cover_ai.py', 'render', '--brief', str(brief_path)]),
            ):
                main()
                call.assert_called_once()
            rendered = load_brief(brief_path)
            self.assertEqual(rendered.source, 'cloudflare-workers-ai')
            self.assertEqual(rendered.model, CLOUDFLARE_DEFAULT_MODEL)
            with Image.open(output) as image:
                self.assertEqual((image.size, image.mode), ((1000, 420), 'RGB'))
            self.assertTrue((Path(directory) / 'main-art.png').is_file())

    def test_failed_render_leaves_existing_assets_untouched(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'main.png'
            output.write_bytes(b'approved cover')
            brief_path = Path(directory) / 'main-cover.json'
            save_brief(brief_path, create_brief('A', 'B', '', 'main.png'))
            original_brief = brief_path.read_bytes()
            with (
                patch('cover_ai.load_credentials_from_env_file'),
                patch('cover_ai.generate_artwork_cloudflare', side_effect=RuntimeError('API failed')),
                patch('sys.argv', ['cover_ai.py', 'render', '--brief', str(brief_path)]),
                self.assertRaises(SystemExit) as caught,
            ):
                main()
            self.assertEqual(caught.exception.code, 1)
            self.assertEqual(output.read_bytes(), b'approved cover')
            self.assertEqual(brief_path.read_bytes(), original_brief)

    def test_removed_provider_and_import_options_are_rejected(self) -> None:
        for option in [('--provider', 'openai'), ('--model', 'old-model'), ('--background', 'old.png')]:
            with (
                self.subTest(option=option),
                patch('sys.argv', ['cover_ai.py', 'render', '--brief', 'unused.json', *option]),
                patch('cover_ai.urlopen') as request,
                self.assertRaises(SystemExit) as caught,
            ):
                main()
            self.assertEqual(caught.exception.code, 2)
            request.assert_not_called()

    @unittest.skipUnless(shutil.which('pwsh'), 'PowerShell is required for post audit regression tests')
    def test_audit_versioned_covers_still_checks_local_file_and_dimensions(self) -> None:
        audit = Path(__file__).resolve().parent / 'audit_posts.ps1'
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory) / 'test-post'
            assets = folder / 'assets'
            assets.mkdir(parents=True)
            post = folder / 'test-post.md'
            for suffix in ('', '?v=cloudflare-20261027', '?v=2#cover'):
                post.write_text(
                    "---\ntitle: 'Test'\npublished: false\ndescription: 'Cover regression test'\n"
                    "tags: 'devops'\n"
                    f"cover_image: 'https://raw.githubusercontent.com/example/repo/main/posts/test/assets/main.png{suffix}'\n"
                    "canonical_url: null\nid: null\nseries: null\ndate: '2026-10-27T00:00:00Z'\n---\n"
                    "Source: https://developers.cloudflare.com/\n"
                    "{% user pwd9000 %}\n"
                    ":octopus: [GitHub](https://github.com/) | :penguin: [X](https://x.com/) | "
                    ":space_invader: [LinkedIn](https://linkedin.com/)\nDate: 27-10-2026\n",
                    encoding='utf-8', newline='\n',
                )
                for size in ((1000, 420), (999, 420)):
                    (assets / 'main.png').write_bytes(png_bytes(size))
                    result = subprocess.run(
                        ['pwsh', '-NoProfile', '-File', str(audit), '-Path', str(post), '-FailOnIssues'],
                        capture_output=True, text=True, check=False,
                    )
                    with self.subTest(suffix=suffix, size=size):
                        if size == (1000, 420):
                            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                        else:
                            self.assertNotEqual(result.returncode, 0)
                            self.assertIn('999x420', result.stdout)
                (assets / 'main.png').unlink()
                result = subprocess.run(
                    ['pwsh', '-NoProfile', '-File', str(audit), '-Path', str(post), '-FailOnIssues'],
                    capture_output=True, text=True, check=False,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('cover file does not exist', result.stdout)

    @unittest.skipUnless(shutil.which('pwsh'), 'PowerShell is required for post audit regression tests')
    def test_audit_accepts_crlf_front_matter(self) -> None:
        audit = Path(__file__).resolve().parent / 'audit_posts.ps1'
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory) / 'test-post'
            assets = folder / 'assets'
            assets.mkdir(parents=True)
            post = folder / 'test-post.md'
            content = (
                "---\ntitle: 'Test'\npublished: true\ndescription: 'CRLF regression test'\n"
                "tags: 'devops'\n"
                "cover_image: 'https://raw.githubusercontent.com/example/repo/main/posts/test/assets/main.png'\n"
                "canonical_url: null\nid: 1\nseries: null\ndate: '2026-10-27T00:00:00Z'\n---\n"
                "Source: https://developers.cloudflare.com/\n"
                "{% user pwd9000 %}\n"
                ":octopus: [GitHub](https://github.com/) | :penguin: [X](https://x.com/) | "
                ":space_invader: [LinkedIn](https://linkedin.com/)\nDate: 27-10-2026\n"
            )
            post.write_bytes(content.replace('\n', '\r\n').encode('utf-8'))
            (assets / 'main.png').write_bytes(png_bytes((1000, 420)))
            result = subprocess.run(
                ['pwsh', '-NoProfile', '-File', str(audit), '-Path', str(post), '-FailOnIssues'],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
