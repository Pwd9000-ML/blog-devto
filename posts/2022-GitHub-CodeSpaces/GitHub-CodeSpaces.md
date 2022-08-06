---
title: Introduction to GitHub CodeSpaces - Building your first Dev Container
published: false
description: A beginners guide to building GitHub CodeSpaces and getting started
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

So today we are going to take a look at a great service available on **GitHub** called **[CodeSpaces](https://docs.github.com/en/codespaces)**.

{% youtube _W9B7qc9lVc %}

In a nutshell a **GitHub codespace** is a development environment running inside of a **container** that's remotely hosted on a cloud based **Virtual Machine** linked to your code repository.

You can almost classify a **CodeSpace** as a **development environment as a service.**

You can customise or even have a bespoke **docker** image as a **GitHub codespace** tailored to meet the needs of your project and developers, by using configuration files along with your projects **source code**, which creates a **repeatable**, **consistent** and **versioned** codespace configuration for all users of the project.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-CodeSpaces/assets/diag.png)

**Codespaces** run on a variety of VM-based compute options hosted by GitHub, from 2 core machines up to 32 core machines. You can connect to your **codespaces** from a **web browser** or locally using **Visual Studio Code**.

At the time of this writing the VM size options for **codespaces** are as follow:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-CodeSpaces/assets/pricing01.png)

## Who can use CodeSpaces?

**Codespaces** can only be enabled in settings by **organisation owners** for **Team** and **Enterprise** Cloud plans. However GitHub will share more information and details on usage of **CodeSpaces** on personal repo's according to the official [frequently asked questions](https://github.com/features/codespaces), so watch this space!

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-CodeSpaces/assets/faq01.png)

**Tip:** Press (dot) `'.'` on any repo to make quick edits powered by Visual Studio Code from a **web browser**.

## Creating your first CodeSpace

All the examples are available on my [GitHub CodeSpaces Demo Repository](https://github.com/Pwd9000-ML/GitHub-Codespaces-Lab).

In this tutorial we will look at how easy it is to create a basic **CodeSpace** to get started.

Afterwards, we will take a deeper look into how to **customise** the **codespace**, and lastly how to use a **custom docker image** hosted on a remote registry.

1. On your GitHub account navigate to `'Your codespaces'` and select `'New Codespace'`. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-CodeSpaces/assets/start01.png)
2. Select the **repository** and **branch** that you want to have cloned onto your **codespace**, as well as the **region** and **machine type** to run your **codespace** and then select `'Create codespace'`. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-CodeSpaces/assets/start02.png)
3. You will then see the **codespace container** being provisioned. (**Note:** GitHubs default image will be used, but we will look at how you can use custom images later on in this tutorial). ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-CodeSpaces/assets/start03.png)
4. Shortly after the **codespace** container is provisioned, **VS Code** will open inside of your **web browser**, already linked up with your code and a terminal to the remote **codespace**. If you have **VS Code** locally installed, it will even detect what extensions you have locally and provision them on the remote **dev container codespace** for you. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-CodeSpaces/assets/start04.png)

On the bottom left side you will see a green square that says **Codespaces**, you can click on this for additional options. If you prefer working on a locally installed copy of **VS Code** you can select the option `'Open in VS Code'`.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-CodeSpaces/assets/start05.png)

**Note:** When using a locally installed copy of VS Code instead of the web browser, you will still be working on the remote **codespace** instance.

With the **codespace** now up and running, you can simply start to work on your code. If you leave your repository and come back later you can always resume your **codespace** experience by navigating to your repository `'Code'` and selecting the `'Codespaces'` tab.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-CodeSpaces/assets/resume01.png)

Let's take a look next at how you can customise your **codepsace** next.

## Customising your CodeSpace

As mentioned, the **codespace** we created will be using GitHubs **default docker image**. So what we will do next is create a few configuration files so that we can customise the **default image**.  

1. Remember that green square at the bottom left corner I talked about earlier that says **Codespaces**, click on this for additional options and select the option `'Add Development Container Configuration Files'`:
  ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-CodeSpaces/assets/config01.png)  
2. Select a predefined container definition. In my case I will select `'Ubuntu'`:
  ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-CodeSpaces/assets/config02.png)  
  **NOTE:** There are growing variety of predefined images that can be selected from on GitHubs maintained [vscode-dev-containers repository](https://github.com/microsoft/vscode-dev-containers/tree/main/containers)
3. Select the Ubuntu version to use:
  ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-CodeSpaces/assets/config03.png)
4. Select the additional features to install inside of the **dev container**:
  ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-CodeSpaces/assets/config04.png)
5. You may also be asked to select what version of the tooling you selected to use.
  ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-CodeSpaces/assets/config05.png)
  ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-CodeSpaces/assets/config06.png)

After the above process you will notice a new folder has been created inside of the root of our repository called `'.devcontainer'` that contains a `'devcontainer.json'` file and a `'dockerfile'`:  

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-CodeSpaces/assets/config07.png)

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my published [Github](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2022-GitHub-CodeSpaces/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
