---
title: GitHub CodeSpaces - Building your first Dev Container
published: false
description: A beginners guide to building GitHub CodeSpaces
tags: 'github, codespaces, devops, development'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-CodeSpaces/assets/main.png'
canonical_url: null
id: 1160283
series: GitHub CodeSpaces Pro Tips
---

## Overview

Have you ever had to build and look after 100s of development virtual machines and environments for your organisations developers to work in? Or maybe you are a developer or IT specialist working with code and starting in a new project and you have to configure your own development environment before you can start working on your code.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-CodeSpaces/assets/pain02.png)

If you are, you are probably well aware of the PAIN points when it comes to maintaining **developer workstations** such as:

- Setup and maintenance of a dev workstation or set of workstations for a project.
- The time that is wasted before a 'first commit' can take place.
- Inconsistency between dev workstations for configurations/tooling/settings.
- Versioning Tools/Extensions, Debuggers and Dependencies.
- Personal or Team based settings and customisations.
- Security and vulnerabilities.
- Hardware spec requirements.

The list goes on, and these are all factors that can cause a lot of pain, frustration and time wasted before actual development can start.

So today we are going to take a look at a great service available in **GitHub** called **[CodeSpaces](https://docs.github.com/en/codespaces)**.

{% youtube _W9B7qc9lVc %}

In a nutshell a **GitHub codespace** is a development environment running inside of a **container** that's remotely hosted on a cloud based **Virtual Machine**.

You can almost classify a **CodeSpace** as a **development environment as a service.**

You can customise or even have a bespoke **docker** image as a **GitHub codespace** tailored to meet the needs of your project and developers, by using configuration files along with your projects **source code**, which creates a **repeatable** and **versioned** codespace configuration for all users of the project.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-CodeSpaces/assets/diag.png)

**Codespaces** run on a variety of VM-based compute options hosted by GitHub, which you can configure from 2 core machines up to 32 core machines. You can connect to your codespaces from a **web browser** or locally using **Visual Studio Code**.

At the time of this writing the VM size options for **codespaces** are as follow:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-CodeSpaces/assets/pricing01.png)

## Who can use CodeSpaces?

**Codespaces** can only be enabled in settings by **organisation owners** for **Team** and **Enterprise** Cloud plans. However GitHub will share more information and details on usage of **CodeSpaces** on personal repo's according to the official [frequently asked questions](https://github.com/features/codespaces), so watch this space!

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-CodeSpaces/assets/faq01.png)

**Tip:** Press (dot) `'.'` on any repo to make quick edits powered by Visual Studio Code from a **web browser**.

## Creating your first CodeSpace

All the examples are available on my [GitHub CodeSpaces Demo Repository](https://github.com/Pwd9000-ML/GitHub-Codespaces-Lab).

In this tutorial we will look at how easy it is to create a basic **CodeSpace** to get started.

Afterwards, we will take a deeper look into how to **customise** the **codespace** image **dockerfile**, and lastly how to use a **custom docker image** hosted on a remote registry such as an **Azure Container Registry (ACR)**. Let's get started.

On your GitHub Account navigate to `'Your codespaces'`:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-CodeSpaces/assets/start01.png)

Select `'New Codespace'`:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-CodeSpaces/assets/start02.png)

Select the **repository** and **branch** that you want to have cloned onto your **codespace**, as well as the **region** and **machine type** to run your **codespace** and then select `'Create codespace'`.

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my published [Github](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2022-GitHub-CodeSpaces/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
