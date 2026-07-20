# Copilot Instructions for `blog-devto`

## Repository contract

- This repository publishes Markdown articles from `posts/<year>/<slug>/` to DEV.to. Each post folder is its source of truth.
- Use the topic-specific template in `Blog-template/` and keep `published: false` while drafting. A merge to `main` is publication approval.
- New and edited posts must pass `pwsh ./scripts/audit_posts.ps1 -Path <post.md> -FailOnIssues`.
- Use `pwsh ./scripts/audit_posts.ps1` without `-FailOnIssues` for an informational legacy-archive report.

## Metadata and assets

- Front matter must include `title`, `published`, `description`, `tags`, `cover_image`, `canonical_url`, `id`, `series`, and `date`.
- Keep descriptions at 150 characters or fewer, use at most four tags, and use an ISO 8601 UTC date.
- New covers belong at `assets/main.png`, must be 1000x420, and must use the raw GitHub URL for this repository.
- When editing a published post, preserve its DEV.to `id`, `canonical_url`, and publication state unless the user explicitly requests a change.
- Use British English, avoid emdashes, remove placeholders, and verify factual or time-sensitive claims with authoritative sources.

## Content and code conventions

- Keep post and asset filenames dash-cased. Use relative links for local code and assets so the post remains portable.
- Store runnable samples in `code/` when practical. Run or review the relevant sample before publishing.
- Use the exact author footer from the selected template, including the social links and `DD-MM-YYYY` date line.
- Check local image references and generated cover dimensions with the audit script before publication.

## Tooling

- Run Prettier against the files you changed, then run `npx embedme <post.md> --verify` when the post contains embedded code.
- CI runs formatting, embedded-code, and changed-post audits. Do not make the CI job rewrite files or re-audit legacy posts.
- The `new-blog-post` skill contains the creation, editing, audit, and template-selection workflow.

## Agent behaviour

- Prefer small, focused edits and review a similar post before drafting a new one.
- Never rename or remove shared assets without searching all references first.
- When generating cover art, use `python scripts/cover_creative.py` and retain varied styles. Supported styles are defined by the script, not duplicated here.
