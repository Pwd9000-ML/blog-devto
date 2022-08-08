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

Welcome to the next part of my series **GitHub Codespaces Pro Tips**, in the last part we spoke about what a **Codespace** is and how to get started with your first **Dev container**.

Since **Codespaces** is a service on **GitHub**, you might be wondering or thinking that the service is limited to **GitHub users** only. The fact is that **Codespaces** is a service that is linked to a **Git** repository hosted on **GitHub**, but that is not a limiting factor to be able to link and use other great services such as **Azure DevOps Boards** and **Azure DevOps Pipelines**.

**Azure DevOps** allows you to closely integrate services such as **Boards** and **Pipelines** with your **GitHub** account/Org.

So in todays tutorial I will be showing you how you can create a hybrid environment with **GitHub and Azure DevOps**, by linking your DevOps **boards** and **pipelines** to **GitHub**, allowing you to ultimately make use of features such as **Codespaces** as well.  

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Codespaces-ado/assets/diag01.png)

Imagine it as a hybrid scenario where you can combine services and features of **GitHub** along with existing **Azure DevOps** services you may already be using.

## Creating an Azure DevOps project

Let's get started by creating an **Azure DevOps** project.

1. Log into your Azure DevOps organisation and select **New project**. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Codespaces-ado/assets/proj01.png)

2. Enter information into the form provided. Provide a name for your project, an optional description, choose the [visibility](https://docs.microsoft.com/en-us/azure/devops/repos/tfvc/comparison-git-tfvc?view=azure-devops), and select `'Git'` as the source control type. Also select the work item [process](https://docs.microsoft.com/en-us/azure/devops/boards/work-items/guidance/choose-process?view=azure-devops&tabs=agile-process). ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Codespaces-ado/assets/proj02.png)

## Linking Project Boards with GitHub

Next we will [connect and link](https://docs.microsoft.com/en-us/azure/devops/boards/github/connect-to-github?view=azure-devops) our **DevOps boards** to **GitHub**.  

1. Choose **'Project Settings'** and under the **Boards** section select **'GitHub connections'**.  ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Codespaces-ado/assets/proj03.png)  

2. Choose **Connect your GitHub account** to use your GitHub account credentials. (**NOTE:** Alternatively you can also connect to your GitHub account using a [Personal Access Token (PAT)](https://docs.microsoft.com/en-us/azure/devops/boards/github/connect-to-github?view=azure-devops#github-pat) instead.)  ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Codespaces-ado/assets/proj04.png)  

3. Next click **'Autorize AzureBoards'**.  ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Codespaces-ado/assets/proj05.png)  

4. Select the **GitHub repositories** you want to link to **Azure Boards** and click **'Save'**.  ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Codespaces-ado/assets/proj06.png)  

5. Review the selected repositories you want to link to **Azure Boards** and click on **'Approve, Install, & Authorize'**.  ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Codespaces-ado/assets/proj07.png)  

6. You'll see the new **GitHub connection** under the project settings. You also have the ability to add/remove additional repositories or remove the GitHub connection entirely.  ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Codespaces-ado/assets/proj08.png)  


## Existing Azure DevOps Project

## Examples

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my published [Github](https://github.com/Pwd9000-ML/GitHub-Codespaces-Lab) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>



#################

### Creating GitHub repository

Let's start by creating a new [GitHub repository](https://docs.github.com/en/get-started/quickstart/create-a-repo).

1. On your **GitHub account**, in the upper-right corner of any page, use the `'+'` drop-down menu, and select **New repository**. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Codespaces-ado/assets/ghrepo01.png)

2. Type a short, memorable name for your repository. For example, "hello-world". ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Codespaces-ado/assets/ghrepo02.png)

3. Optionally, add a description of your repository. For example, "My first repository on GitHub." ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Codespaces-ado/assets/ghrepo03.png)

4. Choose a repository visibility. For more information, see "[About repositories](https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories#about-repository-visibility)." ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Codespaces-ado/assets/ghrepo04.png)

5. Select **Initialize this repository with a README**. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Codespaces-ado/assets/ghrepo05.png)

6. Click **Create repository**. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Codespaces-ado/assets/ghrepo06.png)