---
title: Automate Azure Role Based Access Control (RBAC) with DevOps
published: false
description: DevOps - Automate Azure RBAC
tags: 'tutorial, azure, devops, productivity'
cover_image: assets/Azure-RBAC.png
canonical_url: null
id: 688322
---

## What are Azure Roles and Custom Definitions?

When you start working more and more with Azure permission you will undoubtedly have used Azure RBAC (also known as IAM) and have most likely used some of the great [built-in roles](https://docs.microsoft.com/en-us/azure/role-based-access-control/built-in-roles) that have been created and provided by Microsoft, but sometimes you may come across a requirement or need to have a very specific role tailored with a set of permissions that are more granular than what comes out of the box in a standard Azure (RBAC) built-in role.  

Luckily Azure offers a great deal of flexibility when it comes to defining your own custom roles vs built-in roles. This is where [Custom Role Definitions](https://docs.microsoft.com/en-us/azure/role-based-access-control/role-definitions) comes into play.  

Today we will look at how we can utilize Azure DevOps in creating and also updating our Azure (RBAC) custom role definitions through source control and automatically reflecting those changes in Azure through pipelines without much effort.  

If you are still a bit unclear on what Azure RBAC is, or wanted more information have a look at [Microsoft Docs](https://docs.microsoft.com/en-us/azure/role-based-access-control/overview).

## How to automate Custom Role Definitions in Azure using DevOps
