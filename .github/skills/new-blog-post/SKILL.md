---
name: new-blog-post
description: 'Create, edit, audit, and prepare DEV.to posts using the repository templates, cover generator, and targeted quality checks.'
---

# DEV.to Post Workflow

Use this skill for new articles, edits to existing articles, cover generation, post audits, and publication preparation.

## Choose a mode

- **Create**: start a new post from a topic-specific template.
- **Edit**: change an existing post while preserving its DEV.to identity and publication metadata.
- **Audit**: validate one post, selected posts, changed posts, or the archive informationally.

Ask only for missing information. Infer the year, slug, date, and template when the user's request makes them clear.

## Create mode

Gather or infer:

| Input | Required | Default |
| --- | --- | --- |
| Title | Yes | None |
| Slug | No | Dash-cased title |
| Description | Yes | A concise summary, 150 characters maximum |
| Tags | Yes | Up to four relevant tags |
| Format | No | `tutorial`, `announcement`, `deep-dive`, or `general` |
| Series | No | `null` |
| Cover subtitle | No | Empty |

1. Choose `Blog-template/tutorial.md` for an executable guide, `announcement.md` for a release or news post, `deep-dive.md` for architecture and analysis, or `BlogTemplate.md` for another format.
2. Create `posts/<year>/<slug>/`, copy the selected template to `<slug>.md`, and create `assets/` and `code/` only when needed.
3. Replace every front-matter placeholder. Keep `published: false`, `id: null`, and `canonical_url: null` for a new post.
4. Generate the cover:

   ```powershell
   python scripts/cover_creative.py --title "<Title>" --subtitle "<Subtitle>" --output "posts/<year>/<slug>/assets/main.png"
   ```

   Use `--style` or `--seed` when the user requests a controlled variation. The script's supported styles are authoritative.

5. Draft in British English. Use authoritative sources for factual or time-sensitive claims. Include runnable samples, expected output, and validation steps where relevant.
6. Run the targeted checks in the Validation section.

## Edit mode

- Read the existing front matter before changing it.
- Preserve `id`, `canonical_url`, `published`, `series`, and the existing publication date unless the user explicitly requests a metadata change.
- Do not rename or remove assets until all references have been searched.
- Keep the existing footer unless the user asks to update the author identity or social links.
- Run the audit against the edited post, then run Prettier and embedded-code checks when applicable.

## Audit mode

For one post:

```powershell
pwsh ./scripts/audit_posts.ps1 -Path posts/<year>/<slug>/<slug>.md -FailOnIssues
```

For changed posts in a branch:

```powershell
pwsh ./scripts/audit_posts.ps1 -ChangedOnly -BaseRef origin/main -FailOnIssues
```

For an informational archive report, omit `-FailOnIssues`. Legacy posts are not required to satisfy the current contract unless they are edited.

Report findings by metadata, assets, links, structure, footer, style, and code. Include the file path and a practical correction for each finding.

## Current post contract

- Front matter includes `title`, `published`, `description`, `tags`, `cover_image`, `canonical_url`, `id`, `series`, and `date`.
- `description` is no longer than 150 characters, tags contain no more than four values, and `date` is ISO 8601 UTC.
- New covers are `assets/main.png`, 1000x420 pixels, referenced by the repository's raw GitHub URL.
- The post filename matches its folder slug. Local image links resolve to files in the post folder.
- The post contains no template placeholders or emdashes and uses British English.
- The exact author footer contains `{% user pwd9000 %}`, GitHub, X, LinkedIn, and a `Date: DD-MM-YYYY` line.
- Include primary or authoritative sources for factual claims, especially current product behaviour, version details, pricing, and security guidance.

## Validation

Run locally:

```powershell
npx prettier --write <changed files>
npx prettier --check <changed files>
npx embedme <post.md> --verify
pwsh ./scripts/audit_posts.ps1 -Path <post.md> -FailOnIssues
```

Use `yarn embedme:write` only when `<!-- embedme ... -->` directives need synchronising. Never use the missing `cover_fix.py`; cover dimensions are checked by `audit_posts.ps1`.

## Summary

After completing work, report the post path, selected template, cover path, checks run, and any remaining issues. Remind the user that merging to `main` publishes the post through the repository workflow.
