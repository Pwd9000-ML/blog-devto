---
title: Multi environment AZURE deployments with Terraform and GitHub
published: false
description: Enterprise scale multi environment Azure deployments using Terraform and Github reusable workflows.
tags: 'terraform, iac, github, azuredevops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/assets/main.png'
canonical_url: null
id: 963996
---

### Overview

I have been wanting to do a tutorial to demonstrate how to perform large scale terraform deployments in Azure using a **non-monolithic** approach. I have seen so many large deployments fall into this same trap of using one big **monolithic** configuration when doing deployments at scale. Throwing everything into one unwieldy configuration can be troublesome for many reasons. To name a few:

- Making a small change can potentially break something much larger somewhere else in the configuration unintentionally.
- Build time aka `terraform plan/apply` is increased. A tiny change can take a long time to run as the entire state is checked.
- It can become cumbersome and complex for a team or team member to understand the entire code base.
- Module and provider versioning and dependencies can be fairly confusing to debug in this paradigm.
- It becomes unmanageable, risky and time consuming to plan and implement any changes.

There's also many blogs and tutorials out there on how to integrate **Terraform** with DevOps **CI/CD** processes using Azure DevOps. So I decided to share with you today how to use **Terraform** with **GitHub** instead.

In this tutorial we will use **GitHub reusable workflows** and **GitHub environments** to build enterprise scale multi environment infrastructure deployments in **Azure** using a **non-monolithic** approach, to construct and simplify complex terraform deployments into simpler manageable work streams, that can be updated independently, increase build time, and reduce duplicate workflow code by utilizing **reusable GitHub workflows**.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/assets/mainwf.png)

Things you will get out of this tutorial:

- Learn about **GitHub reusable workflows**.
- Learn how to integrate terraform deployments with **CI/CD** using **GitHub**.
- Learn how to deploy resources in **AZURE** at scale.
- Learn about **multi-stage** deployments and approvals using **GitHub Environments**.

Hopefully you can even utilize these concepts in your own organization to build **AZURE** Infrastructure at scale in your own awesome cloud projects.

### Pre-Requisites

To start things off we will build a few pre-requisites that is needed to integrate our **GitHub** project and workflows with **AZURE** before we can start building resources.

We are going to perform the following steps:

1. **Create Azure resources (Terraform Backend):** (Optional) We will first create a few resources that will host our terraform backend state configuration. We will need a Resource Group, Storage Account and KeyVault. This step is optional only for this demo/tutorial.
2. **Azure Active Directory Service Principal:** We will create an AAD Service Principal/Application that will have access to our Terraform backend and subscription in Azure. We will link this Service Principal with our GitHub project and workflows later in the tutorial.
3. **Create a GitHub repository:** We will create a GitHub project and set up the relevant secrets and environments that we will be using. The project will host our workflows and terraform configurations.
4. **Create some terraform modules:** We will set up a few terraform ROOT modules. Separated and modular from each other (non-monolithic).
5. **Create GitHub Workflows:** After we have our repository and terraform ROOT modules configured we will create our reusable workflows and configure multi-stage deployments to run and deploy resources in Azure based on our terraform ROOT Modules.

I hope you have enjoyed this post and have learned something new. You can find the code samples used in this blog post on my [Github](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}
