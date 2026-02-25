---
title: GitHub Copilot Instructions vs Prompts vs Custom Agents vs Skills vs X vs WHY?
published: false
description: 'Confused about GitHub Copilot customisation? Compare Instructions, Prompts, Custom Agents, Skills, MCP, and Hooks with practical use cases.'
tags: 'githubcopilot, github, devops, ai'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2026/GitHub-Copilot-Customisation-Guide/assets/main.png'
canonical_url: null
id: 3285059
series: GitHub Copilot
date: '2026-02-25T15:10:00Z'
---

## GitHub Copilot Instructions vs Prompts vs Custom Agents vs Skills vs X vs WHY?

If you have been following my recent GitHub Copilot posts, you might have noticed a pattern. We have covered instructions, prompt files, skills, MCP, coding agents, and more. Each feature is powerful on its own. The confusing part is deciding which one to use for a specific problem.

This post is your practical decision guide.

We will compare:

- **Custom Instructions**
- **Prompt Files**
- **Custom Agents**
- **Skills**
- **MCP Servers**
- **Hooks**

---

## The 60-Second Cheat Sheet

| Primitive | Typical location | Scope | Best for | When not to use |
| --- | --- | --- | --- | --- |
| **Custom Instructions** | `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, `AGENTS.md` | Always-on or pattern-based | Team standards and default behaviour | One-off tasks or named workflows |
| **Prompt Files** | `.github/prompts/*.prompt.md` | Manual, on-demand slash command | Repeatable one-shot tasks | Multi-step runbooks with assets |
| **Custom Agents** | `.github/agents/*.agent.md` | Selected agent mode/persona | Specialised role plus tool control | General coding help or tiny tweaks |
| **Skills** | `.github/skills/<name>/SKILL.md` | On-demand and auto-discovered | Reusable multi-step workflows with resources | Simple standards or hard policy enforcement |
| **MCP Servers** | `.vscode/mcp.json` or user `mcp.json` | Tool and data connectivity | Live access to external systems and APIs | Static guidance that does not need external context |
| **Hooks** | `.github/hooks/*.json` | Agent workflow lifecycle events | Hard policy gates and safety controls | Soft guidance or stylistic preferences |

If you remember one thing, remember this:

- **Instructions** for always-on guidance.
- **Prompts** for named one-off tasks.
- **Skills** for reusable workflows.
- **Custom Agents** for role and tool boundaries.
- **MCP** for external live context.
- **Hooks** for hard stop enforcement.

---

## 1) Custom Instructions: "Always apply these rules"

Use custom instructions when you want Copilot to behave consistently without repeating yourself in every chat.

### What they are

- Markdown instructions that are automatically added to context.
- Three flavours:
  - **Global**: `.github/copilot-instructions.md` applies to every chat request in the workspace.
  - **File/task-targeted**: `*.instructions.md` files with an `applyTo` glob pattern or task description match. Store them in `.github/instructions/`.
  - **Multi-agent compatible**: `AGENTS.md` in the workspace root is recognised by multiple AI agents (not only Copilot). Supports subfolder-level scoping for monorepos (experimental).
- Instructions can also be shared at GitHub **organisation level**, so every repository in the org inherits a common baseline.
- Priority order when conflicts occur: personal (user-level) > repository > organisation.

### Suitale Usage Examples

- You want all IaC suggestions to follow your team's naming and tagging conventions, e.g. every resource must include `environment` and `cost-centre` tags.
- You want consistent code style across the repo, e.g. British English in comments, four-space indentation, or a preferred import order.
- You want secure defaults baked into every suggestion, e.g. private endpoints by default, no public IPs without justification, secrets always pulled from a vault.
- You work with multiple AI agents and want a single `AGENTS.md` recognised by all of them, so rules are defined once and shared.

### Do not use when

- You only need a task once.
- You need a named slash command.
- You need a full runbook that includes extra scripts and templates.

### Quick guide: which instruction type?

| Type | When to reach for it |
| --- | --- |
| `copilot-instructions.md` | Single project, Copilot-only |
| `.instructions.md` + `applyTo` | Different rules for different file types or frameworks |
| `AGENTS.md` | Multi-agent workflows, or subfolder-level monorepo rules |
| Organisation instructions | Shared baseline across all repos in a GitHub org |

### DevOps example

"For all cloud IaC, always use least privilege, avoid hardcoded secrets, and follow approved resource naming conventions."

For a deeper walkthrough, see my earlier post: [Instructions and Prompt Files to supercharge VS Code with GitHub Copilot](https://github.com/Pwd9000-ML/blog-devto/blob/main/posts/2025/DevAIOps-Inst-GitHub/DevAIOps-Inst-GitHub.md)

Official docs: [Use custom instructions in VS Code](https://code.visualstudio.com/docs/copilot/customization/custom-instructions)

---

## 2) Prompt Files: "Run this specific play"

Prompt files are reusable slash commands for recurring tasks.

### What they are

- Markdown prompt files, usually in `.github/prompts/*.prompt.md`.
- Invoked with `/` in chat, just like slash commands.
- YAML frontmatter can define the `agent`, `tools`, `model`, and `description`.
- Support built-in variables such as `${selection}`, `${file}`, and `${input:variableName}` for dynamic context.
- Can reference a custom agent via the `agent` field, inheriting that agent's tool set.

### Suitale Usage Examples

- You want a quick `/security-review` command that scans the current file for common misconfigurations such as open ports or missing encryption.
- You want `/generate-module` to scaffold a new IaC module with consistent structure, inputs, outputs, and documentation every time.
- You want `/release-notes` that always follows a fixed changelog format, pulling context from recent commits.
- You want to override the default agent for a specific task by setting `agent: plan` in the frontmatter, e.g. a `/design-review` prompt that runs inside a planning-only agent.

### Do not use when

- You need always-on behavioural standards.
- You need automatic discovery of a rich workflow with supporting resources.
- You need deterministic enforcement logic.

### DevOps example

Create `/pipeline-hardening` that checks secrets handling, approval gates, artifact integrity, and rollback readiness. Use `${input:environment}` to let the user specify which environment to review.

Official docs: [Use prompt files in VS Code](https://code.visualstudio.com/docs/copilot/customization/prompt-files)

---

## 3) Custom Agents: "Use this specialist persona and tool set"

Custom Agents were previously known as custom chat modes.

### What they are

- Agent definition files in `.github/agents/*.agent.md`.
- Define a specialist persona, instructions, allowed tools, and optional **handoffs**.
- Designed for role-specific flows such as planning, review, or implementation.
- **Handoffs** let you chain agents into guided workflows. After one agent finishes, a handoff button appears to transition to the next agent with pre-filled context. For example: Plan > Implement > Review.
- Can run as **subagents** and can also be reused in **background agents** and **cloud agents**.
- Can be shared at **GitHub organisation level**, so every repo in the org gets the same agent definitions.

### Suitale Usage Examples

- You want a **Security Reviewer** agent that can only read code and run linters but never edit files, e.g. a pre-merge review step that flags risks without changing anything.
- You want a **Planner** agent that outputs a structured implementation plan and then hands off to an **Implementation** agent, giving the team a review checkpoint before code is written.
- You want strict tool boundaries, e.g. an **Auditor** agent with access to cloud cost APIs and read-only file tools, but no ability to execute commands or apply changes.
- You need a guided multi-step workflow where each stage has a different persona and tool set, such as Design > Build > Test.

### Do not use when

- You just need a short reusable prompt.
- You only need default team standards.
- You are trying to solve external data access without MCP.

### DevOps example

A `cost-optimiser.agent.md` that only has read-only cloud and repo tools, then **hands off** to a separate implementation agent for approved changes. The handoff button appears automatically after the cost analysis completes.

Official docs: [Custom agents in VS Code](https://code.visualstudio.com/docs/copilot/customization/custom-agents)

---

## 4) Skills: "Package a reusable runbook"

Skills are where things get interesting for SRE and DevOps teams.

### What they are

- Folder-based capability packages with a required `SKILL.md`.
- Stored in `.github/skills/<skill-name>/` (workspace) or `~/.copilot/skills/` (personal, available across all workspaces).
- Can include scripts, templates, references, and examples alongside the instructions.
- Loaded progressively: Copilot reads name and description first, loads full instructions only when relevant, and accesses bundled resources on demand.
- **Portable**: Skills follow the open [Agent Skills standard](https://agentskills.io/). The same skill works across VS Code, GitHub Copilot CLI, and the GitHub Copilot coding agent.

### Suitale Usage Examples

- You want a repeatable incident triage workflow that walks through impact assessment, timeline capture, and owner assignment using a bundled template.
- You want a postmortem assistant that generates a structured report with root-cause analysis, action items, and SLA impact, pulling from scripts and examples in the skill folder.
- You want a CI/CD troubleshooting playbook the whole team can invoke, e.g. a skill that runs diagnostic scripts against a failed pipeline and suggests fixes.
- You want **cross-tool portability** so the same workflow works in VS Code, the CLI, and the coding agent without maintaining separate definitions.

### Do not use when

- You only need a global coding rule.
- You only need a tiny slash command with no supporting resources.
- You need hard policy blocking behaviour.

### DevOps example

A `incident-triage` skill that collects service impact, timeline, likely root causes, next actions, and owner assignments using a consistent template. The same skill can be invoked from the CLI during on-call triage and from VS Code during post-incident review.

My practical Skills deep dive: [GitHub Copilot Skills: Reusable AI Workflows for DevOps and SREs](https://github.com/Pwd9000-ML/blog-devto/blob/main/posts/2026/GitHub-Copilot-Skills-DevOps/GitHub-Copilot-Skills-DevOps.md)

Official docs: [Use Agent Skills in VS Code](https://code.visualstudio.com/docs/copilot/customization/agent-skills)

---

## 5) MCP Servers: "Connect Copilot to live systems"

MCP is often the missing piece when people expect Copilot to access live external context.

### What it is

- MCP (Model Context Protocol) is an open standard for connecting AI models to external tools and services.
- Configured in `.vscode/mcp.json` (workspace) or user profile `mcp.json`. Can also be installed from the VS Code MCP server gallery.
- MCP servers can provide four categories of capability:
  - **Tools**: Actions the agent can invoke (e.g. create an issue, query a database).
  - **Resources**: Data the agent can pull into context (e.g. files, API responses, database rows).
  - **Prompts**: Pre-configured prompt templates contributed by the server.
  - **MCP Apps**: Interactive UI components such as forms and visualisations rendered directly in chat.
- Organisations can centrally manage MCP server access via GitHub policies.

### Suitale Usage Examples

- You need live GitHub data inside chat, e.g. listing open issues, checking workflow run status, or creating a PR directly from a conversation.
- You need live cloud metadata, e.g. pulling resource tags, SKU availability, or cost estimates from Azure, AWS, or GCP during an architecture review.
- You need external system context such as querying a database, pulling monitoring dashboards, or fetching ticket details from a service management tool.

### Do not use when

- Static instructions are enough.
- The task is purely local code guidance.
- You have not reviewed trust and security implications.

### DevOps example

Use GitHub MCP to create issues and inspect workflow runs, then use a cloud-compatible MCP server to pull environment metadata for triage context.

My earlier MCP setup guide: [Supercharge VSCode GitHub Copilot using Model Context Protocol (MCP) - Easy Setup Guide](https://github.com/Pwd9000-ML/blog-devto/blob/main/posts/2025/DevAIOps-MCP-GitHub/DevAIOps-MCP-GitHub.md)

Official docs: [Add and manage MCP servers in VS Code](https://code.visualstudio.com/docs/copilot/customization/mcp-servers)

---

## 6) Hooks: "Enforce policy at execution time"

If instructions are advice, hooks are enforcement.

### What they are

- Deterministic shell commands that run at key strategic points in an agent's workflow.
- Configured as JSON files in `.github/hooks/*.json` in your repository.
- Available hook types include: `sessionStart`, `sessionEnd`, `userPromptSubmitted`, `preToolUse`, `postToolUse`, `agentStop`, `subagentStop`, and `errorOccurred`.
- The `preToolUse` hook is the most powerful because it can **approve or deny** tool executions before they happen.
- Hooks receive detailed JSON input about the agent's actions, enabling context-aware automation.
- Work with both the **Copilot coding agent** on GitHub and **GitHub Copilot CLI**.

### Suitale Usage Examples

- You need a hard control, not a recommendation, e.g. blocking any file edit that adds a public IP to IaC without an approved exception.
- You must block risky operations unless a condition passes, e.g. deny `bash` commands that target production databases or delete cloud resource groups.
- You need consistent compliance checks before agent actions proceed, e.g. validating that every new service deployment includes a required cost tag.
- You want immutable audit logging of every tool invocation for regulatory or internal compliance, e.g. recording who ran what command and when.

### Do not use when

- A style guide or prompt convention is enough.
- You do not need strict allow or deny behaviour.
- You only need static behavioural guidance (use instructions instead).

### DevOps example

A `preToolUse` hook that runs a security check script before any `bash` or `edit` tool call, blocking risky infrastructure changes in production unless required checks pass.

Official docs: [About hooks for Copilot coding agent](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-hooks)

---

## So, Why This Many Primitives?

Because they solve different control layers:

- **Behaviour layer**: Instructions
- **Task invocation layer**: Prompt files
- **Persona and tool boundary layer**: Custom agents
- **Workflow packaging layer**: Skills
- **External connectivity layer**: MCP
- **Policy enforcement layer**: Hooks

This is not feature overlap. This is a composable system. You can mix and match:

- A **custom agent** can reference **instructions files** via Markdown links so you do not duplicate rules.
- A **prompt file** can set `agent:` to run inside a specific **custom agent**, inheriting its tool set.
- A **skill** can bundle scripts that a **custom agent** or **prompt file** invokes.
- An **MCP server** provides tools that any agent, prompt, or skill can call.
- **Hooks** sit underneath everything, enforcing policy regardless of which primitive triggered the action.

The key insight is that each primitive has a different **lifetime** and **trigger**. Instructions are always on. Prompts are invoked manually. Skills are discovered automatically or by slash command. Agents set a persistent persona for a session. MCP provides live external data. Hooks enforce hard gates at execution time.

---

## A Practical "When to Use What" Decision Flow

Walk through these questions in order. Pick the **first** match:

1. Do you need a rule applied to **every** chat request without anyone remembering to activate it? **Instructions**.
2. Do you need a **named, repeatable** task that people invoke on demand? **Prompt File**.
3. Do you need a **specialist persona** with a limited set of tools, or a **multi-step handoff** workflow? **Custom Agent**.
4. Do you need a **reusable multi-step runbook** with scripts, templates, or reference files bundled together? **Skill**.
5. Does the task require **live data from an external system** (GitHub API, cloud metadata, databases)? Add **MCP**.
6. Must a policy be **enforced deterministically** with no chance the model ignores it? Add a **Hook**.

Notice that 1 to 4 are "pick one" decisions, while 5 and 6 are additive layers you stack on top.

---

## What a Mature DevOps Setup Looks Like

A practical stack for a platform engineering team might be:

- **Instructions**: Workspace-level `copilot-instructions.md` for coding and security defaults. Scoped `*.instructions.md` files for IaC, pipeline YAML, and language-specific conventions.
- **Prompt files**: 5 to 10 prompt files for common operational tasks such as `/security-review`, `/release-notes`, `/changelog`, and `/generate-module`.
- **Custom agents**: 2 to 3 agents (planning, implementation, security review) connected via handoffs so the team flows from plan to code to review in one conversation.
- **Skills**: 3 to 6 skills for triage, postmortems, runbook generation, and IaC change risk analysis. These work the same in VS Code, the CLI, and the coding agent.
- **MCP servers**: GitHub MCP for issue and PR management, plus cloud-context MCP servers for pulling live environment metadata during triage.
- **Hooks**: `preToolUse` hooks to block dangerous commands and `postToolUse` hooks for audit logging in autonomous coding agent workflows.

This combination gives you speed, consistency, and safety without forcing everything into one mechanism.

---

## Final Thoughts

If you have ever asked "Should I use instructions, prompts, agents, or skills?", the answer is usually: **use the smallest primitive that solves the actual problem**.

Start simple:

- Add instructions first for always-on standards.
- Add prompt files when you catch yourself typing the same prompt repeatedly.
- Add skills when a workflow needs bundled scripts and templates.
- Add custom agents when you need role boundaries and handoff workflows.
- Add MCP when the task requires live external data.
- Add hooks where policy must be enforced, not suggested.

That is the difference between experimenting with Copilot and operationalising Copilot. Each primitive has a clear purpose, and together they form a composable customisation system.

### _Author_

{% user pwd9000 %}

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [X](https://x.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-pwd9000/)

Date: 25-02-2026
