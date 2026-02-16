---
title: GitHub Copilot SDK - Build AI-Powered DevOps Agents for Your Own Apps
published: false
description: 'Explore the new GitHub Copilot SDK and learn how to embed agentic AI workflows into your DevOps tooling with practical use cases for infrastructure validation, incident response, and pipeline automation.'
tags: 'github, devops, githubcopilot, ai'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2026/GitHub-Copilot-SDK-DevOps/assets/main.png'
canonical_url: null
id: 3259554
series: GitHub Copilot
---

## GitHub Copilot SDK: Build AI-Powered DevOps Agents for Your Own Apps

GitHub Copilot has steadily evolved from an in-editor autocomplete tool into a full-blown agentic platform. The latest step in that journey is the **GitHub Copilot SDK**, now available in **Technical Preview**. It lets you embed the same agent runtime that powers Copilot CLI directly into your own applications, scripts, and services using **Python**, **TypeScript/Node.js**, **Go**, or **.NET**.

For DevOps engineers, this opens up a powerful new pattern: instead of relying solely on Copilot inside your IDE or through GitHub Issues, you can now build **custom AI agents** that plug into your existing operational tooling. Think incident response bots, infrastructure validators, deployment assistants, and compliance checkers, all powered by the Copilot engine and your own custom tools.

In this post we will cover what the SDK is, how it works, how to get started, and walk through six practical DevOps use cases, several drawn from real open-source projects you can explore today.

---

## What Is the GitHub Copilot SDK?

The [GitHub Copilot SDK](https://github.com/github/copilot-sdk) is a set of multi-platform libraries that expose the **Copilot CLI agent runtime** as a programmable interface. Rather than building your own LLM orchestration layer, you get the same production-tested engine that handles planning, tool invocation, file edits, and multi-turn conversations.

### Key Facts

| Detail | Value |
| --- | --- |
| **Repository** | [github/copilot-sdk](https://github.com/github/copilot-sdk) |
| **Status** | Technical Preview |
| **Languages** | TypeScript/Node.js, Python, Go, .NET |
| **Licence** | MIT |
| **Auth** | GitHub OAuth, environment variables (`GITHUB_TOKEN`), or BYOK |
| **Billing** | Counts against your Copilot premium request quota |

### Architecture

All four SDKs share the same communication model. Your application talks to the SDK client, which communicates with the Copilot CLI running in server mode over **JSON-RPC**:

```text
Your Application
       ↓
  SDK Client
       ↓  JSON-RPC
  Copilot CLI (server mode)
```

The SDK **manages the CLI process lifecycle automatically** by default. You can also run the CLI externally in headless server mode and point multiple SDK clients at it, which is useful for shared development environments or debugging.

### What You Can Do

- **Send prompts** and receive responses (streaming or complete).
- **Define custom tools** that the agent can call, with typed parameters and handler functions you control.
- **Connect to MCP servers** (Model Context Protocol) to give the agent access to external services like the GitHub API, databases, or cloud provider tooling.
- **Create custom agents** with specialised personas, system messages, and tool sets.
- **Use any supported model**, including those available through Copilot or your own keys via BYOK (Bring Your Own Key) from providers like OpenAI, Azure AI Foundry, and Anthropic.

---

## Getting Started

### Prerequisites

1. **GitHub Copilot subscription** (Free tier with limited usage, or Pro/Pro+/Business/Enterprise). If using BYOK, no GitHub auth is required.
2. **Copilot CLI** installed and authenticated. Follow the [Copilot CLI installation guide](https://docs.github.com/en/copilot/how-tos/set-up/install-copilot-cli).
3. Your preferred language runtime: **Node.js 18+**, **Python 3.8+**, **Go 1.21+**, or **.NET 8.0+**.

Verify the CLI is working:

```bash
copilot --version
```

### Install the SDK

Pick your language:

```bash
# Node.js / TypeScript
npm install @github/copilot-sdk

# Python
pip install github-copilot-sdk

# Go
go get github.com/github/copilot-sdk/go

# .NET
dotnet add package GitHub.Copilot.SDK
```

### Your First Five Lines

Here is the simplest possible example in TypeScript. It creates a client, opens a session, sends a prompt, and prints the response:

```typescript
import { CopilotClient } from '@github/copilot-sdk';

const client = new CopilotClient();
const session = await client.createSession({ model: 'gpt-4.1' });

const response = await session.sendAndWait({
  prompt: 'What is 2 + 2?',
});
console.log(response?.data.content);

await client.stop();
process.exit(0);
```

And the Python equivalent:

```python
from github_copilot_sdk import CopilotClient

client = CopilotClient()
session = client.create_session(model="gpt-4.1")

response = session.send_and_wait(prompt="What is 2 + 2?")
print(response.data.content)

client.stop()
```

That is it. Five lines to get a Copilot-powered response in your own application.

---

## Adding Streaming and Custom Tools

The real power of the SDK emerges when you add **streaming responses** and **custom tools**. Streaming gives your users real-time feedback while the agent works. Custom tools let the agent call functions you define, bridging the gap between the LLM and your operational systems.

### Streaming Example (TypeScript)

```typescript
import { CopilotClient } from '@github/copilot-sdk';

const client = new CopilotClient();
const session = await client.createSession({
  model: 'gpt-4.1',
  streaming: true,
});

session.on('assistant.message_delta', (event) => {
  process.stdout.write(event.data.deltaContent);
});
session.on('session.idle', () => {
  console.log();
});

await session.sendAndWait({
  prompt: 'Explain blue-green deployments in three sentences.',
});

await client.stop();
process.exit(0);
```

### Custom Tool Example (TypeScript)

```typescript
import { CopilotClient, defineTool } from '@github/copilot-sdk';

const checkPodStatus = defineTool('check_pod_status', {
  description: 'Check the status of Kubernetes pods in a namespace',
  parameters: {
    type: 'object',
    properties: {
      namespace: {
        type: 'string',
        description: 'The Kubernetes namespace',
      },
    },
    required: ['namespace'],
  },
  handler: async (args: { namespace: string }) => {
    // In a real scenario, call kubectl or the Kubernetes API here
    return {
      namespace: args.namespace,
      pods: [
        { name: 'api-server-1', status: 'Running', restarts: 0 },
        { name: 'api-server-2', status: 'CrashLoopBackOff', restarts: 12 },
        { name: 'worker-1', status: 'Running', restarts: 0 },
      ],
    };
  },
});
```

When the agent receives a question like "Are there any unhealthy pods in the production namespace?", it decides to call your `check_pod_status` tool, receives the result, and incorporates it into a natural-language response.

---

## Connecting to MCP Servers

The SDK supports [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) servers out of the box. MCP provides a standardised way for AI agents to interact with external tools and data sources. This is especially relevant for DevOps because you can connect the agent to GitHub, cloud providers, databases, and monitoring APIs without writing custom tool handlers for each one.

For example, connecting to GitHub's MCP server gives the agent access to repositories, issues, pull requests, and more:

```typescript
const session = await client.createSession({
  mcpServers: {
    github: {
      type: 'http',
      url: 'https://api.githubcopilot.com/mcp/',
    },
  },
});
```

You can also connect to local MCP servers. For example, an Azure Bicep schema server:

```json
{
  "mcpServers": {
    "AzureBicep": {
      "type": "local",
      "command": "npx",
      "args": [
        "-y",
        "@azure/mcp@latest",
        "server",
        "start",
        "--namespace",
        "bicepschema",
        "--read-only"
      ]
    }
  }
}
```

The [MCP Servers Directory](https://github.com/modelcontextprotocol/servers) maintains a growing catalogue of community servers, including integrations for Terraform, Docker, Prometheus, and many other DevOps-adjacent tools.

---

## DevOps Use Cases

The SDK is still young, but the community is already building real tools with it. Here are six use cases, several drawn from actual open-source projects and the official cookbook, that show what is possible for DevOps teams.

### Use Case 1: Autonomous SRE Agent for GitHub Actions

**Real project**: [htekdev/github-sre-agent](https://github.com/htekdev/github-sre-agent)

This open-source project is a fully autonomous SRE agent built with the Copilot SDK. It listens for GitHub Actions webhook events and, when a workflow fails, it:

1. **Fetches and analyses logs** via the GitHub MCP server.
2. **Checks GitHub system status** to rule out platform outages.
3. **Searches the web** for known fixes using the Exa AI MCP server.
4. **Makes an intelligent decision**: retry a transient failure, create a detailed issue for a genuine bug, or skip if the failure is expected.
5. **Tracks resolution**: when a previously failed workflow succeeds, it automatically closes the related issue.

The architecture is clean and worth studying. It uses the Copilot SDK's `createSession` with two MCP servers (GitHub and Exa AI) plus custom tools for status checking, note-taking, and workflow tracking. Repository-level configuration lives in `.github/sre-agent.yml`:

```yaml
version: 1
enabled: true
instructions: |
  - This repo uses pnpm, not npm
  - Always check if tests pass before suggesting retry
  - Create issues with label "ci-failure" for tracking
actions:
  retry:
    enabled: true
    maxAttempts: 3
  createIssue:
    enabled: true
    labels:
      - sre-agent
      - automated
      - ci-failure
```

This is a strong example of how the SDK can replace manual on-call triage for CI/CD failures.

---

### Use Case 2: Repository Health Analysis (Repo Doctor)

**Real project**: [glaucia86/repo-doctor](https://github.com/glaucia86/repo-doctor) (53+ stars)

Repo Doctor is an agentic CLI tool built with the Copilot SDK that performs comprehensive health checks across six areas: **documentation**, **developer experience**, **CI/CD**, **testing**, **governance**, and **security**. It delivers a health score (0-100%), prioritised findings (P0/P1/P2), and actionable remediation steps with code snippets.

It offers two analysis modes:

| Mode | How it works | Best for |
| --- | --- | --- |
| **Quick Scan** | Analyses via GitHub API (up to 20 file reads) | Governance review, quick checks |
| **Deep Analysis** | Full source scan using Repomix | Code quality, architecture review |

The killer feature for DevOps teams is the `--issue` flag. After analysis, it automatically creates structured GitHub Issues for each problem found, complete with priority labels, impact assessments, and fix instructions:

```bash
repo-doctor analyze your-org/your-repo --issue

# Creates:
# 🔴 [Repo Doctor] docs: Missing README
# 🟠 [Repo Doctor] ci: No CI/CD Pipeline
# 🟡 [Repo Doctor] dx: Code Quality Issues
```

This pattern, using the SDK to audit repositories and create actionable issues, is directly applicable to platform engineering teams managing dozens of microservice repos.

---

### Use Case 3: Autonomous Coding Loops (Ralph Loop Pattern)

**Source**: [Official Copilot SDK Cookbook](https://github.com/github/awesome-copilot/blob/main/cookbook/copilot-sdk/nodejs/ralph-loop.md)

The Ralph Loop is an autonomous development pattern from the SDK cookbook that is particularly powerful for DevOps automation. The concept: an AI agent iterates through tasks in isolated context windows, with state persisted on disk between iterations. Each loop creates a **fresh session**, reads the current state, does one task, writes results back, and exits.

```typescript
import { readFile } from 'fs/promises';
import { CopilotClient } from '@github/copilot-sdk';

async function ralphLoop(promptFile: string, maxIterations: number = 50) {
  const client = new CopilotClient();
  await client.start();

  try {
    const prompt = await readFile(promptFile, 'utf-8');

    for (let i = 1; i <= maxIterations; i++) {
      console.log(`\n=== Iteration ${i}/${maxIterations} ===`);

      // Fresh session each iteration. Context isolation is the point
      const session = await client.createSession({
        model: 'gpt-4.1',
        workingDirectory: process.cwd(),
        onPermissionRequest: async () => ({ allow: true }),
      });

      try {
        await session.sendAndWait({ prompt }, 600_000);
      } finally {
        await session.destroy();
      }

      console.log(`Iteration ${i} complete.`);
    }
  } finally {
    await client.stop();
  }
}

ralphLoop('PROMPT.md', 20);
```

For DevOps, imagine pointing this at an `IMPLEMENTATION_PLAN.md` that lists infrastructure tasks: "add monitoring to service X", "update Terraform module Y to v2", "write integration tests for pipeline Z". The agent picks the next task, implements it, runs tests, commits, and moves on. The key principles:

- **Fresh context per iteration** prevents context window degradation.
- **Disk as shared state** (`IMPLEMENTATION_PLAN.md`) coordinates between iterations.
- **Backpressure** (tests, builds, lints) ensures quality, the agent must pass them before committing.

This is ideal for burning down infrastructure debt or implementing a batch of related IaC changes unattended.

---

### Use Case 4: Incident Response with PagerDuty and Datadog

**Source**: [microsoft/copilot-sdk-samples](https://github.com/microsoft/copilot-sdk-samples)

Microsoft's official sample repository includes dedicated **PagerDuty** and **Datadog** connector samples that demonstrate how to build incident management and monitoring agents. All connectors support a **mock-first** design, so you can develop and test without live credentials.

Here is how you might wire up an incident response agent that combines both:

```typescript
import { CopilotClient, defineTool } from '@github/copilot-sdk';

// Tools backed by your PagerDuty and Datadog connectors
const getActiveIncidents = defineTool('get_active_incidents', {
  description: 'List active PagerDuty incidents for a service',
  parameters: {
    type: 'object',
    properties: {
      service: { type: 'string', description: 'Service name' },
    },
    required: ['service'],
  },
  handler: async (args: { service: string }) => {
    // In production, call PagerDuty API
    return {
      incidents: [
        {
          id: 'PD-4521',
          title: 'High error rate on payments-api',
          severity: 'P1',
          triggered: '2026-02-15T14:32:00Z',
          assignee: 'on-call-team',
        },
      ],
    };
  },
});

const queryMonitoring = defineTool('query_monitoring', {
  description: 'Query Datadog metrics and logs',
  parameters: {
    type: 'object',
    properties: {
      query: { type: 'string', description: 'Datadog query string' },
      timeRange: { type: 'string', description: 'Time range (e.g. last_1h)' },
    },
    required: ['query', 'timeRange'],
  },
  handler: async (args: { query: string; timeRange: string }) => {
    // In production, call Datadog API
    return {
      metrics: {
        errorRate: '12.4%',
        p99Latency: '2340ms',
        requestsPerSecond: 890,
      },
      recentLogs: [
        'ERROR: Connection pool exhausted for database replica-02',
        'WARN: Retry limit exceeded for downstream service auth-api',
      ],
    };
  },
});

const client = new CopilotClient();
const session = await client.createSession({
  model: 'gpt-4.1',
  streaming: true,
  tools: [getActiveIncidents, queryMonitoring],
  systemMessage: {
    content:
      'You are an incident response assistant. When asked about an incident, ' +
      'gather data from PagerDuty and Datadog, then provide: ' +
      '1) Incident timeline, 2) Affected services and metrics, ' +
      '3) Likely root cause, 4) Recommended remediation steps.',
  },
});

session.on('assistant.message_delta', (event) => {
  process.stdout.write(event.data.deltaContent);
});

await session.sendAndWait({
  prompt:
    'We have a P1 incident on payments-api. Pull the PagerDuty details and check Datadog for the last hour.',
});

await client.stop();
process.exit(0);
```

You could deploy this as a Slack bot, a Teams webhook, or a CLI tool for your on-call team. The agent correlates PagerDuty incident metadata with Datadog metrics and logs, then produces a structured summary with remediation steps.

---

### Use Case 5: PR Age Visualisation and Repository Insights

**Source**: [Official Copilot SDK Cookbook: PR Visualization](https://github.com/github/awesome-copilot/blob/main/cookbook/copilot-sdk/nodejs/pr-visualization.md)

This cookbook recipe demonstrates a powerful pattern: using the SDK with **zero custom tools**. Instead, it relies entirely on the Copilot CLI's built-in capabilities, the GitHub MCP server for fetching PR data, file tools for saving charts, and code execution for generating visualisations.

The core setup is refreshingly simple. No `defineTool` calls, just a session with a system message and a prompt:

```typescript
import { CopilotClient } from '@github/copilot-sdk';

const client = new CopilotClient({ logLevel: 'error' });

const session = await client.createSession({
  model: 'gpt-4.1',
  systemMessage: {
    content: `You are analyzing pull requests for the GitHub repository: ${owner}/${repo}.
Use the GitHub MCP Server tools to fetch PR data.
Use your file and code execution tools to generate charts.
Save any generated images to the current working directory.`,
  },
});

await session.sendAndWait({
  prompt: `Fetch the open pull requests for ${owner}/${repo} from the last week.
Calculate the age of each PR in days.
Generate a bar chart showing the distribution of PR ages.
Save the chart as "pr-age-chart.png".
Summarise the PR health - average age, oldest PR, and how many might be stale.`,
});
```

The agent uses the GitHub MCP server to list PRs, then generates a chart using Python/matplotlib. The interactive session lets you ask follow-up questions like "expand to the last month" or "group by author instead of age".

For DevOps leads, this pattern is gold. Build a scheduled job that runs this weekly and posts the chart to a Slack channel. No API integration code to maintain, just prompts.

---

### Use Case 6: Infrastructure as Code Validation Agent

**The problem**: Your team maintains dozens of Terraform modules. Reviewing them for best practices, security compliance, and naming conventions is time-consuming and inconsistent.

**The solution**: Build a CLI tool that reads a Terraform directory and asks the Copilot agent to validate it against your organisation's policies.

```typescript
import { CopilotClient, defineTool } from '@github/copilot-sdk';
import * as fs from 'fs';
import * as path from 'path';

const readTerraformFiles = defineTool('read_terraform_files', {
  description: 'Read all .tf files from a directory',
  parameters: {
    type: 'object',
    properties: {
      directory: {
        type: 'string',
        description: 'Path to the Terraform module directory',
      },
    },
    required: ['directory'],
  },
  handler: async (args: { directory: string }) => {
    const files = fs
      .readdirSync(args.directory)
      .filter((f) => f.endsWith('.tf'));
    const contents: Record<string, string> = {};
    for (const file of files) {
      contents[file] = fs.readFileSync(
        path.join(args.directory, file),
        'utf-8'
      );
    }
    return contents;
  },
});

const client = new CopilotClient();
const session = await client.createSession({
  model: 'gpt-4.1',
  streaming: true,
  tools: [readTerraformFiles],
  systemMessage: {
    content: `You are an infrastructure validation agent. When given a Terraform directory, read the files and check for:
1. All resources must include tags: Environment, Owner, CostCentre
2. No hardcoded secrets or credentials
3. Backend configuration must use remote state (azurerm or s3)
4. All variables must have descriptions and type constraints
5. Module sources must use version pinning
Report findings as a structured checklist with pass/fail for each rule.`,
  },
});

session.on('assistant.message_delta', (event) => {
  process.stdout.write(event.data.deltaContent);
});

await session.sendAndWait({
  prompt: 'Please validate the Terraform module at ./modules/networking',
});

await client.stop();
```

You could run this as a pre-commit hook, a CI step, or a standalone CLI that your platform team uses during module reviews. Combine it with the Ralph Loop pattern from Use Case 3 to validate and fix an entire library of modules autonomously.

---

## Authentication Options

The SDK supports several authentication methods, giving you flexibility for different environments:

| Method | Use Case |
| --- | --- |
| **GitHub signed-in user** | Local development; uses stored OAuth credentials from `copilot` CLI login |
| **OAuth GitHub App** | Web applications; pass user tokens from your GitHub OAuth app |
| **Environment variables** | CI/CD pipelines; set `COPILOT_GITHUB_TOKEN`, `GH_TOKEN`, or `GITHUB_TOKEN` |
| **BYOK (Bring Your Own Key)** | Air-gapped or custom environments; use your own API keys from OpenAI, Azure AI Foundry, or Anthropic |

For CI/CD integration, environment variables are the most practical. For internal tools, the GitHub OAuth flow gives you per-user billing and audit trails.

> **Note**: BYOK uses key-based authentication only. Microsoft Entra ID (Azure AD), managed identities, and third-party identity providers are not supported at this time.

---

## Tips for DevOps Teams

**Start with a well-defined problem.** The SDK is not a magic box. It works best when you give the agent a clear task, the right tools, and a focused system message. "Analyse these logs and find errors" will outperform "do DevOps stuff."

**Use system messages to encode your standards.** The `systemMessage` field is your equivalent of a runbook. Tell the agent about your naming conventions, required tags, preferred tools, and escalation procedures.

**Combine custom tools with MCP servers.** Use MCP for standard integrations (GitHub API, cloud providers) and custom tools for your organisation-specific logic (internal APIs, proprietary systems).

**Keep tools focused.** Each tool should do one thing well. An agent with ten small, focused tools will perform better than one with three large, multi-purpose tools.

**Review and validate.** The SDK is in Technical Preview. Always review agent outputs before acting on them in production, especially for infrastructure changes or incident response recommendations.

**Be mindful of billing.** Each prompt counts against your Copilot premium request quota. For high-volume automation, consider batching requests and caching responses where appropriate.

---

## Conclusion

The **GitHub Copilot SDK** brings agentic AI out of the IDE and into your operational tooling. For DevOps engineers, this means you can build custom agents that understand your infrastructure, your workflows, and your conventions, and embed them wherever they are most useful: CLI tools, chatbots, CI pipelines, or internal platforms.

The community is already proving the concept. Projects like [github-sre-agent](https://github.com/htekdev/github-sre-agent) (autonomous CI/CD failure triage), [repo-doctor](https://github.com/glaucia86/repo-doctor) (repository health analysis), and Microsoft's [copilot-sdk-samples](https://github.com/microsoft/copilot-sdk-samples) (PagerDuty and Datadog integrations) show that this is not theoretical. The official [cookbook](https://github.com/github/awesome-copilot/blob/main/cookbook/copilot-sdk) adds patterns like Ralph Loops for autonomous task iteration and PR visualisation using zero custom tools.

The SDK is currently in **Technical Preview** with support for **Python, TypeScript, Go, and .NET**, an MIT licence, and a growing ecosystem of MCP integrations. Whether you want to automate SRE workflows, audit repositories, triage incidents, or visualise PR health, the building blocks are ready.

Check out the [GitHub Copilot SDK repository](https://github.com/github/copilot-sdk) and the [getting started guide](https://github.com/github/copilot-sdk/blob/main/docs/getting-started.md) to begin experimenting.

### _Author_

{% user pwd9000 %}

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [X](https://x.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-pwd9000/)

Date: 16-02-2026
