---
title: DevOps/Github service notifications using Azure Logic Apps
published: true
description: Using Azure Logic App to send notifications from RSS feeds
tags: 'tutorial, Azure, github, devops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-Logic-App-RSS/assets/main.png'
canonical_url: null
id: 807719
date: '2021-08-30T19:28:52Z'
---

## Github/DevOps service status

As described in one of my previous post, you can easily check the health status of services like Github and DevOps by going to each services status page. Below is a link to my previous post: {% link <https://dev.to/pwd9000/github-devops-status-2eji> %}

Additionally, both Github and DevOps status pages have RSS feeds we can subscribe to. The Azure platform itself also has its own health status page at the following URL: [https://status.azure.com/en-us/status/](https://status.azure.com/en-us/status/).

In todays tutorial we will create and configure an **Azure Logic App** that will connect to each of these services RSS feeds and send us email notifications when services become degraded, health issues occur or get remediated.

## What is an Azure Logic app?

[Azure Logic Apps](https://docs.microsoft.com/en-us/azure/logic-apps/logic-apps-overview) is a cloud-based platform for creating and running automated workflows that integrate your apps, data, services, and systems. With this platform, you can quickly develop highly scalable integration solutions for your enterprise and business-to-business (B2B) scenarios. As a member of Azure Integration Services, Logic Apps simplifies the way that you connect legacy, modern, and cutting-edge systems across cloud, on premises, and hybrid environments.

## What do we need?

1. **Azure Logic App:** We will create a **[multi-tenant](https://docs.microsoft.com/en-us/azure/logic-apps/single-tenant-overview-compare)** logic app using the **[Consumption](https://docs.microsoft.com/en-us/azure/logic-apps/logic-apps-pricing#consumption-pricing)** pricing plan.
2. **Email Account:** We will also need an email account from a service that works with Azure Logic Apps, such as Outlook.com. For other supported email providers, review **[Connectors](https://docs.microsoft.com/en-us/connectors/connector-reference/connector-reference-logicapps-connectors)** for Azure Logic Apps.

## Creating the Logic App

In the Azure portal search for `logic app` and then add and create the logic app with the following configuration. Under the **Basics** blade, add the following **Instance Details:**

| Name           | Value       |
| -------------- | ----------- |
| Type           | Consumption |
| Logic App name | {Name}      |
| Region         | {Region}    |

![create](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-Logic-App-RSS/assets/create.png)

Add any tags optionally and then select **Review + Create**, and create the Logic App.

## Configuring the Logic App

After the Logic App has been created navigate to the resource, once you click on the resource, the Azure portal will navigate into the **Logic Apps Designer**, here we will select a new **Blank Logic App**:

![blank01](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-Logic-App-RSS/assets/blank01.png)

First we will create a schedule **trigger**. On the connectors and triggers search bar type: `schedule` and select the trigger called `recurrence`:

![schedule](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-Logic-App-RSS/assets/schedule.png)

We will set this trigger to run every 3 minutes:

![time](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-Logic-App-RSS/assets/time.png)

Next we will add each of our RSS feeds as parallel **branches** after our schedule. Click on `+ New step` underneath the `recurrence` schedule trigger and search for `rss`. We will add the action **"List all RSS feed items"** 3x times as we want to check three RSS feeds, one for each of the following service:

1. [https://www.githubstatus.com/history.rss](https://www.githubstatus.com/history.rss) - Github RSS status feed.
2. [https://status.dev.azure.com/\_rss](https://status.dev.azure.com/_rss) - Azure Devops RSS status feed.
3. [https://azurestatuscdn.azureedge.net/en-gb/status/feed/](https://azurestatuscdn.azureedge.net/en-gb/status/feed/) - Azure platform RSS status feed.

![rss_actions](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-Logic-App-RSS/assets/rss_actions.png)

We will configure each **action** under our recurring schedule with the following values:

| Parameter Name   | Value                    |
| ---------------- | ------------------------ |
| The RSS feed URL | {RSS URL Feed}           |
| since            | addminutes(utcnow(), -3) |

**NOTE:** We are using the `since` parameter and an expression `addminutes(utcnow(), -3)` as the value, which will instruct our logic app to check the configured RSS feed URL for any new posts within the last 3 minutes. Since our logic app will run on a recurring schedule every 3 minutes, checking for new posts within the last 3 minutes, we should never miss any health status updates.

![function](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-Logic-App-RSS/assets/function.png)

Also note that we can rename our RSS action so that it is easier to identify:

![rename03](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-Logic-App-RSS/assets/rename03.png)

After configuring up our first RSS action, underneath our `schedule` trigger we will click on the `+` sign and select the option to `add a parallel branch`:

![parallel01](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-Logic-App-RSS/assets/parallel01.png)

Similarly to how we configured our first action, we will add an **action** for our devops status RSS feed and repeat the process a third time to add our azure status RSS feed. After adding all our feeds as parallel branch **actions**, our Logic App designer should look like this:

![actions_final](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-Logic-App-RSS/assets/actions_final.png)

Now that all 3x RSS actions have been set up, the last thing we need to do is configure our email actions. We will create 3x email actions, one for each RSS feed. After each action you will see a `+` sign. Click on the `+` and select **Add an action**:

![action01](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-Logic-App-RSS/assets/action01.png)

Search for `control` and then select the action `for each`:

![fore_each](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-Logic-App-RSS/assets/for_each.png)

We can again rename our control action so that it is easier to identify. In my case I have named these control actions `githubFeedItem`, `devopsFeedItem` and `azureFeedItem`.

For each control action we will configure the RSS `Body` as the output from the previous step and then **add an action**. In the search box, enter `send an email` so that you can find connectors that offer this action. If you have a Microsoft work or school account and want to use **Office 365 Outlook**. Or, if you have a personal Microsoft account, select **Outlook.com**. This example continues with Outlook.com. Select **Send and email (V2)**:

![email02](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-Logic-App-RSS/assets/email02.png)

Many connectors require that you first create a connection and authenticate your identity before you can continue. Our selected email service prompts us to sign in and authenticate our identity before we can continue:

![auth](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-Logic-App-RSS/assets/auth.png)

Once authenticated we can configure our e-mail template:

![template01](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-Logic-App-RSS/assets/template01.png)

Note that we can populate our email template with **dynamic content** to add details about the RSS feed we configured earlier taking the values dynamically from the `Body` of the RSS feed response:

![dynamic](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-Logic-App-RSS/assets/dynamic.png)

As you can see from the next screen, I have created 3x email actions, each with their own unique email template for each given RSS status feed:

![final03](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-Logic-App-RSS/assets/final03.png)

Remember to **save** the logic app when finished. That is it! Optionally we can select **Run Trigger** to manually trigger a test run of the Logic App we just created.

![save](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-Logic-App-RSS/assets/save.png)

Now every time a new health status is posted to any of our configured RSS feeds, we will be notified via an email notification containing the details of the affected service.

![mail01](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-Logic-App-RSS/assets/mail01.png)

![mail02](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-Logic-App-RSS/assets/mail02.png)

I hope you have enjoyed this post and have learned something new. You can also find the JSON code sample and template of the Logic App we built in this tutorial on my [Github](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/Azure-Logic-App-RSS/code) page. :heart:

### _Author_

{% user pwd9000 %}

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) \ :penguin: [Twitter](https://twitter.com/pwd9000) \ :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)
