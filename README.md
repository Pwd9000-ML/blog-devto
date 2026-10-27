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
3. Inspect the saved prompt, then render it with an explicitly chosen image model, or paste it into your preferred image generator and import the resulting art.
4. The compositor crops to exactly **1000x420**, preserves the source art separately, and draws legible text locally. It never asks an image model to spell the title.
5. Review the image at full size and as a thumbnail. Check topic relevance, cropping, misleading imagery, and legibility before publication. This review is a human or agent step, not an automatic semantic quality guarantee.

Create a brief without making an API call or changing an existing cover:

```powershell
python scripts\cover_ai.py brief --title "Lock What Runs" --topic "An immutable anchor securing a chain of CI dependencies while a loose version tag drifts away" --subtitle "GitHub Actions workflow lockfiles" --output posts\2026\github-actions-workflow-lockfiles-devops\assets\main.png
```

The brief is saved beside the cover as `main-cover.json`. For each new variation, run `brief` again; edit its `prompt` if the metaphor needs refinement.

For a real OpenAI image request, set `OPENAI_API_KEY` **outside this repository** using your shell or secret manager, then run:

```powershell
python scripts\cover_ai.py render --brief posts\2026\github-actions-workflow-lockfiles-devops\assets\main-cover.json --model gpt-image-2.5-flare
```

The model name above is listed in the [current OpenAI image-generation guide](https://developers.openai.com/api/docs/guides/image-generation) (checked 27 October 2026). Availability, verification requirements, and billing depend on your API account. Each `render --model` invocation makes **one potentially billable request**, with no automatic retries or regeneration loop. An agent must obtain approval for any additional generation. Only the reviewed prompt goes to the provider; the script never loads the article body or repository files.

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
