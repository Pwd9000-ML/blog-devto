---
title: 'Microsoft Ignite 2026 Book of News: My Six Picks for DevOps Teams'
published: true
description: 'Six Ignite 2026 updates for teams shipping on Azure: what changes in code review, database testing and on-call, and which previews I would pilot.'
tags: 'msignite, devops, azure, github'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2026/microsoft-ignite-2026-book-of-news-devops/assets/main.png'
canonical_url: null
id: 5081239
series: null
date: '2026-11-20T11:21:13Z'
---

Last year, [my Ignite shortlist](https://dev.to/pwd9000/microsoft-ignite-2025-for-devs-devops-my-top-announcements-4f6i) was mostly about where agents would fit in the developer toolchain. This year Microsoft has a much more concrete proposition: if your code lives in Azure Repos, Copilot can now open a pull request there **and** review it. The catch? One of those capabilities is generally available. The other is still in preview.

That distinction runs through the [Microsoft Ignite 2026 Book of News][book]. For this year's DevOps edition, I've picked six announcements by following a change from a developer's branch through CI and into the on-call shift. The one I'd try first isn't an agent at all: it's a disposable Azure SQL database for pull request tests.

## My Ignite shortlist

| What changes | Status on 20 November 2026 |
| --- | --- | --- |
| 1. Copilot reviews pull requests in Azure Repos | Generally available (GA) |
| 2. The Copilot app can open those PRs | Public preview |
| 3. Azure SQL Database runs in a local container | Public preview |
| 4. Azure Monitor health models track a whole workload | GA |
| 5. Azure SRE Agent can investigate from Teams | Public preview |
| 6. Chaos Studio Workspaces organise resilience tests | Workspaces GA, AKS extension in public preview |

### 1. Azure Repos: request a code review without moving your Git repository

If you own an Azure Repos Git repository, you can now [ask Copilot to review a pull request][review] as a generally available feature. An administrator enables reviews, the team can then request one manually or use a branch policy to request one automatically. Findings appear against the relevant lines of the diff. Usage is billed in GitHub AI credits to the Azure subscription linked to the Azure DevOps organisation.

One detail is easy to miss in the GitHub announcement: Azure Repos offers **Lite** and **Balanced** review effort. The **Adaptive** option announced for GitHub pull requests is a separate public preview. Don't design an Azure Repos rollout around a setting your reviewers won't see.

**What I'd do:** Start with manual requests on database changes. After ten PRs, ask the maintainers which comments led to a change they would have missed, and check what those reviews cost. That's a better basis for an automatic branch policy than a count of comments. Keep the existing rules about who approves the merge.

### 2. The Copilot app can author an Azure Repos PR, but it acts as you

The [Azure DevOps integration in the GitHub Copilot app][app] is a different release: a desktop **public preview**, off by default. A local agent session can work on a branch and open an Azure Repos PR. Cloud sessions aren't supported for these repositories. You don't need this integration to use the GA review feature above.

The important bit for platform teams is **whose permissions and name show up on the work**. According to [GitHub's integration guide][app-controls], Azure DevOps permissions still apply, there is no separate per-repository allowlist in the app, and actions appear in Azure DevOps under the signed-in user's name. If someone enables Agent Merge for a PR, the agent can complete it once the repository's checks and policies pass, without another confirmation.

For a first pilot, I'd pick a developer account that already has suitably narrow access and a task with an obvious acceptance test, such as adding a missing regression test. Let the app open the PR, leave Agent Merge off. Then have a second engineer check the diff **and** the activity history. Can they tell what was delegated before they approve it?

### 3. Azure SQL Database in a container: give each PR its own database

Two branches testing incompatible schema changes against the same staging database make for a miserable afternoon. A SQL Server container gives you isolation, but SQL Server isn't quite the target if you're deploying to Azure SQL Database. Microsoft's [new Azure SQL Database container][sql] puts that engine on a developer machine or CI runner. The public preview runs on x64 and ARM64, works offline after the image is downloaded, and doesn't require an Azure subscription for local use.

Take a change that makes a nullable column mandatory. I'd give the PR a fresh database, apply the **previous** schema, seed a row with a null, then run the proposed migration and the application query. Starting with an empty database would miss the very failure this test is supposed to catch. Tear the database down with the job so the next branch starts clean.

**Where I'd draw the line:** this is a development and CI target, not a local copy of the managed service. The [container FAQ][sql-faq] excludes backup and restore, SQL Ledger, and Azure Key Vault integration. If a release changes how encrypted data is accessed, a green container test is useful evidence about the migration, not evidence that the application can read that data in Azure. Keep that check on the managed service.

### 4. Azure Monitor health models: page on checkout, not just on CPU

Suppose database CPU spikes during a sale. The database team sees an alert, but the person carrying the pager needs a different answer: **can customers still check out?** [Azure Monitor health models are now GA][health-ga]. They let you model checkout as a workload, connect its dependencies, and roll existing monitoring signals up into a health state. A health alert can use your existing action group.

I'd start with checkout success rate and latency, with the API and database underneath. Look at a known incident alongside a harmless CPU spike. Would the model have distinguished the two? If both would have paged the checkout team, tune the roll-up before adding more resources. The [Azure Monitor guide][health] also explains billing per monitored signal. A small, useful model beats a meticulously costed map that nobody trusts at 2 am.

### 5. Azure SRE Agent in Teams: bring evidence to the incident chat

Once the checkout alert fires, someone usually leaves the incident chat to look up what changed, then pastes a summary back. In [the new Teams integration][sre], Azure SRE Agent can join the conversation, investigate connected systems and post its findings in the thread. Teams support and Microsoft Entra Agent ID are in **public preview**, the Slack integration is in **private preview**. Adding the agent to a chat doesn't grant it new Azure permissions.

My first exercise would be a read-only replay of a resolved incident. Ask for the deployment nearest the first error and the telemetry that links the two. Compare the reply with the incident timeline. A useful answer points the responder to evidence, “a deployment happened five minutes earlier” is a lead, not a root cause. I'd evaluate that before considering any permission to change a running service.

### 6. Chaos Studio Workspaces: a successful experiment isn't proof of recovery

[Azure Chaos Studio Workspaces][chaos] let a platform team scope a resilience exercise to resources it owns, discover applicable scenarios and get a report showing which actions ran or were skipped. That's a useful change from building up each experiment resource by resource. **Workspaces are GA.** Despite the broader wording in the Book of News, [the AKS extension documentation][aks] explicitly says **public preview**, with no SLA and no intended production use.

Here's where the health model earns its keep. Before a pre-production exercise, write down what the customer should experience, who should be paged, and how long recovery should take. Afterwards, compare the scenario report with the checkout health timeline. The report tells you whether the experiment ran, the timeline and your application checks tell you whether checkout recovered. Those are different results.

## My take: what I'd put in the next sprint

For an **application team**, I'd start with the SQL migration test. It addresses a familiar source of flaky CI, has a clear pass condition, and doesn't give a new tool write access to a shared environment.

For a **platform or SRE team**, I'd start with one GA health model and one question the on-call engineer struggles to answer today. A model that distinguishes “database busy” from “checkout broken” is already useful, whether or not you try SRE Agent.

For an **Azure Repos team**, I'd make two separate decisions: _do we want another reviewer?_ and _do we want software to act under a developer's identity?_ Ignite gave us options for both. It didn't make them the same decision.

### _Author_

{% user pwd9000 %}

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [X](https://x.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-pwd9000/)

Date: 20-11-2026
