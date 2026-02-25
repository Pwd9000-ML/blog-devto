---
name: new-blog-post
description: 'Scaffold, draft, and validate a new DEV.to blog post. Use when: creating a new article, starting a new blog post, scaffolding a post, generating a cover image, checking post quality, validating front matter, fixing post formatting, or auditing an existing post.'
---

# New Blog Post: Scaffold, Draft, and Validate

Create new DEV.to articles with correct structure, front matter, cover art, and house style. Also validates existing posts for consistency issues.

## When to Use

- Creating a brand-new blog post from scratch
- Generating a cover image for any post
- Validating an existing post for front matter, links, footer, or style issues
- Fixing inconsistencies in an existing article

## Step 1: Gather Inputs

Ask the user for the following (infer sensible defaults where possible):

| Input                  | Required | Default                       |
| ---------------------- | -------- | ----------------------------- |
| **Title**              | Yes      | —                             |
| **Slug** (folder name) | No       | Derive from title, dash-cased |
| **Description**        | Yes      | — (must be ≤150 characters)   |
| **Tags**               | Yes      | — (max 4, comma-separated)    |
| **Series**             | No       | `null`                        |
| **Year**               | No       | Current year                  |
| **Cover subtitle**     | No       | Empty                         |

If the user already provided these in their message, skip the interview and proceed.

## Step 2: Create Folder Structure

```
posts/<year>/<slug>/
├── <slug>.md
└── assets/
    └── main.png   (generated in Step 3)
```

- The Markdown filename **must match the folder slug** exactly (dash-cased).
- Create the `assets/` subfolder even if cover generation is deferred.

## Step 3: Generate Cover Image

Run the cover image generator:

```bash
python scripts/cover_creative.py --title "<Title>" --subtitle "<Subtitle>" --output "posts/<year>/<slug>/assets/main.png"
```

- Output must be `assets/main.png` at 1000×420 pixels.
- Default behaviour is weighted random style selection to keep covers varied and creative.
- Optional: set a specific style when requested with `--style mesh-gradient|blueprint|duotone-noise|sunset-waves|minimal-paper|neon-grid|aurora-mist|retro-terminal|geometric-collage`.
- Optional: set `--seed <number>` for repeatable output during refinement.
- If Python or Pillow is unavailable, create the `assets/` folder and note the cover must be added manually.

## Step 4: Populate the Markdown File

Use [Blog-template/BlogTemplate.md](../../Blog-template/BlogTemplate.md) as the skeleton. Apply these **mandatory rules**:

### Front Matter

```yaml
---
title: '<Title>'
published: false
description: '<Description, max 150 chars>'
tags: '<tag1, tag2, tag3, tag4>'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/<year>/<slug>/assets/main.png'
canonical_url: null
id: null
series: <Series or null>
date: '<ISO 8601 timestamp>'
---
```

**Rules:**

- `description` must be ≤150 characters. Count before writing. If it exceeds 150, shorten it.
- `tags` max 4 tags, comma-separated, single-quoted.
- `cover_image` must use the format `https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/...`. Never use `refs/heads/main` variant.
- `published` must be `false` for new posts.
- `id` must be `null` for new posts.
- `date` must be ISO 8601 format: `'YYYY-MM-DDTHH:MM:SSZ'`.
- All string values should be single-quoted.

### Content Style

- Use British English spelling throughout (e.g. colour, organisation, summarise, behaviour).
- Do not use emdashes (—). Use a full stop or comma instead.
- First `##` heading is the article title as rendered by DEV.to.
- Use `##` for major sections, `###` for subsections.
- Separate major sections with `---` horizontal rules only when it improves readability.
- Reference images via raw GitHub CDN: `https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/<year>/<slug>/assets/<file>`.
- Place runnable code samples in a `code/` subfolder when practical, and link with relative paths.
- When referencing facts or external information, use verifiable online sources.

### Footer (Mandatory, Exact Block)

Every post must end with this exact footer:

```markdown
### _Author_

{% user pwd9000 %}

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [X](https://x.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-pwd9000/)

Date: DD-MM-YYYY
```

- LinkedIn URL must be `https://www.linkedin.com/in/marcel-pwd9000/` (single trailing slash, no double slashes).
- Date format is `DD-MM-YYYY` (day-month-year).

## Step 5: Run Quality Checks

After creating or editing a post, validate:

### 5a. Front Matter Validation

- [ ] `description` is ≤150 characters
- [ ] `tags` has at most 4 tags
- [ ] `cover_image` uses `raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/...` (not `refs/heads/main`)
- [ ] `cover_image` points to a file that exists in `assets/`
- [ ] `date` is valid ISO 8601
- [ ] All string values are single-quoted
- [ ] `published: false` for drafts

### 5b. Footer Validation

- [ ] Footer block matches the exact template above
- [ ] LinkedIn URL is `/in/marcel-pwd9000/` (not `/in/marcel-l-61b0a96b/`, not double `//`)
- [ ] Date line is present with `DD-MM-YYYY` format

### 5c. Content Validation

- [ ] No emdashes (—) in text
- [ ] British English spelling used (check common words: colour, organisation, summarise, licence, behaviour, analyse, customise)
- [ ] All image references use valid raw GitHub CDN URLs
- [ ] No broken relative links
- [ ] Markdown filename matches folder slug (dash-cased)

### 5d. Formatting

Run Prettier to ensure consistent formatting:

```bash
yarn prettier:write
```

If the post uses `<!-- embedme -->` directives, sync them:

```bash
yarn embedme:write
```

## Step 6: Summary

After completing all steps, provide:

1. The full path to the new post
2. Any validation issues found and fixed
3. Reminder that the cover image is at `assets/main.png` (or note if generation was skipped)
4. Reminder to set `published: true` and push to `main` when ready to publish

## Audit Mode

When asked to **validate** or **audit** an existing post (rather than create a new one), skip Steps 1-4 and run Step 5 against the specified post. Report all issues found, grouped by category, with specific line numbers and suggested fixes.

For bulk auditing across multiple posts, check each post and produce a summary table:

| Post | Description Length | Cover OK | Footer OK | Style Issues |
| ---- | ------------------ | -------- | --------- | ------------ |

## Reference: Existing Series Names

Use these exact strings when assigning a series to maintain grouping on DEV.to:

- `GitHub Copilot`
- `Terraform ERRORS!`

Check existing posts in the same topic area before creating a new series name.
