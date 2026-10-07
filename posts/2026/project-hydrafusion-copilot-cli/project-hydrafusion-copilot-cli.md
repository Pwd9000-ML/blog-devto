---
title: 'Project HydraFusion: GitHub Copilot Stops Picking a Model and Starts Building a Workflow'
published: false
description: 'HydraFusion runs Single, Cascade or Critique workflows across models in Copilot CLI, VS Code and the app. What the evidence says and how to test it.'
tags: 'githubcopilot, ai, devops, llm'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2026/project-hydrafusion-copilot-cli/assets/main.png'
canonical_url: null
id: 4644278
series: GitHub Copilot - CLI
date: '2026-10-07T16:30:00Z'
---

## Project HydraFusion: GitHub Copilot Stops Picking a Model and Starts Building a Workflow

For the last year, the most consequential decision in a Copilot session has been the model picker. Opus for the hard refactor, a cheaper GPT for the boilerplate, Auto when you could not be bothered. Auto model selection makes that decision for you, one model per request, and gives you a 10% discount for trusting it.

On 4 September 2026 GitHub published [Project HydraFusion](https://github.blog/ai-and-ml/github-copilot/project-hydrafusion-frontier-quality-via-multi-model-orchestration/), a research preview that changes the unit of decision. Instead of choosing a model, the runtime builds an execution plan per prompt: one model solves it directly, or a cheap model drafts and a quality gate decides whether to escalate, or one model drafts and a read-only critic from a different model family reviews it before a single revision. It launched in Copilot CLI and, [on 30 September](https://github.blog/changelog/2026-09-30-hydrafusion-in-vs-code-and-the-github-copilot-app/), reached VS Code and the GitHub Copilot app. GitHub's headline number is 67% lower estimated cost than Claude Opus 5 with higher verified quality on TerminalBench 2.1.

That headline deserves the scrutiny this article gives it. But the more durable story is architectural. Teams have been hand-rolling draft-then-critique and cheap-then-escalate patterns in their own agent code for eighteen months. HydraFusion moves those patterns into the Copilot runtime, with cost accounting per leg, bounded execution, and isolated review. That is what a DevOps engineer should evaluate, and this article gives you a way to do it on your own workload.

If you want the CLI fundamentals first, my [Copilot CLI practical guide](https://dev.to/pwd9000/github-copilot-cli-a-devops-engineers-practical-guide-to-ai-powered-terminal-automation-1jh0) and [evaluating LLM models in Copilot](https://dev.to/pwd9000/evaluating-llm-models-in-github-copilot-a-practical-scoring-and-assessment-guide-1f23) cover the ground this post builds on.

> **Evidence boundary:** this article reflects GitHub's documentation and changelog as of 7 October 2026. HydraFusion is a research preview with no SLA, and GitHub's documentation says it "isn't intended for production workloads". Every benchmark figure below is GitHub's own offline result, quoted with its caveats. I have not benchmarked HydraFusion. I did run a two-prompt smoke test on Copilot CLI 1.0.89 to confirm the headless invocation, the usage file, and the event stream that the evaluation harness relies on. Those results are labelled where they appear and say nothing about quality.

---

## What Changed

**Status:** research preview. The [HydraFusion documentation](https://docs.github.com/en/early-access/copilot/hydrafusion) is explicit: "there's no service level agreement (SLA), and HydraFusion isn't intended for production workloads."

**Surfaces:** Copilot CLI since 4 September, behind experimental mode. Since 30 September, also [VS Code 1.140](https://code.visualstudio.com/updates/v1_140) or later (or VS Code Insiders) and the GitHub Copilot app. The documentation lists only those three surfaces, so Copilot cloud agent, JetBrains IDEs, Visual Studio, and Copilot Chat on github.com are not included.

**Plans:** this is where the sources disagree. The launch post and the original community announcement say HydraFusion is available "on all GitHub Copilot plans". The 30 September changelog says it "is available to Copilot Pro, Pro+, Business, and Enterprise users" and that "for Copilot Business and Enterprise, an administrator must enable preview features". The documentation adds that HydraFusion only uses models that your plan includes and your policies allow, and does not appear in the picker if none qualify. If your plan is not on the changelog's list, check the picker rather than assuming either way.

**Billing:** from the documentation, "you're billed for each model it uses, at that model's standard rate. There's no separate charge for HydraFusion, and the discount for auto model selection doesn't apply." Since [1 June 2026](https://github.blog/changelog/2026-06-01-updates-to-github-copilot-billing-and-plans/), all Copilot plans bill in AI credits (1 credit = $0.01) based on tokens per model, so a HydraFusion request costs the sum of every leg it runs. Model multipliers survive only for legacy annual plans on request-based billing. The documentation also says HydraFusion "keeps your main conversation on the same model whenever possible" to keep the benefit of cached tokens, and that assisting models such as a reviewer "receive only the context they need".

**Enablement:**

| Surface | Steps |
| --- | --- |
| Copilot CLI | Run `copilot update`, start with `copilot --experimental` (or enter `/experimental on` and restart), then enter `/model` and select **HydraFusion (Research Preview)** |
| Copilot CLI, headless | `copilot --experimental --model hydrafusion -p "YOUR-PROMPT"` |
| VS Code 1.140 or later | Turn on `chat.copilot.hydraFusion.enabled`, then select **HydraFusion** in the Chat model picker |
| GitHub Copilot app | Update, open **Settings** > **Experimental**, turn on **HydraFusion**, then select it in the model picker |

If HydraFusion does not appear in the CLI picker, the documentation suggests switching to the prerelease channel with `/update prerelease`. In an organisation, ask whether preview features are enabled for you. The new [default enablement policy](https://github.blog/changelog/2026-09-24-default-enablement-of-copilot-features-for-copilot-business-and-enterprise/) that takes effect on 22 October does not change that, because "preview features remain opt-in".

**Scope guidance from GitHub:** unchanged since launch. "First-turn, single-prompt coding tasks are the best place to start", ideally "substantial, well-scoped coding tasks that you can hand to Copilot in autopilot mode in a single prompt". Multi-turn performance is explicitly the next focus. The documentation now frames the choice plainly: use Auto for everyday work, and HydraFusion for tasks "such as fixing a complex bug or making a change across several files, where additional model passes may be worth the extra time and AI credits".

### Timeline

| Date | What happened |
| --- | --- |
| 16 May 2026 | The [HyDRA](https://arxiv.org/abs/2605.17106) routing paper is published; its capability-scoring router is deployed in Auto for VS Code Chat |
| 4 Sep 2026 | HydraFusion announced as a research preview in Copilot CLI, behind experimental mode |
| Week of 14 Sep 2026 | Auto model selection starts rolling out Efficiency, Balance, and Intelligence tiers |
| 22 to 29 Sep 2026 | Claude Opus 5.5, GPT-6 Sol, GPT-6 Luna, Claude Sonnet 5.5, and GPT-6.1 Sol arrive in Copilot |
| 30 Sep 2026 | HydraFusion reaches VS Code 1.140 and the Copilot app, with step-by-step progress updates |
| 1 Oct 2026 | Dynamic workflows, code-defined orchestration, enter public preview in Copilot CLI, the app, and the SDK |

---

## How It Works

GitHub describes HydraFusion as treating "workflow selection as an optimization problem". Per prompt, it scores the task on capability signals (reasoning, code generation, debugging, tool use) and picks "the least complex workflow expected to meet its needs, using additional model calls only when they are likely to improve the result".

### The three execution patterns

| Pattern | Mechanism (GitHub's description) | When it makes sense |
| --- | --- | --- |
| **Single** | One selected model solves the task directly. | The task is well within a single model's capability; adds no overhead. |
| **Cascade** | An efficient model drafts a solution and a quality gate decides whether to accept it or escalate to a stronger model. | Most tasks are easy, some are not, and you would rather pay for the strong model only on the hard ones. |
| **Critique** | One model drafts a result, an independent read-only critic from a different model family reviews it, and the drafting model revises once. | Tasks where a second opinion catches more than a second attempt would. |

The Critique pattern follows the same approach as [Rubber Duck](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/rubber-duck) in Copilot CLI, which GitHub documents as deliberately running "on a different AI model from the one driving your session", with "read-only access to your codebase" so that it "cannot edit files or run commands that change your environment". HydraFusion automates that invocation and bounds it to one revision.

### What the documentation adds

The HydraFusion documentation fills in several behaviours that the launch post left open:

- **Per-prompt choice.** "HydraFusion chooses an execution pattern for each prompt, so different prompts in the same session can use different execution patterns." Choosing is "a lightweight step that adds little time". In my smoke test, the routing event reported 251 milliseconds.
- **No fixed model list.** The mix of models changes over time, "so there isn't a fixed list of models", and "You can't choose which models HydraFusion uses."
- **A conservative context window.** HydraFusion "doesn't have a context window of its own". The value shown is "based on the smallest limits among the models it uses", so you may be asked to compact a long conversation before you switch to it.
- **Final response only.** You can follow each step while it runs, but "intermediate drafts might be revised or discarded, so HydraFusion only shows you the final response."

### The five operating principles

These are the part of the announcement most worth reading twice, because they describe the runtime guarantees rather than the marketing. Quoted from GitHub:

- **Complete accounting.** "Aggregate cost and usage across every workflow leg, including drafting, critique, revision, escalation, retry, and fallback."
- **Bounded execution.** "Give each leg explicit timeout and cancellation behavior to keep execution and cost within defined limits."
- **Isolated review.** "Run review steps in isolated, tool-less contexts, while solver steps use the shared workspace and normal permission-aware agent loop."
- **Fail-safe application.** "Apply no patch when the workflow is cancelled or fails validation, preventing incomplete changes from reaching the repository."
- **Validated routing.** "Verify workflow definitions, model bindings, fallback behavior, and model availability before execution begins."

Two of these matter more than the others for operations, and one needs a caveat. **Isolated review** means the critic never touches your workspace and never has tools, which is the correct trust boundary for a step whose only job is to disagree. **Fail-safe application** is the caveat. The blog describes applying "no patch when the workflow is cancelled or fails validation", but the limitations section of the product documentation says: "If HydraFusion discards a draft, changes that the draft already made in your workspace, such as file edits, aren't undone automatically." Solver legs run in the shared workspace, so read the principle as _HydraFusion will not knowingly finish on a failed result_, not _your working tree is protected_. Review the diff before you commit, as you would with any agent.

### How the routing policy was built

GitHub did not hand-tune thresholds. The blog describes using beam search to construct the decision policy, measuring each candidate "against a frozen baseline on quality, cost, and failure modes" across TerminalBench 2.1, DeepSWE, and an internal benchmark called CheckpointBench. The hill-climbing record they publish is refreshingly honest: two harness failures between 11 and 25 August produced invalid runs that were excluded, and the strongest configurations arrived on 25 August.

### Where it came from, and what is in the pool

The lineage is now on the record. In the [GitHub Community announcement](https://github.com/orgs/community/discussions/206492), a GitHub maintainer sets out the progression: "Auto V1 (Jan 2026, capacity/SKU-aware per-request selection) → Auto V2 aka. HyDRA (May 2026, intent-scored routing) → HydraFusion (Aug 2026, per-turn orchestration and cache-aware workflows)." The [HyDRA paper](https://arxiv.org/abs/2605.17106) describes a ModernBERT encoder that scores each query on reasoning, code generation, debugging, and tool use, the same four capability signals GitHub cites for HydraFusion. It states that HyDRA "is deployed to all users in GitHub Copilot's VS Code Chat auto-mode", and its first author, Aashna Garg, is also credited on the HydraFusion post. Community write-ups that linked HydraFusion to a routing research paper were right: HydraFusion builds on the router behind Auto and adds multi-model workflows on top.

The model pool is still not published, and that is now a stated policy. The same FAQ says "we don't publish a fixed roster" because "the lineup shifts as new models ship", and adds: "We know some teams need more control here and we're looking into it." The benchmark charts compare HydraFusion with Claude Opus 5, Claude Sonnet 5, and GPT-5.6 Sol, Terra, and Luna as solo models. Those are comparators, not a disclosed pool, and they are now a generation old: Claude Opus 5.5, GPT-6 Sol, GPT-6 Luna, Claude Sonnet 5.5, and GPT-6.1 Sol all arrived in Copilot between 22 and 29 September. GitHub says new models can be evaluated and incorporated "into its model pool", but not when. In the feedback discussion, users reported between 2 and 5 October that HydraFusion was routing to GPT-5.6 Terra and GPT-5.4 rather than the newer GPT-6 family, and one wrote: "This is the main reason I've stopped using HydraFusion for now." That is anecdote, but it is the right question to put to any router.

### HydraFusion vs Auto model selection

|  | Auto model selection | HydraFusion |
| --- | --- | --- |
| Status | GA in Copilot Chat (github.com and supported IDEs), CLI, Copilot app, and cloud agent | Research preview in CLI, VS Code 1.140 or later, and the Copilot app; no SLA |
| Unit of decision | One model per request, re-routed along natural cache boundaries and large shifts in complexity | One execution pattern per prompt, potentially several models within a turn |
| Mechanism | Task complexity plus real-time model health; Efficiency, Balance, and Intelligence tiers in VS Code, CLI, and the app | Capability signals selecting Single, Cascade, or Critique |
| Pricing | Selected model's rate, with a 10% discount on paid plans | Each model's standard rate, summed across legs; no discount |
| Admin model policies | Honoured, documented | Honoured, documented; hidden from the picker if no allowed model qualifies |
| Choose the models yourself | No | No |
| See which model ran | Per response (hover, terminal, or end of response) | CLI progress display; hover in VS Code and the app |

GitHub's own FAQ puts the difference in one line: "Auto picks the optimal model; HydraFusion picks the optimal workflow, possibly using multiple models." It also says "we expect them to come together into a single experience over time." Mario Rodriguez, GitHub's Chief Product Officer, told [VentureBeat](https://venturebeat.com/orchestration/githubs-hydrafusion-cuts-ai-coding-costs-in-every-benchmark-it-only-matches-quality-in-one) that GitHub is "evaluating the possibility of converging HydraFusion into Auto". If you write team guidance today, cover both and expect to rewrite it.

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
2. **The interesting comparison is often GPT-5.6 Sol, not Opus.** On TerminalBench, HydraFusion costs the same as Sol and scores 11.4 points higher. On DeepSWE and CheckpointBench it costs 12.5% and 13.3% more than Sol for 2.2 and 1.4 points more quality. If your team already defaults to a mid-tier model, the cost saving versus your baseline is much smaller than 67%.
3. **TerminalBench 2.1 is described by GitHub itself as relatively saturated**, which is why the harder repository-level DeepSWE matters more, and that is where the margin is thinnest.
4. **CheckpointBench is internal.** GitHub describes it as a multi-turn benchmark curated from real Copilot sessions. Its chart breaks the 276 checkpoints down as 116 easy, 107 medium, and 53 hard, led by Python (92) and TypeScript (48), and dominated by bug fixes (90) and feature implementation (73). You cannot reproduce it.
5. **These are offline, best-tuned configuration, medium reasoning, and pricing-assumption specific.** GitHub says so directly. The research preview exists to find out whether the results survive contact with real developer workloads.
6. **The comparators have moved on.** Every number above predates Claude Opus 5.5, GPT-6 Sol, and GPT-6.1 Sol. "Cheaper than Opus 5" says little about cost against whatever your team adopted at the end of September.

None of this is a criticism of GitHub's transparency, which is better than most model announcements. It is a reason to run your own numbers.

---

## Why DevOps Engineers Should Care

**Cost variance becomes a workflow property.** With a fixed model, cost per task scales roughly with task size. With Cascade, the same prompt can cost a cheap draft or a cheap draft plus a strong-model escalation depending on whether the quality gate fires. With Critique it is always at least two model calls plus a revision. Budget controls need to move from "which model" to "what is the cap per task", which Copilot CLI supports with `--max-ai-credits`. Note the floor: CLI 1.0.89 rejects anything below 30 credits.

**Latency becomes multi-modal.** The documentation says it plainly: "The Single execution pattern behaves much like a request to one model. Cascade and Critique take longer, because they include review passes." Choosing the pattern is cheap. One early hands-on report describes a Cascade run of three to four minutes for a single prompt. That is fine for a task you hand off in autopilot; it is not fine for an interactive loop. GitHub's guidance to start with substantial, well-scoped single-prompt tasks is a latency statement as much as a quality one.

**Visibility is better than at launch, but it is not yet operational telemetry.** At launch you mostly saw the final answer, and the feedback discussion filled with requests to see what was happening. The CLI now shows the chosen pattern, each planned pass with its status, what the current pass is doing, and the elapsed time, and keeps a summary in the conversation afterwards. VS Code and the app show which models were used when you hover over a response. For bug reports, `/collect-debug-logs` captures "the execution pattern and the models used for each step".

Headless runs go further than the documentation does. With `--output-format json`, CLI 1.0.89 emitted `session.fusion_resolved`, `assistant.fusion_phase_started`, `assistant.fusion_phase_completed`, and `session.fusion_completed` events in my smoke test. Between them they carry the pattern, each phase's model and role, its duration, and its token and credit usage. None of that schema is documented, so build on it the way the harness below does: record what is present and tolerate its absence. If you use the [OpenTelemetry tracing approach](https://dev.to/pwd9000/agentic-devops-needs-observability-trace-github-copilot-with-opentelemetry-405c), nothing in GitHub's documentation says whether HydraFusion legs appear as separate spans, so check your own collector before you rely on it.

**Enterprise policy behaviour is documented now; data handling less so.** HydraFusion "only uses models that are available in your plan and allowed by your organization's or enterprise's model policies", and it does not appear at all if none qualify. That answers the most common admin question from launch. It does not answer the follow-up a user posted in the feedback discussion on 23 September: whether usage across critic, fallback, and escalation legs is "covered by existing data processing agreements". I found no HydraFusion-specific statement or staff reply on that point. If it matters to you, ask your account team before you enable preview features.

---

## Before vs Now

| Concern | Fixed model or Auto | HydraFusion (preview) |
| --- | --- | --- |
| Choosing a model per task | Manual, or Auto per request | Runtime picks a workflow per prompt |
| Getting a second opinion | Manual `/rubber-duck` | Built into the Critique pattern, one revision |
| Paying for a strong model only when needed | Manual re-run, or Auto routing | Cascade quality gate escalates automatically |
| Cost predictability | High | Lower; varies with route taken |
| Latency predictability | High | Lower; Cascade and Critique add passes |
| Visibility into intermediate work | Full | Pattern, passes, and models shown; drafts hidden |
| Control over models | Full with a fixed model, none with Auto | None beyond your model policies |
| Availability | GA everywhere | CLI, VS Code 1.140 or later, Copilot app; research preview |
| Vendor exposure per request | One | Potentially several, by design in Critique |

---

## Evaluating HydraFusion on Your Own Workload

The design below compares HydraFusion against two fixed models on a handful of representative tasks, records wall time, AI credits, the models that actually ran, and the HydraFusion pattern, and applies a pass/fail check per task. It is deliberately modest: four tasks, three model configurations, two repetitions each is 24 runs, which is enough to see a pattern and cheap enough to actually finish.

### Prerequisites

- Copilot CLI 1.0.89 or later (`copilot version`), authenticated with `copilot login`. I tested the invocation on 1.0.89; [1.0.92](https://github.com/github/copilot-cli/releases/tag/v1.0.92) is the current stable release.
- A disposable git repository with a real build and test command. Do not use a production repository; `--yolo` approves every tool call without asking.
- HydraFusion visible to you: start `copilot --experimental` once interactively and confirm **HydraFusion (Research Preview)** appears in `/model`. The harness then passes `--experimental` itself for HydraFusion runs only, so the fixed-model baselines run without experimental features.
- A spending cap you are comfortable with. The harness passes `--max-ai-credits` per run, and the CLI requires at least 30.

### Choose tasks that match GitHub's guidance

Pick first-turn, single-prompt, verifiable tasks. Examples that have worked as evaluation prompts in my earlier model comparisons:

1. Add input validation and a unit test to a specific function.
2. Fix a failing test that you have deliberately broken.
3. Convert a callback-style module to async and keep the tests green.
4. Add structured logging to a CLI entry point with a documented format.
5. Write a GitHub Actions workflow that runs the test suite on pull requests with least-privilege permissions.

Each task needs a deterministic check: a test command that must pass, a file that must exist, or a lint rule that must be satisfied.

### The harness

The [evaluation harness](./code/Invoke-HydraFusionEval.ps1) in this article's code folder runs each task against each model configuration in a fresh git worktree. It calls Copilot CLI non-interactively with JSONL output and a usage file, captures wall time, runs your check command, and appends a row to a CSV with the credits used, the models that ran, and, for HydraFusion, the execution pattern. The core HydraFusion invocation looks like this:

```powershell
copilot --experimental `
  -p $task.prompt `
  --model hydrafusion `
  --yolo `
  --no-ask-user `
  --max-ai-credits $MaxCreditsPerRun `
  --usage-output-file $usagePath `
  --output-format json `
  --log-level none `
  --no-color
```

Fixed-model runs use the same options without `--experimental`. What the harness reads, and how far to trust it:

- **The model identifier is documented.** `copilot --experimental --model hydrafusion -p` is GitHub's documented headless path. On CLI 1.0.89 it exited cleanly and emitted HydraFusion events in the JSONL stream. Other identifiers follow the names in `/model`; I confirmed `gpt-5.6-sol` and `gpt-5.6-luna` in the same test.
- **Credits come from the usage file, and its schema is not documented.** `--usage-output-file` writes "final usage statistics as JSON". In CLI 1.0.89 that file contains a `totalNanoAiu` field and a per-model `modelMetrics` map. I checked the unit against GitHub's published GPT-5.6 Sol rates: 15,015 cache-write tokens at $5.00 per million, plus 3 input and 5 output tokens, comes to $0.0752, and the file reported 7,518,700,000. Credits are therefore `totalNanoAiu / 1e9`. Spot-check against `/usage` before you publish a cost comparison.
- **The pattern comes from undocumented events.** The harness reads `pattern` and `outcome` from `session.fusion_completed`. If a future CLI renames them, those columns stay empty rather than wrong.

> **Smoke test, not a benchmark.** On 7 October I sent the same one-word prompt ("Reply with the single word OK. Do not use any tools.") through CLI 1.0.89 twice. HydraFusion chose Single on `gpt-5.6-sol` and used 7.52 credits in 10.7 seconds. Running `gpt-5.6-luna` directly used 0.37 credits in 8.3 seconds. Both runs wrote about 15,000 tokens to the prompt cache; the difference is the per-token rate of the model HydraFusion chose. This says nothing about quality on real tasks. It does show why the documentation says "for quick or routine tasks, select **Auto** instead".

Run it like this:

```powershell
./code/Invoke-HydraFusionEval.ps1 `
  -RepositoryPath 'C:\src\eval-lab' `
  -TasksPath './code/tasks.sample.json' `
  -ModelIds @('hydrafusion', 'gpt-5.6-sol', 'claude-opus-5') `
  -Repetitions 2 `
  -MaxCreditsPerRun 300 `
  -OutputCsv './hydrafusion-eval.csv' `
  -TrustTaskFile
```

Swap the fixed models for your team's current default. GitHub's benchmarks used GPT-5.6 Sol and Claude Opus 5, which keeps your results comparable with theirs, but the newer GPT-6 and Claude 5.5 models are the more useful baseline for a decision today.

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
- **Pattern mix per task.** The `FusionPatterns` column shows whether HydraFusion chose Single, Cascade, or Critique, so you no longer have to infer escalations from a bimodal wall-time distribution.
- **Credits per passing task.** The summary calculates it when every run produced a usage file. Credits per attempt rewards cheap failures.
- **Models that actually ran.** `ModelsUsed` lists every model in the usage file. If HydraFusion keeps choosing models older than your team's default, you want to know that before you adopt it.
- **Diff size and test changes.** Open a few diffs from each configuration. A Critique pass that removes a test to make it green is a failure your check command may not catch. Discarded drafts do not roll back their edits, so look at the whole worktree, not just the final answer.

Record the model configurations, CLI version, and date. The preview will change under you and a result without provenance is not evidence.

---

## Security and Governance Considerations

The realistic threat model here is not new, but the routing changes some of the numbers.

- **Multiple vendors see your prompt.** The Critique pattern sends context to a critic from a different model family by design, although the documentation says assisting models "receive only the context they need". HydraFusion honours your model policies, so a model you have disabled is not used. If your data handling agreements distinguish between model providers, your allow-list is now the control that matters, because one request may touch more than one provider.
- **The critic cannot act.** Isolated, tool-less review is the right design. A prompt injection that reaches the critic can only influence text that the solver then chooses to act on. The solver still runs under the normal permission-aware agent loop, so your existing permission model and, for Business and Enterprise, the [enterprise managed permissions](https://github.blog/changelog/2026-09-09-enterprise-managed-permissions-for-github-copilot-agent-operations/) that went GA on 9 September, remain the effective controls.
- **Do not count on fail-safe application to clean up.** The documentation says edits made by a discarded draft "aren't undone automatically". Run HydraFusion on a branch or a disposable worktree and review the diff before you commit. That is the same discipline as any agent, but it is a less comfortable reading than the launch post suggests.
- **Budget caps are your circuit breaker.** Cascade escalations are the case where cost grows without you choosing it. Use `--max-ai-credits` on every non-interactive run; it is not optional in CI-adjacent use. For teams, user-level budgets and the budget increase requests that went GA for Business and Enterprise in September give administrators an approval step when someone hits a limit.
- **Preview access is a clean gate.** For Business and Enterprise, an administrator must enable preview features, and the default enablement policy that starts on 22 October leaves previews opt-in. Pilot HydraFusion in one organisation rather than enabling it everywhere.
- **Autopilot plus `--yolo` is a high-trust configuration.** Use it only in disposable environments. GitHub's statement that the preview "isn't intended for production workloads" points the same way.

---

## Limitations and Gotchas

- **Three surfaces only.** Copilot CLI, VS Code 1.140 or later, and the Copilot app. Not cloud agent, JetBrains IDEs, Visual Studio, or Copilot Chat on github.com.
- **Research preview, no SLA.** Names, availability, and behaviour can change without notice. The CLI picker says "HydraFusion (Research Preview)"; VS Code and the app just say "HydraFusion".
- **No control over the pool.** You cannot choose or exclude models beyond your policy allow-list, and there is no fixed list. Community reports suggest new models are not picked up immediately.
- **No latency figures from GitHub.** The preview is explicitly intended to learn "how orchestration affects latency and cost in practice".
- **First-turn tasks are still the sweet spot.** Multi-turn is next on GitHub's list. Patterns are chosen per prompt, so a long session can mix them, but do not judge HydraFusion on a long iterative session yet.
- **No sub-agents.** "HydraFusion works separately from subagents and doesn't start them", so sub-agent work is not orchestrated by it. If your sessions are sub-agent heavy, a large share of the work sits outside HydraFusion's routing.
- **Discarded drafts leave edits behind.** Covered above, and worth repeating because it is easy to miss.
- **A conservative context window.** The window shown is the smallest among the models HydraFusion uses, so switching to it mid-session may force a compaction.
- **Undocumented telemetry schema.** The progress display and debug logs are documented. The JSONL event fields and usage file fields that make automation possible are not.
- **Community verification is still thin.** As of 7 October, the [Hacker News thread](https://news.ycombinator.com/item?id=49566788) has 35 comments, the GitHub feedback discussion has about two dozen, and I found no independent benchmark. The reports pull in both directions: one user found "the credits burn has been 10% of what I'm used to" compared with running every session on Opus 5, while another spent around 2,300 credits on an implementation they expected to cost 1,800. The scepticism on Hacker News remains reasonable: adding software between a model and a harness can lift single-benchmark scores, and the claim that matters is whether the margin survives messy real repositories.

---

## Real-World Use Cases

1. **Batch code maintenance in autopilot.** Dependency upgrade fallout, lint sweeps, and deprecation fixes across a repository, where a cheap draft usually suffices and the gate escalates the awkward ones.
2. **Cost reduction for teams defaulting to a frontier model.** If your engineers run Opus 5 for everything, GitHub's figures suggest a large saving for similar quality on single-prompt tasks. Verify on your workload first, and against the newer models as well.
3. **Refactors where a second opinion matters.** Migrations and interface changes are where the Critique pattern's independent reviewer earns its extra call.
4. **Choosing between runtime and code-defined orchestration.** Since 1 October, [dynamic workflows](https://github.blog/changelog/2026-10-01-dynamic-workflows-in-copilot-cli-and-the-copilot-app/) let you define an orchestration in code inside a Copilot extension, in Copilot CLI, the app, and the SDK. One of GitHub's examples asks two models whether old review comments still matter and reports only when both agree. Use HydraFusion when you want the runtime to decide how much work a task needs. Use a dynamic workflow when you need the same steps every time, checkpoints for a human, and a process you can review in a pull request.
5. **Evaluation practice.** Even if you never adopt it, running the harness above against three configurations is a better way to choose your team's default model than reading benchmark tables.

---

## My Take

This is opinion, clearly labelled.

The direction is right, and the month since launch has made it more credible, not less. In September I would have listed three blockers: no visibility of the route, undocumented behaviour under enterprise model policies, and CLI-only availability. GitHub has addressed all three to a useful degree. The CLI shows the pattern and each pass, model policies are documented and honoured, and VS Code and the app have it. That is a fast response to feedback for a research preview, and it suggests GitHub is treating runtime orchestration as product direction rather than a demo.

The benchmark story is still more modest than the headline. Winning one of three, matching on the others, and doing it at a third of the cost of Opus 5 is a genuinely good result against the most expensive comparator. Against a sensible mid-tier default the saving is small, and the comparators are now a generation behind. The honest pitch remains "you no longer have to choose", not "67% cheaper".

What still stops me recommending it as a team default: no control over the pool, reports that it lags new models, an undocumented telemetry schema, and the gap between "apply no patch" in the blog and "aren't undone automatically" in the documentation. That last one is not a bug, it is how solver legs in a shared workspace behave, but it deserves the same prominence as the principle.

I expect HydraFusion to stop being a separate picker entry, because GitHub has said it expects Auto and HydraFusion to "come together into a single experience over time". When that happens, the habits in this article (a fixed baseline, a deterministic check, credits per passing task, and a record of which models actually ran) are what will tell you whether the merged Auto is good for your workload. Build them now, while you can still compare the two side by side.

---

## Conclusion

- HydraFusion is a research preview with no SLA, available in Copilot CLI, VS Code 1.140 or later, and the Copilot app. In the CLI, start with `--experimental` and select it in `/model`, or run it headless with `--model hydrafusion`.
- It chooses Single, Cascade, or Critique per prompt, using capability signals that descend from the HyDRA router behind Auto.
- Billing is each model's standard rate summed across legs, with no Auto discount.
- Model policies are honoured, sub-agents are out of scope, and discarded drafts do not roll back their edits.
- GitHub's offline results show +4.9 points at 67% lower cost than Opus 5 on TerminalBench 2.1, and slightly lower quality at 36% to 65% lower cost on DeepSWE and CheckpointBench, all against models that have since been superseded.
- The model pool, latency profile, and telemetry schema remain undocumented, but the CLI's JSONL output and `--usage-output-file` give you enough to measure it yourself.
- Evaluate it on your own tasks with a spending cap, a deterministic check, and a fixed-model baseline before you change any defaults.

Choosing a model was never the interesting problem. Constructing the right amount of work for each task is, and HydraFusion is GitHub's first public attempt at solving it inside the product rather than leaving it to you.

---

## Sources

| Source | Type | Date checked | What it verifies |
| --- | --- | --- | --- |
| [Project HydraFusion: frontier quality via multi-model orchestration](https://github.blog/ai-and-ml/github-copilot/project-hydrafusion-frontier-quality-via-multi-model-orchestration/) | GitHub Blog (published 4 Sep 2026) | 7 Oct 2026 | Patterns, principles, benchmark table and embedded chart data, CheckpointBench breakdown, caveats, launch plans and billing statement |
| [Using HydraFusion](https://docs.github.com/en/early-access/copilot/hydrafusion) | GitHub Docs | 7 Oct 2026 | No SLA, surfaces, enablement, `--model hydrafusion`, billing, policies, progress display, `/collect-debug-logs`, limitations |
| [HydraFusion in VS Code and the GitHub Copilot app](https://github.blog/changelog/2026-09-30-hydrafusion-in-vs-code-and-the-github-copilot-app/) | GitHub Changelog (30 Sep 2026) | 7 Oct 2026 | VS Code and app availability, eligible plans, admin preview opt-in, progress improvements |
| [GitHub Copilot weekly releases: September 7](https://github.blog/changelog/2026-09-10-github-copilot-weekly-releases-september-7/) | GitHub Changelog | 7 Oct 2026 | Original CLI `/experimental` rollout |
| [HydraFusion feedback discussion](https://github.com/orgs/community/discussions/206492) | GitHub Community (maintainer post and replies) | 7 Oct 2026 | Auto to HyDRA to HydraFusion lineage, no fixed roster, convergence with Auto, user reports on cost and model choice |
| [HyDRA: Hybrid Dynamic Routing Architecture for Heterogeneous LLM Pools](https://arxiv.org/abs/2605.17106) | Research paper (arXiv, May 2026) | 7 Oct 2026 | Capability signals, deployment in VS Code Chat Auto |
| [VS Code 1.140 release notes](https://code.visualstudio.com/updates/v1_140) | Microsoft (30 Sep 2026) | 7 Oct 2026 | HydraFusion research preview in VS Code |
| [GitHub Copilot in VS Code, September 2026 releases](https://github.blog/changelog/2026-10-01-github-copilot-in-vs-code-september-2026-releases/) | GitHub Changelog | 7 Oct 2026 | HydraFusion in the Agents window model picker |
| [Auto model selection](https://docs.github.com/en/copilot/concepts/models/auto-model-selection) | GitHub Docs | 7 Oct 2026 | Per-request routing at cache boundaries, tiers, 10% discount, honours model policies |
| [GitHub Copilot weekly releases: September 14](https://github.blog/changelog/2026-09-18-github-copilot-weekly-releases-september-14/) | GitHub Changelog | 7 Oct 2026 | Auto tiers, budget increase requests GA |
| [GitHub Copilot weekly releases: September 21](https://github.blog/changelog/2026-09-25-github-copilot-weekly-releases-september-21/) | GitHub Changelog | 7 Oct 2026 | Claude Opus 5.5, GPT-6 Sol, GPT-6 Luna availability |
| [Claude Sonnet 5.5 in GitHub Copilot](https://github.blog/changelog/2026-09-28-claude-sonnet-5-5-in-github-copilot/) and [GPT-6.1 Sol in GitHub Copilot](https://github.blog/changelog/2026-09-29-gpt-6-1-sol-in-github-copilot/) | GitHub Changelog | 7 Oct 2026 | Newer models released after the benchmarks |
| [Dynamic workflows in Copilot CLI and the Copilot app](https://github.blog/changelog/2026-10-01-dynamic-workflows-in-copilot-cli-and-the-copilot-app/) | GitHub Changelog (1 Oct 2026) | 7 Oct 2026 | Code-defined orchestration, public preview |
| [Default enablement of Copilot features](https://github.blog/changelog/2026-09-24-default-enablement-of-copilot-features-for-copilot-business-and-enterprise/) | GitHub Changelog | 7 Oct 2026 | 22 October policy date, previews remain opt-in |
| [Enterprise managed permissions for Copilot agent operations](https://github.blog/changelog/2026-09-09-enterprise-managed-permissions-for-github-copilot-agent-operations/) | GitHub Changelog | 7 Oct 2026 | Managed permissions GA on 9 September |
| [Rubber duck in Copilot CLI](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/rubber-duck) | GitHub Docs | 7 Oct 2026 | Critic runs on a different model, read-only, cannot change the environment |
| [Supported AI models in Copilot](https://docs.github.com/en/copilot/reference/ai-models/supported-models) | GitHub Docs | 7 Oct 2026 | Current model list and release status |
| [Models and pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing) | GitHub Docs | 7 Oct 2026 | AI credit billing, GPT-5.6 Sol and Luna per-token rates, multipliers legacy only |
| [Updates to GitHub Copilot billing and plans](https://github.blog/changelog/2026-06-01-updates-to-github-copilot-billing-and-plans/) | GitHub Changelog (1 Jun 2026) | 7 Oct 2026 | Usage-based billing for all plans |
| [Copilot CLI programmatic reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-programmatic-reference) and [command reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference) | GitHub Docs | 7 Oct 2026 | `-p`, `--model`, `--yolo`, `--output-format json`, `copilot version`, `copilot login` |
| [Set a session limit](https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/set-session-limit) | GitHub Docs | 7 Oct 2026 | `--max-ai-credits` |
| [Copilot CLI releases](https://github.com/github/copilot-cli/releases) | GitHub repository | 7 Oct 2026 | 1.0.92 current stable (5 Oct 2026) |
| Copilot CLI 1.0.89 `copilot --help` and smoke test | Local test (7 Oct 2026) | 7 Oct 2026 | `--usage-output-file`, `--log-level`, `--no-color`, 30-credit minimum, `fusion_*` JSONL events, usage file fields |
| [VentureBeat: GitHub's HydraFusion](https://venturebeat.com/orchestration/githubs-hydrafusion-cuts-ai-coding-costs-in-every-benchmark-it-only-matches-quality-in-one) | Trade press (4 Sep 2026) | 7 Oct 2026 | Mario Rodriguez quote on converging with Auto |
| [Hacker News discussion](https://news.ycombinator.com/item?id=49566788) | Community | 7 Oct 2026 | Developer sentiment, benchmark scepticism |
| [InfoQ: GitHub HydraFusion](https://www.infoq.com/news/2026/09/github-hydrafusion/) | Trade press | 7 Oct 2026 | Independent summary of the launch |
| [Hands-on: HydraFusion in Copilot CLI](https://www.stephenwthomas.com/artificial-intelligence/hydrafusion-github-copilot-cli/) | Practitioner blog | 7 Oct 2026 | Cascade run duration anecdote |

---

### _Author_

{% user pwd9000 %}

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [X](https://x.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-pwd9000/)

Date: 07-10-2026
