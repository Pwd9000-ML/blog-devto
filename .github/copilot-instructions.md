## GitHub Copilot Project Instructions (blog-devto)

@azure Rule - Use Azure Best Practices: When generating code for Azure, running terminal commands for Azure, or performing operations related to Azure, invoke the Azure best‑practices tool before making changes.

### Repository Purpose
Static source-of-truth for dev.to articles under `posts/` (grouped by year). Each folder may contain an `assets/` subfolder for images and optional `code/` samples embedded into articles via `embedme`.

### Authoring a New Post
1. Create: `posts/<YEAR>/<Slug-Title>/<Slug-Title>.md` (match folder & filename).
2. Add front matter between leading and trailing `---` including (in order): `title`, `published` (false until ready), `description`, `tags` (single quoted, comma separated, lower-case where possible), `cover_image` (raw GitHub URL), `canonical_url` (null if none), `id` (omit/null for new), `date` (ISO 8601 if scheduling), `series` (optional).
3. Use British English spelling (standardise, customisation, behaviour, organisation, optimise, etc.).
4. Defer `id` until after the article exists on dev.to (see README “How to find the ID”).
5. Reference images via canonical raw URL under the post's `assets/` directory.

### Required Footer Pattern
Add at end (before EOF):
```
### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [X/Twitter](https://x.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}
```
Older posts may also embed a Buy Me A Coffee button; keep if present, do not add by default.

### Conventions & Lint Notes
* Avoid trailing punctuation in headings (MD026) – no colon at end.
* Preferred unordered list marker: asterisk `*` (MD004); don't churn legacy dashes.
* Code fences: specify language (`bash`, `powershell`, `terraform`, `json`, `yaml`, `markdown`).
* Keep `### _Author_` even though MD049 flags underscore emphasis; this is intentional.
* Tag formatting: lower-case concise topics (`terraform, azure, iac, devops`).

### Embedding Code Samples
Place files under `posts/<YEAR>/<Slug>/code/`. Use regular fenced blocks referencing those files so `embedme` can inject content. After editing samples run:
* `yarn embedme:write` – refresh embedded snippets
* `yarn prettier:write` – format
Validate with `yarn embedme:check` and `yarn prettier:check` before commit.

### Updating Existing Articles
* Preserve existing `id` & `date`; never reuse an `id`.
* Add new sections without renaming established headings to preserve external anchors.

### Safety & Content
* Never commit secrets; use obvious placeholders (`<SUBSCRIPTION_ID>`, `<RESOURCE_GROUP>`).
* Image links must target `main` branch raw URL for dev.to rendering.

### Quick QA Checklist Before Commit
1. Front matter complete & valid.
2. British English spelling audit (search for `-ize`, `behavior`, etc.).
3. Footer present.
4. `yarn embedme:check` & `yarn prettier:check` pass.
5. No large (>1MB) unoptimised images.

Feedback welcome—extend these instructions only with patterns demonstrably used in the repo.