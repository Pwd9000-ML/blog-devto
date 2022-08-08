---
title: Migrating your development environments to GitHub Codespaces on Azure DevOps
published: false
description: Migrating your development environments to GitHub Codespaces in Azure DevOps
tags: 'github, codespaces, azuredevops, development'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Codespaces-ado/assets/main01.png'
canonical_url: null
id: 1161896
series: GitHub Codespaces Pro Tips
---

## Overview

Welcome to the next part of my series **GitHub Codespaces Pro Tips**, in the last part we spoke a lot about what a **Codespace** is and how to get started with your first **Dev container**.

Since **Codespaces** is a service on **GitHub**, you might be wondering or thinking that the service is limited to **GitHub** customers only. The fact is that **Codespaces** is a service that is linked to a **Git** repository hosted on **GitHub**, but that is not a limiting factor to be able to use the service in other development platforms such as **Azure DevOps**.

**Azure DevOps** as well as most other popular cloud development platforms allows you to use **Git** repositories hosted on **GitHub** for your source code.

In todays tutorial I will be showing you how you can create an **Azure DevOps** project using a **Git** repository hosted on **GitHub** and making your first commit using **GitHub Codespaces**.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Codespaces-ado/assets/diag.png)

We will also look at how you can migrate an existing **Git** repository hosted on **Azure DevOps** to **GitHub**, keeping everything else such as your **pipelines**, **boards**, **test plans** and **artifacts** in **Azure DevOps** but working with a **git** code repository hosted on **GitHub** using **codespaces**. Imagine it as a hybrid scenario where you can combine **codespaces** with existing **Azure DevOps** projects and environments to make use of this great service.

## Greenfield Azure DevOps Project

Let's start by creating a new [GitHub repository](https://docs.github.com/en/get-started/quickstart/create-a-repo).

1. On your **GitHub account**, in the upper-right corner of any page, use the `'+'` drop-down menu, and select **New repository**. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Codespaces-ado/assets/ghrepo01.png)

2. Type a short, memorable name for your repository. For example, "hello-world". ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Codespaces-ado/assets/ghrepo02.png)

3. Optionally, add a description of your repository. For example, "My first repository on GitHub." ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Codespaces-ado/assets/ghrepo03.png)

4. Choose a repository visibility. For more information, see "[About repositories](https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories#about-repository-visibility)." ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Codespaces-ado/assets/ghrepo04.png)

5. Select **Initialize this repository with a README**. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Codespaces-ado/assets/ghrepo05.png)

6. Click **Create repository**. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Codespaces-ado/assets/ghrepo06.png)

## Existing Azure DevOps Project

## Examples

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my published [Github](https://github.com/Pwd9000-ML/GitHub-Codespaces-Lab) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
