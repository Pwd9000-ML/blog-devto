---
title: DevOps/Github service notifications using Azure Logic App
published: false
description: Using Azure Logic App to send notifications from RSS feeds
tags: 'tutorial, Azure, github, devops'
cover_image: https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Logic-App-RSS/assets/main.png
canonical_url: null
id: 807719
---

## Github/DevOps service status

As described in my previous post, you can easily check the status of Github and DevOps services: {% link <https://dev.to/pwd9000/github-devops-status-2eji> %}

As mentioned, status pages for both Github and DevOps have RSS feeds we can subscribe to. In fact the Azure platform itself also has its own health status page you can take a look at here: [https://status.azure.com/en-us/status/](https://status.azure.com/en-us/status/). In todays tutorial we will build an **Azure Logic App** that will subscribe to each services RSS feed and send us email notifications on feed updates, such as when services become degraded, when health issues occur or when health issues get remediated.

## What is an Azure Logic app?

[Azure Logic Apps](https://docs.microsoft.com/en-us/azure/logic-apps/logic-apps-overview) is a cloud-based platform for creating and running automated workflows that integrate your apps, data, services, and systems. With this platform, you can quickly develop highly scalable integration solutions for your enterprise and business-to-business (B2B) scenarios. As a member of Azure Integration Services, Logic Apps simplifies the way that you connect legacy, modern, and cutting-edge systems across cloud, on premises, and hybrid environments.

## What do we need?

1. **Azure Logic App:** We will create a **[multi-tenant](https://docs.microsoft.com/en-us/azure/logic-apps/single-tenant-overview-compare)** logic app using the **[Consumption](https://docs.microsoft.com/en-us/azure/logic-apps/logic-apps-pricing#consumption-pricing)** pricing plan.
2. **Email Account:** We will also need an email account from a service that works with Azure Logic Apps, such as Outlook.com. For other supported email providers, review **[Connectors](https://docs.microsoft.com/en-us/connectors/connector-reference/connector-reference-logicapps-connectors)** for Azure Logic Apps.

## Create Logic App

First wee need to create the logic app. In the Azure portal search for `logic app` and then add and create the logic app with the following configuration:
Under the **Basics** blade, add the following **Instance Details:**

| Name           | Value              |
| -------------- | ------------------ |
| Type           | Consumption        |
| Logic App name | {Name}             |
| Publish        | Workflow           |
| Region         | {Region}           |

![create](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Logic-App-RSS/assets/create.png)

## Configure Logic App

### _Author_

{% user pwd9000 %}
