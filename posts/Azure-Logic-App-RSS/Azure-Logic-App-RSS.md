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

As described in my previous post, you can easily check the status of Github and DevOps services: {% link <https://https://dev.to/pwd9000/github-devops-status-2eji> %}

As mentioned, status pages for both the Github and DevOps service also has an RSS feed we can subscribe to. In fact the Azure platform itself also has it's very own health status page you can take a look at here: [https://status.azure.com/en-us/status/](https://status.azure.com/en-us/status/). In todays tutorial we will build an Azure Logic App that will subscribe to each services RSS feed and send us email notifications on feed updates, such as when services become degraded or when health issues occur or get remediated.

## x

## How to use

### _Author_

{% user pwd9000 %}
