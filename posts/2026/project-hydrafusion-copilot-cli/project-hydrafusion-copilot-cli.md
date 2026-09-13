---
title: 'Project HydraFusion: GitHub Copilot Stops Picking a Model and Starts Building a Workflow'
published: false
description: 'HydraFusion builds Single, Cascade or Critique workflows across models in Copilot CLI. What the benchmarks really say and how to evaluate it.'
tags: 'githubcopilot, ai, devops, llm'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2026/project-hydrafusion-copilot-cli/assets/main.png'
canonical_url: null
id: null
series: GitHub Copilot - CLI
date: '2026-09-13T16:30:00Z'
---

## Project HydraFusion: GitHub Copilot Stops Picking a Model and Starts Building a Workflow

For the last year, the most consequential decision in a Copilot session has been the model picker. Opus for the hard refactor, a cheaper GPT for the boilerplate, Auto when you could not be bothered. Auto model selection made that decision for you, once per session, and gave you a 10% discount for trusting it.

On 4 September 2026 GitHub published [Project HydraFusion](https://github.blog/ai-and-ml/github-copilot/project-hydrafusion-frontier-quality-via-multi-model-orchestration/), a research preview in Copilot CLI that changes the unit of decision. Instead of choosing a model, the runtime builds an execution plan per request: one model solves it directly, or a cheap model drafts and a quality gate decides whether to escalate, or one model drafts and a read-only critic from a different vendor reviews it before a single revision. GitHub's headline number is 67% lower estimated cost than Claude Opus 5 with higher verified quality on TerminalBench 2.1.

That headline deserves the scrutiny this article gives it. But the more durable story is architectural. Teams have been hand-rolling draft-then-critique and cheap-then-escalate patterns in their own agent code for eighteen months. HydraFusion moves those patterns into the Copilot runtime, with cost accounting per leg, bounded execution, and a fail-safe patch policy. That is what a DevOps engineer should evaluate, and this article gives you a way to do it on your own workload.

If you want the CLI fundamentals first, my [Copilot CLI practical guide](https://dev.to/pwd9000/github-copilot-cli-a-devops-engineers-practical-guide-to-ai-powered-terminal-automation-1jh0) and [evaluating LLM models in Copilot](https://dev.to/pwd9000/evaluating-llm-models-in-github-copilot-a-practical-scoring-and-assessment-guide-1f23) cover the ground this post builds on.

> **Evidence boundary:** HydraFusion is a research preview. GitHub states that "results, models, workflows, availability, names, and product behavior may change". Every benchmark figure below is GitHub's own offline result, quoted with its caveats. I have not run HydraFusion against a benchmark myself. The evaluation harness later in the article is a reproducible design, verified for syntax against Copilot CLI 1.0.83, not a claim of measured results.

---

## What Changed

**Status:** research preview, available in GitHub Copilot CLI only, on all Copilot plans, behind `/experimental`. Announced on the GitHub Blog on 4 September 2026 and included in the [10 September weekly changelog](https://github.blog/changelog/2026-09-10-github-copilot-weekly-releases-september-7/). It is not in VS Code, the Copilot app, or cloud agent. The VS Code 1.137 release notes do not mention it.

**Billing:** GitHub's callout states that "usage is based on the tokens consumed by the models HydraFusion uses, priced at each model's standard rate". There is no surcharge and, unlike Auto model selection, no discount. Since 1 June 2026 Copilot bills agentic usage in AI credits (1 credit = $0.01) based on tokens per model, so a HydraFusion request costs the sum of every leg it runs. Premium request multipliers only apply to legacy annual plans and are not relevant here.

**Enablement:** in Copilot CLI, run `/update`, then `/experimental on`, then `/model` and select **HydraFusion (Research Preview)**. One hands-on report notes that enabling experimental mode restarted the CLI, and the picker label in the changelog screenshot reads "HydraFusion (Preview)". Expect naming to move.

**Scope guidance from GitHub:** "first-turn, single-prompt coding tasks are the best place to start", ideally "substantial, well-scoped coding tasks that you can hand to Copilot in autopilot mode in a single prompt". Multi-turn performance is explicitly the next focus.

---

## How It Works

GitHub describes HydraFusion as treating "workflow selection as an optimization problem". Per request, it scores the task on capability signals (reasoning, code generation, debugging, tool use) and picks "the least complex workflow expected to meet its needs, using additional model calls only when they are likely to improve the result".

### The three execution patterns

| Pattern | Mechanism (GitHub's description) | When it makes sense |
| --- | --- | --- |
| **Single** | One selected model solves the task directly. | The task is well within a single model's capability; adds no overhead. |
| **Cascade** | An efficient model drafts a solution and a quality gate decides whether to accept it or escalate to a stronger model. | Most tasks are easy, some are not, and you would rather pay for the strong model only on the hard ones. |
| **Critique** | One model drafts a result, an independent read-only critic from a different model family reviews it, and the drafting model revises once. | Tasks where a second opinion catches more than a second attempt would. |

The Critique pattern follows the same approach as [Rubber Duck](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/rubber-duck) in Copilot CLI, which GitHub documents as deliberately running "on a different AI model from the one driving your session" with read-only access that "cannot edit files or run commands". HydraFusion automates that invocation and bounds it to one revision.

### The five operating principles

These are the part of the announcement most worth reading twice, because they describe the runtime guarantees rather than the marketing. Quoted from GitHub:

- **Complete accounting.** "Aggregate cost and usage across every workflow leg, including drafting, critique, revision, escalation, retry, and fallback."
- **Bounded execution.** "Give each leg explicit timeout and cancellation behavior to keep execution and cost within defined limits."
- **Isolated review.** "Run review steps in isolated, tool-less contexts, while solver steps use the shared workspace and normal permission-aware agent loop."
- **Fail-safe application.** "Apply no patch when the workflow is cancelled or fails validation, preventing incomplete changes from reaching the repository."
- **Validated routing.** "Verify workflow definitions, model bindings, fallback behavior, and model availability before execution begins."

Two of these matter more than the others for operations. **Isolated review** means the critic never touches your workspace and never has tools, which is the correct trust boundary for a step whose only job is to disagree. **Fail-safe application** means a cancelled or failed workflow leaves your repository untouched rather than half-patched. Both are properties you would have to build yourself if you assembled the same pattern from separate agents.

### How the routing policy was built

GitHub did not hand-tune thresholds. The blog describes using beam search to construct the decision policy, measuring each candidate "against a frozen baseline on quality, cost, and failure modes" across TerminalBench 2.1, DeepSWE, and an internal benchmark called CheckpointBench. The hill-climbing record they publish is refreshingly honest: two harness failures between 11 and 25 August produced invalid runs that were excluded, and the strongest configurations arrived on 25 August.

What GitHub has **not** published is the model pool. The benchmark charts compare HydraFusion against Claude Opus 5, Claude Sonnet 5, and GPT-5.6 Sol, Terra, and Luna as solo models, but those are comparators, not a disclosed pool. GPT-6 Astra, which reached GA in Copilot on 4 September, is not mentioned. Some community write-ups link HydraFusion to a Microsoft research paper on hybrid dynamic routing; GitHub has not confirmed that, so treat it as inference.

### HydraFusion vs Auto model selection

|  | Auto model selection | HydraFusion |
| --- | --- | --- |
| Status | GA across Chat, VS Code, CLI, app, cloud agent | Research preview, CLI only |
| Unit of decision | One model per session (re-evaluated at compaction boundaries) | One workflow per request, potentially multiple models |
| Mechanism | Task complexity plus real-time model health | Capability signals selecting Single, Cascade, or Critique |
| Pricing | 10% discount on paid plans | Standard token rates summed across legs |
| Honours admin model policies | Yes, documented | Not documented |

Mario Rodriguez, GitHub's Chief Product Officer, is quoted in secondary coverage as saying that Auto "is about intelligently selecting a model and HydraFusion is about orchestrating a workflow". I could not read the original VentureBeat article directly, so treat the quote as second-hand, but it matches GitHub's own framing.

---

## Reading the Benchmarks Honestly

GitHub's published table, relative to Claude Opus 5, all models at medium reasoning effort:

| Benchmark         | Cost vs Opus 5 | Quality vs Opus 5 |
| ----------------- | -------------- | ----------------- |
| TerminalBench 2.1 | 67% lower      | +4.9 points       |
| DeepSWE           | 36% lower      | -1.5 points       |
| CheckpointBench   | 65% lower      | -0.1 points       |

The blog's embedded charts carry the absolute figures, which are more useful for cost modelling:

| Benchmark | HydraFusion | Opus 5 | GPT-5.6 Sol |
| --- | --- | --- | --- |
| TerminalBench 2.1 (pass@1, $/task) | 84.7%, $0.30 | 79.8%, $0.90 | 73.3%, $0.30 |
| DeepSWE (pass@1, $/task) | 62.6%, $2.70 | 64.1%, $4.20 | 60.4%, $2.40 |
| CheckpointBench (session score, $/task) | 77.5%, $8.50 | 77.6%, $24.10 | 76.1%, $7.50 |

A few observations that the headline does not tell you:

1. **HydraFusion beat Opus 5 on one benchmark out of three.** On the other two it is slightly behind on quality and substantially cheaper. "Frontier quality at lower cost" is a fair summary; "better than Opus" is not.
2. **The interesting comparison is often GPT-5.6 Sol, not Opus.** On TerminalBench, HydraFusion costs the same as Sol and scores 11 points higher. On DeepSWE and CheckpointBench it costs 12% more than Sol for 2 and 1.4 points more quality. If your team already defaults to a mid-tier model, the cost saving versus your baseline is much smaller than 67%.
3. **TerminalBench 2.1 is described by GitHub itself as relatively saturated**, which is why the harder repository-level DeepSWE matters more, and that is where the margin is thinnest.
4. **CheckpointBench is internal.** GitHub says it contains 276 checkpoints from real Copilot sessions, balanced across language and task type. You cannot reproduce it.
5. **These are offline, best-tuned configuration, medium reasoning, and pricing-assumption specific.** GitHub says so directly. The research preview exists to find out whether the results survive contact with real developer workloads.

None of this is a criticism of GitHub's transparency, which is better than most model announcements. It is a reason to run your own numbers.

---

## Why DevOps Engineers Should Care

**Cost variance becomes a workflow property.** With a fixed model, cost per task scales roughly with task size. With Cascade, the same prompt can cost a cheap draft or a cheap draft plus a strong-model escalation depending on whether the quality gate fires. With Critique it is always at least two model calls plus a revision. Budget controls need to move from "which model" to "what is the cap per task", which Copilot CLI already supports with `--max-ai-credits`.

**Latency becomes multi-modal.** A Single route returns like any model. A Cascade that escalates or a Critique with revision takes minutes. One early hands-on report describes a Cascade run of three to four minutes for a single prompt. That is fine for a task you hand off in autopilot; it is not fine for an interactive loop. GitHub's guidance to start with substantial, well-scoped single-prompt tasks is a latency statement as much as a quality one.

**Opacity is the trade-off.** You get one coherent response and one permission-aware change set. You do not see the intermediate drafts or, as far as the current preview documents, which pattern was chosen and why. The runtime records "the role, outcome, cost, latency, and diagnostics of each leg" internally, but that telemetry is not exposed to you today. If you have adopted the [OpenTelemetry tracing approach](https://dev.to/pwd9000/agentic-devops-needs-observability-trace-github-copilot-with-opentelemetry-405c) for Copilot, expect a HydraFusion request to look like one span until GitHub surfaces leg-level detail.

**Enterprise policy interaction is undocumented.** Auto model selection is documented to honour organisation model policies. HydraFusion has no entry in the supported models list or the models-and-pricing tables, and nothing states how it behaves when an administrator has disabled one of the models it might route to. If you run model allow-lists, that is the first question to put to your account team.

---

## Before vs Now

| Concern | Fixed model or Auto | HydraFusion (preview) |
| --- | --- | --- |
| Choosing a model per task | Manual, or Auto once per session | Runtime picks a workflow per request |
| Getting a second opinion | Manual `/rubber-duck` | Built into the Critique pattern, one revision |
| Paying for a strong model only when needed | Manual re-run with a different model | Cascade quality gate escalates automatically |
| Cost predictability | High | Lower; varies with route taken |
| Latency predictability | High | Lower; Cascade and Critique add legs |
| Visibility into intermediate work | Full | Final result only |
| Availability | GA everywhere | CLI, experimental, research preview |
| Vendor exposure per request | One | Potentially several, by design in Critique |

---

## Evaluating HydraFusion on Your Own Workload

The design below compares HydraFusion against two fixed models on a handful of representative tasks, records wall time and raw JSONL output, and applies a pass/fail check per task. It is deliberately modest: four tasks, three model configurations, two repetitions each is 24 runs, which is enough to see a pattern and cheap enough to actually finish.

### Prerequisites

- Copilot CLI 1.0.83 or later (`copilot version`), authenticated with `copilot login`.
- A disposable git repository with a real build and test command. Do not use a production repository; autopilot mode with `--yolo` approves tool calls without asking.
- Experimental mode enabled once interactively: `/experimental on`, then confirm HydraFusion appears in `/model`.
- A spending cap you are comfortable with. The harness passes `--max-ai-credits` per run.

### Choose tasks that match GitHub's guidance

Pick first-turn, single-prompt, verifiable tasks. Examples that have worked as evaluation prompts in my earlier model comparisons:

1. Add input validation and a unit test to a specific function.
2. Fix a failing test that you have deliberately broken.
3. Convert a callback-style module to async and keep the tests green.
4. Add structured logging to a CLI entry point with a documented format.
5. Write a GitHub Actions workflow that runs the test suite on pull requests with least-privilege permissions.

Each task needs a deterministic check: a test command that must pass, a file that must exist, or a lint rule that must be satisfied.

### The harness

The [evaluation harness](./code/Invoke-HydraFusionEval.ps1) in this article's code folder runs each task against each model configuration in a fresh git worktree, calls Copilot CLI non-interactively with JSONL output, captures wall time, runs your check command, and appends a row to a CSV. The core invocation looks like this:

```powershell
copilot -p $task.Prompt `
  --model $modelId `
  --yolo `
  --max-ai-credits $MaxCreditsPerRun `
  --output-format json `
  --log-level none `
  --no-color
```

Two honest caveats about that command:

- `--model` accepts a model identifier. The identifier HydraFusion uses in non-interactive mode is not documented as of 13 September 2026, and GitHub's published enablement path is the interactive `/model` picker. The harness takes the identifier as a parameter so you can supply whatever `/model` displays, and it records failures rather than guessing.
- Credits consumed per run are visible interactively via `/usage` and in the JSONL event stream. The harness records wall time and pass/fail for every run and stores the raw JSONL alongside so you can extract usage events once you have confirmed the field names your CLI version emits. Do not trust a cost column you have not verified against `/usage`.

Run it like this:

```powershell
./code/Invoke-HydraFusionEval.ps1 `
  -RepositoryPath 'C:\src\eval-lab' `
  -TasksPath './code/tasks.sample.json' `
  -ModelIds @('hydrafusion', 'claude-opus-5', 'gpt-5.6-sol') `
  -Repetitions 2 `
  -MaxCreditsPerRun 300 `
  -OutputCsv './hydrafusion-eval.csv'
```

The task file is a simple JSON array. A [sample](./code/tasks.sample.json) is included:

```json
[
  {
    "id": "validate-input",
    "prompt": "In src/orders.ts, add input validation to createOrder so that quantity must be a positive integer and customerId must be a non-empty string. Throw a ValidationError with a clear message. Add unit tests in tests/orders.test.ts covering both failure cases and one success case. Run the tests and make sure they pass.",
    "check": "npm test -- --runTestsByPath tests/orders.test.ts"
  }
]
```

### What to look at

Load the CSV and compare per model:

- **Pass rate** per task, not just overall. HydraFusion may win on some task types and lose on others; GitHub's own results say as much.
- **Wall time distribution.** Look at the spread, not the mean. A bimodal distribution for HydraFusion is the Cascade gate firing.
- **Credits per passing task**, once you have verified the usage figures against `/usage`. Credits per attempt rewards cheap failures.
- **Diff size and test changes.** Open a few diffs from each configuration. A Critique pass that removes a test to make it green is a failure your check command may not catch.

Record the model configurations, CLI version, and date. The preview will change under you and a result without provenance is not evidence.

---

## Security and Governance Considerations

The realistic threat model here is not new, but the routing changes some of the numbers.

- **Multiple vendors see your prompt.** The Critique pattern sends context to a critic from a different model family by design. If your data handling agreements distinguish between model providers, a single HydraFusion request may now touch more than one. GitHub's model policy and data handling terms still apply; check whether your organisation's exclusions are honoured before enabling it on sensitive repositories.
- **The critic cannot act.** Isolated, tool-less review is the right design. A prompt injection that reaches the critic can only influence text that the solver then chooses to act on. The solver still runs under the normal permission-aware agent loop, so your existing permission model and, for Business and Enterprise, the enterprise managed deny/ask/allow policies that went GA on 9 September, remain the effective controls.
- **Fail-safe application protects the working tree.** A cancelled or failed workflow applies no patch. That is materially better than a manual two-agent setup where the first agent's edits are already on disk when the second agent objects.
- **Budget caps are your circuit breaker.** Cascade escalations are the case where cost grows without you choosing it. `--max-ai-credits` on every non-interactive run is not optional in CI-adjacent use.
- **Autopilot plus `--yolo` is a high-trust configuration.** Use it only in disposable environments, which is also the environment GitHub recommends for evaluating the preview.

---

## Limitations and Gotchas

- **Copilot CLI only.** No VS Code, app, or cloud agent surface. The VS Code team is thanked in the announcement, which suggests intent, but nothing is committed.
- **Research preview.** Names, availability, and behaviour can change without notice. The label has already appeared as both "Research Preview" and "Preview".
- **Undisclosed model pool.** You cannot reason about data residency, provider mix, or retention from the documentation because the pool is not published.
- **No latency figures from GitHub.** The preview is explicitly intended to learn "how orchestration affects latency and cost in practice".
- **First-turn tasks only, for now.** Multi-turn is next on GitHub's list. Do not judge it on a long iterative session yet.
- **No leg-level telemetry exposed.** You see one result, not the route.
- **Sub-agent routing is not addressed.** A Hacker News commenter who uses Copilot CLI heavily pointed out that Auto only switches at session start or compaction and does not route sub-agents. Whether HydraFusion routes inside sub-agent calls is not documented.
- **Community verification is thin.** As of 13 September, there is one Hacker News thread with about twenty comments, a handful of hands-on blog posts, and no independent benchmark. The scepticism there is reasonable: adding software between a model and a harness can lift single-benchmark scores, and the claim that matters is whether the margin survives messy real repositories.

---

## Real-World Use Cases

1. **Batch code maintenance in autopilot.** Dependency upgrade fallout, lint sweeps, and deprecation fixes across a repository, where a cheap draft usually suffices and the gate escalates the awkward ones.
2. **Cost reduction for teams defaulting to a frontier model.** If your engineers run Opus 5 for everything, GitHub's figures suggest a large saving for similar quality on single-prompt tasks. Verify on your workload first.
3. **Refactors where a second opinion matters.** Migrations and interface changes are where the Critique pattern's independent reviewer earns its extra call.
4. **A baseline for your own router.** If you are building orchestration on the Copilot SDK, HydraFusion is a useful reference point for what the platform will offer natively, so you can focus your effort where it differs.
5. **Evaluation practice.** Even if you never adopt it, running the harness above against three configurations is a better way to choose your team's default model than reading benchmark tables.

---

## My Take

This is opinion, clearly labelled.

The direction is right and slightly overdue. Cascade and critique are the two orchestration patterns with the best evidence behind them, and moving them into the runtime with proper cost accounting and a fail-safe patch policy is exactly the kind of platform work individual teams should not be repeating. I would rather GitHub owned the bounded execution and isolated review guarantees than trust a hundred bespoke implementations.

The benchmark story is more modest than the headline. Winning one of three, matching on the others, and doing it at a third of the cost of Opus 5 is a genuinely good result. It is also a result against the most expensive comparator. Against a sensible mid-tier default, the saving is small and the quality gain is a couple of points. The honest pitch is "you no longer have to choose", not "67% cheaper".

What would make me adopt it beyond experiments: route-level visibility (which pattern ran, which models, what each leg cost), documented behaviour under enterprise model policies, and availability outside the CLI. Until then, it is a research preview that is worth an afternoon and a CSV, and worth watching closely, because runtime orchestration is where the next real gain in coding agents is likely to come from. GitHub says as much, and on that point I agree with them.

---

## Conclusion

- HydraFusion is a research preview in Copilot CLI, enabled with `/experimental on` and selected via `/model`, available on all Copilot plans and billed at standard token rates summed across legs.
- It chooses one of three execution patterns per request: Single, Cascade, or Critique, using a beam-searched policy built on capability signals.
- Five runtime principles matter operationally: complete accounting, bounded execution, isolated review, fail-safe application, and validated routing.
- GitHub's offline results show +4.9 points at 67% lower cost than Opus 5 on TerminalBench 2.1, and slightly lower quality at 36% to 65% lower cost on DeepSWE and CheckpointBench.
- The model pool, enterprise policy behaviour, latency profile, and leg-level telemetry are all undocumented today.
- Evaluate it on your own tasks with a spending cap, a deterministic check, and a fixed-model baseline before you change any defaults.

Choosing a model was never the interesting problem. Constructing the right amount of work for each task is, and HydraFusion is GitHub's first public attempt at solving it inside the product rather than leaving it to you.

---

## Sources

| Source | Type | Date checked | What it verifies |
| --- | --- | --- | --- |
| [Project HydraFusion: frontier quality via multi-model orchestration](https://github.blog/ai-and-ml/github-copilot/project-hydrafusion-frontier-quality-via-multi-model-orchestration/) | GitHub Blog (published 4 Sep 2026) | 13 Sep 2026 | Patterns, principles, benchmark table and chart data, caveats, enablement steps, plans, billing statement |
| [GitHub Copilot weekly releases: September 7](https://github.blog/changelog/2026-09-10-github-copilot-weekly-releases-september-7/) | GitHub Changelog | 13 Sep 2026 | HydraFusion in `/experimental`, CLI-only placement |
| [Rubber duck in Copilot CLI](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/rubber-duck) | GitHub Docs | 13 Sep 2026 | Critic runs on a different model family, read-only, adds latency |
| [Auto model selection](https://docs.github.com/copilot/concepts/models/auto-model-selection) | GitHub Docs | 13 Sep 2026 | Auto mechanics, 10% discount, honours model policies |
| [Supported AI models in Copilot](https://docs.github.com/en/copilot/reference/ai-models/supported-models) | GitHub Docs | 13 Sep 2026 | Current model list; no HydraFusion entry |
| [Models and pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing) | GitHub Docs | 13 Sep 2026 | Token-based AI credit billing, per-model rates, multipliers legacy only |
| [Copilot CLI command reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference) | GitHub Docs | 13 Sep 2026 | CLI commands and authentication options |
| [Copilot CLI releases](https://github.com/github/copilot-cli/releases) | GitHub repository | 13 Sep 2026 | CLI 1.0.83 dated 4 Sep 2026; `/usage` per-model credit breakdown |
| [VS Code 1.137 release notes](https://code.visualstudio.com/updates/v1_137) | Microsoft docs | 13 Sep 2026 | No HydraFusion availability in VS Code |
| [Hacker News discussion](https://news.ycombinator.com/item?id=49566788) | Community | 13 Sep 2026 | Developer sentiment, sub-agent routing concern, benchmark scepticism |
| [InfoQ: GitHub HydraFusion](https://www.infoq.com/news/2026/09/github-hydrafusion/) | Trade press | 13 Sep 2026 | Independent summary, plan and billing confirmation |
| [Hands-on: HydraFusion in Copilot CLI](https://www.stephenwthomas.com/artificial-intelligence/hydrafusion-github-copilot-cli/) | Practitioner blog | 13 Sep 2026 | Enablement restart, Cascade run duration and credits anecdote |

---

### _Author_

{% user pwd9000 %}

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [X](https://x.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-pwd9000/)

Date: 13-09-2026
