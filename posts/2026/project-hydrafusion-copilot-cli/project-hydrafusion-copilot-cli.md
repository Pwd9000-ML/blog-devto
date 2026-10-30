---
title: 'From Project HydraFusion to GitHub Copilot Fusion: Model Orchestration in Copilot'
published: true
description: 'A dated look at Project HydraFusion, now GitHub Copilot Fusion GA: how model orchestration works, what changed, and how to evaluate it.'
tags: 'githubcopilot, ai, devops, llm'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2026/project-hydrafusion-copilot-cli/assets/main.png?v=cloudflare-20261030'
canonical_url: null
id: 4644278
series: GitHub Copilot - CLI
date: '2026-10-12T08:18:03Z'
---

## From Project HydraFusion to GitHub Copilot Fusion: Model Orchestration in Copilot

Project HydraFusion began as a research preview in Copilot CLI on 4 September 2026, expanded to VS Code and the Copilot app on [30 September](https://github.blog/changelog/2026-09-30-hydrafusion-in-vs-code-and-the-github-copilot-app/), and became generally available as Copilot Fusion on 28 October. Fusion combines multi-model orchestration with Copilot Auto model selection. This post looks at how it works, what the historical benchmarks do and do not tell us, and how to evaluate it against real tasks.

If you want the CLI fundamentals first, my [Copilot CLI practical guide](https://dev.to/pwd9000/github-copilot-cli-a-devops-engineers-practical-guide-to-ai-powered-terminal-automation-1jh0) and [evaluating LLM models in Copilot](https://dev.to/pwd9000/evaluating-llm-models-in-github-copilot-a-practical-scoring-and-assessment-guide-1f23) cover the ground this post builds on.

---

## From research preview to generally available Fusion

**Current status:** GitHub Copilot Fusion is **generally available**, announced on 28 October 2026. Project HydraFusion's multi-model orchestration is now combined with Copilot Auto model selection. The 4 September and 30 September details below describe the earlier research-preview rollout, not current Fusion status.

**Surfaces and plans:** The [GA announcement](https://github.blog/changelog/2026-10-28-route-and-orchestrate-models-with-github-copilot-fusion/) says Fusion is available on all Copilot plans in Visual Studio Code, the GitHub Copilot app, GitHub Copilot CLI, and JetBrains IDEs. The preview's earlier surface and plan limits no longer describe the GA offer.

**Model and administrator controls:** Fusion uses models allowed by the user's plan and applicable model policies. Enterprise administrators can configure which models are available to Copilot Fusion separately, and the [enterprise managed settings](https://docs.github.com/copilot/reference/enterprise-administrators/enterprise-managed-settings#fusiontier) reference documents `fusionTier` for setting the default effort level. This is more control than the research preview's user-facing model picker suggested, Fusion still chooses the specific models for each task.

**Billing:** Fusion bills each model it uses at that model's standard rate. GitHub announced a **limited-time 30% discount on model costs for paid Copilot plans**, see the [announcement](https://github.blog/changelog/2026-10-28-route-and-orchestrate-models-with-github-copilot-fusion/) for its terms.

**Getting started:** Update your client, choose **Copilot Fusion** in the model picker, and select an effort level. The user-selectable levels are **Standard**, **High**, and **Max**. The preview-specific `hydrafusion` model name and experimental setup are not current setup guidance.

**Effort guidance:** Current [Fusion documentation](https://docs.github.com/copilot/concepts/models/copilot-fusion) describes Standard as balancing cost, quality, and latency for everyday work, High for substantial, well-scoped coding tasks, and Max for the deepest reasoning and most thorough analysis. Fusion chooses the model and execution pattern for each prompt, and can use different patterns in the same conversation.

### Timeline

| Date | What happened |
| --- | --- |
| 16 May 2026 | The [HyDRA](https://arxiv.org/abs/2605.17106) routing paper is published, its capability-scoring router is deployed in Auto for VS Code Chat |
| 4 Sep 2026 | HydraFusion announced as a research preview in Copilot CLI, behind experimental mode |
| 30 Sep 2026 | HydraFusion reaches VS Code 1.140 and the Copilot app, with step-by-step progress updates |
| 28 Oct 2026 | [GitHub Copilot Fusion becomes generally available](https://github.blog/changelog/2026-10-28-route-and-orchestrate-models-with-github-copilot-fusion/), combining HydraFusion's multi-model orchestration with Auto model selection and offering Standard, High, and Max effort levels. Available on all Copilot plans in VS Code, the Copilot app, Copilot CLI, and JetBrains IDEs |

---

## How Copilot Fusion Works

GitHub describes Fusion as a runtime model router and orchestrator. For each task, it uses capability signals for reasoning, code generation, debugging, and tool use to select models and an execution pattern that meets the quality bar for the chosen effort level. It also considers real-time system health and availability and routes at natural cache boundaries and significant changes in conversation complexity.

### The three execution patterns

| Pattern | Mechanism (GitHub's description) | When it makes sense |
| --- | --- | --- |
| **Single** | One selected model solves the task directly. | The task is well within a single model's capability, adds no overhead. |
| **Cascade** | An efficient model drafts a solution and a quality gate decides whether to accept it or escalate to a stronger model. | Most tasks are easy, some are not, and you would rather pay for the strong model only on the hard ones. |
| **Critique** | One model drafts a response while multiple models independently critique it in parallel, their feedback is aggregated, and the original model revises its response. | Tasks where independent reviews may improve the result enough to justify the extra model calls. |

![diagram](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2026/project-hydrafusion-copilot-cli/assets/fusion.png)

This differs from the original preview description, which focused on a single read-only critic and one revision. The current [Fusion documentation](https://docs.github.com/copilot/concepts/models/copilot-fusion) describes multiple critics working in parallel, with their feedback aggregated before the drafting model revises. Do not assume the preview's exact critic implementation or limits still apply.

### Where it came from, and what is in the pool

As noted in the [GitHub Community announcement](https://github.com/orgs/community/discussions/206492): "Auto V1 (Jan 2026, capacity/SKU-aware per-request selection) → Auto V2 aka. HyDRA (May 2026, intent-scored routing) → HydraFusion (Aug 2026, per-turn orchestration and cache-aware workflows)." The [HyDRA paper](https://arxiv.org/abs/2605.17106) describes a ModernBERT encoder that scores each query on reasoning, code generation, debugging, and tool use, the same four capability signals GitHub cites for HydraFusion. It states that HyDRA "is deployed to all users in GitHub Copilot's VS Code Chat auto-mode", and its first author, Aashna Garg, is also credited on the HydraFusion post. Community write-ups that linked HydraFusion to a routing research paper were right: HydraFusion builds on the router behind Auto and adds multi-model workflows on top.

GitHub does not publish a fixed Fusion model roster because the pool changes as models arrive and are evaluated. Enterprise administrators can configure which enabled models Fusion may use, while users do not select individual models for each task. The original preview benchmarks compared HydraFusion with Claude Opus 5, Claude Sonnet 5, and GPT-5.6 variants, those are benchmark comparators, not a disclosed Fusion roster.

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

**Cost varies by workflow.** Fusion can use one model or add review and escalation calls depending on the task and effort level. Each model is billed at its standard rate, with a limited-time discount announced for paid plans. Evaluate costs under your organisation's actual billing terms.

**Latency depends on the selected pattern.** GitHub says Cascade and Critique take longer because they include review model calls, while selecting a pattern adds minimal latency. Measure latency on your own prompts and effort levels.

**Visibility is useful, but not a telemetry contract.** Current documentation says you can follow progress and see which models were used. It does not document a stable event schema for dashboards or CI reporting. If you use the [OpenTelemetry tracing approach](https://dev.to/pwd9000/agentic-devops-needs-observability-trace-github-copilot-with-opentelemetry-405c), verify what your collector records instead of assuming each orchestration step appears as a separate span.

**Enterprise controls are now more explicit.** Fusion uses models available to the user under their plan and applicable model policies. Enterprise admins can configure the models Fusion may use and set a default Fusion effort level through managed settings. These controls matter because a single task can involve multiple models. The linked product docs describe model availability and routing, but do not by themselves establish which contractual data-processing terms apply to each model provider, organisations with provider-specific restrictions should confirm their applicable terms with GitHub.

---

## Before vs Now

| Concern | Before: choose a model or use Auto | Now: Copilot Fusion |
| --- | --- | --- |
| Choosing models and workflow | Choose a model, or let Auto select one model per request | Fusion selects models and an execution pattern for each task |
| Effort | Model-specific reasoning settings | Standard, High, or Max, balancing speed/cost and deeper reasoning |
| Review and escalation | Manual re-run or separate review workflow | Cascade and Critique add model calls when Fusion considers them useful |
| Billing | Selected model's rate, Auto had its own pricing terms | Each model used is billed at its standard rate, GitHub advertises a limited-time 30% discount on Fusion model costs for paid plans |
| Administrator controls | Model policies | Model policies plus Fusion-specific model availability and an enterprise-managed default effort |
| Availability | Separate experiences with their own plan and client support | GA on all Copilot plans in VS Code, the Copilot app, Copilot CLI, and JetBrains IDEs |
| Visibility | Depends on the selected model and client | Progress is visible, hover over the effort level to see models used |
| Vendor exposure per task | Depends on the one selected model | Potentially multiple models, depending on the execution pattern |

---

## Evaluating Copilot Fusion on Your Own Workload

The evaluation method still applies: compare Fusion with fixed-model baselines on representative tasks, using the same prompt, repository state, and deterministic checks. Run them in a branch or disposable worktree, then compare:

- **Task outcomes:** record pass/fail for each task, not just an aggregate score.
- **Effort and model use:** note the selected effort and models shown by the client.
- **Time and cost:** record elapsed time and available usage or cost data, don't infer per-run costs from undocumented telemetry.
- **Change quality:** inspect the full diff, including tests, for every configuration.

Use tasks such as a targeted bug fix, a small refactor, or a code change with a clear test. Record the client version, date, baseline model, effort level, and applicable pricing terms.

---

## Security and Governance Considerations

The realistic threat model here is not new, but the routing changes some of the numbers.

- **A task may involve multiple models.** Fusion can route work through different models and its Critique pattern uses multiple models. Review which models are enabled for Fusion and make sure your organisation's policies and contractual requirements permit them.
- **Treat model-generated review as advisory.** The current docs describe the Critique flow, but do not describe it as a security boundary or replace ordinary code review. Prompt injection in repository content can still influence an agent's work, keep permissions scoped and review proposed changes.
- **Review changes before accepting them.** Use a branch or disposable worktree and inspect the full diff, orchestration is not a substitute for code review.
- **Roll out deliberately.** GA status does not remove the need for model-policy review, least-privilege agent permissions, test gates, and human review before accepting code changes.

---

## Limitations and Gotchas

- **The route is not fully user-directed.** You choose Fusion and an effort level, Fusion selects the models and execution pattern. The model pool changes over time. Enterprise admins can control which models are available to Fusion, but users do not pick each model for each step.
- **Extra orchestration can cost time and credits.** GitHub says Cascade and Critique take longer because they include review model calls. The new benchmark reports a relative speed result for its test setup, not a latency guarantee for every task.
- **The context window is conservative.** Fusion has no context window of its own, its displayed context value is based on the models it uses.
- **Only the final response is shown.** Users can follow execution progress and see models used, but intermediate drafts may be revised or discarded.

---

## Real-World Use Cases

1. **Batch code maintenance in autopilot.** Dependency upgrade fallout, lint sweeps, and deprecation fixes across a repository, where Fusion can use a straightforward model path for simpler tasks and add review or escalation when warranted.
2. **Cost and quality trade-offs for teams.** GitHub's Fusion Max result reports similar benchmark quality to a named comparator at lower average API cost, token use, and elapsed time. Treat that as a reason to run a local evaluation, not a forecast of your own savings.
3. **Refactors where a second opinion matters.** Migrations and interface changes are cases where Fusion's Critique pattern may justify its additional model calls.
4. **Choosing between runtime and code-defined orchestration.** Since 1 October, [dynamic workflows](https://github.blog/changelog/2026-10-01-dynamic-workflows-in-copilot-cli-and-the-copilot-app/) let you define an orchestration in code inside a Copilot extension, in Copilot CLI, the app, and the SDK. One of GitHub's examples asks two models whether old review comments still matter and reports only when both agree. Use Fusion when you want the runtime to decide which models and execution pattern a task needs. Use a dynamic workflow when you need the same steps every time, checkpoints for a human, and a process you can review in a pull request.
5. **Evaluation practice.** Compare Fusion and fixed-model baselines on the same representative tasks rather than choosing a team default from benchmark tables alone.

---

## My Take

The transition from HydraFusion preview to Copilot Fusion GA combines model selection and multi-model orchestration in one experience. Administrator controls for the model pool and default effort also give platform teams a way to shape access.

The newer Fusion Max result is promising, but it does not erase the caveats in the preview benchmarks or prove that every team will see the same savings. Its Artificial Analysis score and cost, token, and time comparisons are tied to that benchmark and configuration. The honest operational response is to evaluate the model and effort settings against your own codebase, tests, latency tolerance, and billing terms.

I would pilot Fusion rather than switch organisation-wide defaults on the strength of the announcement. Set an approved model pool, choose effort levels for the workload, measure task outcomes, and review the resulting code. Compare quality, cost, latency, and policy fit on representative tasks before changing a team-wide default.

---

## Conclusion

- GitHub Copilot Fusion became generally available on 28 October 2026, on all Copilot plans in VS Code, the Copilot app, Copilot CLI, and JetBrains IDEs.
- Fusion combines Auto model selection with HydraFusion's multi-model orchestration. Users choose Standard, High, or Max effort, Fusion chooses models and execution patterns per task.
- GitHub bills each model at its standard rate and announced a limited-time 30% discount on Fusion model costs for paid plans.
- Enterprise admins can configure which models Fusion may use and set a default effort level. Keep model access and agent permissions aligned with your organisation's policies.
- The preview benchmark results remain historical. GitHub has since reported a Fusion Max score of 60 on the Artificial Analysis Coding Agent Index, with cost, token, and time comparisons against Claude Code with Opus 5.5 Max, evaluate that separately from the older benchmarks.
- Evaluate Fusion on representative tasks using deterministic checks, a fixed-model baseline, cost and latency measurements, and review of the full diff.

Choosing the right amount of model work for each task is still the important problem. Copilot Fusion is GitHub's GA product for that approach, the engineering discipline remains to validate its results against your own delivery, cost, and security requirements.

---

### _Author_

{% user pwd9000 %}

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [X](https://x.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-pwd9000/)

Date: 12-10-2026
