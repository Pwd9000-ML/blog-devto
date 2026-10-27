---
name: new-blog-post
description: 'Create, edit, audit, and publish DEV.to articles in this repository. Use for posts, templates, cover images, and publication preparation. All new covers are varied, topic-driven AI artwork generated with Cloudflare Workers AI.'
---

# DEV.to repository workflow

Each `posts/<year>/<slug>/` folder is the source of truth. This project skill defines the current cover workflow; do not follow older shared skill commands for removed generators or other providers.

## Create

1. Infer the year and slug and read a similar post. Choose a template in `Blog-template/`: `tutorial.md`, `announcement.md`, `deep-dive.md`, or `BlogTemplate.md`, according to the article format.
2. Create `posts/<year>/<slug>/<slug>.md` and `assets/`; add `code/` for executable samples when appropriate.
3. Replace all template placeholders. New posts start with `published: false`, `id: null`, and `canonical_url: null` unless publication is explicitly approved.
4. Research current claims using authoritative sources before drafting. Write in British English, distinguish preview from GA, and never invent testing results.
5. Before creating the cover brief, ask the user to choose one art direction or GitHub theme unless they already specified either in the current request. Show all options from **Cover style choices** with their meanings, wait for their answer, then generate a Cloudflare cover using the procedure below.
6. Validate the post, assets, formatting, and relevant runnable samples.

## Covers: AI-generated with Cloudflare only

Use `scripts/cover_ai.py` with the fixed model `@cf/leonardo/lucid-origin`. Every cover is original AI artwork that visualises the article's topic with one concrete metaphor, with a dark, quiet left side where the title is composed locally for readability. Covers should vary between posts. Do not copy a previous cover's look.

### Cover style choices

For every new post, ask the user to pick one art direction or GitHub theme before creating the brief unless they already specified one in the current request. Do not choose randomly, infer silently, or reuse a previous choice without asking. Present all seven art directions and all three GitHub themes:

| Style | Option | Meaning |
| --- | --- | --- |
| Cinematic diorama | `--art-direction cinematic-diorama` | Miniature model-like scene with dramatic studio lighting and shallow depth of field. |
| Editorial collage | `--art-direction editorial-collage` | Layered cut-paper collage with magazine-style material textures. |
| Isometric world | `--art-direction isometric-world` | Detailed 3D isometric scene with a few meaningful, connected objects. |
| Paper sculpture | `--art-direction paper-sculpture` | Sculpted-paper scene with bold shapes and dimensional shadows. |
| Macro materials | `--art-direction macro-materials` | Close-up physical objects in glass, ceramic, and brushed metal. |
| Neon night | `--art-direction neon-night` | Moody night scene with volumetric light, glowing edges, and reflections. |
| Technical illustration | `--art-direction technical-illustration` | Polished conceptual illustration with precise shapes and rich texture. |
| GitHub core | `--github-theme core` | GitHub-inspired isometric contribution-graph cubes with green accents. |
| GitHub security | `--github-theme security` | GitHub-inspired isometric cubes with green and security-blue accents. |
| GitHub Copilot | `--github-theme copilot` | GitHub-inspired isometric cubes with green and Copilot-purple accents. |

Use exactly one selected option. GitHub themes override art directions and exclude characters or mascots.

Create a brief from a public visual metaphor that fits the article:

```powershell
python scripts\cover_ai.py brief --title "<Short headline>" --subtitle "<Subtitle>" --topic "<Public visual concept>" <selected-style-option> --output posts\<year>\<slug>\assets\main.png
```

The headline is composed locally, not sent to the model. Never request third-party logos, mascots, copied artwork, fake UI, or generated lettering.

Review `assets/main-cover.json`, then generate once:

```powershell
python scripts\cover_ai.py render --brief posts\<year>\<slug>\assets\main-cover.json
```

Credentials come from environment variables or the git-ignored root `.env`: `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_API_TOKEN`. Do not read, print, commit, or transmit credentials to chat. If missing, ask the user to configure them locally. Do not overwrite `.env` with the example file.

Each render makes one request. Cloudflare's free allocation is finite and paid accounts may incur charges. Ask for approval before any additional generation. API failure or quota exhaustion blocks generation; never substitute a procedural image, another provider, or imported artwork.

Keep all three assets: `main.png` (1000x420 RGB), `main-art.png`, and `main-cover.json`. Review full-size and thumbnail output for relevance, cropping, unwanted text, and readable typography. Do not claim a brief or mocked test is a real generated image.

## Edit and publish

- Read existing front matter; preserve `id`, `canonical_url`, `published`, `series`, publication date, and author footer unless the user approves a change.
- Only replace a cover when requested. A new published cover needs a new version query on its raw GitHub URL, for example `assets/main.png?v=cloudflare-20261027`. Keep the canonical local asset at `assets/main.png`.
- An asset-only push does not trigger the publishing workflow. Include the cover URL change in Markdown and check the active workflow before publishing.
- Pushes to `main` and `feature/**`, and manual dispatch, can publish live; PRs and `dev` checks dry-run. Do not publish unapproved drafts or assume every branch is safe.
- After approved publication, verify the public DEV.to article and cover image.

## Post contract and validation

- Required front matter: `title`, `published`, `description` (150 characters max), `tags` (four max), `cover_image`, `canonical_url`, `id`, `series`, UTC ISO `date`.
- Match the Markdown filename to the folder slug. New names are dash-cased. Relative image/code links must resolve inside the post folder.
- Cover URLs use raw GitHub `main` paths. New covers are exactly 1000x420.
- No placeholders or emdashes. Use the exact template author footer, including `{% user pwd9000 %}`, social links, and `Date: DD-MM-YYYY`.
- Include primary sources for time-sensitive claims and practical testing, prerequisites, permissions, and troubleshooting for tutorials.

```powershell
python -m unittest discover -s scripts -p test_cover_ai.py
npx prettier --write <changed-markdown-and-json-files>
npx prettier --check <changed-markdown-and-json-files>
pwsh scripts\audit_posts.ps1 -Path posts\<year>\<slug>\<slug>.md -FailOnIssues
```

Pass the actual Markdown file, not its folder, and confirm the audit scans the post. Run `npx embedme <post.md> --verify` only if embedded-code directives exist. Do not rewrite unrelated legacy posts. Report checks, remaining blockers, and whether the changes were actually published.
