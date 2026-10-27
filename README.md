# Devto - Blog - Status

## Build Status

[![publish to Dev.to](https://github.com/Pwd9000-ML/blog-devto/actions/workflows/publish-to-devto.yml/badge.svg?branch=master)](https://github.com/Pwd9000-ML/blog-devto/actions/workflows/publish-to-devto.yml) [![Dependabot](https://badgen.net/badge/Dependabot/enabled/green?icon=dependabot)](https://dependabot.com/)

## How to

### How to find the ID of a blog post on dev.to?

Unfortunately, dev.to does not display the ID of the blog post on the page. So once it's created, you can open your browser console (Usually F12 OR 'Option + ⌘ + J' (on macOS), or 'Shift + CTRL + J' (on Windows/Linux)) and paste the following code to retrieve the blog post ID:  
`$('div[data-article-id]').getAttribute('data-article-id')`  
If anyone knows of an easier way please help by submitting a PR here. :smile:

### How to test locally with yarn?

- Install Yarn and navigate to the repo root. Run `Yarn` to download `node_modules` and dependencies described in `package.json`. This will also update / create `yarn.lock`

- `package.json` also contains some scripts that can then be run locally for `prettier` and `embedme`. Also used in the Github Action when a post is published

### AI-generated cover artwork (Cloudflare Workers AI)

All new post covers are AI-generated with `scripts/cover_ai.py` using **Cloudflare Workers AI**, model **`@cf/leonardo/lucid-origin`**. The old procedural generator and the alternative-provider/import paths have been removed.

Each cover is original, topic-specific artwork: the AI paints a concrete visual metaphor for the article on the right, with a quiet dark left side where the title and subtitle are added locally with Pillow. Every `brief` randomly picks an art direction (`cinematic-diorama`, `editorial-collage`, `isometric-world`, `paper-sculpture`, `macro-materials`, `neon-night`, `technical-illustration`) and a palette, so covers vary from post to post. Use `--art-direction` to choose one explicitly.

For GitHub-centric posts you can optionally add `--github-theme core|security|copilot` to get GitHub-inspired isometric key art (contribution-graph cubes, glass objects, GitHub Green with blue or purple accents), based on the public [GitHub illustration](https://brand.github.com/graphic-elements/illustration) and [colour](https://brand.github.com/foundations/color) guidelines. Never ask the model for logos, mascots, copied artwork, or fabricated UI. Titles are omitted from image prompts to avoid unwanted AI lettering.

#### Set up credentials

1. Sign in to [Cloudflare](https://dash.cloudflare.com/).
2. Open **Workers AI → Use REST API → Create a Workers AI API Token** and copy your token and Account ID ([official setup](https://developers.cloudflare.com/workers-ai/get-started/rest-api/)).
3. If you do not already have `.env`, copy `.env.example` to `.env` in the repository root. Add `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_API_TOKEN`. Never overwrite an existing credentials file or commit it.

The script loads only those two keys when rendering. Environment variables take precedence. `.env` and `.env.*` are git-ignored except `.env.example`. Git ignore does not prevent OneDrive syncing the file or other local tools reading it. Never paste credentials into chat or log them.

#### Create and review a brief

```powershell
python scripts\cover_ai.py brief --title "<Short headline>" --subtitle "<Subtitle>" --topic "<Public visual metaphor for the article>" --output posts\<year>\<slug>\assets\main.png
```

Example (the published lockfiles cover, using the optional GitHub theme):

```powershell
python scripts\cover_ai.py brief --title "Lock What Runs" --subtitle "GitHub Actions workflow lockfiles" --topic "A glowing isometric pipeline of glass cubes secured by translucent padlocks" --github-theme security --output posts\2026\github-actions-workflow-lockfiles-devops\assets\main.png
```

This writes `main-cover.json` beside the cover without making an API call or modifying an existing image. Supply a **public** visual metaphor, never private article text, repository code, personal data, or credentials. `--seed` repeats the art direction and palette, not the model's pixels.

#### Generate once

```powershell
python scripts\cover_ai.py render --brief posts\<year>\<slug>\assets\main-cover.json
```

The script makes exactly **one** Cloudflare request for a 1344x576 image, then crops and composes a **1000x420 RGB PNG**. It saves the source as `main-art.png`, the cover as `main.png`, and updates `main-cover.json` with the source and model. Keep all three together.

There are no automatic retries, alternative providers, or procedural fallbacks. Missing credentials, invalid images, and API failures stop with explicit errors; HTTP errors disclose status and numeric provider codes, not response messages or tokens. Ask the user before making an additional generation request.

Cloudflare provides a daily free allocation; generation is not unlimited, and paid accounts can incur charges above their allowance. Check the current [pricing](https://developers.cloudflare.com/workers-ai/platform/pricing/) and [Lucid Origin model terms](https://developers.cloudflare.com/workers-ai/models/lucid-origin/) before use. Do not promise a fixed number of free images.

#### Review, validate, and publish

Inspect the cover at full size and as a thumbnail. Check topic relevance, cropping, title legibility, and unwanted text or misleading imagery. No automatic semantic-quality guarantee is provided.

```powershell
python -m unittest discover -s scripts -p test_cover_ai.py
pwsh scripts\audit_posts.ps1 -Path posts\<year>\<slug>\<slug>.md -FailOnIssues
```

Pass the **Markdown file**, not its folder, to the audit and confirm that it scans the intended post. Tests use synthetic images and mocked API calls; they do not consume quota.

Use the raw GitHub URL for `assets/main.png` in front matter. When replacing a published cover, change the URL's version query (for example `?v=cloudflare-20261027`) so DEV.to requests the new artwork. Preserve the article ID, publication date, and other metadata. An asset-only push does not trigger the current publishing workflow: include the cover URL change in the Markdown, publish only after approval, then verify the public DEV.to article and image.

Repository agents must follow the project [new-blog-post skill](./.github/skills/new-blog-post/SKILL.md) for all future posts.
