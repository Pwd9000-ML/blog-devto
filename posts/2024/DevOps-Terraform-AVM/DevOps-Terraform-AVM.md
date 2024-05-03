---
title: Azure Verified Modules using Terraform
published: true
description: DevOps - Terraform - Azure Verified Modules - Learn how to use Azure Verified Modules in Terraform to deploy resources in Azure.
tags: 'terraform, azure, iac, devops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/DevOps-Terraform-AVM/assets/main.png'
canonical_url: null
id: 1824654
date: '2024-05-03T16:30:30Z'
---

## Overview

This post is also part of a LIVE session delivered at **Global Azure 2024** (See below for the recording).

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/DevOps-Terraform-AVM/assets/GlobalAzure2024-500.png)

Today we are going to talk about **Azure Verified Modules** (AVM) and how to use them in Terraform.

But fist what are they? **Microsoft Azure Verified Modules** (AVM) are a curated set of **infrastructure-as-code** (IaC) modules that are compliant with the Azure Well-Architected Framework and is actively maintained, tested and verified by Microsoft. These modules are designed to help you build secure, scalable, and resilient cloud environments on Azure.

You can use **Azure Verified Modules** (AVM) in either a **Bicep** or **Terraform** configuration where configuration options are uniform and consistent across multiple modules, in terms of best practices and security. Because of this uniform and consistent configuration framework and design pattern, similarities in options across multiple modules is a key feature of Azure Verified Modules (AVM).

This is achieved by having the same configuration variables/parameters across all modules in the same pattern and features, namely **[interfaces](https://azure.github.io/Azure-Verified-Modules/specs/shared/#id-rmfr4---category-composition---avm-consistent-feature--extension-resources-value-add?wt.mc_id=DT-MVP-5004771)**, which makes it easier to use and understand the modules and attain a consistent configuration across all modules.

With Infrastructure as Code (IAC) there are a few challenges. One of the biggest is the effort required to write and maintain modules, especially in a fast-paced environment like Azure where innovation is constant. Many Microsoft partners, developers and community supporter develop their own modules, but the level of maintenance and support can vary widely.

Relying on community-shared modules can be risky due to uncertainty about their upkeep. That's where Microsoft has seen the opportunity to invest time, people, and resources to address this challenge ny introducing **Azure Verified Modules** (AVM).

## Benefits of Azure Verified Modules

- Supported by Microsoft FTEs directly.
- Modules undergo thorough testing to ensure functionality.
- Modules follow consistent design patterns and features which improve usability and maintainability.

## Interfaces

Examples of Consistent **[feature interfaces](https://azure.github.io/Azure-Verified-Modules/specs/shared/interfaces?wt.mc_id=DT-MVP-5004771)** to name a few:

- Diagnostic Settings
- Role Assignments
- Resource Locks
- Tags
- Managed Identities
- Private Endpoints
- Customer Managed Keys
- Azure Monitor Alerts

## Live Demo Recording

Have a look at my session recording for a live demo of AMV with **Terraform** at timestamp - **1h10m**:

{% youtube 5dtRWBfj4xY %}

## Labs

Also check out these amazing labs to learn more:

- [Bicep Lab](https://learn.microsoft.com/en-us/samples/azure-samples/avm-bicep-labs/avm-bicep-labs?wt.mc_id=DT-MVP-5004771)
- [Terraform Lab](https://learn.microsoft.com/en-us/samples/azure-samples/avm-terraform-labs/avm-terraform-labs?wt.mc_id=DT-MVP-5004771)

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
