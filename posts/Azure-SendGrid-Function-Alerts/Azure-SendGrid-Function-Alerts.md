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

I recently posted a tutorial on how to better manage and maintain the lifecycle of Azure resources, automating resource decommissions by using a simple **Decommission** tag with a date value, and an Azure serverless **Function App**. The tutorial also includes how to track successful and failed decommissions using the **function apps** own storage account by recording the decommission events into table storage.  

The full tutorial can be found here: {% link <https://dev.to/pwd9000/automate-azure-resource-decommissions-with-tracking-aok> %}  

This brings me to this new tutorial I want to share with you today. I was thinking how we can even better the process by also getting an email alert when a resource has been decommissioned or if a decommission has failed, and perhaps including the error message if it was a failure in an email alert? So today I will share with you a general guide on how we can utilize a service in Azure called **SenGrid** to send us email notifications from an **Azure Function App**.  

This tutorial is only a general guide on how to utilize the **SendGrid** service inside of a **Function App** to send notification emails and does not follow on my previous tutorial. This guide is meant to serve as a supplement to show how to set up the **SendGrid** service and utilize the service in any **Powershell** based **Function App** in any environment, giving the ability to send email notifications to relevant stakeholders.  

Feel free to integrate the steps in this tutorial in addition to my previous blog post mentioned above, if you have the additional requirement to be notified by email about resource decommissions. Let's get started.

## What is SendGrid?

[SendGrid](https://docs.sendgrid.com/for-developers/partners/microsoft-azure-2021#create-a-twilio-sendgrid-account) is a third party provider in Azure that provides a cloud-based email service. The service manages various types of email including shipping notifications, friend requests, sign-up confirmations, and email newsletters. It also handles internet service provider (ISP) monitoring, domain keys, sender policy framework (SPF), and feedback loops. Additionally provides link tracking, open rate reporting. It also allows companies to track email opens, unsubscribes, bounces, and spam reports.

Azure offers a variety of **[SendGrid pricing plans](https://sendgrid.com/marketing/sendgrid-services-cro/#pricing-app)**. For the purpose of our use case and this tutorial we will create and use the **FREE** plan which gives us access to the API and also 100 emails/day forever.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-SendGrid-Function-Alerts/assets/sendgrid_free1.png)

## Steps to set up

We are going to need to perform the following steps:  

1. **Create Azure resources:** (Optional) We will first create a Resource Group, PowerShell based Function App and KeyVault. This step is optional only for this demo/tutorial.
2. **Create a SendGrid account:** We will create a FREE SendGrid account and then verify the account and sender.
3. **Generate a SendGrid API Key:** We will generate an API Key, store this key in the key vault and consume it in our PowerShell function to authenticate to the SendGrid service.
4. **Create a SendGrid API PowerShell Function:** We will create a PowerShell function to interact with the SendGrid API and service to send an email notification.
5. **Integrate PowerShell Function into Function App:** We will integrate our PowerShell function into our Function App and test.

## 1. Create Azure resources



I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my [Github](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/Azure-SendGrid-Function-Alerts/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}
