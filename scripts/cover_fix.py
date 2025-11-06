#!/usr/bin/env python3
"""Audit and optionally fix cover images so they conform to 1000x420."""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict
from urllib.parse import urlparse

try:
    from PIL import Image
except ImportError:  # pragma: no cover - runtime dependency check
    print("Pillow is required: python -m pip install pillow", file=sys.stderr)
    sys.exit(1)

try:
    RESAMPLE = Image.Resampling.LANCZOS  # type: ignore[attr-defined]
except AttributeError:  # pragma: no cover - older Pillow
    RESAMPLE = Image.LANCZOS

EXPECTED_SIZE = (1000, 420)
MISSING_PLACEHOLDER = "(cover png missing)"


def resolve_repo_root(current: Path) -> Path:
    return current.resolve().parents[1]


def resolve_article_root(article_arg: str, repo_root: Path) -> Path:
    target = Path(article_arg)
    if not target.is_absolute():
        target = (repo_root / target).resolve()
    if target.is_file():
        return target.parent
    if target.is_dir():
        return target
    raise FileNotFoundError(f"Article path not found: {article_arg}")


def find_article_markdown(article_dir: Path) -> Path | None:
    preferred = article_dir / f"{article_dir.name}.md"
    if preferred.exists():
        return preferred
    for p in sorted(article_dir.glob("*.md")):
        return p
    return None


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


def path_from_cover_url(cover_url: str, repo_root: Path) -> Path | None:
    try:
        u = urlparse(cover_url)
        if not u.scheme.startswith("http"):
            return None
        # raw.githubusercontent.com/<owner>/<repo>/<branch>/<rest>
        parts = [p for p in u.path.split("/") if p]
        if "raw.githubusercontent.com" in u.netloc and len(parts) >= 4:
            rel_parts = parts[3:]  # after branch
            rel_path = "/".join(rel_parts)
            return (repo_root / rel_path).resolve()
        # Fallback: locate /main/ segment
        if "/main/" in u.path:
            rel = u.path.split("/main/", 1)[1]
            return (repo_root / rel).resolve()
    except Exception:
        return None
    return None


def cover_priority(path: Path) -> Tuple[int, str]:
    name = path.name.lower()
    if name == "main.png":
        return (0, name)
    if name.startswith("main"):
        return (1, name)
    if "cover" in name:
        return (2, name)
    return (3, name)


def select_asset_images(assets_dir: Path, image_name: str | None) -> Tuple[List[Path], List[Path]]:
    if not assets_dir.is_dir():
        return [], []
    if image_name:
        candidate = assets_dir / image_name
        if candidate.exists():
            return [candidate], []
        return [], [candidate]

    pngs = sorted((p for p in assets_dir.iterdir() if p.suffix.lower() == ".png"), key=cover_priority)
    if pngs:
        return [pngs[0]], []
    return [], [assets_dir / MISSING_PLACEHOLDER]


def enumerate_article_assets(posts_root: Path, image_name: str | None, prefer_front_matter: bool) -> Tuple[List[Path], List[Path]]:
    images: List[Path] = []
    missing: List[Path] = []
    for assets_dir in posts_root.glob("**/assets"):
        article_dir = assets_dir.parent
        if not article_dir.is_dir():
            continue
        markdown = find_article_markdown(article_dir)
        if not markdown:
            continue
        if prefer_front_matter and image_name is None:
            meta = parse_front_matter(markdown)
            cover_url = meta.get("cover_image") if meta else None
            if cover_url:
                local = path_from_cover_url(cover_url, posts_root.parent)
                if local and local.exists():
                    images.append(local)
                    continue
            fallback = assets_dir / "main.png"
            if fallback.exists():
                images.append(fallback)
                continue
            missing.append(assets_dir / MISSING_PLACEHOLDER)
            continue

        found, not_found = select_asset_images(assets_dir, image_name)
        images.extend(found)
        missing.extend(not_found)
    return images, missing


def inspect_image(path: Path) -> Tuple[Tuple[int, int] | None, str | None]:
    try:
        with Image.open(path) as img:
            size = img.size
        return size, None
    except Exception as exc:  # pragma: no cover - report runtime issues
        return None, str(exc)


def average_colour(image: Image.Image) -> Tuple[int, int, int]:
    rgb = image.convert("RGB")
    thumb = rgb.resize((1, 1), RESAMPLE)
    return thumb.getpixel((0, 0))


def pad_to_expected(image: Image.Image) -> Image.Image:
    original_mode = image.mode
    rgb = image.convert("RGBA")
    ratio = min(EXPECTED_SIZE[0] / rgb.width, EXPECTED_SIZE[1] / rgb.height)
    new_size = (max(1, int(rgb.width * ratio)), max(1, int(rgb.height * ratio)))
    resized = rgb.resize(new_size, RESAMPLE)
    bg_colour = average_colour(rgb)
    canvas = Image.new("RGBA", EXPECTED_SIZE, bg_colour + (255,))
    offset = (
        (EXPECTED_SIZE[0] - new_size[0]) // 2,
        (EXPECTED_SIZE[1] - new_size[1]) // 2,
    )
    canvas.paste(resized, offset, resized if resized.mode == "RGBA" else None)
    return canvas.convert(original_mode) if original_mode in ("RGB", "RGBA", "P", "L") else canvas.convert("RGB")


def stretch_to_expected(image: Image.Image) -> Image.Image:
    original_mode = image.mode
    stretched = image.convert("RGBA").resize(EXPECTED_SIZE, RESAMPLE)
    return stretched.convert(original_mode) if original_mode in ("RGB", "RGBA", "P", "L") else stretched.convert("RGB")


def backup_file(path: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = path.with_suffix(path.suffix + f".bak-{timestamp}")
    shutil.copy2(path, backup_path)
    return backup_path


def fix_image(path: Path, stretch: bool) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    with Image.open(path) as img:
        original_size = img.size
        fixer = stretch_to_expected if stretch else pad_to_expected
        corrected = fixer(img)
        corrected.save(path)
    return original_size, EXPECTED_SIZE


def collect_targets(
    repo_root: Path,
    article: str | None,
    image_name: str | None,
    prefer_front_matter: bool,
) -> Tuple[List[Path], List[Path]]:
    posts_root = repo_root / "posts"
    if article:
        try:
            article_root = resolve_article_root(article, repo_root)
        except FileNotFoundError as exc:
            print(exc, file=sys.stderr)
            return [], []
        assets_dir = article_root / "assets"
        if assets_dir.is_dir():
            if prefer_front_matter and image_name is None:
                markdown = find_article_markdown(article_root)
                meta = parse_front_matter(markdown)
                cover_url = meta.get("cover_image") if meta else None
                if cover_url:
                    local = path_from_cover_url(cover_url, repo_root)
                    if local and local.exists():
                        return [local], []
                fallback = assets_dir / "main.png"
                if fallback.exists():
                    return [fallback], []
                return [], [assets_dir / MISSING_PLACEHOLDER]
            found, not_found = select_asset_images(assets_dir, image_name)
            return found, not_found
        # Treat path as a container of articles (e.g. posts/2025)
        return enumerate_article_assets(article_root, image_name, prefer_front_matter)
    return enumerate_article_assets(posts_root, image_name, prefer_front_matter)


def describe(path: Path, repo_root: Path) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Check and fix non-conforming cover images.")
    parser.add_argument("--article", help="Optional path to a specific article directory or markdown file")
    parser.add_argument("--image", help="Specific image filename to inspect (otherwise auto-detected)")
    parser.add_argument(
        "--front-matter",
        action="store_true",
        help="Only target the cover declared in article front matter; fallback to assets/main.png",
    )
    parser.add_argument("--fix", action="store_true", help="Apply padding/stretch corrections where needed")
    parser.add_argument("--stretch", action="store_true", help="Stretch images to fit instead of padding")
    parser.add_argument("--no-backup", action="store_true", help="Skip writing .bak copies before fixing")
    args = parser.parse_args()

    repo_root = resolve_repo_root(Path(__file__))
    images, missing = collect_targets(repo_root, args.article, args.image, args.front_matter)

    if not images and not missing:
        print("No images found to inspect.")
        return

    non_conformant: List[Tuple[Path, Tuple[int, int]]] = []
    errored: List[Tuple[Path, str]] = []

    for image_path in images:
        size, error = inspect_image(image_path)
        if error:
            errored.append((image_path, error))
            continue
        if size != EXPECTED_SIZE:
            non_conformant.append((image_path, size))

    target_desc = args.image if args.image else "auto-detected PNG"
    print(f"Checked {len(images)} image(s) targeting {target_desc}.")
    conforming = len(images) - len(non_conformant) - len(errored)
    print(f"✔ Conforming: {conforming}")
    print(f"▲ Needs attention: {len(non_conformant)}")
    print(f"✖ Errors: {len(errored)}")

    if missing:
        print("\nMissing image(s):")
        for candidate in missing:
            print(f"  - {describe(candidate, repo_root)} (expected but not found)")

    if non_conformant:
        print("\nNon-conforming image(s):")
        for path, size in non_conformant:
            print(f"  - {describe(path, repo_root)} -> {size[0]}x{size[1]}")

    if errored:
        print("\nErrors opening image(s):")
        for path, message in errored:
            print(f"  - {describe(path, repo_root)} :: {message}")

    if not args.fix or not non_conformant:
        if non_conformant:
            print("\nRun with --fix to correct the listed image(s).")
        return

    for path, size in non_conformant:
        if not args.no_backup and path.exists():
            backup = backup_file(path)
            print(f"Backup -> {describe(backup, repo_root)}")
        original, updated = fix_image(path, args.stretch)
        print(
            f"Fixed {describe(path, repo_root)}: {original[0]}x{original[1]} -> {updated[0]}x{updated[1]}"
        )

    print("\nAll requested fixes applied. Re-run without --fix to verify.")


if __name__ == "__main__":
    main()
