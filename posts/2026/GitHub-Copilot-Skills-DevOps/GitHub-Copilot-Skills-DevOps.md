---
title: 'GitHub Copilot Skills: Reusable AI Workflows for DevOps and SREs'
published: true
description: 'Learn GitHub Copilot Skills in VS Code: what they are, how to set them up, and DevOps/SRE use cases from beginner to advanced.'
tags: 'githubcopilot, github, devops, ai'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2026/GitHub-Copilot-Skills-DevOps/assets/main.png'
id: 3281741
series: GitHub Copilot
date: '2026-02-24T16:35:29Z'
---

## GitHub Copilot Skills: Reusable AI Workflows for DevOps and SREs

If you're a DevOps engineer or SRE, you probably have a handful of repeatable tasks that keep coming back: triaging failed pipelines, checking for risky Terraform changes, writing runbooks, and turning messy incident notes into something your team can actually use.

Until recently, you could get part of the way there with **custom instructions** and **prompt files**. They are both great, but they do not fully solve the same problem: packaging a repeatable, multi-step workflow with its own supporting assets.

This is where **Agent Skills** comes in. Agent Skills is an open standard (see [agentskills.io](https://agentskills.io/)) that works with GitHub Copilot in VS Code, Copilot CLI, and the Copilot coding agent.

In this post we will cover what Skills are, how to set them up in VS Code, and how to use them from beginner scenarios to more advanced DevOps and SRE use cases.

---

## What Are GitHub Copilot Skills?

A **Skill** is an on-demand, reusable workflow for Copilot. A Skill lives in a folder, has a required `SKILL.md`, and can include supporting resources such as scripts, references, and templates.

At a high level, it is designed for:

- **Repeatable workflows** you want to reuse across a team
- **Multi-step procedures** that benefit from checklists and branching logic
- **Bundled assets** such as scripts, templates, and short reference docs

The key idea is **progressive loading**:

1. Copilot first uses the Skill `name` and `description` for discovery.
2. If the request matches, it loads the Skill instructions.
3. It only loads extra resources when the Skill references them.

This makes Skills a good fit for DevOps because you can keep the default Copilot experience lean, then load a specialised runbook only when you need it.

---

## Skills vs Prompts vs Instructions vs Agents vs Hooks

Skills sit in the same overall customisation system as instructions, prompt files, custom agents, and hooks. They are not a replacement. They are a different primitive.

Here is a practical DevOps-oriented way to think about them:

| Primitive | Best for | DevOps example |
| --- | --- | --- |
| **Workspace instructions** | Always-on standards | "Tag every Azure resource with `owner` and `env`" |
| **File instructions** | Standards for certain files | Helm chart defaults for `**/values.yaml` |
| **Prompt files** | One-shot tasks | "Summarise this sprint's deployment changelog" |
| **Skills** | Reusable workflows with assets | Kubernetes rollback playbook + kubectl scripts |
| **Custom agents** | Specialised role and tool limits | Cost-optimisation advisor (read-only) |
| **Hooks** | Deterministic enforcement | Reject Terraform plans that drop deletion protection |

If you're new to Copilot customisation, my rule of thumb is:

- Use **instructions** when you want Copilot to behave consistently all the time.
- Use a **prompt file** when you want a reusable one-off command.
- Use a **Skill** when you want a repeatable workflow that feels like a runbook.

---

## Prerequisites

To use Skills effectively, you will want:

1. **VS Code** with GitHub Copilot enabled
2. A repo (or workspace) where you can commit the Skill folder so your team can share it

In VS Code chat, type `/skills` to open the **Configure Skills** menu and confirm VS Code can see your workspace Skills.

Skills can be stored in a few locations. For team usage, the simplest is the repository:

- `.github/skills/<skill-name>/SKILL.md`

VS Code also recognises `.claude/skills/` and `.agents/skills/` as project skill directories. For personal skills that follow you across workspaces, use `~/.copilot/skills/`.

If you want to share Skills across multiple repos, VS Code also supports additional search locations via the `chat.agentSkillsLocations` setting.

---

## Your First Skill (Beginner Setup)

### 1) Create the folder

Create this structure:

```text
.github/skills/incident-triage/
└── SKILL.md
```

### 2) Add SKILL.md

The front matter must match the folder name.

```markdown
---
name: incident-triage
description: 'Triage production incidents and failed deployments. Use when: a pipeline fails, an alert fires, or you need an incident update for stakeholders.'
argument-hint: 'Optional: service name, environment, and alert link'
---

# Incident Triage

## When to Use

- Pipeline failed in `prod`
- Pager/alert fired and you need a first response
- You need a status update for stakeholders

## Procedure

1. Confirm the affected service, environment, and impact
2. Collect signal: alerts, recent deploys, logs, and error budgets
3. Identify likely root cause categories (deploy, dependency, infra, config)
4. Recommend next actions: rollback, mitigation, escalation
5. Write an incident update in a consistent format

## Output Format

Return:

- Impact summary
- Timeline
- Suspected causes
- Next actions
- Owner assignments
```

That is enough to get started. The Skill is now discoverable based on the description.

---

## Using Skills in Chat

There are two ways Skills help you day-to-day:

1. **Manual invocation**: you can run the Skill as a slash command.
2. **Automatic discovery**: Copilot can decide to load the Skill when the request matches the description.

To invoke a Skill manually, type `/` in the chat input, pick the Skill, and then add any extra context. For example: `/incident-triage payments-api prod https://alert-link`.

You can control this with optional front matter:

- `user-invokable: false` hides it from `/` commands
- `disable-model-invocation: true` prevents automatic loading, but keeps slash use

This matters for teams. Some Skills are safe to auto-load. Others might be better as explicit, opt-in runbooks.

---

## DevOps and SRE Use Cases (Practical)

Here are a few Skills that are genuinely useful in real operations.

### Use Case 1: CI/CD Failure Triage

**Goal**: Standardise how you investigate failures and what you record.

A Skill can:

- Ask for the workflow URL and failing job name
- Require you to record whether it looks transient or deterministic
- Produce a consistent issue template for follow-up

### Use Case 2: Terraform Change Risk Review

**Goal**: Make IaC reviews consistent across a team.

A Skill can:

- Require you to list affected environments
- Check for risky patterns (public exposure, identity changes, state migration)
- Output a simple go/no-go summary and required approvals

### Use Case 3: Runbook Generator

**Goal**: Turn tribal knowledge into a maintained operational runbook.

A Skill can:

- Enforce sections (Symptoms, Checks, Rollback, Escalation)
- Add a "Safety" section (blast radius, data loss risk)
- Produce a markdown runbook that matches your house style

### Use Case 4: Postmortem Assistant

**Goal**: Reduce the time from incident to learning.

A Skill can:

- Convert incident notes into a timeline
- Extract contributing factors and remediation items
- Enforce blameless language and clear action items

---

## Advanced Patterns (Where Skills Get Interesting)

Once the basics work, Skills shine when you treat them like reusable operational modules.

### 1) Bundle references and templates

Keep `SKILL.md` short and link out to extra files in the same folder:

- `references/` for short docs you want to load on demand
- `assets/` for templates (issue templates, runbook templates)
- `scripts/` for small utilities

### 2) Keep descriptions keyword-rich

The `description` is the discovery surface. If you want the Skill to load for DevOps/SRE workflows, include words like:

- incident, outage, on-call, pipeline, deployment, rollback
- terraform, kubernetes, azure, aws, gcp
- security review, compliance, audit

### 3) Decide which Skills auto-load

For teams, I recommend:

- Auto-load for safe, low-risk guidance Skills (triage checklists)
- Manual-only for high-impact Skills that might lead to edits or deployments

---

## Real Examples You Can Explore

This repo already contains a working Skill you can inspect:

- `.github/skills/new-blog-post/SKILL.md` in this repository

If you want ready-made public examples to learn from (without relying on GitHub code search), start here:

- https://github.com/github/awesome-copilot (community collection)
- https://github.com/anthropics/skills (reference skills)

Copy any skill folder into `.github/skills/`, then tweak the wording and guardrails until it matches how your team works.

If you want to find more public examples on GitHub, search for the folder pattern:

- `path:.github/skills SKILL.md`

Note that GitHub code search may require you to sign in.

For the authoritative reference, see the VS Code documentation:

- https://code.visualstudio.com/docs/copilot/customization/agent-skills

---

## Tips for Adoption in DevOps Teams

- **Start with one runbook**: pick a repetitive task (CI triage) and ship one Skill.
- **Treat Skills as code**: version them, review changes, keep them short and intentional.
- **Measure outcomes**: shorter time to triage, fewer repeated mistakes, better incident updates.
- **Keep it safe**: do not turn every Skill into an autonomous actor. Default to guidance and checklists.

---

## Conclusion

GitHub Copilot Skills are a practical way to turn the workflows in your head into something your whole team can reuse. For DevOps and SREs, that means more consistent triage, better runbooks, and faster, calmer incident response.

If you want, I can also turn the example `incident-triage` Skill into a full folder with templates and a lightweight script so you can drop it straight into `.github/skills/`.

### _Author_

{% user pwd9000 %}

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [X](https://x.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-pwd9000/)

Date: 24-02-2026
