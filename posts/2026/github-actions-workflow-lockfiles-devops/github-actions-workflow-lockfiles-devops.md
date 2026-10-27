---
title: 'GitHub Actions Workflow Lockfiles: Pin What Actually Runs'
published: true
description: 'Use GitHub Actions workflow lockfiles to pin action dependencies, review updates, and reduce supply-chain risk in CI.'
tags: 'githubactions, security, devops, tutorial'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2026/github-actions-workflow-lockfiles-devops/assets/main.png?v=cloudflare-20261027'
canonical_url: null
id: 4927956
series: null
date: '2026-10-27T11:59:53Z'
---

## GitHub Actions Workflow Lockfiles: Pin What Actually Runs

A workflow can look unchanged in Git while the code it runs has changed upstream. A reference such as `actions/checkout@v4` points to a tag, and tags can move. GitHub Actions workflow dependency lockfiles address that gap by recording the exact commits behind a workflow's action references.

GitHub announced workflow lockfiles in public preview on 14 October 2026. They are maintained with a GitHub CLI extension, reviewed like other dependency changes, and can be enforced by repository, organisation, or enterprise policy. This is a practical supply-chain control, not a guarantee that every dependency is safe.

## What changed?

Before lockfiles, teams could pin actions to full commit SHAs directly in workflow YAML. That is still a valid security practice, but it can make files harder to read and does not provide the same built-in inventory of transitive action dependencies. GitHub's new lockfile records dependency references and their resolved commits separately.

| Before | With a workflow lockfile |
| --- | --- |
| A tag or branch is resolved when a job runs. | An onboarded workflow runs the commit recorded in its lockfile. |
| Teams maintain full commit SHAs in workflow YAML or rely on tags. | The workflow can keep a readable version reference while the lockfile records the commit. |
| Transitive action dependencies are difficult to inventory consistently. | The lockfile records transitive action dependencies, subject to documented scope limits. |
| Reviewers may not see that a tag now resolves to different code. | A lockfile change makes the resolved commit visible in a pull request. |

The generated file is `.github/workflows/actions.lock`. It includes the workflow-to-dependency mapping and, for each dependency, the reference, resolved commit, and numeric owner and repository identifiers. GitHub uses those identifiers to check that the repository behind a name is still the repository that was locked.

## Prerequisites

- A repository hosted on GitHub.com or GitHub Enterprise Cloud, including Enterprise Cloud with data residency. GitHub Free, Team, and Enterprise plans are included in the public preview.
- Git and an authenticated GitHub CLI installation (`gh`) on the machine where you will onboard the workflows.
- Permission to read the repository and create or update local files. An administrator is needed to configure organisation or enterprise enforcement policies.
- Existing GitHub Actions workflows whose `uses:` references you have reviewed and intend to lock.

The extension does not currently support GitHub Enterprise Server. The feature is in public preview and can change.

## How it works

The extension reads workflows under `.github/workflows/`, resolves supported action references, and writes the generated lockfile. Once a workflow is onboarded, its action dependencies must be represented in the lockfile. At run time, GitHub Actions uses the recorded commit rather than trusting a tag or branch to remain unchanged.

The lockfile is maintained by `gh actions-lock`; do not edit it by hand. Dependabot can update a matching lockfile entry when it updates an action in an already-onboarded workflow. It does not onboard workflows that have no lockfile entries.

## Step-by-step: onboard a repository

Start from the repository root. First make sure the action references point to versions you actually want to use. A lockfile faithfully pins the current resolution; it does not review the action for you.

Install the extension:

```shell
gh extension install github/gh-actions-lock
```

Generate or update the lockfile:

```shell
gh actions-lock
```

To onboard just one workflow, pass its path:

```shell
gh actions-lock .github/workflows/ci.yml
```

Review the complete diff before committing it:

```shell
git status --short
git diff -- .github/workflows
```

The extension may rewrite workflow references to more specific versions and will create or update `actions.lock`. Check that every change is expected, especially changes to a locked commit or to `owner_id` and `repo_id`. A changed repository identity is a reason to investigate, not to approve automatically.

Before merging, verify the lockfile against the repository:

```shell
gh actions-lock --verify
```

This performs network checks. The separate `--verify-local` option is an offline coverage check only; it does not verify dependency provenance.

Commit the workflow and lockfile changes together. Then configure Dependabot for GitHub Actions if it is not already enabled, so supported version updates can update the corresponding lockfile entry in the same pull request.

## Enforcing lockfiles

The preview includes a **Require lockfile** policy for enterprise, organisation, and repository administrators. Use the policy to move from a pilot to broader enforcement. GitHub's Evaluate mode is available to Enterprise customers; consult the current enforcement documentation for the available settings and rollout behaviour.

Start with shared workflow repositories and a small set of representative repositories. Resolve local actions, check any actions allowlist, and review the generated changes before enabling enforcement. An allowlist may need to match locked commit SHAs rather than the old tags.

## Testing and verification

Run `gh actions-lock --verify` before merging a workflow change. It checks that the lockfile matches the workflow dependencies and performs network-backed validation. Add this check to your CI process if your team wants ongoing verification; the extension repository provides a sample workflow to adapt.

For ongoing operational assurance, review lockfile diffs as dependency changes. A successful verification does not mean an action's behaviour is harmless; it confirms the lockfile state and provenance checks described by the tool.

## Troubleshooting

- **A workflow is skipped because a local action cannot be resolved:** local paths such as `uses: ./path` resolve from the repository root. Correct the path, then rerun the extension. The tool has options to migrate or ignore local actions, but review their consequences first.
- **A tag moved upstream:** inspect the upstream repository history. If the change is legitimate, use `gh actions-lock --relock` to resolve it again. Do not use `--accept-moved` in automation; it accepts a new resolution that needs deliberate review.
- **An action is no longer allowed:** after onboarding, the allowlist is checked against locked commit SHAs. Update the policy deliberately rather than loosening it broadly.
- **Dependabot reports that onboarding is required:** Dependabot updates entries for locked workflows, but it does not add lockfile coverage for a workflow automatically. Onboard that workflow with `gh actions-lock`.

## Security boundaries and limitations

Lockfiles reduce the risk of a tag or branch moving to different code without a corresponding repository change. They do not prove that the locked code is trustworthy.

Important boundaries:

- Container images are not locked. Use image digests where appropriate and review image updates separately.
- A reusable workflow's dependencies are covered by the lockfile in the repository where that reusable workflow is defined. Onboard shared workflow repositories as well as their callers.
- Local `./...` actions are not followed like remote actions, and can require migration or an explicit ignore option.
- A lockfile may need to be regenerated when workflows or `uses:` dependencies change.
- The extension and lockfile format are in public preview and pre-1.0; review release notes before relying on automation or policy behaviour.

## Production considerations

Treat lockfile adoption as dependency governance, not as a one-time pinning exercise. Keep Dependabot enabled, review commit changes in pull requests, test policy enforcement on a representative set of repositories, and assign an owner for shared workflows. If you have repositories on GitHub Enterprise Server, keep using your existing pinning controls until the extension supports that platform.

## Conclusion

Workflow lockfiles make the code selected by a workflow more visible and reproducible, while retaining readable references in the YAML. They can close an important gap in Actions supply-chain hygiene, especially when paired with Dependabot and an enforcement policy. The important caveat is scope: lock what the tool supports, review every update, and keep treating dependencies as code that can carry risk.

## Sources

| Source | Type | Date | What it verifies |
| --- | --- | --- | --- |
| [Workflow dependency lockfiles](https://docs.github.com/en/actions/concepts/security/workflow-dependency-lockfiles) | GitHub documentation | Checked 27 October 2026 | Lockfile format, dependency coverage, preview status, and runtime behaviour |
| [Locking action dependencies in a repository's workflows](https://docs.github.com/en/actions/how-tos/secure-your-work/lock-workflow-dependencies) | GitHub documentation | Checked 27 October 2026 | Extension installation, onboarding, verification, Dependabot, and troubleshooting |
| [GitHub Actions workflow lockfiles in public preview](https://github.blog/changelog/2026-10-14-github-actions-workflow-lockfiles-in-public-preview) | GitHub Changelog | 14 October 2026 | Announcement, plan availability, and enforcement policy |
| [gh-actions-lock](https://github.com/github/gh-actions-lock) | Official GitHub repository | Checked 27 October 2026 | CLI modes, limitations, and sample verification workflow |
| [Enforcing lockfiles for action dependencies](https://docs.github.com/en/actions/how-tos/administer/enforce-workflow-lockfiles) | GitHub documentation | Checked 27 October 2026 | Administrative policy and enforcement |

### _Author_

{% user pwd9000 %}

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [X](https://x.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-pwd9000/)

Date: 27-10-2026
