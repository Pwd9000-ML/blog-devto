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

As mentioned, status pages for both Github and DevOps have RSS feeds we can subscribe to. In fact the Azure platform itself also has its own health status page you can take a look at here: [https://status.azure.com/en-us/status/](https://status.azure.com/en-us/status/).  

In todays tutorial we will build a basic **Azure Logic App** that will subscribe to each services RSS feed and send us email notifications on feed updates, such as when services become degraded, when health issues occur or when health issues get remediated.

## What is an Azure Logic app?

[Azure Logic Apps](https://docs.microsoft.com/en-us/azure/logic-apps/logic-apps-overview) is a cloud-based platform for creating and running automated workflows that integrate your apps, data, services, and systems. With this platform, you can quickly develop highly scalable integration solutions for your enterprise and business-to-business (B2B) scenarios. As a member of Azure Integration Services, Logic Apps simplifies the way that you connect legacy, modern, and cutting-edge systems across cloud, on premises, and hybrid environments.

## What do we need?

1. **Azure Logic App:** We will create a **[multi-tenant](https://docs.microsoft.com/en-us/azure/logic-apps/single-tenant-overview-compare)** logic app using the **[Consumption](https://docs.microsoft.com/en-us/azure/logic-apps/logic-apps-pricing#consumption-pricing)** pricing plan.
2. **Email Account:** We will also need an email account from a service that works with Azure Logic Apps, such as Outlook.com. For other supported email providers, review **[Connectors](https://docs.microsoft.com/en-us/connectors/connector-reference/connector-reference-logicapps-connectors)** for Azure Logic Apps.

## Create Logic App

In the Azure portal search for `logic app` and then add and create the logic app with the following configuration.
Under the **Basics** blade, add the following **Instance Details:**

| Name           | Value              |
| -------------- | ------------------ |
| Type           | Consumption        |
| Logic App name | {Name}             |
| Publish        | Workflow           |
| Region         | {Region}           |

![create](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Logic-App-RSS/assets/create.png)

## Configure Logic App (Triggers)

After the logic app has been created navigate to the logic app resource, once you click on the resource, teh Azure portal will navigate you into the **Logic Apps Designer**, here you will select **Blank Logic App**:

![blank](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Logic-App-RSS/assets/blank.png)

Next we will add each of our RSS feeds as triggers. We will add the same trigger **"when a feed item is published"** 3x times as we want to check three RSS feeds, one for each service:

- [https://www.githubstatus.com/history.rss](https://www.githubstatus.com/history.rss) - Github RSS status feed.
- [https://status.dev.azure.com/_rss](https://status.dev.azure.com/_rss) - Azure Devops RSS status feed.
- [https://azurestatuscdn.azureedge.net/en-gb/status/feed/](https://azurestatuscdn.azureedge.net/en-gb/status/feed/) - Azure platform RSS status feed.

![triggers](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Logic-App-RSS/assets/triggers.png)

Also note that we can rename each trigger to identify them easier:

![rename](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Logic-App-RSS/assets/rename.png)

Also note the setting **"Chosen property will be used to determine"** is set to **PublishDate** which is the property that determines which items are new, and we will check each feed every 3 minutes for any updates.  

## Configure Logic App (Actions)

Now that all 3 triggers have been set up the last thing we need to configure are our email actions. We will create 3x email actions, one for each trigger. After each trigger you will see a `+` sign. Click on the `+` and select **Add an action** and in the search box, enter `send an email` so that you can find connectors that offer this action. If you have a Microsoft work or school account and want to use **Office 365 Outlook**. Or, if you have a personal Microsoft account, select **Outlook.com**. This example continues with Outlook.com. Select **Send and email (V2)**.

![email01](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Logic-App-RSS/assets/email01.png)

Many connectors require that you first create a connection and authenticate your identity before you can continue. Our selected email service prompts us to sign in and authenticate our identity before we can continue.

![auth](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Logic-App-RSS/assets/auth.png)

Once authenticated we can configure our e-mail template.

![template](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Logic-App-RSS/assets/template.png)

Note that we can use **dynamic content** to add details about the RSS published feed we configured from each trigger, to our email template.

![dynamic](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Logic-App-RSS/assets/dynamic.png)

As you can see from the next screen, we have created 3x email actions, each with their own unique email template for each given services RSS status feed.

![final](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Logic-App-RSS/assets/final.png)

Now **save** the logic app and that is it. Optionally you can also select **Run Trigger** to manually trigger a run.

![save](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Logic-App-RSS/assets/save.png)

Every time a health status is posted to any of our configured RSS feeds, we will be notified of the health status of the particular service that is affected.

![mail](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Logic-App-RSS/assets/mail.png)

I hope you have enjoyed this post and have learned something new. :heart:

### _Author_

{% user pwd9000 %}
