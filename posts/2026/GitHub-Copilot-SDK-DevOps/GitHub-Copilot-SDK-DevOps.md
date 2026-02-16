---
title: 'GitHub Copilot SDK - Build AI-Powered DevOps Agents for Your Own Apps'
published: false
description: 'Explore the new GitHub Copilot SDK and learn how to embed agentic AI workflows into your DevOps tooling with practical use cases for infrastructure validation, incident response, and pipeline automation.'
tags: 'github, devops, githubcopilot, ai'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2026/GitHub-Copilot-SDK-DevOps/assets/main.png'
canonical_url: null
id: null
series: GitHub Copilot
date: '2026-02-16T00:00:00Z'
---

## GitHub Copilot SDK: Build AI-Powered DevOps Agents for Your Own Apps

GitHub Copilot has steadily evolved from an in-editor autocomplete tool into a full-blown agentic platform. The latest step in that journey is the **GitHub Copilot SDK**, now available in **Technical Preview**. It lets you embed the same agent runtime that powers Copilot CLI directly into your own applications, scripts, and services using **Python**, **TypeScript/Node.js**, **Go**, or **.NET**.

For DevOps engineers, this opens up a powerful new pattern: instead of relying solely on Copilot inside your IDE or through GitHub Issues, you can now build **custom AI agents** that plug into your existing operational tooling. Think incident response bots, infrastructure validators, deployment assistants, and compliance checkers, all powered by the Copilot engine and your own custom tools.

In this post we will cover what the SDK is, how it works, how to get started, and walk through four practical DevOps use cases with code samples you can adapt today.

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

Here are four practical scenarios where the Copilot SDK can add real value to a DevOps team's tooling.

### Use Case 1: Infrastructure as Code Validation Agent

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

You could run this as a pre-commit hook, a CI step, or a standalone CLI that your platform team uses during module reviews.

---

### Use Case 2: Incident Response Assistant

**The problem**: When production incidents occur, engineers spend valuable time pulling information from multiple sources: logs, metrics, deployment history, and runbooks.

**The solution**: Build an incident response agent that aggregates data from your monitoring stack and provides a situation summary.

```python
from github_copilot_sdk import CopilotClient, define_tool

@define_tool(
    name="get_recent_deployments",
    description="Get recent deployments for a service",
    parameters={
        "type": "object",
        "properties": {
            "service": {"type": "string", "description": "Service name"}
        },
        "required": ["service"]
    }
)
def get_recent_deployments(service: str):
    # In production, query your deployment API or GitHub API
    return {
        "service": service,
        "deployments": [
            {"version": "v2.4.1", "time": "2026-02-15T14:30:00Z",
             "status": "success", "deployer": "ci-pipeline"},
            {"version": "v2.4.0", "time": "2026-02-14T09:15:00Z",
             "status": "success", "deployer": "ci-pipeline"},
        ]
    }

@define_tool(
    name="query_metrics",
    description="Query application metrics for a given time range",
    parameters={
        "type": "object",
        "properties": {
            "service": {"type": "string", "description": "Service name"},
            "metric": {"type": "string", "description": "Metric name"},
            "duration": {"type": "string", "description": "Time range"}
        },
        "required": ["service", "metric", "duration"]
    }
)
def query_metrics(service: str, metric: str, duration: str):
    # In production, query Prometheus, Datadog, or Azure Monitor
    return {
        "service": service,
        "metric": metric,
        "values": [
            {"time": "14:30", "value": 45},
            {"time": "14:35", "value": 120},
            {"time": "14:40", "value": 350},
            {"time": "14:45", "value": 890},
        ]
    }

client = CopilotClient()
session = client.create_session(
    model="gpt-4.1",
    tools=[get_recent_deployments, query_metrics],
    system_message={
        "content": (
            "You are an incident response assistant for a DevOps team. "
            "When asked about an incident, gather deployment history and "
            "metrics, then provide a structured summary with: "
            "1) Timeline of events, 2) Likely root cause, "
            "3) Recommended next steps."
        )
    }
)

response = session.send_and_wait(
    prompt=(
        "The payments-api service is returning 500 errors "
        "since about 14:35 UTC. Help me investigate."
    )
)
print(response.data.content)
client.stop()
```

The agent calls your tools to gather data, correlates the deployment at 14:30 with the error spike at 14:35, and presents a clear summary. You could integrate this into a Slack bot or a Teams webhook for your on-call team.

---

### Use Case 3: Pipeline Troubleshooting Bot

**The problem**: Failed CI/CD pipelines generate long log files. Engineers often spend 15 to 30 minutes reading through logs to find the root cause.

**The solution**: Build an agent that fetches pipeline logs and analyses them.

```typescript
import { CopilotClient, defineTool } from '@github/copilot-sdk';

const getPipelineLogs = defineTool('get_pipeline_logs', {
  description:
    'Fetch the logs from a GitHub Actions workflow run',
  parameters: {
    type: 'object',
    properties: {
      runId: {
        type: 'string',
        description: 'The workflow run ID',
      },
    },
    required: ['runId'],
  },
  handler: async (args: { runId: string }) => {
    // In production, use the GitHub API:
    // GET /repos/{owner}/{repo}/actions/runs/{run_id}/logs
    return {
      runId: args.runId,
      status: 'failure',
      jobs: [
        {
          name: 'build',
          status: 'success',
          duration: '2m 14s',
        },
        {
          name: 'test',
          status: 'failure',
          duration: '4m 52s',
          error:
            "FAIL src/auth/token.test.ts - TypeError: Cannot read properties of undefined (reading 'verify')",
        },
        {
          name: 'deploy',
          status: 'skipped',
        },
      ],
    };
  },
});

const client = new CopilotClient();
const session = await client.createSession({
  model: 'gpt-4.1',
  streaming: true,
  tools: [getPipelineLogs],
  systemMessage: {
    content:
      'You are a CI/CD troubleshooting assistant. When given a failed workflow run, fetch the logs and provide: 1) Which job failed and why. 2) The likely root cause. 3) A suggested fix with code if applicable.',
  },
});

session.on('assistant.message_delta', (event) => {
  process.stdout.write(event.data.deltaContent);
});

await session.sendAndWait({
  prompt: 'Workflow run 9847 failed. What went wrong?',
});

await client.stop();
process.exit(0);
```

By connecting this to the **GitHub MCP server** instead of a mock tool, you get live access to real workflow run data without writing API integration code at all.

---

### Use Case 4: Deployment Status Dashboard Agent

**The problem**: Stakeholders constantly ask "Is feature X deployed to staging yet?" and engineers have to check multiple systems to answer.

**The solution**: Build an agent with tools that query your deployment state and present it in plain English.

```typescript
import { CopilotClient, defineTool } from '@github/copilot-sdk';

const getEnvironmentStatus = defineTool('get_environment_status', {
  description:
    'Get the current deployment status for a given environment',
  parameters: {
    type: 'object',
    properties: {
      environment: {
        type: 'string',
        description: 'Environment name (dev, staging, production)',
      },
    },
    required: ['environment'],
  },
  handler: async (args: { environment: string }) => {
    // In production, query your deployment API or Kubernetes API
    return {
      environment: args.environment,
      services: [
        {
          name: 'api-gateway',
          version: 'v3.12.0',
          lastDeployed: '2026-02-15T16:00:00Z',
          healthy: true,
        },
        {
          name: 'payments-api',
          version: 'v2.4.1',
          lastDeployed: '2026-02-15T14:30:00Z',
          healthy: false,
        },
        {
          name: 'notifications',
          version: 'v1.8.3',
          lastDeployed: '2026-02-14T11:00:00Z',
          healthy: true,
        },
      ],
    };
  },
});

const client = new CopilotClient();
const session = await client.createSession({
  model: 'gpt-4.1',
  tools: [getEnvironmentStatus],
  systemMessage: {
    content:
      'You are a deployment status assistant. Answer questions about what is deployed where, highlight any unhealthy services, and provide version comparisons across environments when asked.',
  },
});

const response = await session.sendAndWait({
  prompt:
    'What is currently deployed to staging? Are there any unhealthy services?',
});
console.log(response?.data.content);

await client.stop();
process.exit(0);
```

Wrap this in a Slack slash command or a Teams bot and your entire organisation can self-serve deployment status queries without pinging the platform team.

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

The SDK is currently in **Technical Preview** with support for **Python, TypeScript, Go, and .NET**, an MIT licence, and a growing ecosystem of MCP integrations. Whether you want to validate Terraform, triage incidents, debug pipelines, or surface deployment status, the building blocks are ready.

Check out the [GitHub Copilot SDK repository](https://github.com/github/copilot-sdk) and the [getting started guide](https://github.com/github/copilot-sdk/blob/main/docs/getting-started.md) to begin experimenting. The [cookbook and recipes](https://github.com/github/awesome-copilot/blob/main/cookbook/copilot-sdk) are also a great resource for practical patterns across all four languages.

### _Author_

{% user pwd9000 %}

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [X](https://x.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-pwd9000/)

Date: 16-02-2026
