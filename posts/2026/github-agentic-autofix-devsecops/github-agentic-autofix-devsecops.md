---
title: 'Can Copilot Fix Its Own Security Findings? Testing GitHub Agentic Autofix'
published: false
description: 'Evaluate GitHub agentic autofix, from alert assignment and validation to cost, review, rollback, and adoption.'
tags: 'github, security, devsecops, githubcopilot'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2026/github-agentic-autofix-devsecops/assets/main.png'
canonical_url: null
id: null
series: GitHub Copilot - Automation
date: '2026-07-27T00:00:00Z'
---

## Can Copilot Fix Its Own Security Findings? Testing GitHub Agentic Autofix

GitHub can now assign a code scanning alert directly to Copilot cloud agent. The agent explores the repository, changes code, attempts validation, and opens a draft pull request. That is more ambitious than generating a patch beside one vulnerable line. It is also not the same as proving that a vulnerability is gone.

The practical answer to the title is therefore: **Copilot can attempt end-to-end remediation, but the strength of the evidence depends on the scanner and your CI controls. A human still owns the security decision.**

This deep dive goes beyond my earlier [introduction to Copilot coding agent](https://dev.to/pwd9000/using-github-copilot-coding-agent-for-devops-automation-3f43). Rather than surveying general coding tasks, it examines one narrow DevSecOps question: how should a team test, review, and govern agentic autofix without mistaking automation for assurance?

> **Evidence boundary:** Agentic autofix is a paid public preview. I have not invented a successful run, timing result, credit charge, or vulnerability closure. The experiment below is a reproducible evaluation design for an eligible sandbox. Product behaviour is grounded in GitHub's 10 July 2026 announcement, its 16 July clarification, and linked GitHub documentation.

---

## What GitHub Announced, and What It Clarified

On 10 July 2026, GitHub announced [agentic autofix for code scanning alerts in public preview](https://github.blog/changelog/2026-07-10-agentic-autofix-for-code-scanning-alerts-in-public-preview). The original workflow is straightforward:

1. Assign one or more code scanning alerts to Copilot.
2. Copilot cloud agent inspects relevant files across the codebase.
3. It proposes a fix and attempts to validate it.
4. It iterates when necessary.
5. It opens a draft pull request containing the changes, an explanation, and validation details.

GitHub says generation typically takes two to four minutes, but that is product guidance, not a result measured in this article.

The editor's note added on **16 July 2026** matters. It clarified that assignment works for **all first-party and third-party code scanning alerts**. In other words, eligibility is not limited to CodeQL findings. Alerts uploaded by integrated tools through SARIF can also be assigned.

That does not make all validation equal. GitHub's detailed [autofix documentation](https://docs.github.com/en/enterprise-cloud@latest/code-security/concepts/code-scanning/autofix-for-code-scanning) says agentic autofix re-runs CodeQL using the code-scanning query suite on a best-effort basis. It cannot confirm alerts from custom CodeQL queries or the security-extended suite through that validation path, and fix quality for third-party alerts is not guaranteed.

This distinction is the centre of a sound evaluation:

| Question | Answer in the preview |
| --- | --- |
| Can the alert be assigned? | Yes, for first-party and third-party code scanning alerts. |
| Can Copilot edit multiple files? | Yes. The cloud agent explores the wider codebase. |
| Does GitHub open a pull request? | Yes, normally a draft pull request with a summary and validation notes. |
| Is the originating finding always re-proven as closed? | No. Built-in validation has scanner and query-suite limits. |
| Is the pull request ready to merge without review? | No. Validation, behaviour, dependencies, and risk still require human review. |

Do not extend the claim beyond code scanning. Dependabot and secret scanning are separate alert families with their own remediation workflows.

---

## The Agent Loop Is the Real Change

Classic Copilot Autofix translates alert context into a single suggested change. Agentic autofix delegates a task to Copilot cloud agent, which can use repository context and tools over several iterations.

The loop is roughly:

```text
alert context
    -> inspect related code and repository instructions
    -> form a remediation plan
    -> edit one or more files
    -> run available analysis and tests
    -> inspect failures or remaining findings
    -> revise the change
    -> open a draft pull request for review
```

Repository and organisation custom instructions apply while the agent works. That makes existing engineering guidance part of the control plane. A repository that tells agents to run focused tests, avoid new dependencies, and preserve public APIs gives the remediation loop better constraints than a repository with no executable acceptance criteria.

Validation must still be read scanner by scanner:

- **CodeQL code-scanning suite:** Copilot can re-run CodeQL and use the result to iterate.
- **Custom or security-extended CodeQL queries:** the documented built-in re-run does not prove those alerts are resolved. Re-run the repository's actual advanced setup in PR CI.
- **Third-party SARIF alerts:** assignment is supported, but the scanner's own PR workflow remains the authoritative check. A clean CodeQL result does not close a Semgrep, Snyk, Checkmarx, or other third-party finding.
- **Functional behaviour:** no static analyser proves that the application still meets its requirements. Unit, integration, contract, and negative security tests remain essential.

The agent may also report that it could not validate a fix or that an alert appears to be a false positive. That is useful evidence, not an invitation to auto-dismiss the finding.

---

## Four Ways to Assign Work

GitHub exposes the same remediation idea through four entry points:

1. **Individual alert UI:** open a code scanning alert and choose **Assign to Copilot**.
2. **Alert backlog batch:** select between 1 and 25 alerts and assign them together. Copilot works on the selected set in one pull request.
3. **Security campaign:** select between 1 and 25 campaign alerts for one pull request. This fits an organised remediation deadline, but it increases review and rollback coupling.
4. **REST API:** update one code scanning alert and set `assignees` to `['copilot-swe-agent[bot]']`.

The repository includes a [safe PowerShell REST helper](./code/assign-alert-to-copilot.ps1). Preview its target without making a request:

```powershell
./code/assign-alert-to-copilot.ps1 `
  -Owner 'acme-security' `
  -Repository 'agentic-autofix-lab' `
  -AlertNumber 42 `
  -WhatIf
```

For an authorised run, set `GITHUB_TOKEN` in the process environment and omit `-WhatIf`. The helper sends:

```http
PATCH /repos/acme-security/agentic-autofix-lab/code-scanning/alerts/42
Accept: application/vnd.github+json
X-GitHub-Api-Version: 2026-03-10

{"assignees":["copilot-swe-agent[bot]"]}
```

The [Update a code scanning alert endpoint](https://docs.github.com/en/enterprise-cloud@latest/rest/code-scanning/code-scanning?apiVersion=2026-03-10#update-a-code-scanning-alert) returns `200 OK` on success. Classic personal access tokens need `security_events` for private or public repositories, or `public_repo` for public repositories only. Use the least-privileged supported token for your automation and never place it in the script, command history, or repository.

Start with one alert. A batch saves orchestration time, but it makes attribution harder: which edit fixed which alert, which check failed, and which change should be reverted? Batch only alerts that share a component, scanner, owner, and rollback unit.

---

## Licence, Policy, and Cost Boundaries

The preview requires both sides of the product boundary:

- An active **GitHub Code Security or GitHub Advanced Security** licence.
- A **GitHub Copilot licence** with Copilot cloud agent enabled.
- Copilot Autofix available in the repository.
- GitHub Actions available for the cloud agent environment and validation work.

Administrators can disable Copilot Autofix at enterprise, organisation, or repository level. Because agentic autofix relies on that setting, disabling classic Autofix also blocks the agentic experience. Administrators can separately opt repositories out of Copilot cloud agent. An enterprise policy set to not allowed cannot be overridden lower in the hierarchy; allowing it merely lets organisation and repository administrators choose.

The billing model is materially different from classic Autofix:

| Route | Copilot licence | AI Credits | Actions minutes | Output |
| --- | --- | --- | --- | --- |
| Classic Copilot Autofix | Not required | No | Not for generation | One suggested fix to review and apply |
| Agentic autofix | Required | Yes | Yes | Iterative agent session and draft PR |
| Manual remediation | No | No | Normal CI usage | Engineer-authored change and PR |

During public preview, AI Credits are consumed only when a fix runs on alerts assigned to Copilot. The announcement says this usage is not itemised separately from other Copilot activity during the preview. Agent activity also consumes GitHub Actions minutes. Do not promise a fixed cost per alert: session depth, batch size, tests, runner type, and retries can change consumption.

Set a pilot budget before enabling broad campaigns. Track assigned alerts, agent sessions, Actions duration, PR outcome, and human review time together. A cheap generated patch that creates an expensive review queue is not a successful control.

---

## A Reproducible Sandbox Evaluation

Use an organisation-owned sandbox that has the required licences and policies. Do not test with production secrets, customer data, or a live deployment path.

### 1. Prepare representative findings

Create three small, intentionally vulnerable examples with deterministic tests:

- A CodeQL alert from the documented code-scanning suite.
- A CodeQL alert produced only by your custom or security-extended configuration.
- A third-party alert uploaded as SARIF by the scanner you actually use.

Keep each case on the default branch, record the alert number and tool, and ensure the scanner also runs on pull requests. Add functional tests that fail if a simplistic security patch changes intended behaviour.

### 2. Establish the baseline

Before assignment, record:

- Commit SHA, scanner version, query suite, rule ID, severity, and alert URL.
- Passing and failing test results.
- Existing alert count for every enabled scanner.
- Repository instructions and agent setup workflow revision.
- The expected secure behaviour, including negative test cases.

Without that baseline, an alert disappearing could mean a real fix, a changed path, a scanner configuration change, or stale analysis.

### 3. Run isolated assignments

Assign one alert at a time through the UI. Reserve the API helper for a second pass after the manual flow is understood. Capture the agent session log, draft PR, changed files, explanation, validation commands, Actions runs, elapsed time, and AI Credit reporting available to your administrators.

Do not steer the first run unless it is blocked. You want to observe the default behaviour. In a later run, add precise repository instructions and compare whether the agent chooses better tests and smaller changes. Because model output is non-deterministic, repeat representative cases rather than treating one success as a rate.

### 4. Apply a merge gate

A candidate passes only when all applicable checks are true:

| Gate | Reviewer question |
| --- | --- |
| Scanner closure | Did the original scanner, rule, configuration, and branch report the finding as fixed? |
| Regression scan | Did the change introduce new first-party or third-party alerts? |
| Functional safety | Do unit, integration, contract, and negative security tests pass? |
| Patch quality | Is the root cause fixed without broad rewrites or suppression? |
| Dependency integrity | Are new names real, supported, pinned appropriately, and licence-approved? |
| Scope | Can every changed file be traced to the assigned alert? |
| Reviewability | Is the PR small enough for a security-aware engineer to understand? |
| Operations | Are configuration, telemetry, runbooks, and rollback impacts addressed? |

Report outcomes as **validated**, **partially validated**, **not validated**, or **incorrect**. “PR opened” and “agent says fixed” are activity measures, not security outcomes.

---

## Review Risks and Rollback

GitHub's [responsible-use guidance](https://docs.github.com/en/enterprise-cloud@latest/code-security/responsible-use/security-and-quality-ai-features) is direct: generated fixes can contain syntax errors, change semantics, address only part of a vulnerability, introduce another vulnerability, or suggest an unsupported or even fabricated dependency. Large files and repositories can also cause relevant context to be truncated. The same alert may produce different changes on repeated runs.

Review the data flow, trust boundaries, error paths, and tests, not just the highlighted line. Watch for common weak fixes such as swallowing an exception, removing functionality, adding a broad allow-list, weakening input validation, or suppressing the rule. Verify every dependency independently.

Before merge, rollback is simple: stop steering the session, close the draft PR, and retain the session log for evaluation. After merge, revert the remediation PR rather than hand-editing around it, then rerun the original scanner and functional tests. Never dismiss an alert merely to align the dashboard with the agent's claim.

One-alert PRs make this process much cleaner. For batch remediation, require a commit or clearly separable diff per alert and confirm the entire batch shares one rollback decision.

GitHub states that data handled by Copilot Autofix is not used for LLM training, but your normal source-code access, data classification, and third-party scanner policies still apply.

---

## Troubleshooting the Preview

**The Assign to Copilot control is missing:** check the Code Security or Advanced Security licence, Copilot licence, cloud agent policy, Copilot Autofix setting, repository opt-out, Actions availability, and your access to the alert. Remember that upstream enterprise policy wins.

**The REST helper returns an error:** `400` usually points to the request, `403` can indicate an archived repository or missing Code Security entitlement, `404` can indicate an inaccessible repository or alert, and `503` is a service availability response. Confirm API version `2026-03-10`, token scopes, alert number, and repository before retrying.

**A PR opens without convincing validation:** inspect the agent session log. Determine whether the alert came from a custom query, the security-extended suite, or a third-party scanner. Ensure the exact scanner runs on the PR and that its credentials and dependencies are available without weakening the agent environment.

**The alert stays open after a plausible fix:** compare branch, commit SHA, analysis category, and configuration. The same alert can be produced by multiple code scanning configurations, and stale configurations can disagree. Re-run the authoritative workflow rather than relying on the PR description.

**The patch is too broad:** ask Copilot in a PR comment to reduce scope, preserve the public API, and add a regression test. If the design remains difficult to verify, close the PR and remediate manually. Delegation is optional; accountability is not.

---

## A Sensible Adoption Path

Start in observe mode with low-complexity, well-tested alerts in a non-production repository. Use individual assignments and require a security-aware reviewer. Compare agentic autofix with classic suggestions and manual fixes on patch size, scanner closure, regressions, review time, elapsed time, and cost.

Move to broader repositories only after the same scanner-specific gates are automated in branch protection. Introduce small homogeneous batches next. Security campaigns should come last, after ownership, budgets, concurrency, rollback, and audit evidence are established.

The feature is promising because it can do the tedious middle of remediation: investigate context, draft a multi-file change, run tools, and package evidence in a pull request. Its value is not that Copilot can mark its own work correct. Its value is that it can produce a testable candidate while deterministic scanners, repository tests, policy, and human review remain independent.

That is the right answer to “Can Copilot fix its own security findings?” Let it try. Make your delivery system prove the result.

---

## Sources and Further Reading

- [Agentic autofix for code scanning alerts in public preview](https://github.blog/changelog/2026-07-10-agentic-autofix-for-code-scanning-alerts-in-public-preview), including the 16 July 2026 clarification
- [About autofix for code scanning](https://docs.github.com/en/enterprise-cloud@latest/code-security/concepts/code-scanning/autofix-for-code-scanning)
- [Resolving code scanning alerts](https://docs.github.com/en/enterprise-cloud@latest/code-security/how-tos/manage-security-alerts/manage-code-scanning-alerts/resolve-alerts)
- [Disabling autofix for code scanning security alerts](https://docs.github.com/en/enterprise-cloud@latest/code-security/how-tos/manage-security-alerts/manage-code-scanning-alerts/disabling-autofix-for-code-scanning)
- [REST API endpoints for code scanning](https://docs.github.com/en/enterprise-cloud@latest/rest/code-scanning/code-scanning?apiVersion=2026-03-10#update-a-code-scanning-alert)
- [Usage-based billing for organisations and enterprises](https://docs.github.com/en/enterprise-cloud@latest/copilot/concepts/billing/usage-based-billing-for-organizations-and-enterprises)
- [Application card: GitHub security and quality AI features](https://docs.github.com/en/enterprise-cloud@latest/code-security/responsible-use/security-and-quality-ai-features)
- [Fixing alerts in a security campaign](https://docs.github.com/en/enterprise-cloud@latest/code-security/how-tos/manage-security-alerts/remediate-alerts-at-scale/fixing-alerts-in-security-campaign)

### _Author_

{% user pwd9000 %}

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [X](https://x.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-pwd9000/)

Date: 27-07-2026
