---
title: Get email alerts from serverless Azure functions using SendGrid
published: false
description: Azure - Function app alerts via SendGrid
tags: 'azurefunctions, azure, serverless, sendgrid'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-SendGrid-Function-Alerts/assets/main.png'
canonical_url: null
id: 947134
---

## Overview

I recently posted a tutorial on how to better manage and maintain Azure resource lifecycle and decommissions by automating the decommission process by using a simple **Decommission** tag with a date value, and an Azure serverless **Function App**. The tutorial also includes how we can track successful decommissions and failed decommissions using the **function apps** own storage account by recording the automated decommission events into table storage.

The full tutorial can be found here: {% link <https://dev.to/pwd9000/automate-azure-resource-decommissions-with-tracking-aok> %}

So this brings me to this new tutorial I wanted to share with you today. I was thinking how we can even better the process by also getting an email alert when a resource has been successfully decommissioned or if a decommission has failed, perhaps including the error message if it was a failure in the email alert? So today I will share with you a general guide on how we can utilize a service in Azure called **SenGrid** to send us an email from an Azure **Function App**.

This tutorial will only be a general guide on how to utilize **SendGrid** in an Azure Function App to send emails and does not follow on my previous tutorial. This post is mainly meant to serve as a supplement and guide guide to set up **SendGrid** to use in any Powershell based Function App in your own environment to send email alerts.

But by no means feel free to also integrate the steps in this tutorial in addition to my previous blog post. Let's get started.

## What is SendGrid?

XYZ

## Pre-Requisites

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my [Github](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/Azure-SendGrid-Function-Alerts/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}
