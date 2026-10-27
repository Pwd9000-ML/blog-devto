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

### Topic-specific AI cover artwork

Use `scripts/cover_ai.py` for illustrated, topic-driven covers rather than random background patterns. The existing `scripts/cover_creative.py` remains available, with its existing behaviour unchanged.

The workflow separates an art brief, image creation, and deterministic typography:

1. An agent or author chooses a **public** visual concept from the article's topic. Do not send private drafts, repository content, credentials, or personal data.
2. `brief` randomly chooses from six art directions and five palettes. Re-running it avoids the previous direction for that output. `--seed` repeats the art direction and prompt, not the image model's pixels.
3. Inspect the saved prompt, then render it with Cloudflare Workers AI (default, free daily allocation) or OpenAI, or paste it into your preferred image generator and import the resulting art.
4. The compositor crops to exactly **1000x420**, preserves the source art separately, and draws legible text locally. It never asks an image model to spell the title.
5. Review the image at full size and as a thumbnail. Check topic relevance, cropping, misleading imagery, and legibility before publication. This review is a human or agent step, not an automatic semantic quality guarantee.

Create a brief without making an API call or changing an existing cover:

```powershell
python scripts\cover_ai.py brief --title "Lock What Runs" --topic "An immutable anchor securing a chain of CI dependencies while a loose version tag drifts away" --subtitle "GitHub Actions workflow lockfiles" --output posts\2026\github-actions-workflow-lockfiles-devops\assets\main.png
```

The brief is saved beside the cover as `main-cover.json`. For each new variation, run `brief` again; edit its `prompt` if the metaphor needs refinement.

Image generation reads credentials from environment variables or from a local, git-ignored `.env` file. Copy `.env.example` to `.env` in the repository root and fill in only the provider you use. `.gitignore` excludes `.env` and `.env.*` (except `.env.example`). The script reads only `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`, and `OPENAI_API_KEY` from this file, only when `render --provider` runs, and an existing environment variable takes precedence. Note that `.env` still syncs if the repository sits in a cloud-synced folder such as OneDrive.

#### Default: Cloudflare Workers AI (free daily allocation)

1. Create or sign in to a free [Cloudflare account](https://dash.cloudflare.com/sign-up/workers-and-pages).
2. In the dashboard, open **Workers AI**, select **Use REST API**, and choose **Create a Workers AI API Token**. Copy the token and the **Account ID** into `.env` as `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` ([REST API guide](https://developers.cloudflare.com/workers-ai/get-started/rest-api/)).
3. Render the saved brief:

```powershell
python scripts\cover_ai.py render --brief posts\2026\github-actions-workflow-lockfiles-devops\assets\main-cover.json --provider cloudflare
```

This uses `@cf/black-forest-labs/flux-1-schnell` with 8 steps (the model's maximum). For a wider, potentially more detailed image, add `--model @cf/leonardo/lucid-origin`, which requests 1344x576. According to [Workers AI pricing](https://developers.cloudflare.com/workers-ai/platform/pricing/) (checked 27 October 2026), every account gets 10,000 Neurons per day at no charge, resetting at 00:00 UTC. FLUX schnell costs 4.8 Neurons per 512x512 tile plus 9.6 per step, and Lucid Origin costs 636 Neurons per tile plus 12 per step. On the Workers Free plan, requests beyond the allocation fail rather than being billed. Review the [FLUX schnell terms](https://bfl.ai/legal/terms-of-service) and the Lucid Origin model terms before publishing.

#### Optional: OpenAI (billed)

```powershell
python scripts\cover_ai.py render --brief posts\2026\github-actions-workflow-lockfiles-devops\assets\main-cover.json --provider openai --model gpt-image-2.5-flare
```

The model name above is listed in the [current OpenAI image-generation guide](https://developers.openai.com/api/docs/guides/image-generation) (checked 27 October 2026). OpenAI API usage needs API billing credit; it is not included in a ChatGPT subscription, and organisation verification may be required.

Each `render --provider` invocation makes **exactly one request**, with no automatic retries or regeneration loop. An agent must obtain approval for any additional generation. Only the reviewed prompt goes to the provider; the script never loads the article body or repository files. Errors report the HTTP status and provider error codes only, never response bodies or credentials.

Alternatively, import artwork generated in another application:

```powershell
python scripts\cover_ai.py render --brief posts\2026\github-actions-workflow-lockfiles-devops\assets\main-cover.json --background C:\Images\lockfiles-art.png
```

Input art must be at least 1000x420. Rendering writes `main.png`, `main-art.png`, and updates the brief with the source and model. Keep these assets together for review and future recomposition. Missing credentials, invalid images, and API failures stop with an error; they never silently produce a procedural substitute. Creating a brief alone is **not** image generation.

Visual inspiration, not copied assets: the [VS Code/Copilot cover](https://dev.to/hamidrazadev/vs-code-1143-copilot-harness-default-compare-models-and-other-updates-worth-knowing-2l3j) demonstrates headline/illustration separation; the [security incident cover](https://dev.to/varshithvhegde/the-most-embarrassing-private-key-in-web-pki-history-f9b) demonstrates a story-led technical collage. Neither example's production method is assumed to be AI-generated.

Validate the new workflow without contacting an image provider:

```powershell
python -m unittest discover -s scripts -p test_cover_ai.py
```
