---
title: 'From Project HydraFusion to GitHub Copilot Fusion: Model Orchestration in Copilot'
published: true
description: 'A dated look at Project HydraFusion, now GitHub Copilot Fusion GA: how model orchestration works, what changed, and how to evaluate it.'
tags: 'githubcopilot, ai, devops, llm'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2026/project-hydrafusion-copilot-cli/assets/main.png'
canonical_url: null
id: 4644278
series: GitHub Copilot - CLI
date: '2026-10-12T08:18:03Z'
---

![diagram](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2026/project-hydrafusion-copilot-cli/assets/fusion.png)  

## From Project HydraFusion to GitHub Copilot Fusion: Model Orchestration in Copilot

This article began as an assessment of Project HydraFusion's research preview. As of 29 October 2026, that multi-model orchestration is part of GitHub Copilot Fusion, which also brings together Copilot Auto model selection. The preview-era CLI tests and benchmark analysis below remain useful as a dated snapshot, but their setup instructions, availability, and pricing are not current Fusion guidance.

On 4 September 2026 GitHub published [Project HydraFusion](https://github.blog/ai-and-ml/github-copilot/project-hydrafusion-frontier-quality-via-multi-model-orchestration/), first as a research preview in Copilot CLI and later, [on 30 September](https://github.blog/changelog/2026-09-30-hydrafusion-in-vs-code-and-the-github-copilot-app/), in VS Code and the GitHub Copilot app. Its core idea remains: let Copilot choose a model and execution pattern for each task rather than making the user select every model call. The original preview benchmarks are discussed below as historical results; GitHub has since published a separate Copilot Fusion Max result.

The durable engineering question is still how much orchestration a task needs, and what it costs in quality, latency, model usage, and policy complexity. Fusion is now a generally available Copilot experience rather than a research preview; the evaluation advice below remains relevant, but the old preview-only commands should not be assumed to work unchanged.

If you want the CLI fundamentals first, my [Copilot CLI practical guide](https://dev.to/pwd9000/github-copilot-cli-a-devops-engineers-practical-guide-to-ai-powered-terminal-automation-1jh0) and [evaluating LLM models in Copilot](https://dev.to/pwd9000/evaluating-llm-models-in-github-copilot-a-practical-scoring-and-assessment-guide-1f23) cover the ground this post builds on.

---

## From research preview to generally available Fusion

**Current status:** GitHub Copilot Fusion is **generally available**, announced on 28 October 2026. Project HydraFusion's multi-model orchestration is now combined with Copilot Auto model selection. The 4 September and 30 September details below describe the earlier research-preview rollout, not current Fusion status.

**Surfaces and plans:** The [GA announcement](https://github.blog/changelog/2026-10-28-route-and-orchestrate-models-with-github-copilot-fusion/) says Fusion is available on all Copilot plans in Visual Studio Code, the GitHub Copilot app, GitHub Copilot CLI, and JetBrains IDEs. The preview's earlier surface and plan limits no longer describe the GA offer.

**Model and administrator controls:** Fusion uses models allowed by the user's plan and applicable model policies. Enterprise administrators can configure which models are available to Copilot Fusion separately, and the [enterprise managed settings](https://docs.github.com/copilot/reference/enterprise-administrators/enterprise-managed-settings#fusiontier) reference documents `fusionTier` for setting the default effort level. This is more control than the research preview's user-facing model picker suggested; Fusion still chooses the specific models for each task.

**Billing:** Fusion bills each model it uses at that model's standard rate. GitHub's announcement offers users on paid Copilot plans a **limited-time 30% discount on model costs when using Fusion**. That is distinct from the preview-era statement below that HydraFusion had no Auto discount; use the [current announcement](https://github.blog/changelog/2026-10-28-route-and-orchestrate-models-with-github-copilot-fusion/) for the current promotion and billing terms.

**Getting started:** GitHub's current instruction is to update your client, choose **Copilot Fusion** in the model picker, and select an effort level. Fusion's user-selectable levels are **Standard**, **High**, and **Max**. The preview-specific `hydrafusion` model name, experimental flag, VS Code setting, and opt-in instructions below are historical and are not current setup guidance.

**Effort guidance:** Current [Fusion documentation](https://docs.github.com/copilot/concepts/models/copilot-fusion) describes Standard as balancing cost, quality, and latency for everyday work; High for substantial, well-scoped coding tasks; and Max for the deepest reasoning and most thorough analysis. Fusion chooses the model and execution pattern for each prompt, and can use different patterns in the same conversation.

### Timeline

| Date | What happened |
| --- | --- |
| 16 May 2026 | The [HyDRA](https://arxiv.org/abs/2605.17106) routing paper is published, its capability-scoring router is deployed in Auto for VS Code Chat |
| 4 Sep 2026 | HydraFusion announced as a research preview in Copilot CLI, behind experimental mode |
| Week of 14 Sep 2026 | Auto model selection starts rolling out Efficiency, Balance, and Intelligence tiers |
| 22 to 29 Sep 2026 | Claude Opus 5.5, GPT-6 Sol, GPT-6 Luna, Claude Sonnet 5.5, and GPT-6.1 Sol arrive in Copilot |
| 30 Sep 2026 | HydraFusion reaches VS Code 1.140 and the Copilot app, with step-by-step progress updates |
| 1 Oct 2026 | Dynamic workflows, code-defined orchestration, enter public preview in Copilot CLI, the app, and the SDK |
| 28 Oct 2026 | [GitHub Copilot Fusion becomes generally available](https://github.blog/changelog/2026-10-28-route-and-orchestrate-models-with-github-copilot-fusion/), combining HydraFusion's multi-model orchestration with Auto model selection and offering Standard, High, and Max effort levels. Available on all Copilot plans in VS Code, the Copilot app, Copilot CLI, and JetBrains IDEs |

---

## How Copilot Fusion Works

GitHub describes Fusion as a runtime model router and orchestrator. For each task, it uses capability signals for reasoning, code generation, debugging, and tool use to select models and an execution pattern that meets the quality bar for the chosen effort level. It also considers real-time system health and availability and routes at natural cache boundaries and significant changes in conversation complexity.

### The three execution patterns

| Pattern | Mechanism (GitHub's description) | When it makes sense |
| --- | --- | --- |
| **Single** | One selected model solves the task directly. | The task is well within a single model's capability, adds no overhead. |
| **Cascade** | An efficient model drafts a solution and a quality gate decides whether to accept it or escalate to a stronger model. | Most tasks are easy, some are not, and you would rather pay for the strong model only on the hard ones. |
| **Critique** | One model drafts a response while multiple models independently critique it in parallel; their feedback is aggregated, and the original model revises its response. | Tasks where independent reviews may improve the result enough to justify the extra model calls. |

This differs from the original preview description, which focused on a single read-only critic and one revision. The current [Fusion documentation](https://docs.github.com/copilot/concepts/models/copilot-fusion) describes multiple critics working in parallel, with their feedback aggregated before the drafting model revises. Do not assume the preview's exact critic implementation or limits still apply.

**Important things to note:**

- **Per-prompt choice.** Fusion can choose a different execution pattern for each prompt in a conversation. GitHub says selecting the pattern adds minimal latency; the 251 ms routing event recorded in my CLI smoke test is a preview-era observation, not a current performance guarantee.
- **Dynamic model pool, policy controls.** GitHub says the pool changes as models become available and are evaluated. Users do not choose the individual model for each step, but enterprise admins can configure which models Fusion may use through [model availability policies](https://docs.github.com/copilot/how-tos/administer-copilot/manage-for-enterprise/manage-availability-of-default-models#configuring-models-available-for-copilot-fusion).
- **A conservative context window.** Fusion has no separate context window; the displayed value is based on the limits of the models it uses.
- **Progress without draft disclosure.** You can follow steps and the models being used, but intermediate drafts may be revised or discarded; Fusion returns the final response.

### Preview-era operating principles

The original HydraFusion announcement described the following design principles. They are useful context for how the preview was built, but the current GA documentation does not restate all of them as guarantees:

- **Complete accounting.** "Aggregate cost and usage across every workflow leg, including drafting, critique, revision, escalation, retry, and fallback."
- **Bounded execution.** "Give each leg explicit timeout and cancellation behavior to keep execution and cost within defined limits."
- **Isolated review.** "Run review steps in isolated, tool-less contexts, while solver steps use the shared workspace and normal permission-aware agent loop."
- **Fail-safe application.** "Apply no patch when the workflow is cancelled or fails validation, preventing incomplete changes from reaching the repository."
- **Validated routing.** "Verify workflow definitions, model bindings, fallback behavior, and model availability before execution begins."

The practical caution still stands: do not treat an orchestration's validation as a substitute for reviewing the workspace. The preview documentation warned that edits made by a discarded draft might not be undone automatically. The current Fusion pages linked here do not restate that exact behaviour as a guarantee either way. Run coding agents on a branch or disposable worktree and inspect the complete diff before committing.

### How the routing policy was built

For the original preview, GitHub said it used beam search to construct the routing policy and measured candidates "against a frozen baseline on quality, cost, and failure modes" across TerminalBench 2.1, DeepSWE, and its internal CheckpointBench. Those details and the August tuning results describe the preview research, not a complete account of how today's Fusion policy is trained or updated.

### Where it came from, and what is in the pool

As noted in the [GitHub Community announcement](https://github.com/orgs/community/discussions/206492): "Auto V1 (Jan 2026, capacity/SKU-aware per-request selection) → Auto V2 aka. HyDRA (May 2026, intent-scored routing) → HydraFusion (Aug 2026, per-turn orchestration and cache-aware workflows)." The [HyDRA paper](https://arxiv.org/abs/2605.17106) describes a ModernBERT encoder that scores each query on reasoning, code generation, debugging, and tool use, the same four capability signals GitHub cites for HydraFusion. It states that HyDRA "is deployed to all users in GitHub Copilot's VS Code Chat auto-mode", and its first author, Aashna Garg, is also credited on the HydraFusion post. Community write-ups that linked HydraFusion to a routing research paper were right: HydraFusion builds on the router behind Auto and adds multi-model workflows on top.

GitHub does not publish a fixed Fusion model roster because the pool changes as models arrive and are evaluated. The preview feedback thread captured an earlier concern: users reported in early October that HydraFusion was routing to older models. Treat those reports as historical, not evidence about the current pool. Enterprise admins now have a documented control to configure which enabled models Fusion may use, while users still do not select individual models for each task. The original preview benchmark charts compared HydraFusion with Claude Opus 5, Claude Sonnet 5, and GPT-5.6 variants; those are benchmark comparators, not a disclosed Fusion model roster.

### Before Fusion: Auto model selection and HydraFusion (preview-era snapshot)

This table records the separate products as they stood in the original article on 12 October 2026. Its pricing and availability details were superseded by the 28 October Fusion announcement.

|  | Auto model selection | HydraFusion research preview |
| --- | --- | --- |
| Status | GA in Copilot Chat (github.com and supported IDEs), CLI, Copilot app, and cloud agent | Research preview in CLI, VS Code 1.140 or later, and the Copilot app, no SLA |
| Unit of decision | One model per request, re-routed along natural cache boundaries and large shifts in complexity | One execution pattern per prompt, potentially several models within a turn |
| Mechanism | Task complexity plus real-time model health, Efficiency, Balance, and Intelligence tiers in VS Code, CLI, and the app | Capability signals selecting Single, Cascade, or Critique |
| Pricing | Selected model's rate, with a 10% discount on paid plans | Each model's standard rate, summed across legs, no discount |
| Admin model policies | Honoured, documented | Honoured, documented, hidden from the picker if no allowed model qualifies |
| Choose the models yourself | No | No |
| See which model ran | Per response (hover, terminal, or end of response) | CLI progress display, hover in VS Code and the app |

That separation is now historical: GitHub Copilot Fusion combines Auto model selection with HydraFusion's multi-model orchestration. The preview's forward-looking comments about a possible convergence have been superseded by the 28 October GA announcement.

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

1. **HydraFusion beat Opus 5 on one benchmark out of three.** On the other two it is slightly behind on quality and substantially cheaper. "Frontier quality at lower cost" is a fair summary, "better than Opus" is not.
2. **The interesting comparison is often GPT-5.6 Sol, not Opus.** On TerminalBench, HydraFusion costs the same as Sol and scores 11.4 points higher. On DeepSWE and CheckpointBench it costs 12.5% and 13.3% more than Sol for 2.2 and 1.4 points more quality. If your team already defaults to a mid-tier model, the cost saving versus your baseline is much smaller than 67%.
3. **TerminalBench 2.1 is described by GitHub itself as relatively saturated**, which is why the harder repository-level DeepSWE matters more, and that is where the margin is thinnest.
4. **CheckpointBench is internal.** GitHub describes it as a multi-turn benchmark curated from real Copilot sessions. Its chart breaks the 276 checkpoints down as 116 easy, 107 medium, and 53 hard, led by Python (92) and TypeScript (48), and dominated by bug fixes (90) and feature implementation (73). You cannot reproduce it.
5. **These are offline, best-tuned configuration, medium reasoning, and pricing-assumption specific.** GitHub says so directly. The preview research was not a substitute for measuring results on real developer workloads.
6. **The comparators have moved on.** Every number above predates Claude Opus 5.5, GPT-6 Sol, and GPT-6.1 Sol. "Cheaper than Opus 5" says little about cost against whatever your team adopted at the end of September.

None of this is a criticism of GitHub's transparency, which is better than most model announcements. It is a reason to run your own numbers.

### A newer Copilot Fusion Max result

The 28 October announcement reports a separate result from the **Artificial Analysis Coding Agent Index**: Copilot Fusion Max scored **60**, within two points of Claude Code with Opus 5.5 Max. GitHub says Fusion achieved that result at about half the average API cost per task, using about half as many tokens, and taking about 40% less time per task.

This is a new data point, not a direct update to the TerminalBench, DeepSWE, or CheckpointBench table above. The benchmark, configuration, and comparator differ, so do not combine the scores or treat GitHub's result as a guarantee for your workload. Measure your own tasks and compare against the models and tools your team actually uses.

---

## Why DevOps Engineers Should Care

**Cost variance becomes a workflow property.** With a fixed model, cost per task scales roughly with task size. Fusion can use one model or add review and escalation calls depending on the task and selected effort level. GitHub bills each model at its standard rate and currently advertises a limited-time 30% discount on Fusion model costs for paid plans. The preview-era `--max-ai-credits` observations below came from CLI 1.0.89; check the current client documentation and your plan's billing controls before using that flag or translating the observed minimum into a current spend limit.

**Latency depends on the selected pattern.** GitHub's current documentation says Cascade and Critique take longer because they include review model calls, while selecting a pattern adds minimal latency. One early hands-on report describes a three-to-four-minute Cascade run for a single prompt; treat that as a preview-era observation, not a current expectation. For interactive work, measure the latency of your own prompts and effort levels.

**Visibility is better, but it is not yet operational telemetry.** Current Fusion documentation says you can follow execution progress and hover over the effort level to see the models used. That is useful for manual review, but it is not the same as a documented, stable event schema for dashboards or CI reporting. For bug reports, the preview-era `/collect-debug-logs` command captured "the execution pattern and the models used for each step"; verify current debug-log behaviour before relying on that workflow.

Headless runs went further than the preview documentation did. With `--output-format json`, CLI 1.0.89 emitted `session.fusion_resolved`, `assistant.fusion_phase_started`, `assistant.fusion_phase_completed`, and `session.fusion_completed` events in my preview-era smoke test. Between them they carried the pattern, each phase's model and role, duration, and token and credit usage. That schema was undocumented and is not verified for current Fusion. If you use the [OpenTelemetry tracing approach](https://dev.to/pwd9000/agentic-devops-needs-observability-trace-github-copilot-with-opentelemetry-405c), the current Fusion docs do not say whether orchestration legs appear as separate spans, so check your collector before relying on it.

**Enterprise controls are now more explicit.** Fusion uses models available to the user under their plan and applicable model policies. Enterprise admins can configure the models Fusion may use and set a default Fusion effort level through managed settings. These controls matter because a single task can involve multiple models. The linked product docs describe model availability and routing, but do not by themselves establish which contractual data-processing terms apply to each model provider; organisations with provider-specific restrictions should confirm their applicable terms with GitHub.

---

## Before vs Now

| Concern | Before: choose a model or use Auto | Now: Copilot Fusion |
| --- | --- | --- |
| Choosing models and workflow | Choose a model, or let Auto select one model per request | Fusion selects models and an execution pattern for each task |
| Effort | Model-specific reasoning settings | Standard, High, or Max, balancing speed/cost and deeper reasoning |
| Review and escalation | Manual re-run or separate review workflow | Cascade and Critique add model calls when Fusion considers them useful |
| Billing | Selected model's rate; Auto had its own pricing terms | Each model used is billed at its standard rate; GitHub advertises a limited-time 30% discount on Fusion model costs for paid plans |
| Administrator controls | Model policies | Model policies plus Fusion-specific model availability and an enterprise-managed default effort |
| Availability | Separate experiences with their own plan and client support | GA on all Copilot plans in VS Code, the Copilot app, Copilot CLI, and JetBrains IDEs |
| Visibility | Depends on the selected model and client | Progress is visible; hover over the effort level to see models used |
| Vendor exposure per task | Depends on the one selected model | Potentially multiple models, depending on the execution pattern |

---

## Evaluating Copilot Fusion on Your Own Workload

The evaluation method still applies to Fusion: compare it with fixed-model baselines on representative tasks, record wall time, cost, models used, and whether the checks pass. The code and command below are a **historical research-preview harness**, tested with Copilot CLI 1.0.89 and the `hydrafusion` identifier. GitHub's GA instructions now say to update your client and select **Copilot Fusion** in the model picker. The old command, identifier, output events, and credit limits are not verified as current; check the current client documentation before adapting the harness.

### Prerequisites

- For current Fusion, use an updated supported client and select Copilot Fusion from its model picker. GitHub's 28 October announcement lists VS Code, the Copilot app, Copilot CLI, and JetBrains IDEs, on all Copilot plans.
- The historical harness below was tested with Copilot CLI 1.0.89; [1.0.92](https://github.com/github/copilot-cli/releases/tag/v1.0.92) was the stable release cited when this article was first published. Neither version is presented as current here.
- A disposable git repository with a real build and test command. Do not use a production repository, `--yolo` approves every tool call without asking.
- A spending limit appropriate for your plan. The preview-era harness used `--max-ai-credits`; verify current CLI options and billing controls before using or relying on that argument.

### Choose tasks that match GitHub's guidance

Pick first-turn, single-prompt, verifiable tasks. Examples that have worked as evaluation prompts in my earlier model comparisons:

1. Add input validation and a unit test to a specific function.
2. Fix a failing test that you have deliberately broken.
3. Convert a callback-style module to async and keep the tests green.
4. Add structured logging to a CLI entry point with a documented format.
5. Write a GitHub Actions workflow that runs the test suite on pull requests with least-privilege permissions.

Each task needs a deterministic check: a test command that must pass, a file that must exist, or a lint rule that must be satisfied.

### The preview-era CLI harness

The [evaluation harness](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2026/project-hydrafusion-copilot-cli/code/Invoke-HydraFusionEval.ps1) in this article's code folder runs each task against each model configuration in a fresh git worktree. It calls Copilot CLI non-interactively with JSON output and a usage file, captures wall time, runs your check command, and appends a row to a CSV with the credits used, the models that ran, and, for the preview, the execution pattern. This is a historical example, not current Fusion setup documentation. The preview invocation was:

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

- **The model identifier was documented for the preview.** `copilot --experimental --model hydrafusion -p` was the documented headless path at the time. On CLI 1.0.89 it exited cleanly and emitted HydraFusion events in the JSONL stream. Do not assume the preview identifier or these event names are the current Fusion interface.
- **Credits come from the usage file, and its schema is not documented.** `--usage-output-file` writes "final usage statistics as JSON". In CLI 1.0.89 that file contains a `totalNanoAiu` field and a per-model `modelMetrics` map.

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

For a current evaluation, use fixed-model baselines that your team actually uses and the current Fusion model-picker workflow. GitHub's older preview benchmarks used GPT-5.6 Sol and Claude Opus 5; those make the historical results comparable but are not necessarily useful current baselines.

The task file is a simple JSON array. A [sample](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2026/project-hydrafusion-copilot-cli/code/tasks.sample.json) is included:

```json
[
  {
    "id": "validate-input",
    "prompt": "In src/orders.ts, add input validation to createOrder so that quantity must be a positive integer and customerId must be a non-empty string. Throw a ValidationError with a clear message. Add unit tests in tests/orders.test.ts covering both failure cases and one success case. Run the tests and make sure they pass.",
    "check": "npm test -- --runTestsByPath tests/orders.test.ts"
  },
  {
    "id": "fix-failing-test",
    "prompt": "The test suite currently has one failing test in tests/pricing.test.ts. Find the root cause in the implementation (not the test), fix it, and run the full test suite until it passes. Do not modify or delete tests.",
    "check": "npm test"
  },
  {
    "id": "structured-logging",
    "prompt": "Add structured JSON logging to the CLI entry point in src/cli.ts. Each log line must include timestamp, level, message, and a correlationId that is generated once per invocation. Keep existing behaviour and make sure the build and tests pass.",
    "check": "npm run build && npm test"
  },
  {
    "id": "ci-workflow",
    "prompt": "Create .github/workflows/test.yml that runs npm ci and npm test on pull requests to main using ubuntu-latest and Node 20. Use a top-level permissions block with contents: read only, and pin actions/checkout and actions/setup-node to specific major versions.",
    "check": "node -e \"process.exit(require('fs').existsSync('.github/workflows/test.yml') ? 0 : 1)\""
  }
]
```

### What to look at

Load the CSV and compare per model:

- **Pass rate** per task, not just overall. Fusion may perform differently across task types; aggregate scores can hide useful differences.
- **Pattern mix per task.** In the preview harness, the `FusionPatterns` column shows whether HydraFusion chose Single, Cascade, or Critique. Confirm the current client exposes equivalent data before automating this comparison.
- **Cost per passing task.** Compare like-for-like tasks, including failures and retries, and account for any applicable Fusion discount.
- **Models that actually ran.** Use current client details to record the models Fusion reports. If a model is outside your approved pool, revisit the model policies with your administrator.
- **Diff size and test changes.** Open a few diffs from each configuration. A generated change that removes a test to make it green is a failure your check command may not catch. Review the whole worktree, not just the final answer.

Record the model configurations, client version, date, and applicable pricing terms. The older `FusionPatterns`, usage-file, and JSONL fields in this preview harness are not a documented GA telemetry contract.

---

## Security and Governance Considerations

The realistic threat model here is not new, but the routing changes some of the numbers.

- **A task may involve multiple models.** Fusion can route work through different models and its Critique pattern uses multiple models. Review which models are enabled for Fusion and make sure your organisation's policies and contractual requirements permit them.
- **Treat model-generated review as advisory.** The current docs describe the Critique flow, but do not describe it as a security boundary or replace ordinary code review. Prompt injection in repository content can still influence an agent's work; keep permissions scoped and review proposed changes.
- **Do not rely on orchestration to clean the workspace.** The preview documentation warned that edits from a discarded draft might not be automatically undone; current docs linked here do not restate that behaviour either way. Use a branch or disposable worktree and inspect the full diff before committing.
- **Keep cost controls current.** Fusion charges for each model used, with a limited-time 30% discount on model costs for paid plans announced on 28 October. Verify applicable budgets and CLI limits for your plan and client rather than treating a preview-era command as a current circuit breaker.
- **Roll out deliberately.** GA status does not remove the need for model-policy review, least-privilege agent permissions, test gates, and human review before accepting code changes.

---

## Limitations and Gotchas

- **The route is not fully user-directed.** You choose Fusion and an effort level; Fusion selects the models and execution pattern. The model pool changes over time. Enterprise admins can control which models are available to Fusion, but users do not pick each model for each step.
- **Extra orchestration can cost time and credits.** GitHub says Cascade and Critique take longer because they include review model calls. The new benchmark reports a relative speed result for its test setup, not a latency guarantee for every task.
- **The context window is conservative.** Fusion has no context window of its own; its displayed context value is based on the models it uses.
- **Only the final response is shown.** Users can follow execution progress and see models used, but intermediate drafts may be revised or discarded.
- **Do not carry preview assumptions forward.** The research-preview no-SLA statement, surface restrictions, first-turn guidance, sub-agent behaviour, discarded-edit warning, and JSON telemetry fields belong to the old preview documentation or CLI tests. Check current product docs before relying on any of them as GA behaviour.

---

## Real-World Use Cases

1. **Batch code maintenance in autopilot.** Dependency upgrade fallout, lint sweeps, and deprecation fixes across a repository, where Fusion can use a straightforward model path for simpler tasks and add review or escalation when warranted.
2. **Cost and quality trade-offs for teams.** GitHub's Fusion Max result reports similar benchmark quality to a named comparator at lower average API cost, token use, and elapsed time. Treat that as a reason to run a local evaluation, not a forecast of your own savings.
3. **Refactors where a second opinion matters.** Migrations and interface changes are cases where Fusion's Critique pattern may justify its additional model calls.
4. **Choosing between runtime and code-defined orchestration.** Since 1 October, [dynamic workflows](https://github.blog/changelog/2026-10-01-dynamic-workflows-in-copilot-cli-and-the-copilot-app/) let you define an orchestration in code inside a Copilot extension, in Copilot CLI, the app, and the SDK. One of GitHub's examples asks two models whether old review comments still matter and reports only when both agree. Use Fusion when you want the runtime to decide which models and execution pattern a task needs. Use a dynamic workflow when you need the same steps every time, checkpoints for a human, and a process you can review in a pull request.
5. **Evaluation practice.** Even if you never adopt it, running the harness above against three configurations is a better way to choose your team's default model than reading benchmark tables.

---

## My Take

The transition from HydraFusion preview to Copilot Fusion GA is a meaningful product change: model selection and multi-model orchestration are now one experience, available across more clients and plans. The current docs also make administrator controls clearer, including the ability to configure Fusion's model pool and default effort. This is more useful to platform teams than a separate experimental picker because it gives administrators a documented place to shape access.

The newer Fusion Max result is promising, but it does not erase the caveats in the preview benchmarks or prove that every team will see the same savings. Its Artificial Analysis score and cost, token, and time comparisons are tied to that benchmark and configuration. The honest operational response is to evaluate the model and effort settings against your own codebase, tests, latency tolerance, and billing terms.

I would pilot Fusion rather than switch a whole organisation's defaults on the strength of the announcement. Set an approved model pool, choose an effort level for the workload, instrument real task outcomes, and review the resulting code. Keep the historical preview harness as an evaluation pattern, but first verify its CLI model name, telemetry fields, and spending controls against the current client.

The convergence that GitHub had previously described as a future possibility has now happened in Copilot Fusion. The enduring lesson from the preview is not that one router always wins; it is to compare quality, cost, latency, and policy fit on representative tasks before changing a team-wide default.

---

## Conclusion

- GitHub Copilot Fusion became generally available on 28 October 2026, on all Copilot plans in VS Code, the Copilot app, Copilot CLI, and JetBrains IDEs.
- Fusion combines Auto model selection with HydraFusion's multi-model orchestration. Users choose Standard, High, or Max effort; Fusion chooses models and execution patterns per task.
- GitHub bills each model at its standard rate and announced a limited-time 30% discount on Fusion model costs for paid plans.
- Enterprise admins can configure which models Fusion may use and set a default effort level. Keep model access and agent permissions aligned with your organisation's policies.
- The preview benchmark results remain historical. GitHub has since reported a Fusion Max score of 60 on the Artificial Analysis Coding Agent Index, with cost, token, and time comparisons against Claude Code with Opus 5.5 Max; evaluate that separately from the older benchmarks.
- The old `--experimental --model hydrafusion` walkthrough and its telemetry observations are preview-era. Verify current client commands and output before adapting them.
- Evaluate Fusion on representative tasks using deterministic checks, a fixed-model baseline, cost and latency measurements, and review of the full diff.

Choosing the right amount of model work for each task is still the important problem. Copilot Fusion is GitHub's GA product for that approach; the engineering discipline remains to validate its results against your own delivery, cost, and security requirements.

## Sources

| Source | Date | What it verifies |
| --- | --- | --- |
| [GitHub Changelog: Route and orchestrate models with GitHub Copilot Fusion](https://github.blog/changelog/2026-10-28-route-and-orchestrate-models-with-github-copilot-fusion/) | 28 October 2026 | GA status, supported plans and clients, effort levels, billing and discount, and the Fusion Max benchmark result |
| [GitHub Docs: About GitHub Copilot Fusion](https://docs.github.com/copilot/concepts/models/copilot-fusion) | Checked 29 October 2026 | Current routing behaviour, execution patterns, effort levels, progress, and model visibility |
| [GitHub Docs: Managing model availability for Copilot Fusion](https://docs.github.com/copilot/how-tos/administer-copilot/manage-for-enterprise/manage-availability-of-default-models#configuring-models-available-for-copilot-fusion) | Checked 29 October 2026 | Enterprise control over which models Fusion can use |
| [GitHub Docs: Enterprise managed settings](https://docs.github.com/copilot/reference/enterprise-administrators/enterprise-managed-settings#fusiontier) | Checked 29 October 2026 | The `fusionTier` setting for a default Fusion effort level |

---

### _Author_

{% user pwd9000 %}

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [X](https://x.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-pwd9000/)

Date: 12-10-2026
