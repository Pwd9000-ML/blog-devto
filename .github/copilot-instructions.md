# Copilot Instructions for `blog-devto`

## Project snapshot

- This repo is a content workspace that publishes Markdown articles to DEV.to. Each article lives under `posts/<year>/<slug>/` and is the single source of truth for that post.
- Use `Blog-template/BlogTemplate.md` as the starting skeleton. Copy it into the new post folder and update the front matter (title, description, tags, cover path, ISO8601 date).
- Every post keeps media in an `assets/` subfolder. Ensure the cover image is saved as `assets/main.png` (1000×420) and referenced in front matter via the raw GitHub URL pointing to `main`.

## Writing workflow

- Draft content in Markdown. Keep `published: false` until ready to ship; DEV.to automation key off this flag and the `id` field (leave `null` for new posts).
- Follow the house style for author footer (`{% user pwd9000 %}` followed by the social links block). Reuse the block from the template.
- For long form guides, break sections with `##` headings; DEV.to will treat the first heading as the article title H1.
- Dont use emdashes instead use a full stop or a comma where appropriate instead of emdashes.
- Use British English spelling and style throughout each article.
- When referencing facts or external information, check that sources are correct and use verifiable online sources.

## Code and assets conventions

- Store runnable samples next to the article inside a `code/` folder when practical. Reference them from the Markdown with relative paths (e.g., `[link](./code/sample.ps1)`).
- When embedding generated diagrams or screenshots, place them in the post's `assets/` folder and link via the raw GitHub CDN (`https://raw.githubusercontent.com/.../assets/<file>`).
- Keep filenames dash-cased; this matches existing slugs and avoids URL encoding surprises.
- If you rename any file under an article's `assets/` folder, you must update all references in the article's Markdown:
  - Update front matter `cover_image` to the new raw GitHub URL if the cover filename changes.
  - Update any in-body image links and diagrams that reference the old filename.
  - Prefer keeping the cover named `assets/main.png` (1000×420). If you intentionally use a different filename, ensure the front matter `cover_image` matches it.
  - After changes, run `python scripts/cover_fix.py --article <post-path>` to validate size, and quickly scan the Markdown for broken image links.

## Tooling & quality gates

- Run `yarn install` once to pull `prettier` and `embedme`.
- Formatting: `yarn prettier:write` (or `yarn prettier:check` in CI) respects `.prettierrc.json` (80 char wrap, single quotes, no prose wrap). Apply before committing.
- Embedded code fences: if you add `<!-- embedme path/to/file -->` directives, sync them with `yarn embedme:write` and validate with `yarn embedme:check`.
- Linting/test automation is lightweight here; the `publish-to-devto` GitHub Action assumes posts follow the template and that assets exist.

## Tips for agents

- Prefer updating existing posts in place; multiple articles may share assets, so confirm relative links before renaming.
- When generating new cover art, include the MD2MMD logo or relevant branding and export to `main.png` at 1000×420 to keep DEV.to card previews sharp.
- When changing any asset filenames, search-and-replace references within the corresponding `*.md` file in the same folder so links and the `cover_image` remain correct.
- Review similar posts within the target year for voice, section ordering, and footer usage before drafting large changes.
