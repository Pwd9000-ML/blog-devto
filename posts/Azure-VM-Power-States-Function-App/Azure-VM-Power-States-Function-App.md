---
title: Power virtual machines ON or OFF using an Azure function app
published: false
description: Azure - Function App to control VM power states
tags: 'tutorial, powershell, productivity, azure'
cover_image: assets/mainFunc1.png
canonical_url: null
id: 724055
date: '2021-06-10T10:19:00Z'
---

## What is an Azure function?

Azure Functions is a cloud service available on-demand that provides all the continually updated infrastructure and resources needed to run your applications. You focus on the pieces of code that matter most to you, and Functions handles the rest. Functions provides serverless compute for Azure. You can use Functions to build web APIs, respond to database changes, process IoT streams, manage message queues, and more.  

{% youtube 8-jz5f_JyEQ %}

For more details on Azure Functions have a look at the [Microsoft Documentation](https://docs.microsoft.com/en-us/azure/azure-functions/functions-overview)  

Today we will look at how we can create a function app using PowerShell as the code base, that will allow us to check the power state of a virtual machine or stop / start a virtual machine by passing a URL request via a web browser or a JSON body to the function app.

## How to control Azure virtual machines power states using an Azure function

In this tutorial we will:  
- create an Azure function app
- use PowerShell to control Virtual machines power states.

### _Author_

Marcel.L - pwd9000@hotmail.co.uk
