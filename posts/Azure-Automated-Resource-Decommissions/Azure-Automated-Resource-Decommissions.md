---
title: Automate Azure Resource Decommissions (with tracking)
published: false
description: Azure - Automate Azure Resource Decommissions
tags: 'azurefunctions, azure, serverless, automation'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/Azure-Automated-Resource-Decommissions/assets/main.png'
canonical_url: null
id: 930485
---

## Overview

Today we are going to look at a common use case around resource management in Azure, how to manage our resource decommissions more effectively, and even having the ability for our users to self serve a resource decommission by simply using an Azure tag, and also be able to track decommissions or failed decommissions using a tracker table **(Azure table storage)**.

We can ease the management of handling our resource decommissions by simply using **[Tags](https://docs.microsoft.com/en-us/azure/azure-resource-manager/management/tag-resources?tabs=json)** and automate the decommission process using an Azure serverless **[Function App](https://docs.microsoft.com/en-us/azure/azure-functions/functions-overview)** with **Powershell** as the code base set on a daily run trigger. We will also utilize the **[Funtion Apps](https://docs.microsoft.com/en-us/azure/azure-functions/functions-overview)** own storage account to create two **tables**. One called **Tracker** to track successful decommissions by **resource ID** and date of decommission, and also a table called **Failed** in which we will track failed decommissions. Say for example if a resource had a resource lock on it or some sort of other failure that does not allow our automation to successfully complete the decommission task.

So in this demo I will be using a **[Resource Tag](https://docs.microsoft.com/en-us/azure/azure-resource-manager/management/tag-resources?tabs=json)** called **Decommission**. The value will be a date format of **dd/MM/yyyy**.

| Tag Key      | Tag Value  |
| ------------ | ---------- |
| Decommission | dd/MM/yyyy |

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-Automated-Resource-Decommissions/assets/dateTag.png)

The idea is simple, place the **Decommission** tag on the **resource** OR **resource group** that you would like to decommission as well as the date that you want that decommission to take place on. The function app will run on a daily **Cron** schedule and search resources/resource groups that are tagged with the **Decommission** key and evaluate based on the given **Date** value whether the decommission should be initiated or not, and also track the decommission by recording the event into an Azure **Storage Account Table** with the resource ID and date of the successful/failed decommission, so that we can track and audit our automated events.

## Pre-Requisites

so
