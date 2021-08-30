---
title: DevOps/Github service notifications using Azure Logic Apps
published: true
description: Using Azure Logic App to send notifications from RSS feeds
tags: 'tutorial, Azure, github, devops'
cover_image: https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Logic-App-RSS/assets/main.png
canonical_url: null
id: 807719
---

## Github/DevOps service status

As described in my previous post, you can easily check the status of Github and DevOps services: {% link <https://dev.to/pwd9000/github-devops-status-2eji> %}

Additionally, status pages for both Github and DevOps have RSS feeds we can subscribe to. In fact the Azure platform itself also has its own health status page you can take a look at here: [https://status.azure.com/en-us/status/](https://status.azure.com/en-us/status/).  

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

## Configure Logic App

After the logic app has been created navigate to the logic app resource, once you click on the resource, the Azure portal will navigate you into the **Logic Apps Designer**, here you will select **Blank Logic App**:

![blank01](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Logic-App-RSS/assets/blank01.png)

Next we will create a schedule trigger. On the connectors and triggers search bar type: `schedule` and select the trigger called `recurrence`:

![schedule](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Logic-App-RSS/assets/schedule.png)

We will set this trigger to run every 3 minutes.

![time](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Logic-App-RSS/assets/time.png)

Next we will add each of our RSS feeds as parallel **actions** underneath our schedule. Click on `+ New step` underneath the `recurrence` trigger and search for `rss`. We will add the action **"List all RSS feed items"** 3x times as we want to check three RSS feeds, one for each service:

- [https://www.githubstatus.com/history.rss](https://www.githubstatus.com/history.rss) - Github RSS status feed.
- [https://status.dev.azure.com/_rss](https://status.dev.azure.com/_rss) - Azure Devops RSS status feed.
- [https://azurestatuscdn.azureedge.net/en-gb/status/feed/](https://azurestatuscdn.azureedge.net/en-gb/status/feed/) - Azure platform RSS status feed.

![rss_actions](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Logic-App-RSS/assets/rss_actions.png)

We will configure each action under our recurrence schedule with the following values:

| Parameter Name   | Value                    |
| ---------------- | ------------------------ |
| The RSS feed URL | {RSS URL Feed}           |
| since            | addminutes(utcnow(), -3) |

**NOTE:** We are only using the `since` parameter and an expression `addminutes(utcnow(), -3)` as the value, which will basically instruct our logic app to check the given RSS feed for any new posts within the last 3 minutes. Since our logic app will run on a recurring schedule every 3 minutes, checking for new posts within the last 3 minutes, we should never miss any updates.

![function](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Logic-App-RSS/assets/function.png)

Also note that we can rename our action so that it is easier to identify:

![rename02](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Logic-App-RSS/assets/rename02.png)

After setting up our first RSS action, underneath our `schedule` trigger we will click on the `+` sign and select the option `add a parallel branch`:

![parallel01](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Logic-App-RSS/assets/parallel01.png)

Similarly we will add an **action** for our devops status RSS feed and repeat the process a third time to also add our azure status RSS feed. After adding all our feeds as parallel **actions**, our Logic App design should look like this:

![actions_final](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Logic-App-RSS/assets/actions_final.png)

Now that all 3 actions have been set up the last thing we need to configure are our email actions. We will create 3x email actions, one for each RSS feed. After each action you will see a `+` sign. Click on the `+` and select **Add an action**:

![action01](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Logic-App-RSS/assets/action01.png)

Search for `control` and then select the action `for each`:

![fore_each](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Logic-App-RSS/assets/for_each.png)

We can again rename our control action so that it is easier to identify. Within the **for each** action we will configure `Body` as the output from previous steps and then **add an action**. In the search box, enter `send an email` so that you can find connectors that offer this action. If you have a Microsoft work or school account and want to use **Office 365 Outlook**. Or, if you have a personal Microsoft account, select **Outlook.com**. This example continues with Outlook.com. Select **Send and email (V2)**:

![email02](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Logic-App-RSS/assets/email02.png)

Many connectors require that you first create a connection and authenticate your identity before you can continue. Our selected email service prompts us to sign in and authenticate our identity before we can continue:

![auth](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Logic-App-RSS/assets/auth.png)

Once authenticated we can configure our e-mail template:

![template01](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Logic-App-RSS/assets/template01.png)

Note that we can use **dynamic content** to add details about the RSS published feed we configured from each trigger, to our email template:

![dynamic](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Logic-App-RSS/assets/dynamic.png)

As you can see from the next screen, we have created 3x email actions, each with their own unique email template for each given services RSS status feed.

![final03](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Logic-App-RSS/assets/final03.png)

Now **save** the logic app and that is it. Optionally you can also select **Run Trigger** to manually trigger a run.

![save](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Logic-App-RSS/assets/save.png)

Every time a health status is posted to any of our configured RSS feeds, we will be notified of the health status of the particular service that is affected.

![mail01](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Logic-App-RSS/assets/mail01.png)

![mail02](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Logic-App-RSS/assets/mail02.png)

I hope you have enjoyed this post and have learned something new. You can also find the JSON code sample and template of the Logic App we built in this tutorial on my [Github](https://github.com/Pwd9000-ML/blog-devto/tree/master/posts/Azure-Logic-App-RSS/code) page. :heart:

### _Author_

{% user pwd9000 %}
