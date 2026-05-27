---
title: 'GitHub Copilot CLI Plugins and Marketplaces: Extend Your Terminal Agent'
published: true
description: 'Learn how GitHub Copilot CLI plugins and marketplaces work, how to install them, and how to build your own.'
tags: 'githubcopilot, cli, devops, tutorial'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2026/GitHub-Copilot-CLI-Plugins-Marketplace/assets/main.png'
canonical_url: null
id: 3764842
series: GitHub Copilot - CLI
---

## GitHub Copilot CLI Plugins and Marketplaces: Extend Your Terminal Agent

GitHub Copilot CLI already gives you an AI assistant in the terminal. Plugins make it more powerful by letting you install reusable agents, skills, hooks, and tool integrations as packages.

Instead of manually copying prompt files, wiring MCP servers, or sharing setup notes in a wiki, you can package those capabilities once and install them from a marketplace. In this guide, we will look at how Copilot CLI plugins work, how to find and install them, how marketplaces are structured, and how to build a small plugin of your own.

> **Quick tip:** if you ever forget a flag, run `copilot plugin --help` or `copilot plugin <subcommand> --help`. The CLI ships its own up to date reference.

### Are these the same as GitHub Copilot Extensions?

This is a common point of confusion, so let us clear it up first. GitHub Copilot Extensions and Copilot CLI plugins are different systems.

|  | GitHub Copilot Extensions | Copilot CLI plugins |
| --- | --- | --- |
| Where they run | VS Code, Visual Studio, JetBrains, github.com | Copilot CLI in your terminal |
| Distribution | [GitHub Marketplace](https://github.com/marketplace?type=apps&copilot_app=true) (GitHub Apps) | Git-repository based plugin marketplaces |
| Install command | Install on GitHub.com, enable in the IDE | `copilot plugin install` |
| What they extend | The Copilot chat experience in IDEs | The Copilot CLI agent, its tools, agents, skills, and MCP servers |

Both extend Copilot, but they are not interchangeable. This post is about the CLI flavour.

---

## What Is a Copilot CLI Plugin?

A Copilot CLI plugin is an installable package that extends GitHub Copilot CLI with reusable customisations. According to the official [about CLI plugins](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-cli-plugins) page, plugins can bundle:

| Component | Typical location | What it adds |
| --- | --- | --- |
| Custom agents | `agents/*.agent.md` | Specialist agent modes for focused work |
| Skills | `skills/<name>/SKILL.md` | Reusable task instructions and workflows |
| Hooks | `hooks.json` | Commands that run at lifecycle events |
| MCP servers | `.mcp.json` or `.github/mcp.json` | External tools and data sources |
| LSP servers | `lsp.json` or `.github/lsp.json` | Language server integrations |

That means a plugin is not just an MCP server. It is a distribution format. A plugin can contain only a custom agent, only a set of skills, a bundle of MCP servers, or a combination of all of these.

After installation, Copilot CLI stores plugin contents under the user's Copilot directory and loads them into future sessions. Marketplace plugins are installed under:

```text
~/.copilot/installed-plugins/<marketplace>/<plugin-name>
```

Direct installs are stored under:

```text
~/.copilot/installed-plugins/_direct/<source-id>
```

> The plugin manifest itself (`plugin.json`) can live in any of these locations inside the plugin repo, checked in this order: `.plugin/plugin.json`, `plugin.json`, `.github/plugin/plugin.json`, or `.claude-plugin/plugin.json`. The last one exists for compatibility with Claude Code plugin layouts.

### Plugins versus manual configuration

You can add custom agents, MCP servers, and skills manually without using a plugin at all. Plugins are simply a better way to distribute those things. The official docs summarise it like this:

| Feature    | Manual configuration in a repository | Plugin                   |
| ---------- | ------------------------------------ | ------------------------ |
| Scope      | Single repository                    | Any project              |
| Sharing    | Manual copy and paste                | `copilot plugin install` |
| Versioning | Git history                          | Marketplace versions     |
| Discovery  | Searching repositories               | Marketplace browsing     |

If you find yourself copying the same `agents/` folder into multiple repositories, that is a strong signal it should be a plugin.

---

## How Plugins Relate to MCP

MCP, or Model Context Protocol, is the open standard used by AI tools to connect models to external tools and data sources. GitHub documents MCP support across Copilot surfaces in [About Model Context Protocol](https://docs.github.com/en/copilot/concepts/about-mcp).

Copilot CLI can use MCP servers directly, without plugins. For example, you can add an MCP server interactively:

```bash
/mcp add
```

Or you can edit the global MCP configuration file:

```text
~/.copilot/mcp-config.json
```

A plugin can wrap that configuration and make it reusable. Instead of telling every developer to paste the same JSON into their config file, you can ship the MCP server configuration inside a plugin and let them install it with one command.

For example, a plugin might include this `.mcp.json` file:

```json
{
  "mcpServers": {
    "playwright": {
      "type": "local",
      "command": "npx",
      "args": ["@playwright/mcp@latest"],
      "env": {},
      "tools": ["*"]
    }
  }
}
```

That plugin would give Copilot CLI browser automation tools through the Playwright MCP server whenever the plugin is loaded.

---

## Finding Plugins

Copilot CLI ships with two registered marketplaces by default:

| Marketplace | Repository | Purpose |
| --- | --- | --- |
| `copilot-plugins` | [`github/copilot-plugins`](https://github.com/github/copilot-plugins) | Official GitHub Copilot plugins |
| `awesome-copilot` | [`github/awesome-copilot`](https://github.com/github/awesome-copilot) | Community collection of plugins, agents, skills, prompts, and MCP integrations |

You can list the marketplaces registered with your CLI:

```bash
copilot plugin marketplace list
```

Inside an interactive Copilot CLI session, use the slash command:

```text
/plugin marketplace list
```

To browse plugins from a marketplace:

```bash
copilot plugin marketplace browse awesome-copilot
```

Or from inside the session:

```text
/plugin marketplace browse awesome-copilot
```

The `awesome-copilot` project also has a web UI at [awesome-copilot.github.com](https://awesome-copilot.github.com), which is useful when you want to search and filter through community entries before installing anything locally.

There is also a separate [GitHub MCP Registry](https://github.com/mcp) for discovering MCP servers. That registry is useful when you want raw MCP servers, but it is not the same thing as a Copilot CLI plugin marketplace. Plugins can bundle MCP servers, but marketplaces distribute complete Copilot CLI plugin packages.

---

## Installing and Managing Plugins

The main install command is:

```bash
copilot plugin install <plugin-spec>
```

The plugin specification can point to a marketplace entry, a GitHub repository, a subdirectory, another Git URL, or a local folder.

| Install source | Example |
| --- | --- |
| Marketplace entry | `copilot plugin install database-data-management@awesome-copilot` |
| GitHub repository root | `copilot plugin install johnpapa/ai-ready` |
| GitHub repository subdirectory | `copilot plugin install dotnet/skills:plugins/dotnet` |
| Git URL | `copilot plugin install https://github.com/owner/repo.git` |
| Local path | `copilot plugin install ./my-plugin` |

You can also install from inside an interactive session:

```text
/plugin install database-data-management@awesome-copilot
```

Useful management commands include:

```bash
copilot plugin list
copilot plugin update <plugin-name>
copilot plugin update --all
copilot plugin disable <plugin-name>
copilot plugin enable <plugin-name>
copilot plugin uninstall <plugin-name>
```

Marketplace management uses a nested command group:

```bash
copilot plugin marketplace add owner/repo
copilot plugin marketplace list
copilot plugin marketplace browse <marketplace-name>
copilot plugin marketplace remove <marketplace-name>
copilot plugin marketplace remove --force <marketplace-name>
```

The `--force` option matters. If a marketplace has installed plugins, Copilot CLI will not remove it unless you explicitly force removal, which also removes the plugins installed from that marketplace.

---

## Good Plugins to Try

Here are a few useful examples from the official and community marketplaces. Always inspect a plugin before installing it, especially if it defines MCP servers or hooks.

| Plugin | Marketplace | What it is useful for | Install command |
| --- | --- | --- | --- |
| `advanced-security` | `copilot-plugins` | GitHub Advanced Security workflows such as secret scanning and dependency scanning | `copilot plugin install advanced-security@copilot-plugins` |
| `spark` | `copilot-plugins` | GitHub Spark integration | `copilot plugin install spark@copilot-plugins` |
| `azure` | `awesome-copilot` | Azure skills and Azure MCP server integration | `copilot plugin install azure@awesome-copilot` |
| `microsoft-docs` | `awesome-copilot` | Microsoft Learn documentation through MCP | `copilot plugin install microsoft-docs@awesome-copilot` |
| `devops-oncall` | `awesome-copilot` | Incident triage chat mode, prompts, and instructions for DevOps on-call work | `copilot plugin install devops-oncall@awesome-copilot` |
| `dotnet` | `awesome-copilot` | Everyday .NET and C# development skills | `copilot plugin install dotnet@awesome-copilot` |
| `dotnet-test` | `awesome-copilot` | .NET testing, coverage, and framework-specific test guidance | `copilot plugin install dotnet-test@awesome-copilot` |
| `chrome-devtools-plugin` | `awesome-copilot` | Chrome DevTools and browser debugging workflows | `copilot plugin install chrome-devtools-plugin@awesome-copilot` |
| `ai-ready` | `awesome-copilot` | Repository analysis and AI-readiness configuration | `copilot plugin install ai-ready@awesome-copilot` |

For DevOps engineers, the Azure, database, documentation, browser debugging, and security plugins are the most immediately practical. They extend the CLI from a general assistant into a specialist operator for the stack you actually use.

---

## Building Your Own Plugin

Let us build a small plugin that gives Copilot CLI a specialised deployment helper agent and a deployment checklist skill.

Create this folder structure:

```text
my-devops-plugin/
├── plugin.json
├── agents/
│   └── release-engineer.agent.md
└── skills/
    └── deployment-checklist/
        └── SKILL.md
```

The only required field in `plugin.json` is `name`, but real plugins should include a description, version, author, licence, keywords, and explicit component paths.

```json
{
  "name": "devops-release-helper",
  "description": "Release engineering helpers for CI/CD, deployment checks, and incident-safe rollouts.",
  "version": "1.0.0",
  "author": {
    "name": "Example Platform Team",
    "email": "platform@example.com"
  },
  "license": "MIT",
  "keywords": ["devops", "deployment", "cicd", "release"],
  "agents": "agents/",
  "skills": "skills/"
}
```

Now create the agent file:

```markdown
---
name: release-engineer
description: Helps plan, validate, and troubleshoot safe production releases.
tools: ['bash', 'view', 'rg', 'glob']
---

You are a release engineering assistant. Focus on safe deployments, rollback-readiness, observability, and clear operator hand-offs.

Before recommending a deployment, check for:

- CI status and failing tests
- Database migrations and rollback impact
- Feature flags and progressive rollout options
- Monitoring dashboards, alerts, and log queries
- Rollback commands and owner contact points
```

Then create the skill:

```markdown
---
name: deployment-checklist
description: Create a deployment readiness checklist for the current repository.
---

Review the current repository and produce a deployment readiness checklist.

Include:

1. Build and test validation
2. Infrastructure or configuration changes
3. Database migration risk
4. Secrets and environment variables
5. Monitoring and alerting checks
6. Rollback plan
7. Post-deployment verification

Flag anything that looks risky or missing.
```

Install it locally:

```bash
copilot plugin install ./my-devops-plugin
```

Check that Copilot CLI can see it:

```bash
copilot plugin list
```

Then start an interactive session and inspect loaded agents and skills:

```text
/agent
/skills list
```

If you change files inside a local plugin, reinstall it:

```bash
copilot plugin install ./my-devops-plugin
```

Plugin contents are cached at install time, so editing the source folder does not automatically update the installed copy.

---

## Creating a Plugin Marketplace

A Copilot CLI marketplace is not the same as the traditional [GitHub Marketplace](https://github.com/marketplace). It is a Git repository based registry. Any repository can become a marketplace by adding a `marketplace.json` file at:

```text
.github/plugin/marketplace.json
```

A simple marketplace might look like this:

```json
{
  "name": "platform-team-plugins",
  "owner": {
    "name": "Example Platform Team",
    "email": "platform@example.com"
  },
  "metadata": {
    "description": "Curated Copilot CLI plugins for our engineering organisation.",
    "version": "1.0.0"
  },
  "plugins": [
    {
      "name": "devops-release-helper",
      "description": "Release engineering helpers for CI/CD and safe deployments.",
      "version": "1.0.0",
      "source": "./plugins/devops-release-helper"
    }
  ]
}
```

If that file lives in `octo-org/platform-copilot-plugins`, users can register the marketplace with:

```bash
copilot plugin marketplace add octo-org/platform-copilot-plugins
```

Then they can browse it:

```bash
copilot plugin marketplace browse platform-team-plugins
```

And install from it:

```bash
copilot plugin install devops-release-helper@platform-team-plugins
```

This is where marketplaces become powerful for teams. A platform team can curate approved plugins for cloud operations, security reviews, incident response, documentation, and release engineering. Developers get a simple install command, while the organisation keeps the source in Git where it can be reviewed, versioned, and audited.

---

## Enterprise Plugin Standards

For larger organisations, GitHub documents [enterprise plugin standards](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-enterprise-plugin-standards) as a public preview feature. Enterprise administrators can publish standard marketplaces and enabled plugins through `.github/copilot/settings.json` in the enterprise `.github-private` repository.

An example configuration looks like this:

```json
{
  "extraKnownMarketplaces": {
    "our-internal-marketplace": {
      "source": {
        "source": "github",
        "repo": "acme-corp/copilot-plugins"
      }
    }
  },
  "enabledPlugins": {
    "security-scanner@our-internal-marketplace": true,
    "code-standards@our-internal-marketplace": true
  }
}
```

This gives enterprises a central way to make known marketplaces available and enable approved plugins for users.

---

## Security Considerations

Plugins can change what Copilot CLI can do, so treat them like developer tooling that runs with your local permissions.

### Inspect before installing

Before installing a plugin, inspect:

- `plugin.json`, to understand what components are included
- `.mcp.json`, to see which external tools or endpoints are configured
- `hooks.json`, to see commands that may run automatically
- Agent and skill instructions, to understand behavioural changes

The [`github/awesome-copilot`](https://github.com/github/awesome-copilot) repository also warns that community customisations come from third-party developers and should be inspected before use.

### Understand MCP policy

For Copilot Business and Enterprise, GitHub documents that MCP server use is controlled by organisation or enterprise policy and is disabled by default. If a plugin relies on MCP servers, users may need admin policy changes before it can work.

### Be careful with tool approvals

Copilot CLI has a tool approval model for actions such as shell commands and file changes. Approving a broad command for the rest of a session can be convenient, but it also increases risk. Keep approval narrow when you are testing a new plugin, and avoid running the CLI with `--allow-all-tools` while you are evaluating an untrusted plugin. Use `--allow-tool` for the specific tools you actually need.

### Prefer reviewed marketplaces

For teams, the best pattern is to create an internal marketplace. Put plugin changes through pull request review, pin versions where possible, and document what each plugin is allowed to do.

---

## Practical DevOps Use Cases

Here are a few ways I would use Copilot CLI plugins in a DevOps workflow.

| Use case | Plugin pattern |
| --- | --- |
| Cloud operations | Bundle Azure or AWS MCP servers with cloud runbook skills |
| Incident response | Ship an incident commander agent with log query and triage skills |
| Release engineering | Package deployment checklists, rollback prompts, and CI/CD helpers |
| Security review | Combine GitHub Advanced Security skills with secure coding agents |
| Documentation | Install documentation MCP plugins so Copilot can ground answers in official docs |
| Platform enablement | Publish internal standards as agents and skills through a team marketplace |

The key point is repeatability. A good plugin turns tribal knowledge into a versioned package that every engineer can install and use in the same way.

---

## Limitations and Current State

There are a few important details to keep in mind.

- The docs do not show a `copilot plugin search` command. Discovery is through marketplace browsing and web UIs such as `awesome-copilot.github.com`.
- Plugin files are cached at install time. Reinstall local plugins after editing them.
- Plugin agents and skills do not override project-level or personal customisations. Project context still wins.
- MCP servers from plugins may be affected by organisation or enterprise policy.
- Enterprise plugin standards and the GitHub MCP Registry are documented as public preview features, so behaviour may change.
- There is no separate plugin pricing model documented in the sources I reviewed. Plugins appear to be part of the Copilot CLI experience, but marketplace entries may depend on external services with their own costs.

---

## Final Thoughts

Copilot CLI plugins are a practical way to make the terminal agent fit your real workflow. They turn agents, skills, hooks, MCP servers, and language integrations into installable packages. Marketplaces then give teams and communities a way to share those packages without copy-paste setup instructions.

If you are just getting started, browse `awesome-copilot`, install one or two plugins that match your stack, and inspect how they are structured. Then build a small internal plugin for a workflow your team repeats every week. Deployment checks, incident triage, and security review are all great first candidates.

The best plugins will not replace engineering judgement. They will capture your team's judgement and make it easier to apply consistently from the terminal.

### _Author_

{% user pwd9000 %}

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [X](https://x.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-pwd9000/)

Date: 27-05-2026
