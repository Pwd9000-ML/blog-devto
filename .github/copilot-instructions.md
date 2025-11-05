# Copilot Instructions for `blog-devto`

## Project snapshot

- This repo is a content workspace that publishes Markdown articles to DEV.to. Each article lives under `posts/<year>/<slug>/` and is the single source of truth for that post.
- Use `Blog-template/BlogTemplate.md` as the starting skeleton. Copy it into the new post folder and update the front matter (title, description, tags, cover path, ISO8601 date).
- Every post keeps media in an `assets/` subfolder. Ensure the cover image is saved as `assets/main.png` (1000×420) and referenced in front matter via the raw GitHub URL pointing to `main`.

## Writing workflow

- Draft content in Markdown. Keep `published: false` until ready to ship; DEV.to automation key off this flag and the `id` field (leave `null` for new posts).
- Follow the house style for author footer (`{% user pwd9000 %}` followed by the social links block). Reuse the block from the template.
- For long form guides, break sections with `##` headings; DEV.to will treat the first heading as the article title H1.

## Code and assets conventions

- Store runnable samples next to the article inside a `code/` folder when practical. Reference them from the Markdown with relative paths (e.g., `[link](./code/sample.ps1)`).
- When embedding generated diagrams or screenshots, place them in the post's `assets/` folder and link via the raw GitHub CDN (`https://raw.githubusercontent.com/.../assets/<file>`).
- Keep filenames dash-cased; this matches existing slugs and avoids URL encoding surprises.

## Tooling & quality gates

- Run `yarn install` once to pull `prettier` and `embedme`.
- Formatting: `yarn prettier:write` (or `yarn prettier:check` in CI) respects `.prettierrc.json` (80 char wrap, single quotes, no prose wrap). Apply before committing.
- Embedded code fences: if you add `<!-- embedme path/to/file -->` directives, sync them with `yarn embedme:write` and validate with `yarn embedme:check`.
- Linting/test automation is lightweight here; the `publish-to-devto` GitHub Action assumes posts follow the template and that assets exist.

## Tips for agents

- Prefer updating existing posts in place; multiple articles may share assets, so confirm relative links before renaming.
- When generating new cover art, include the MD2MMD logo or relevant branding and export to `main.png` at 1000×420 to keep DEV.to card previews sharp.
- Review similar posts within the target year for voice, section ordering, and footer usage before drafting large changes.
