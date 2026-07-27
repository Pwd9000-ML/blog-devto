---
title: 'Agentic DevOps Needs Observability: Trace GitHub Copilot with OpenTelemetry'
published: false
description: 'Trace GitHub Copilot agents with OpenTelemetry and Jaeger, then turn spans, metrics and events into practical DevOps signals.'
tags: 'githubcopilot, opentelemetry, devops, observability'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2026/github-copilot-opentelemetry-observability/assets/main.png'
canonical_url: null
id: null
series: GitHub Copilot - Automation
date: '2026-07-27T00:00:00Z'
---

## Agentic DevOps Needs Observability: Trace GitHub Copilot with OpenTelemetry

An agent can read files, call a model, run tools, delegate to a subagent and edit code in one request. When that request feels slow or fails, a final chat message is not enough evidence to explain what happened.

On 8 July 2026, GitHub announced [enterprise-managed OpenTelemetry export for VS Code and Copilot CLI](https://github.blog/changelog/2026-07-08-enterprise-managed-opentelemetry-export-for-vs-code-and-cli). Administrators can now direct Copilot telemetry to an approved collector and govern the endpoint, transport, resource attributes, headers and content capture.

That enterprise control builds on the OpenTelemetry support already documented in VS Code. Copilot Chat can emit traces, metrics and events for agent orchestration, model calls and tool execution. The result is operational evidence for questions such as:

- Which part of an agent request consumed the time?
- Which model or tool is producing errors?
- How many model turns does a task require?
- Are subagents linked to the parent trace?
- Is telemetry reaching the collector without capturing prompts or source code?

It is important to set the boundary early. Telemetry can show latency, errors, token use and observed user actions. It does not prove that generated code is correct, that an engineer was productive, or that an agent made a good decision. Tests, reviews and delivery outcomes remain separate evidence.

> **Current status:** Product behaviour and managed-setting values in this tutorial reflect the official documentation available on 27 July 2026. Pilot managed settings against your supported client versions before broad deployment.

---

## What You Will Build

You will run Jaeger locally in Docker, configure VS Code to export Copilot agent telemetry over OTLP/HTTP, produce an agent trace and inspect its hierarchy. Content capture remains disabled throughout the local walkthrough.

```txt
Copilot Chat in VS Code
        |
        | OTLP/HTTP on localhost:4318
        v
Jaeger all-in-one container
        |
        v
Trace UI on localhost:16686
```

The sample also includes an enterprise `managed-settings.json` shape for a later rollout. Local Jaeger uses transient in-memory storage, so this is a development exercise rather than a production observability platform.

## Prerequisites

You need:

- a current VS Code build with GitHub Copilot Chat
- Docker Desktop or Docker Engine with Docker Compose
- permission to run a local container and bind ports `16686`, `4317` and `4318`
- a workspace where you can send a harmless agent request

No GitHub enterprise administration is required for the local exercise. Enterprise-managed delivery requires the appropriate GitHub plan and administrative access.

## Step 1: Understand the Trace You Are Looking For

VS Code follows the OpenTelemetry Generative AI semantic conventions where a standard attribute exists. A typical request creates this span tree:

```txt
invoke_agent copilot
  |-- chat <model>              model requests one or more tools
  |-- execute_tool <tool-name>  VS Code runs the tool
  |-- chat <model>              model produces the next action or response
  `-- execute_hook <hook-name>  when a configured hook runs
```

`invoke_agent` wraps the full orchestration. Each `chat` span represents one model API call, while each `execute_tool` span records an individual tool invocation. A subagent receives the trace context, so its own `invoke_agent` span appears below the parent tool span when the runtime can propagate that context.

The attributes use three namespaces:

| Namespace | Purpose |
| --- | --- |
| `gen_ai.*` | OpenTelemetry GenAI semantic conventions, including operation, provider, model and token attributes |
| `github.copilot.*` | Canonical Copilot-specific attributes for new queries and dashboards |
| `copilot_chat.*` | Legacy VS Code extension attributes retained for compatibility |

Prefer `gen_ai.*` and `github.copilot.*` for new dashboards. The legacy namespace is still useful when an existing query depends on it.

Even with content capture off, metadata can include the repository remote, branch, commit SHA, GitHub organisation, model, token counts, tool names and errors. Treat that metadata according to your organisation's data classification rather than assuming that "no prompts" means "no sensitive context".

## Step 2: Start Jaeger Locally

The tutorial pins the current Jaeger 2.20 all-in-one image and binds every port to the loopback interface:

<!-- embedme code/compose.yaml -->

```yaml
services:
  jaeger:
    image: cr.jaegertracing.io/jaegertracing/jaeger:2.20.0
    ports:
      - '127.0.0.1:16686:16686'
      - '127.0.0.1:4317:4317'
      - '127.0.0.1:4318:4318'
```

From the post directory, start it:

```powershell
docker compose -f code/compose.yaml up -d
docker compose -f code/compose.yaml ps
```

Open `http://localhost:16686`. The service list can be empty because no trace has arrived yet. Port `4318` receives OTLP/HTTP, `4317` receives OTLP/gRPC, and `16686` serves the Jaeger UI.

## Step 3: Enable Copilot OpenTelemetry Without Content

Open **Preferences: Open User Settings (JSON)** in VS Code and merge these keys into your settings:

<!-- embedme code/vscode-settings.json -->

```json
{
  "github.copilot.chat.otel.enabled": true,
  "github.copilot.chat.otel.exporterType": "otlp-http",
  "github.copilot.chat.otel.otlpEndpoint": "http://localhost:4318",
  "github.copilot.chat.otel.captureContent": false
}
```

Reload VS Code after changing the configuration. Keeping `captureContent` false excludes full prompts, responses, system prompts, tool schemas, tool arguments and tool results. Metadata such as timing, model names and token counts is still emitted.

You can configure the same route with environment variables such as `OTEL_EXPORTER_OTLP_ENDPOINT`, but environment variables override user settings. A managed policy overrides both. The effective value order is managed policy, environment variable, user setting, then default.

Do not append `/v1/traces` to this base endpoint. An OTLP/HTTP exporter constructs signal-specific paths from `http://localhost:4318`.

## Step 4: Generate and Inspect a Trace

Send a small agent request that causes at least one read-only tool call:

```txt
Read package.json, explain what each script validates, and do not edit any files.
```

Wait for the response, then return to Jaeger:

1. Select `copilot-chat` in **Service**.
2. Select **Find Traces**.
3. Open the newest `invoke_agent` trace.
4. Expand the `chat` and `execute_tool` children.

Inspect the root duration first. A long root with short model spans can indicate tool or orchestration time. A long `chat` span points towards model or network latency. Repeated `chat` and `execute_tool` pairs show how many reasoning turns the task needed. An `error.type` attribute marks a failed operation.

Useful attributes include:

- `gen_ai.request.model` and `gen_ai.response.model`
- `gen_ai.usage.input_tokens` and `gen_ai.usage.output_tokens`
- `gen_ai.tool.name` and `gen_ai.tool.type`
- `github.copilot.agent.type`
- `github.copilot.git.repository`, branch and commit attributes
- `copilot_chat.time_to_first_token`

You should not see `gen_ai.input.messages`, `gen_ai.output.messages`, tool arguments or tool results because content capture is disabled.

Jaeger is ideal for this trace walkthrough, but it is not the complete destination for every emitted signal. Use an OpenTelemetry Collector with a metrics and logs backend when you want durable metrics, event analysis, retention controls and alerting.

## Step 5: Turn Signals Into Useful SLIs

Start with service level indicators that describe the system, not the developer. Set targets only after measuring a representative baseline.

| Question | Signal | Example SLI |
| --- | --- | --- |
| Are agent requests completing promptly? | `copilot_chat.agent.invocation.duration` | 95th percentile end-to-end duration below a team-defined threshold |
| Are model calls responsive? | `gen_ai.client.operation.duration` and `copilot_chat.time_to_first_token` | 95th percentile model duration and time to first token |
| Are tools reliable? | `copilot_chat.tool.call.count`, duration and `error.type` | Successful tool calls divided by all tool calls, grouped by tool |
| Are tasks looping? | `copilot_chat.agent.turn.count` | Percentage of invocations above a reviewed turn-count threshold |
| Is token demand changing? | `gen_ai.client.token.usage` | Input and output token distribution by resolved model |
| Are edits retained? | edit acceptance and survival metrics | Trend for investigation, never a correctness score |

Events add detail around individual moments. Examples include `copilot_chat.session.start`, `copilot_chat.tool.call`, `copilot_chat.agent.turn`, edit feedback and cloud-session invocation. Use them to explain a metric change, such as which tool began failing after an extension update.

Avoid leaderboards based on token counts, accepted lines or session volume. More activity can mean harder work, unnecessary loops or a misconfigured agent. Edit acceptance and survival are behavioural observations, not proof of quality or productivity.

## Step 6: Apply Privacy Before Scale

OpenTelemetry is off by default, and content capture is separately opt-in. Keep that separation in production.

A practical privacy review should cover:

- data categories in attributes, events and optional content
- approved collector endpoints and TLS validation
- access control for traces, metrics and logs
- retention, deletion and regional storage requirements
- sampling and attribute limits
- repository URLs, branch names and commit identifiers
- whether prompts, file contents or tool results are ever justified

If content is required for a short investigation, use a restricted pilot, a defined expiry and a collector with suitable access controls. Return to metadata-only capture afterwards. Observability data should not become an ungoverned copy of source code and conversations.

## Step 7: Manage Configuration Centrally

The 8 July announcement lets administrators deliver a `telemetry` block through native MDM, server-managed settings or a protected file. This example keeps content disabled and locked:

<!-- embedme code/managed-settings.json -->

```json
{
  "telemetry": {
    "enabled": true,
    "endpoint": "https://otel-gateway.corp.example",
    "protocol": "http/protobuf",
    "captureContent": false,
    "lockCaptureContent": true,
    "serviceName": "github-copilot",
    "resourceAttributes": {
      "deployment.environment": "production",
      "team.name": "developer-platform"
    },
    "headers": {
      "X-Scope-OrgID": "developer-platform"
    }
  }
}
```

The header is deliberately non-secret. Supply real collector credentials through your managed delivery system, never in a repository. Managed exporter headers are applied only to the Copilot Chat extension exporter and are not copied into environment variables, which prevents them leaking into tool subprocesses. In the current release, those managed headers are also not delivered to the agent host process, so test authentication for every client path.

Two precedence rules matter:

1. For managed channels, native MDM wins over server-managed settings, which wins over file-based settings. From VS Code 1.128, the highest channel that supplies any managed settings wins outright rather than merging with lower channels.
2. For each telemetry value, policy wins over environment variables, user settings and defaults.

On Windows, native settings use `HKEY_LOCAL_MACHINE\SOFTWARE\Policies\GitHubCopilot`. File-based settings use `%ProgramFiles%\GitHubCopilot\managed-settings.json`. Server-managed settings come from `copilot/managed-settings.json` in the selected `.github-private` governance repository.

File-based settings should be administrator-owned, not world-writable and not symlinked. Use **Developer: Policy Diagnostics** to confirm the active channel. Reload VS Code when telemetry policy changes because the agent host resolves its configuration at startup.

There is one vocabulary caveat. The VS Code user setting uses exporter values such as `otlp-http` and `otlp-grpc`, while the current GitHub managed-settings reference lists `http/json` and `http/protobuf` for `telemetry.protocol`. The launch announcement also mentions gRPC. Treat the live managed-settings reference and your deployed client build as the contract during a pilot rather than copying a user-setting value blindly.

## Copilot CLI Transport Caveats

Not every CLI trace has the same parentage.

- A background Copilot CLI agent hosted by VS Code produces a `copilot-chat` wrapper span with native `github-copilot` SDK spans beneath it in the same trace.
- A terminal CLI session runs in a separate process. It emits independent root traces under service `github-copilot`, so it is not linked to the extension trace.
- The terminal CLI runtime supports OTLP/HTTP only. If gRPC is configured, it still uses HTTP. Point it at an HTTP-capable port such as `4318` unless the backend deliberately serves both protocols on one port.

Search both `copilot-chat` and `github-copilot` before concluding that telemetry is missing. Also verify that collector authentication works for the agent host and terminal process, especially when the extension receives a managed header that those paths do not.

## OpenTelemetry Is Not Session Audit Streaming

GitHub's [Copilot agent session streaming](https://github.blog/changelog/2026-07-02-copilot-agent-session-streaming-is-now-in-public-preview) is a separate enterprise capability. It sends Copilot usage records across supported clients to an audit stream or exposes the latest records through an enterprise REST API. It is designed for central auditability and can include session prompts, responses and tool calls when enabled.

OpenTelemetry is client-side operational instrumentation sent to an OTLP collector selected by the user or administrator. It gives detailed timing, hierarchy, errors, model metadata and tool telemetry.

Use OTel for reliability engineering and trace diagnosis. Use session audit streaming for enterprise governance, compliance and cross-client activity records. One does not replace the other, and their access, retention and privacy decisions should be reviewed independently.

## Troubleshooting

### Jaeger has no `copilot-chat` service

Confirm the container is running, the endpoint is `http://localhost:4318`, OTel is enabled and VS Code was reloaded. Send a new request after enabling telemetry because earlier sessions are not backfilled.

### The collector returns `404` or connection errors

Use the base OTLP/HTTP endpoint without `/v1/traces`. Check that port `4318` is published and that a proxy or endpoint security rule is not intercepting loopback traffic.

### CLI traces appear disconnected

That is expected for terminal CLI sessions. Search the `github-copilot` service. Only background CLI sessions hosted in the VS Code process share the extension trace.

### Prompt or tool content is absent

That is the expected result with `captureContent: false`. Do not enable content merely to make a trace look richer. Start with metadata and use VS Code's Agent Debug Log for local diagnosis where appropriate.

### A user setting has no effect

Check environment variables and **Developer: Policy Diagnostics**. Managed values override environment variables and user settings, while environment variables override user settings.

### Metrics do not appear in Jaeger

Jaeger is the trace viewer in this tutorial. Route the emitted metrics and events through an OpenTelemetry Collector to a backend that supports those signal types.

## Cleanup and Rollout

Stop and remove the local container:

```powershell
docker compose -f code/compose.yaml down --remove-orphans
```

For enterprise rollout, begin with a small device group and metadata-only capture. Confirm endpoint authentication, both service names, CLI transport behaviour and policy precedence. Then define a short list of reliability SLIs, retention controls and alert owners. Review false alarms before expanding coverage.

Correlate telemetry with tests, review findings, incidents and deployment outcomes when evaluating an agentic workflow. Keep those evidence sources distinct. A fast, low-token trace can still produce an incorrect change, while a slow trace may reflect a genuinely difficult task.

## Authoritative Sources

- [GitHub Changelog: Enterprise-managed OpenTelemetry export for VS Code and CLI](https://github.blog/changelog/2026-07-08-enterprise-managed-opentelemetry-export-for-vs-code-and-cli)
- [VS Code: Monitor agent usage with OpenTelemetry](https://code.visualstudio.com/docs/agents/guides/monitoring-agents)
- [VS Code: Configure telemetry export with OpenTelemetry](https://code.visualstudio.com/docs/enterprise/ai-settings#_configure-telemetry-export-with-opentelemetry)
- [GitHub Docs: Enterprise managed settings reference](https://docs.github.com/copilot/reference/enterprise-managed-settings-reference)
- [GitHub Docs: Streaming the audit log for your enterprise](https://docs.github.com/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/streaming-the-audit-log-for-your-enterprise)
- [Jaeger: Getting started](https://www.jaegertracing.io/docs/2.20/getting-started/)
- [OpenTelemetry: OTLP exporter configuration](https://opentelemetry.io/docs/languages/sdk-configuration/otlp-exporter/)

## Conclusion

Agentic DevOps needs the same operational discipline as any other distributed system. A connected `invoke_agent` trace makes model calls, tools, hooks and subagents inspectable without capturing conversation content by default. Start locally, establish reliable signals, govern the export path and keep correctness claims tied to engineering evidence rather than telemetry volume.

### _Author_

{% user pwd9000 %}

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [X](https://x.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-pwd9000/)

Date: 27-07-2026
