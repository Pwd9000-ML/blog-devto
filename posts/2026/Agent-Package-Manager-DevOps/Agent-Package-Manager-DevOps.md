---
title: 'Agent Package Manager (APM): A DevOps Guide to Reproducible AI Agents'
published: false
description: 'A DevOps-focused guide to Microsoft APM: install the CLI, pin agent dependencies in apm.yml, and pull plugins from awesome-copilot.'
tags: 'githubcopilot, github, devops, ai'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2026/Agent-Package-Manager-DevOps/assets/main.png'
canonical_url: null
series: GitHub Copilot - Customisation
---

## Agent Package Manager (APM): A DevOps Guide t Reproducible AI Agents

If you have been customising GitHub Copilot, Claude Code, or Cursor for your team, you have probably hit the same wall I did. You spend a weekend crafting the perfect set of instructions, prompts, skills, and chat modes, you commit them to `.github/` and `.claude/`, and then a teammate joins the project and has a totally different agent experience because their config drifted weeks ago.

There has been no `package.json` for AI agent configuration. Until now.

[**APM (Agent Package Manager)**](https://github.com/microsoft/apm) is an open-source project from Microsoft that treats agent configuration the same way npm, pip, or NuGet treat code dependencies. You declare what your project needs in an `apm.yml` file, commit a lockfile, and every developer or CI runner gets the exact same agent setup in seconds.

In this post we will look at APM from a DevOps angle, walk through a first install, and then wire it up to the [**awesome-copilot**](https://awesome-copilot.github.com/) marketplace so you can pull in battle-tested plugins, skills, and agents without writing any of your own.

![APM GitHub repository](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2026/Agent-Package-Manager-DevOps/assets/apm-repo.png)

---

## Why APM Matters for DevOps

The official tagline on the [microsoft/apm README](https://github.com/microsoft/apm) says it plainly:

> APM – Agent Package Manager. An open-source, community-driven dependency manager for AI agents. Think `package.json`, `requirements.txt`, or `Cargo.toml`, but for AI agent configuration.

From a platform engineering perspective, that unlocks a few things we normally take for granted on the code side:

- **Reproducibility.** An `apm.lock.yaml` pins every dependency to a full 40-character commit SHA, so a clone today and a clone in six months produce the same agent behaviour.
- **Portability.** The same manifest works across GitHub Copilot, Claude Code, Cursor, OpenCode, and Codex. Write once, run in every editor on the team.
- **Governance.** No central registry means there is no single point of compromise. Everything resolves from git, over SSH or HTTPS, and a built-in `apm audit` scans for hidden Unicode and prompt-injection payloads at install time.
- **CI friendly.** There is an official [`microsoft/apm-action`](https://github.com/microsoft/apm-action), a SARIF output for Code Scanning, and a bundle-and-ship flow (`apm pack` / `apm unpack`) for matrix and air-gapped builds.
- **No runtime footprint.** Per the [security docs](https://microsoft.github.io/apm/enterprise/security/), APM has no telemetry, no callbacks, and no arbitrary code execution. It is literally `git clone` plus `cp` plus a manifest.

APM is still a **working draft** (manifest schema 0.1, CLI in the 0.x range), so pin versions and expect the odd rough edge, but the shape of the tool is already very useful.

---

## Core Concepts in Plain English

APM introduces a handful of concepts. Here is what they actually mean.

| Concept | What it is | Where it lives |
| --- | --- | --- |
| `apm.yml` | Manifest that declares your project's agent dependencies. | Repo root, committed. |
| `apm.lock.yaml` | Lockfile pinning every dep to an exact commit SHA. | Repo root, committed. |
| `apm_modules/` | Where downloaded packages are cached. Think `node_modules`. | Repo root, gitignored. |
| Deployed files | Primitives copied into `.github/`, `.claude/`, `.cursor/`, etc. after install. | Committed, so Copilot on github.com also sees them. |
| Primitives | The building blocks: instructions, prompts, agents, skills, chatmodes, hooks, plugins, MCP servers. | Inside packages. |
| Marketplace | A git-hosted index (e.g. awesome-copilot) you can search and install from. | Remote. |

The important DevOps takeaway is that **`apm.yml`, `apm.lock.yaml`, and the deployed files under `.github/`, `.claude/`, and `.cursor/` all get committed**. `apm_modules/` does not. This is exactly the opposite of npm, and it is deliberate: it means Copilot on github.com and any teammate who has not run `apm install` yet still get the correct context.

---

## Installing the APM CLI

APM ships native binaries for macOS, Linux, and Windows x86_64. Pick whichever installer suits your platform.

**Linux and macOS:**

```bash
curl -sSL https://aka.ms/apm-unix | sh
```

**Windows (PowerShell):**

```powershell
irm https://aka.ms/apm-windows | iex
```

**Homebrew, Scoop, or pip (alternative paths):**

```bash
# Homebrew
brew install microsoft/apm/apm

# Scoop (Windows)
scoop bucket add apm https://github.com/microsoft/scoop-apm
scoop install apm

# pip (works but the native installer is the recommended path)
pip install apm-cli
```

Verify the install and check for updates:

```bash
apm --version
apm update --check
```

`apm update` will self-upgrade using the same native installer that put it on your machine.

![APM documentation home](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2026/Agent-Package-Manager-DevOps/assets/apm-docs-home.png)

---

## Your First `apm.yml`

Scaffold a manifest in an existing repo:

```bash
cd my-devops-project
apm init -y
```

That creates an `apm.yml` that looks roughly like this. Here is the richer version straight out of the [dependencies guide](https://microsoft.github.io/apm/guides/dependencies/), annotated so you can see what each line buys you:

```yaml
name: your-project
version: 1.0.0
dependencies:
  apm:
    # A whole Anthropic skill (folder with SKILL.md + assets)
    - anthropics/skills/skills/frontend-design

    # A plugin from the awesome-copilot marketplace
    - github/awesome-copilot/plugins/context-engineering

    # A single agent primitive file from any repo
    - github/awesome-copilot/agents/api-architect.agent.md

    # A full APM package pinned to a tag
    - microsoft/apm-sample-package#v1.0.0

    # Any git host (GitLab, Bitbucket, Azure DevOps, self-hosted)
    - https://gitlab.com/acme/coding-standards.git

    # Local path, useful for monorepos
    - ./packages/my-shared-skills

    # Object form when you need a sub-path and a ref
    - git: https://gitlab.com/acme/coding-standards.git
      path: instructions/security
      ref: v2.0

  mcp:
    # MCP server reference from the GitHub MCP Registry
    - io.github.github/github-mcp-server
```

The dependency string follows a consistent pattern: **`<host>/<owner>/<repo>[/<sub-path>][#<ref>]`**. If you omit the host, `github.com` is assumed. Ref pinning is standard git: tags (`#v1.0.0`), branches (`#main`), or raw commits (`#a1b2c3…`).

---

## How to Use APM: A 5 Minute Walkthrough

Let us take the exact example the APM maintainer shared and run it end to end.

### 1. Install a single plugin on the fly

```bash
apm install github/awesome-copilot/plugins/context-engineering
```

Three things happen:

1. APM clones the `github/awesome-copilot` repo (shallow, depth 1) into `apm_modules/`.
2. It detects that `plugins/context-engineering` is a plugin folder (has a `plugin.json`) and copies its primitives into `.github/`, `.claude/`, `.cursor/`, or wherever your target agent expects them.
3. It adds an entry to `apm.yml` under `dependencies.apm:` and records the resolved commit SHA in `apm.lock.yaml`.

### 2. Or commit a full manifest and install everything

Hand-edit `apm.yml` with the dependencies you want, then run:

```bash
apm install
```

This resolves every dep in the manifest (including transitive ones), pins each to a commit SHA, and deploys the primitives into your project.

### 3. Inspect what you pulled in

```bash
apm deps list          # flat table, with primitive counts
apm deps tree          # hierarchical view of transitive deps
apm view github/awesome-copilot/plugins/context-engineering versions   # list tags/branches
```

### 4. Keep things fresh

```bash
apm outdated           # diff lockfile vs remote refs
apm deps update        # re-resolve and bump the lockfile
apm uninstall github/awesome-copilot/plugins/context-engineering
apm prune              # remove anything no longer referenced
```

### 5. Commit the right files

```gitignore
# .gitignore
apm_modules/
```

Commit `apm.yml`, `apm.lock.yaml`, and the deployed `.github/`, `.claude/`, `.cursor/` directories. Your teammates now get the identical agent setup after `git pull && apm install`.

---

## Wiring Up the awesome-copilot Marketplace

[awesome-copilot](https://awesome-copilot.github.com/) is GitHub's community-curated library of Copilot agents, instructions, skills, prompts, chat modes, hooks, and plugins. It is pre-registered as the default marketplace in Copilot CLI and VS Code, and APM knows about it too.

![awesome-copilot home](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2026/Agent-Package-Manager-DevOps/assets/awesome-copilot-home.png)

### Register and search

```bash
apm marketplace add github/awesome-copilot
apm marketplace list
apm search "terraform@awesome-copilot"
apm marketplace browse awesome-copilot
```

### Install with the short `@awesome-copilot` suffix

```bash
apm install azure-cloud-development@awesome-copilot
apm install devops-oncall@awesome-copilot
```

This is equivalent to the long form `apm install github/awesome-copilot/plugins/azure-cloud-development`, but nicer to type and easier to share in docs.

Crucially, and this is the point the APM maintainer was making, **awesome-copilot entries do not need to ship their own `apm.yml`**. APM detects the shape of each folder (plugin, skill, hook package, single primitive file) and handles it correctly. You get to consume the full community catalogue without the authors having to adopt APM first.

![awesome-copilot plugins](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2026/Agent-Package-Manager-DevOps/assets/awesome-copilot-plugins.png)

### DevOps picks worth installing today

Here are a handful of entries I reach for on every project. Verify names against the live marketplace before pinning, since the catalogue moves fast.

| Entry | APM reference | Why DevOps engineers care |
| --- | --- | --- |
| Azure cloud development plugin | `github/awesome-copilot/plugins/azure-cloud-development` | Bicep, Terraform, serverless, cost optimisation. |
| DevOps on-call plugin | `github/awesome-copilot/plugins/devops-oncall` | Prompts and a chat mode for incident triage on Azure. |
| Azure IaC generator agent | `github/awesome-copilot/agents/azure-iac-generator.agent.md` | Single-file agent, drops in as `.agent.md`. |
| Azure Policy analyser agent | `github/awesome-copilot/agents/azure-policy-analyzer.agent.md` | Reviews policy assignments and compliance. |
| Agent governance skill | `github/awesome-copilot/skills/agent-governance` | Guardrails and review checklists for agent rollouts. |
| Agent supply chain skill | `github/awesome-copilot/skills/agent-supply-chain` | Threat modelling for agent dependencies. |
| App Insights instrumentation skill | `github/awesome-copilot/skills/appinsights-instrumentation` | Adds telemetry calls to your code. |

A realistic `apm.yml` for a DevOps repo might look like this:

```yaml
name: platform-engineering-toolkit
version: 1.0.0
dependencies:
  apm:
    - github/awesome-copilot/plugins/azure-cloud-development#main
    - github/awesome-copilot/plugins/devops-oncall
    - github/awesome-copilot/skills/agent-governance
    - github/awesome-copilot/skills/appinsights-instrumentation
    - github/awesome-copilot/agents/azure-iac-generator.agent.md
  mcp:
    - io.github.github/github-mcp-server
```

Run `apm install`, commit the result, and every engineer on the team picks up the same Azure, DevOps, and governance tooling the next time they pull.

---

## Running APM in CI

For pipeline reproducibility, use the official [`microsoft/apm-action`](https://github.com/microsoft/apm-action) (GitHub Actions) or the native installer in any other CI system.

A minimal GitHub Actions example that enforces lockfile integrity and runs the security audit:

```yaml
name: Agent Config CI
on: [push, pull_request]

jobs:
  apm:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install APM
        run: curl -sSL https://aka.ms/apm-unix | sh

      - name: Resolve dependencies
        run: apm install --dry-run

      - name: Security audit
        run: apm audit --ci -f sarif -o apm-audit.sarif

      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: apm-audit.sarif
```

A few things to call out:

- `apm install --dry-run` fails the job if the lockfile and manifest disagree, catching accidental drift in PRs.
- `apm audit` scans downloaded primitives for hidden Unicode and prompt-injection characters (the "Glassworm" class of attacks) and can emit SARIF for GitHub Code Scanning, JSON for custom pipelines, or Markdown for step summaries.
- For matrix or air-gapped builds, use `apm pack --archive` in one job to produce a tarball and `apm unpack` in downstream jobs to avoid re-cloning every dep.

---

## Publishing Your Own APM Package

There is no registry and no `apm publish`. Publishing is literally "push to a git repo". The layout the [first-package tutorial](https://microsoft.github.io/apm/getting-started/first-package/) recommends is:

```text
my-team-standards/
├── apm.yml
└── .apm/
    ├── instructions/
    ├── prompts/
    ├── skills/
    ├── agents/
    └── hooks/
```

Workflow:

```bash
apm init my-team-standards
# drop primitives under .apm/...
git init && git add . && git commit -m "Initial package"
git tag v1.0.0
git remote add origin https://github.com/my-org/my-team-standards.git
git push -u origin main --tags
```

Teammates or other repos consume it with:

```bash
apm install my-org/my-team-standards#v1.0.0
```

Tag releases with semver, keep a CHANGELOG, and treat breaking changes the way you would for any library.

---

## DevOps Best Practices and Pitfalls

A short list of things I wish I had known before I started using APM in anger.

- **Pin with tags, not `main`.** It is tempting to track a branch, but the whole point of the lockfile is that upgrades are deliberate. Use `#v1.0.0` style refs and bump with `apm deps update`.
- **Commit the deployed files.** If you do not commit `.github/`, `.claude/`, or `.cursor/`, Copilot on github.com (and first-time clones before `apm install`) will miss context.
- **Use `devDependencies` for authoring helpers.** When you are building a plugin with `apm init --plugin`, anything you `apm install --dev` is excluded from the shipped bundle.
- **Keep MCP trust explicit.** Transitive MCP servers require `--trust-transitive-mcp` to auto-register. That is a feature, not an annoyance: an `.agent.md` you installed should not be allowed to silently bring a new MCP server into your editor.
- **Treat APM deps like any other supply chain.** Review the upstream repo, pin to a commit SHA for critical deps, and run `apm audit` in CI. The [agent-supply-chain skill](https://awesome-copilot.github.com/) in awesome-copilot is a decent starting checklist.
- **Global installs have their place.** `apm install -g <pkg>` deploys to `~/.copilot/`, `~/.claude/`, and friends, which is handy for personal utilities you want everywhere, without touching per-project manifests.

---

## Conclusion

APM finally gives AI agent configuration the same treatment we have long given our code: a manifest, a lockfile, transitive resolution, a marketplace, audit tooling, and CI integration. For DevOps and platform engineering teams, that is the difference between "my Copilot is faster than yours" and "our whole team benefits from the same curated agent stack, reproducibly, every time".

Combine it with [awesome-copilot](https://awesome-copilot.github.com/) and you get an instant on-ramp: hundreds of community-maintained plugins, skills, and agents you can pull into any project with one line of YAML.

My suggested next steps:

1. Install the APM CLI and run `apm init` in one of your repos.
2. Add one plugin from awesome-copilot, for example `apm install devops-oncall@awesome-copilot`.
3. Commit `apm.yml`, `apm.lock.yaml`, and the deployed files, then wire up `microsoft/apm-action` in CI.
4. Once you are comfortable, package your own team standards under `.apm/` and share them across repos.

If you want to dig deeper, the [APM docs](https://microsoft.github.io/apm/), the [CLI reference](https://microsoft.github.io/apm/reference/cli-commands/), and the [enterprise security guide](https://microsoft.github.io/apm/enterprise/security/) are the three pages worth bookmarking.

### _Author_

{% user pwd9000 %}

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [X](https://x.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-pwd9000/)

Date: 21-04-2026
