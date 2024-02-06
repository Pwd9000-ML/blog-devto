---
title: GitHub + Dev Hackathon 2023 - Self-hosted Azure Pipelines Agent Codespace/Dev Container
published: true
description: GitHub + DEV Hackathon 2023 Submission - Self-hosted Azure Pipelines Agent Codespace/Dev Container
tags: 'githubhack23, codespaces, devcontainers, cicd'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Dev-Hackathon-2023/assets/main01.png'
canonical_url: null
id: 1461121
series: Hackathons
date: '2023-05-08T10:34:38Z'
---

## What I built

Created a community **Codespace** that has an **Azure Pipelines agent** built into the Codespace. The Codespace can register itself via **[Codepsace Secrets](https://docs.github.com/en/codespaces/managing-your-codespaces/managing-encrypted-secrets-for-your-codespaces?wt.mc_id=DT-MVP-5004771)** as a self-hosted **Azure pipelines agent** into an Azure DevOps **Agent pool**, and be used to run Azure pipelines using the compute power of the Codespace.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Codespaces-DevOps-Agent/assets/diag01.png)

### Category Submission

👷 DIY Deployments 👷

### App Link

<https://containers.dev/templates>

| Template Name | Maintainer |
| --- | --- |
| [Azure Pipelines Agent](https://github.com/Pwd9000-ML/devcontainer-templates/tree/main/src/azure-pipelines-agent-devcontainer) | Marcel Lupo @Pwd9000-ML |

### Screenshots

- Add [Codespace secrets](https://docs.github.com/en/codespaces/managing-your-codespaces/managing-encrypted-secrets-for-your-codespaces?wt.mc_id=DT-MVP-5004771) on the GitHub repository where the Codespace is to be spun up

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Dev-Hackathon-2023/assets/sec02.png)

- Select `Add Dev Container Configuration Files...`

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-ADO-Codespace-video/assets/add01.png)

- Select `Create a new configuration...`

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-ADO-Codespace-video/assets/add02.png)

- Select `Show All Definitions...`

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-ADO-Codespace-video/assets/add03.png)

- Select `Azure Pipelines Agent`

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-ADO-Codespace-video/assets/add04.png)

Self hosted Azure Pipelines agent registers on agent pool and runs inside Codespace at launch

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Codespaces-DevOps-Agent/assets/run06.png)

### Description

_Use and utelise your codespace compute power to also run a self hosted azure pipelines agent. This devcontainer can be used as a codespace that will create and attach a `self-hosted azure pipelines agent` inside of the codespace and attach/register the ADO agent with an Azure DevOps agent pool by using `secrets for codespaces` as parameter values:_

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Dev-Hackathon-2023/assets/sec02.png)

### Link to Source Code

<https://github.com/Pwd9000-ML/devcontainer-templates/tree/main/src/azure-pipelines-agent-devcontainer>

### Permissive License

[MIT LICENSE](https://github.com/Pwd9000-ML/Azure-Service-Bus-SAS-Management/blob/master/LICENSE)

## Background (What made you decide to build this particular app? What inspired you?)

Wanted to create a way to be able to **build** as well as **test** my Azure Pipelines (CI/CD) processes, but not have the hassle and costs of building a separate self hosted agent. To instead utilise the same **Codespace** I'm already working in to also use as my Azure Pipelines agent.

### How I built it (How did you utilize GitHub Actions or GitHub Codespaces? Did you learn something new along the way? Pick up a new skill?)

Learned how to create community **Codepsaces** to contribute to the wider Dev community and I hope that many others will find my Codespace useful and also contribute to making it even better.

## Video Tutorial - How to use

{% youtube 4CPoHrLgO1E %}

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
