---
title: Self-hosted Azure Pipelines Agent Codespace/Dev Container
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

I built and published a community **Codespace** that has an **Azure Pipelines agent** built into the Codespace. The Codespace can register itself via **Codepsace Secrets** as a self-hosted **Azure pipelines agent** into an Azure DevOps **Agent pool**, and be used to run Azure pipelines using the compute power of the Codespace.

### Category Submission

👷 DIY Deployments 👷

### App Link

<https://containers.dev/templates>

| Template Name | Maintainer |
| --- | --- |
| [Azure Pipelines Agent](https://github.com/Pwd9000-ML/devcontainer-templates/tree/main/src/azure-pipelines-agent-devcontainer) | Marcel Lupo @Pwd9000-ML |

### Screenshots

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

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
