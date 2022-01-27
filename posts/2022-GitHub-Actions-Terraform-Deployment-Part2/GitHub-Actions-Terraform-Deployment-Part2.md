---
title: Multi environment AZURE deployments with Terraform and GitHub (Part 2)
published: false
description: Enterprise scale multi environment Azure deployments using Terraform and Github Actions.
tags: 'terraform, iac, github, azuredevops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part2/assets/main.png'
canonical_url: null
id: 969349
series: Using Terraform on GitHub
---

### Overview

This tutorial uses examples from the following GitHub demo project [template repository](https://github.com/Pwd9000-ML/Azure-Terraform-Deployments).

Welcome to part 2 of my series on **Using Terraform on GitHub**. In [part 1](https://dev.to/pwd9000/multi-environment-azure-deployments-with-terraform-and-github-2450) of this series we looked at how to build enterprise scale multi environment infrastructure deployments in **Azure** using a **non-monolithic** approach, to construct and simplify complex terraform deployments into simpler manageable work streams, that can be updated independently, increase build time, and reduce duplicate workflow code by utilizing **reusable GitHub workflows**.

Recently I decided to create two public **GitHub Actions** on the GitHub Actions marketplace called **[Terraform Plan for AZURE](https://github.com/marketplace/actions/terraform-plan-for-azure)** and **[Terraform Apply for AZURE](https://github.com/marketplace/actions/terraform-apply-for-azure)**. So in this part of the series I will show how you can use the public marketplace actions instead of reusable workflows.

### Pre-Requisites

The pre-requisites we need to start using terraform on Github is exactly the same as in [part 1](https://dev.to/pwd9000/multi-environment-azure-deployments-with-terraform-and-github-2450) of this series. I would recommend going through [part 1](https://dev.to/pwd9000/multi-environment-azure-deployments-with-terraform-and-github-2450) first, and follow the same steps for 1-3.

We are going to perform the following steps:

1. **Create Azure Resources (Terraform Backend):** (Optional) We will first create a few resources that will host our terraform backend state configuration. We will need a Resource Group, Storage Account and KeyVault. We will also create an **Azure Active Directory App & Service Principal** that will have access to our Terraform backend and subscription in Azure. We will link this Service Principal with our GitHub project and workflows later in the tutorial.
2. **Create a GitHub Repository:** We will create a GitHub project and set up the relevant secrets and (optional) GitHub environments that we will be using. The project will host our workflows and terraform configurations.
3. **Create Terraform Modules (Modular):** We will set up a few terraform ROOT modules. Separated and modular from each other (non-monolithic).

   The only difference in this part of the series will be Step 4. Instead of creating **re-usable GitHub workflows** we will be creating a normal workflow with the marketplace actions.

4. **Create GitHub Workflows using marketplace Actions:** After we have our repository and terraform ROOT modules configured we will create a workflow and configure multi-stage deployments using public marketplace actions to run and deploy resources in Azure based on our terraform ROOT Modules.

## Steps 1 - 3

Refer to [part 1](https://dev.to/pwd9000/multi-environment-azure-deployments-with-terraform-and-github-2450) of this series.

## 4. Create GitHub Workflows using marketplace Actions

df
