---
title: 'Copilot Agent Safety: Permissions, Sandboxing and Computer Use'
published: false
description: 'Understand how Copilot permissions, local sandboxing, and computer use differ, and how to introduce them safely to DevOps teams.'
tags: 'githubcopilot, security, devops, ai'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2026/copilot-agent-safety-permissions-sandboxing/assets/main.png'
canonical_url: null
id: null
series: null
date: '2026-10-27T10:43:16Z'
---

## Copilot Agent Safety: Permissions, Sandboxing and Computer Use

The useful question is not whether an AI agent can run a command. It is what happens when the command is unnecessary, unsafe, or based on misleading repository content.

Three recent GitHub Copilot capabilities address different parts of that problem: assisted permissions, local sandboxing, and computer use. They are not interchangeable. Assisted permissions evaluates requests, sandboxing constrains some local execution, and computer use gives Copilot a way to operate desktop applications. Together they can reduce risk, but they do not remove the need for policy, review, and least privilege.

> **Status checked 27 October 2026:** assisted permissions is generally available in Copilot CLI, Visual Studio Code, and the GitHub Copilot app. Local sandboxing in the Copilot app and computer use are in public preview.

## What changed?

| Capability | What it controls | Current status |
| --- | --- | --- |
| Assisted permissions | Whether eligible command, path, or URL requests are approved automatically or sent to a person | GA in Copilot CLI, VS Code, and Copilot app |
| Local sandboxing | What some local agent-executed processes can access on the filesystem, network, and system | Public preview; OS and client support differ |
| Computer use | Whether Copilot can interact with desktop applications through their visual and accessibility interfaces | Public preview in Copilot CLI and the Copilot app on macOS and Windows |

These are separate controls. A permission decision is not a sandbox boundary, and a sandbox does not establish that an action in a business application is appropriate.

## How the controls fit together

### Assisted permissions: a model evaluates a request

In assisted mode, Copilot uses a language model to assess eligible requests, such as running a command, accessing a path, or opening a URL. Existing permission rules and enterprise restrictions are evaluated first. The model may approve a request it judges safe in the context of the task; if it is uncertain, Copilot asks for approval.

That makes assisted permissions a middle ground between manual prompts and unconditional approval. It is not a deterministic allowlist. GitHub explicitly warns that the model can make mistakes and approve dangerous or unintended actions.

To enable it in an interactive Copilot CLI session:

```text
/permissions assisted
```

To return to manual approval:

```text
/permissions manual
```

In non-interactive or autopilot runs, requests that still need approval are denied rather than waiting for a person. The safety review can also be unavailable; in that case, the request follows the session's normal permission handling.

### Local sandboxing: constrain the execution environment

Local sandboxing is powered by Microsoft's eXecution Container technology. It applies an operating-system-level policy to restrict access to selected files, network resources, and capabilities. It is not a separate virtual machine or container.

In Copilot CLI, local sandboxing can be enabled in a session with:

```text
/sandbox enable
```

The Copilot app has its own local sandbox settings for repository and working-tree sessions. Settings are separate between the app and CLI. In the app, project settings control the default for new local sessions; they do not change a session that is already running.

Local sandboxing is off by default. Supported operating systems and the protections available vary. GitHub's documentation calls out limitations, including weaker Windows network protection than macOS and Linux, and the fact that the CLI's in-process built-in file tools rely on software checks rather than being constrained directly by the OS sandbox.

### Computer use: extend the agent into desktop applications

Computer use lets Copilot read accessible application content or visual context, click controls, enter text, press keys, scroll, and navigate across applications. It is intended for tasks where a direct API, terminal command, filesystem tool, browser tool, or MCP server is not a better fit.

In Copilot CLI, computer use can be enabled with:

```text
/computer on
```

It is also available in the Copilot app. The feature follows the tool permission settings for the client. You may approve access for one session or save an "Always allow" decision for an application. Saved approvals are local and can apply across the CLI and app on the same computer.

Computer use is not a reason to automate high-impact GUI tasks without review. Interfaces change; Copilot can select the wrong control or enter information into the wrong place. An application window can also expose sensitive data to the agent.

## A practical defence-in-depth pattern

For a local development task, consider the controls in this order:

1. **Start with least privilege.** Use a repository or working tree that does not contain unrelated credentials or sensitive data.
2. **Keep deny rules and enterprise restrictions.** Assisted permissions does not override them.
3. **Enable local sandboxing where supported.** Grant only the paths, network access, and credentials the task needs.
4. **Use assisted permissions instead of unconditional approval.** Review actions Copilot takes, especially when changing files or reaching external systems.
5. **Treat computer use as a separate approval surface.** Avoid "Always allow" for applications that contain sensitive information or support financial, production, or administrative actions.
6. **Review the result outside the agent session.** Inspect the diff, run tests and security checks, and use your normal pull request and deployment controls.

| Risk | Relevant control | Remaining responsibility |
| --- | --- | --- |
| An unnecessary shell command | Assisted permissions | Inspect the command and keep restrictive rules |
| A command reads or writes outside the project | Local sandboxing | Verify OS support and effective policy |
| Copilot acts in a GUI-only application | Computer-use approval | Confirm the target window and review every consequential change |
| Prompt injection in repository content | None of these controls is a complete defence | Treat repository data as untrusted; keep permissions and credentials narrow |

## Testing a rollout safely

Use a disposable repository or a non-production project first. In Copilot CLI, enable assisted permissions with `/permissions assisted` and sandboxing with `/sandbox enable`. Confirm the active modes using the commands documented for your CLI version, then ask Copilot to perform a small, reversible task.

Observe which actions proceed and which require approval. Review the session's tool activity, inspect the repository diff, and run tests yourself. For computer use, try a low-impact task in an application that contains no sensitive information. Do not validate safety by asking an agent to bypass controls or by connecting it to a production system.

Before enabling these capabilities broadly, test the actual operating systems, client versions, enterprise managed settings, and workflows your developers use. A setting that is available in one client may not have the same scope or enforcement in another.

## Limitations and security considerations

- **Assisted permissions is probabilistic.** GitHub warns that it may approve a dangerous action. It reduces prompts; it does not replace sandboxing or access restrictions.
- **Sandbox support is not identical across operating systems.** Read the current OS requirements and limitations. On Windows, some network controls rely on programs honouring proxy settings and do not provide the same protection against direct connections as macOS and Linux.
- **Some file operations are not OS-confined.** Copilot CLI's built-in file tools run in-process and enforce policy through software checks. Treat this as a different boundary from an isolated VM.
- **Computer use can misread dynamic interfaces.** It may click or type in the wrong place, repeat an action, or expose on-screen information to the model.
- **"Always allow" persists locally.** Avoid it for applications with sensitive data or high-impact controls.
- **Enterprise policy still matters.** Administrators can disable features or set restrictions. A local preference cannot override managed settings.
- **Cloud sessions differ.** Copilot's tool permission controls are not available for cloud sessions in the same way as local sessions.

## Production considerations

Do not treat any single toggle as an agent security programme. Maintain short-lived and narrowly scoped credentials, keep deny rules in force, separate development access from production, and require human review for changes that affect users or infrastructure. Record which Copilot surfaces and managed settings are approved, and review the policy as feature availability changes.

## Conclusion

The important distinction is what each control can and cannot guarantee. Assisted permissions reduces interruptions but asks a model to judge actions. Sandboxing limits some local process access but varies by operating system and client. Computer use reaches GUI-only workflows but adds a new way to affect sensitive applications.

Use them as layers around a tightly scoped task, not as a substitute for one another. Keep the final authority with the engineer, especially when an action can change production, expose data, or affect another person.

## Sources

| Source | Type | Date | What it verifies |
| --- | --- | --- | --- |
| [Assisted permissions generally available](https://github.blog/changelog/2026-10-26-github-copilot-assisted-permissions-generally-available) | GitHub Changelog | 26 October 2026 | GA status, supported Copilot surfaces, and enterprise controls |
| [Allowing safe commands to run without manual approval](https://docs.github.com/en/copilot/concepts/customizations/allowing-safe-commands) | GitHub documentation | Checked 27 October 2026 | Assisted permission behaviour, commands, limitations, and warnings |
| [About cloud and local sandboxes for GitHub Copilot](https://docs.github.com/en/copilot/concepts/security-governance-and-network-settings/about-cloud-and-local-sandboxes) | GitHub documentation | Checked 27 October 2026 | Sandbox mechanism, operating system support, and security limitations |
| [Local sandboxing in the GitHub Copilot app](https://github.blog/changelog/2026-09-23-local-sandboxing-in-the-github-copilot-app) | GitHub Changelog | 23 September 2026 | Copilot app local sandbox public preview |
| [Computer use in GitHub Copilot](https://docs.github.com/en/copilot/concepts/agent-capabilities/agent-powered-workflows-and-operations/computer-use) | GitHub documentation | Checked 27 October 2026 | Preview status, supported surfaces, permissions, and risks |
| [Copilot computer use changelog](https://github.blog/changelog/2026-10-01-github-copilot-can-now-interact-with-desktop-apps) | GitHub Changelog | 1 October 2026 | Announcement and enablement information |

### _Author_

{% user pwd9000 %}

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [X](https://x.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-pwd9000/)

Date: 27-10-2026
