---
title: Self-hosted Azure Pipelines Agent Codespace/Dev Container
published: true
description: GitHub + DEV Hackathon 2023 Submission - Self-hosted Azure Pipelines Agent Codespace/Dev Container
tags: 'githubhack23, codespaces, devcontainers, cicd'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Dev-Hackathon-2023/assets/main1.png'
canonical_url: null
id: 1461121
series: Hackathons
---

## What I built

I built and published a community **Codespace** that has an **Azure Pipelines agent** built into the Codespace. The Codespace can register itself via **Codepsace Secrets** as a self-hosted **Azure pipelines agent** into an Azure DevOps **Agent pool**, and be used to run Azure pipelines using the compute power of the Codespace.

### Category Submission

👷 DIY Deployments 👷

### App Link

<https://containers.dev/templates>

| Template Name | Maintainer |
| --- | --- |
| [Azure Pipelines Agent](https://github.com/Pwd9000-ML/devcontainer-templates/tree/main/src/azure-pipelines-agent-devcontainer) | Marcel Lupo @Pwd9000-ML |

### Screenshots

### Description

_Use and utelise your codespace compute power to also run a self hosted azure pipelines agent. This devcontainer can be used as a codespace that will create and attach a `self-hosted azure pipelines agent` inside of the codespace and attach/register the ADO agent with an Azure DevOps agent pool by using `secrets for codespaces` as parameter values:_

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Dev-Hackathon-2023/assets/sec02.png)

### Link to Source Code

{% github <https://github.com/Pwd9000-ML/devcontainer-templates/tree/main/src/azure-pipelines-agent-devcontainer> %}

- [README](https://github.com/Pwd9000-ML/devcontainer-templates/blob/main/src/azure-pipelines-agent-devcontainer/README.md)

### Permissive License

- [MIT LICENSE](https://github.com/Pwd9000-ML/Azure-Service-Bus-SAS-Management/blob/master/LICENSE)

## Background (What made you decide to build this particular app? What inspired you?)

I wanted a way to be able to **build** as well as **test** my Azure Pipelines (CI/CD) processes, but not have the hassle and costs of building a separate self hosted agent. I wanted to instead use the same **Codespace** I am already working in to also use as my Azure Pipelines Agent.

### How I built it (How did you utilize GitHub Actions or GitHub Codespaces? Did you learn something new along the way? Pick up a new skill?)

I learned how to make community **Codepsaces** to contribute to the wider Dev community and I hope that many others will find my Codespace useful and also contribute to making it even better.

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
