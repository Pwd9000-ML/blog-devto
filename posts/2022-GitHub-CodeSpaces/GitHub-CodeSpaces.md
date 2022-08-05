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

Have you ever had to build and look after 100s of development virtual machines and environments for your organisations developers to work in?  
Or maybe you are a developer or IT specialist working with code and starting in a new project and you have to configure your own development environment before you can start working.  

If you are, you are probably aware of the PAIN-ful problems when it comes to maintaining **developer workstations** such as:  

- Setting up and maintaining a developer workstation or set of workstations for a project.
- Setup time which is wasted before 'first commit'.
- Inconsistency between developer workstations and inconsistent configuration/tooling/settings.
- Maintaining developer Tools/Extensions, Debuggers, Dependencies and versioning.
- Personal or Team based settings and customisations.
- Hardware spec requirements.

The list goes on, and these are all factors that can cause a lot of pain, frustration and time wasting before actual development can start.  

So today we are going to take a look at a great service available in **GitHub** called **[CodeSpaces](https://docs.github.com/en/codespaces)**.  

{% youtube _W9B7qc9lVc}  

In a nutshell a **GitHub codespace** is a development environment running inside of a **container** that's remotely hosted on a cloud based **Virtual Machine**. You can also customise or even have a bespoke **docker** image as a **GitHub codespace**, by using configuration files in the **source code** of your repository, which creates a **repeatable** and **versioned** codespace configuration for all users of the project.  

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-CodeSpaces/assets/csdiagram.png)  

**GitHub codespaces** run on a variety of VM-based compute options hosted by GitHub.com, which you can configure from 2 core machines up to 32 core machines. You can connect to your codespaces from a **web browser** or locally using **Visual Studio Code**.  

At the time of this writing the VM size options for **codespaces** are as follow:  

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-CodeSpaces/assets/pricing01.png)  

## Who can use CodeSpaces?

**Codespaces** can only be enabled in settings by **organization owners** for **Team** and **Enterprise Cloud plans** currently. However GitHub will share more information and details on usage of **CodeSpaces** on personal Repo's according to the official [frequently asked questions](https://github.com/features/codespaces), so watch this space:  

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-CodeSpaces/assets/faq01.png)

**Tip:** Press `.` on any repo to make quick edits powered by Visual Studio Code.  

## Creating your first CodeSpace

In today's tutorial we will look at how easy it is to create a basic **CodeSpace** to get started. Afterwards, we will take a deeper look into how to create a **custom image** that can be maintained using a **dockerfile**, and lastly how to use an image hosted on a remote registry such as an **Azure Container Registry (ACR)**. Let's get started.  

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my published [Github](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2022-GitHub-CodeSpaces/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
