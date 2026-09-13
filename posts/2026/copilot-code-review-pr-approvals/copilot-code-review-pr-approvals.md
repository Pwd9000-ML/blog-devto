---
title: Copilot Can Now Approve Pull Requests. Should It Count Toward Your Branch Protection?
published: true
description: 'Copilot code review can now submit approvals that satisfy required reviews. How the controls compose, what is undocumented, and a safe rollout.'
tags: 'githubcopilot, github, devops, codereview'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2026/copilot-code-review-pr-approvals/assets/main.png'
canonical_url: null
id: 4644186
series: GitHub Copilot - Automation
---

## Copilot Can Now Approve Pull Requests. Should It Count Toward Your Branch Protection?

Until this month, a Copilot code review was advice. It left a **Comment** review, never an **Approve** or **Request changes**, and GitHub's own documentation was explicit that Copilot reviews did not count toward required approvals. You could ignore it, act on it, or argue with it, but it never moved the merge button.

On 1 September 2026 that changed. Copilot code review now includes an **approval assessment** in every review, and administrators can authorise Copilot to submit an approving review that **counts toward the repository's required-approvals rule**. Ten days later GitHub followed up with auto-resolution of Copilot's own comments, shell-tool execution during reviews, and an ensemble of agents at the Lite effort level.

This is the moment where AI code review stops being a suggestion layer and becomes part of the control plane. That deserves more scrutiny than "turn it on and see". This article covers what changed, exactly how the controls compose across enterprise, organisation, and repository, what GitHub has not documented yet, and a rollout pattern that lets you benefit without quietly weakening branch protection.

If you want the wider landscape of Copilot review surfaces, my earlier [definitive guide to code reviews with Copilot](https://dev.to/pwd9000/mastering-code-reviews-with-github-copilot-the-definitive-guide-3nfp) still applies. This post is narrowly about the approval capability and the governance around it.

> **Evidence boundary:** Copilot approvals are a public preview and GitHub's docs say they are "subject to change". Everything below about product behaviour is grounded in the 1 and 11 September 2026 changelog entries and GitHub Docs as of 13 September 2026.

---

## What Changed

Three changelog entries in two weeks matter here.

**[27 August 2026.](https://github.blog/changelog/2026-08-27-copilot-code-review-resolution-reasons-and-expanded-capabilities/)** The 300 file / 20,000 line limit on Copilot code review no longer applies, and reviewers gained resolution reasons (**Addressed**, **Won't fix**, **Incorrect**) on Copilot comments. 

**[1 September 2026.](https://github.blog/changelog/2026-09-01-copilot-code-review-can-now-approve-pull-requests/)** Two related things shipped in public preview for Copilot Pro, Pro+, Max, Business, and Enterprise:

1. **Approval assessments.** Every Copilot review now states in its overview comment whether Copilot considers the pull request ready to approve. GitHub is explicit: "An approval assessment alone does not count toward merge requirements."
2. **Copilot approvals.** When enabled, Copilot can submit an approval that counts toward the required-approvals rule "the same way a teammate's approval would". If new commits are pushed, the approval is dismissed like a human's, and you can re-request a review.

**[11 September 2026.](https://github.blog/changelog/2026-09-11-auto-resolution-and-analysis-updates-in-copilot-code-review/)** Copilot now resolves its own review comments during a re-review when a later commit addresses them, writes a generated commit message when you apply a Copilot suggestion, runs "the full set of shell tools from the Copilot SDK" behind the Copilot agent firewall to validate what it reviews, and uses an ensemble of agents at the Lite effort level. GitHub reports the ensemble increased addressed comments per review by 47% for high severity findings, 31% for medium, and 11% for low, while reducing review cost by about 8%.

Read together, the story is clear. The reviewer got more capable (it can build and run tests), more efficient (ensemble at Lite), and, optionally, authoritative (it can approve). The first two are uncontroversial. The third changes what your branch protection means.

---

## How the Controls Compose

This is where most of the value of this article lives, because the changelog summarises the controls and the docs spread them across three pages. Here is the full chain as documented in [Configuring code review by GitHub Copilot](https://docs.github.com/en/copilot/how-tos/copilot-on-github/set-up-copilot/configure-code-review).

### Enterprise

Path: enterprise **AI controls** > **Available Agents** > **Copilot code review**, then **Allow Copilot to approve pull requests**.

| Option | Effect |
| --- | --- |
| Disabled everywhere | Default. No organisation can enable approvals. |
| Let organizations decide | Delegates to organisation settings. |
| Enable for selected organizations | Allow-list specific organisations. |

### Organisation

Path: organisation **Settings** > **Copilot** > **Code review** > **Approvals** > **Count Copilot approvals toward merge requirements**.

| Option | Effect |
| --- | --- |
| Enabled everywhere | Every repository counts Copilot approvals. |
| Let repositories decide | Delegates to repository settings. |
| Enable for selected repositories | Allow-list specific repositories. |
| Disabled everywhere | No repository counts Copilot approvals. |

### Repository

Path: repository **Settings** > **Copilot** > **Code review** > **Auto-approval**.

| Setting | What it does |
| --- | --- |
| Allow Copilot to approve pull requests | Lets Copilot submit an **Approve** review at all. |
| Allow Copilot approvals to count toward merge requirements | Lets that approval satisfy the ruleset's required-approvals count. |
| File paths | Optional. One glob per line, up to 15. The approval counts only when **every changed file** in the pull request matches at least one glob. Blank means all files. |

The **two-toggle design** at repository level is the detail to internalise. You can allow Copilot to post an Approve review (useful signal in the timeline) without letting that review satisfy branch protection. The second toggle is the one that changes merge semantics.

### Where automatic review lives

Approvals are not configured in rulesets. Automatic review is. The ruleset rule is **Automatically request Copilot code review**, with sub-options **Review new pushes** and **Review draft pull requests**. In the REST rulesets API this is rule type `copilot_code_review` with parameters `review_on_push` and `review_draft_pull_requests` ([REST API: repository rules](https://docs.github.com/en/rest/repos/rules)).

That separation has a practical consequence for the 11 September auto-resolution feature: Copilot resolves its comments **during a re-review**. If your ruleset does not enable **Review new pushes**, a re-review only happens when someone requests it, so comments will not auto-resolve on their own.

### The effective decision

Putting the chain together, a Copilot approval satisfies your required-approvals rule only when **all** of these are true:

```text
enterprise policy allows the org
  AND org policy allows the repo
  AND repo: "Allow Copilot to approve pull requests" = on
  AND repo: "Allow Copilot approvals to count toward merge requirements" = on
  AND (file paths blank OR every changed file matches a configured glob)
  AND Copilot's assessment is "ready to approve"
  AND no commit was pushed after the approval
```

Any false in that chain and you are back to the pre-September behaviour: a review with an assessment that a human reads and acts on.

---

## Before vs Now

| Aspect | Before 1 Sep 2026 | Now (public preview) |
| --- | --- | --- |
| Review type Copilot can leave | Comment only | Comment, or Approve when enabled |
| Effect on required approvals | None | Counts when enabled at every level |
| Readiness signal | Implicit in comment tone | Explicit approval assessment in every overview comment |
| Scope control | Repository on/off for reviews | Repository-level path globs for counting approvals |
| Comment lifecycle | Humans resolve threads | Copilot resolves its own threads on re-review when addressed |
| Validation during review | Static read of the diff | Shell tools inside the agent firewall (build, test, scripts) |
| Size limits | 300 files / 20k lines | Removed |
| Lite effort | Single pass | Ensemble of agents |
| Default effort (from 28 Sep 2026) | Lite | Balanced |

That last row is a cost item you should not miss. GitHub's [28 August billing changelog](https://github.blog/changelog/2026-08-28-upcoming-changes-to-github-copilot-policies-and-billing/) states that a review effort value of **Default** will use **Balanced** from 28 September 2026. According to the [Copilot code review concept page](https://docs.github.com/en/copilot/concepts/agents/code-review), a Lite review typically consumes an estimated $0.05 to $1 of AI credits and a Balanced review $0.25 to $5, excluding GitHub Actions minutes. If you never explicitly chose Lite, your per-review cost ceiling rises fivefold in two weeks. Select **Lite** explicitly if that is what you want.

---

## Why This Matters for Delivery Governance

Required approvals are not a productivity feature. They are a control that auditors, security teams, and incident reviewers rely on. Letting a model satisfy that control is a policy decision, not a settings tweak. Three angles matter.

**Separation of duties.** Copilot can now be on both sides of a pull request: author (via Copilot cloud agent) and reviewer (via Copilot code review). GitHub already has a ruleset rule, **Require an additional approval for unattributed Copilot pull requests** (public preview, enabled by default), that adds one approval when Copilot opens a PR with no human attribution. The documentation for that rule and the documentation for Copilot approvals do not reference each other, so whether a Copilot approval can satisfy the _extra_ approval on a Copilot-authored PR is not stated. Assume nothing; test it in your sandbox before relying on it.

**Prompt injection becomes merge-relevant.** A reviewer that only comments is a low-value target for content injected into a diff, a commit message, or a linked issue. A reviewer whose approval unblocks merge is a higher-value target. GitHub's agent firewall and read-only review contexts reduce that surface, but the correct mitigation is structural: keep a human approval on paths where a bad merge is expensive.

**Metrics drift.** Auto-resolution changes what "open review comments" means in your dashboards. A thread resolved by Copilot after a fix commit is a good outcome, but it is now indistinguishable in a naive count from a thread a human resolved. If you report on review health, tag the resolver.

---

## A Path-Scoped Configuration That Makes Sense

The file paths control is the feature that turns "should an AI approve?" from a yes/no argument into an engineering decision. Here is a starting configuration for a repository where Copilot's approval is allowed to count only for low-blast-radius change classes.

### 1. Ruleset for the default branch

Import this via **Settings** > **Rules** > **Rulesets** > **Import a ruleset**, or with the REST API. A copy lives in the article's [code folder](https://github.com/Pwd9000-ML/blog-devto/blob/main/posts/2026/copilot-code-review-pr-approvals/code/main-branch-ruleset.json).

```json
{
  "name": "main: reviewed merges",
  "target": "branch",
  "enforcement": "active",
  "conditions": {
    "ref_name": {
      "include": ["~DEFAULT_BRANCH"],
      "exclude": []
    }
  },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 1,
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": true,
        "require_last_push_approval": true,
        "required_review_thread_resolution": true,
        "allowed_merge_methods": ["squash"]
      }
    },
    {
      "type": "copilot_code_review",
      "parameters": {
        "review_on_push": true,
        "review_draft_pull_requests": false
      }
    }
  ]
}
```

To create it from the terminal:

```powershell
gh api "repos/$env:OWNER/$env:REPO/rulesets" --method POST --input ./code/main-branch-ruleset.json
```

`gh api` uses your existing `gh auth login` token. Creating repository rulesets requires repository admin permissions. Do not put a personal access token in the command or in the file.

### 2. CODEOWNERS for the paths that must stay human

```text
# .github/CODEOWNERS
*                       @acme/platform-reviewers
/infra/**               @acme/platform-security
/src/auth/**            @acme/identity-team
/.github/workflows/**   @acme/platform-security
```

Because the ruleset requires code owner review, any PR touching these paths needs a designated human owner regardless of what Copilot does. The interaction between Copilot approvals and code owner reviews is not documented, and the safe assumption is that Copilot is not a code owner.

### 3. Repository Copilot approval settings

In **Settings** > **Copilot** > **Code review**:

- Review effort level: **Lite** (set it explicitly, given the 28 September default change).
- **Allow Copilot to approve pull requests**: on.
- **Allow Copilot approvals to count toward merge requirements**: on.
- **File paths**:

```text
docs/**
*.md
CHANGELOG.md
```

With this configuration, a documentation-only PR can be merged with Copilot's approval plus a passing CODEOWNERS check from `@acme/platform-reviewers` if that team is also required for `*`. If you want docs PRs to merge on Copilot's approval alone, narrow the `*` CODEOWNERS entry so it does not cover `docs/**` and Markdown files. That is a deliberate choice; make it in a PR that the security team reviews.

### 4. Organisation and enterprise

Set the enterprise policy to **Enable for selected organizations** and the organisation policy to **Enable for selected repositories**. Add only the pilot repository. Allow-lists at both levels mean a repository admin cannot opt in without a platform-level decision, which is exactly the property you want for a control that affects merge gating.

---

## Validating the Behaviour in a Sandbox

Do not trust a settings page. Prove the behaviour with two pull requests in a non-production repository that has the configuration above.

**PR A: in scope.** Change only `docs/getting-started.md`. Let the automatic review run. Expect an overview comment containing an approval assessment. If Copilot judges it ready, expect an **Approve** review from `copilot-pull-request-reviewer[bot]` and the required-approvals check to turn green.

**PR B: mixed scope.** Change `docs/getting-started.md` and `src/auth/session.ts`. Expect the review, expect the assessment, and expect the approval **not** to count, because not every changed file matches a glob. Expect the code owner requirement for `/src/auth/**` to remain unsatisfied.

**PR A, second push.** Push a trivial follow-up commit to PR A. Expect Copilot's approval to be dismissed. With **Review new pushes** on, expect a re-review and, if the diff still passes, a fresh approval.

Inspect the review state from the terminal:

```powershell
gh pr view 42 --json reviews --jq '.reviews[] | {author: .author.login, state: .state, submittedAt: .submittedAt}'
```

Expected shape of the output for PR A after the automatic review:

```json
{
  "author": "copilot-pull-request-reviewer[bot]",
  "state": "APPROVED",
  "submittedAt": "2026-09-14T09:12:41Z"
}
```

Then confirm merge-readiness from the same data source your automation would use:

```powershell
gh pr view 42 --json mergeStateStatus,reviewDecision --jq '{mergeStateStatus, reviewDecision}'
```

`reviewDecision` should remain `REVIEW_REQUIRED` for both PRs until `@acme/platform-reviewers` approves PR A; after that, PR A can become `APPROVED` if Copilot satisfies the required-approval and last-push rules, while PR B remains `REVIEW_REQUIRED`. Record the undocumented interactions rather than assuming them.

A small PowerShell helper that runs these checks for a list of PR numbers is included in the [code folder](https://github.com/Pwd9000-ML/blog-devto/blob/main/posts/2026/copilot-code-review-pr-approvals/code/check-copilot-approvals.ps1).

---

## What GitHub Has Not Documented Yet

Being precise about the gaps is more useful than pretending they do not exist. As of 13 September 2026:

| Question | Status |
| --- | --- |
| Does a Copilot approval satisfy **Require approval of the most recent reviewable push**? | Not documented. The rule requires approval "by someone other than the person who pushed it". A fresh Copilot approval after the last push plausibly qualifies, but no docs page says so. |
| Does a Copilot approval satisfy **Require review from Code Owners**? | Not documented. Copilot is not a CODEOWNERS entity. Assume no. |
| Does a Copilot approval trigger **auto-merge**? | Not documented. If the approval satisfies all required rules, standard auto-merge logic would presumably proceed. Test it. |
| Can a Copilot approval satisfy the extra approval from **Require an additional approval for unattributed Copilot pull requests**? | Not documented. |
| Exact wording of approval assessment outcomes | Not documented beyond "whether Copilot considers the pull request ready to approve". |
| REST or GraphQL surface for the approval settings | None found in the rulesets API or the Copilot REST API. Configuration is UI-only for now. |
| Audit log | Settings changes surface as `copilot.code_review_repository_settings_updated` and `copilot.code_review_organization_settings_updated`. No approval-specific event is documented. |
| GitHub Enterprise Server | The docs are versioned for GitHub.com and Enterprise Cloud only. No GHES availability is stated. |

---

## Limitations and Gotchas

- **15 globs per repository.** Enough for a focused allow-list, not enough to enumerate a monorepo.
- **Excluded content.** According to the concept page, Copilot code review does not review dependency management files such as `package.json` or `Gemfile.lock`, log files, or SVGs. Be cautious about letting an approval count on lockfile-only PRs when the reviewer did not read the lockfile.
- **Re-review repetition.** GitHub's usage docs note that Copilot may repeat comments on re-review even if they were dismissed.
- **Budget blocks reviews.** If a user-level budget, enterprise, or cost centre spending limit is exhausted, reviews are blocked. An automatic review that never runs cannot approve, and your PR will wait for a human. That is the right failure mode, but it will surprise people.
- **Actions dependency.** Agentic review capabilities run on GitHub Actions. If GitHub-hosted runners are disabled, the docs say reviews fall back to a more limited review.
- **Preview status.** Names, options, and behaviour can change. Re-check the docs before you cite this configuration in an audit.

---

## Real-World Use Cases

1. **Documentation repositories.** Allow-list `docs/**` and Markdown, keep a human code owner on anything else. Approvals count, humans are freed from reviewing typo fixes.
2. **Generated client SDKs.** For a repository where CI regenerates an OpenAPI client, allow-list the generated directory and require a human only when the generator config changes.
3. **Second approver on two-approval repositories.** Keep `required_approving_review_count` at 2 and let Copilot count as one. A human still signs every merge, and the human reviewer starts from Copilot's findings.
4. **Terraform formatting and comment-only changes.** Allow-list a narrowly scoped module path where changes are cosmetic. Keep `/infra/**` under a security code owner so anything material still needs a person.
5. **Inner-source contributions.** In organisations where external-team PRs wait days for an owner, Copilot's approval assessment gives the owner a triaged starting point even when it does not count.

---

## My Take

This is opinion, clearly labelled.

Letting Copilot's approval **count** is defensible only when three things hold: the change class is genuinely low blast radius, the path allow-list is narrow enough that generated files and incidental edits do not defeat it, and a human still owns the merge decision on anything security-relevant through CODEOWNERS. Under those conditions the feature removes real toil. Outside them, it is a way to make branch protection look intact while removing the person who was providing the protection.

The approval **assessment**, on the other hand, should be on everywhere. It costs nothing extra, it is a better signal than scanning fifteen comments to infer whether the reviewer was broadly happy, and it trains teams to read Copilot's judgement critically before anyone proposes letting it count.

The 11 September changes are the more important technical shift. A reviewer that can run the build and the tests inside a firewalled environment is a different class of tool from one that reads a diff. That is what will eventually make the approval question less fraught. Until GitHub documents the CODEOWNERS and last-push interactions, and exposes the settings through an API you can enforce with policy-as-code, treat counting approvals as a pilot, not a platform default.

---

## Conclusion

- Copilot code review can now approve pull requests, in public preview, and that approval can count toward required approvals when enabled at enterprise, organisation, and repository level.
- The controls compose as an all-must-be-true chain, with a two-toggle repository design and up to 15 path globs where every changed file must match.
- Approvals are configured in Copilot settings, automatic review is configured in rulesets, and auto-resolution depends on re-reviews actually running.
- CODEOWNERS, last-push approval, auto-merge, and the unattributed-Copilot-PR rule interactions are not documented. Test them before you depend on them.
- From 28 September 2026, **Default** effort means **Balanced**. Choose Lite explicitly if you want Lite pricing.
- Start with the assessment on and counting off, pilot counting on a path-scoped, low-risk repository, and keep humans on every path where a bad merge is expensive.

Copilot earning the right to approve is a reasonable direction. Whether it has earned it in your repository is a question only your evidence can answer.


---

### _Author_

{% user pwd9000 %}

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [X](https://x.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-pwd9000/)

Date: 13-09-2026
