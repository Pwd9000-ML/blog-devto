---
title: Implement CI/CD with GitHub - Deploy Azure Functions
published: false
description: Implementing CI/CD with GitHub by automating Azure Function deployment
tags: 'githubactions, azuredevops, github, azurefunctions'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Function-CICD/assets/main.png'
canonical_url: null
id: 1051702
---

## Overview

In todays tutorial we will take a look at implementing CI/CD with GitHub by using GitHub Actions to automate Azure Function deployment.  
Bringing and maintaining our Azure Functions into a Git repository also brings all the benefits of version control, source code management and automated build and deployment of our functions into Azure though CI/CD.

## Pre-requisites

To get started you'll need a few things, firstly:

- An Azure Subscription
- A GitHub Account and Git repository

You will also need to install a few local pre-requirements on the machine you will be working on. In my case I will prepare my machine for developing **C#** Functions, but you can take a look at some of the other code stacks here: [Run Local Requirements](https://docs.microsoft.com/en-us/azure/azure-functions/functions-develop-vs-code?tabs=csharp#prerequisites)

- Azure Functions Core Tools
- VSCode
- Azure Functions for Visual Studio Code
- C# for Visual Studio Code

## Create an Azure Function App

Lets start by creating a resource group and a windows dotnet function app in our Azure subscription. For this step I have written a PowerShell script using Azure CLI. You can also find ths script on my [GitHub repository](https://github.com/Pwd9000-ML/blog-devto/blob/main/posts/2022-GitHub-Function-CICD/code/Azure-Pre-Reqs.ps1).

```powershell
#Log into Azure
az login

# Setup Variables.
$randomInt = Get-Random -Maximum 9999
$subscriptionId = $(az account show --query id -o tsv)
$resourceGroupName = "GitHub-Managed-Function-Demo"
$storageName = "demofuncsa$randomInt"
$functionAppName = "demofunc$randomInt"
$region = "uksouth"

# Create a resource resourceGroupName
az group create --name "$resourceGroupName" --location "$region"

# Create an azure storage account for function app
az storage account create `
    --name "$storageName" `
    --location "$region" `
    --resource-group "$resourceGroupName" `
    --sku "Standard_LRS" `
    --kind "StorageV2" `
    --https-only true `
    --min-tls-version "TLS1_2"

# Create a Function App
az functionapp create `
    --name "$functionAppName" `
    --storage-account "$storageName" `
    --consumption-plan-location "$region" `
    --resource-group "$resourceGroupName" `
    --os-type "Windows" `
    --runtime "dotnet" `
    --runtime-version "6" `
    --functions-version "4" `
    --assign-identity
```

The above script created a resource group containing the function app, function app storage and insights as well as the consumption app service plan.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Function-CICD/assets/func.png)

## Create a GitHub repository

Next up head over to your GitHub account and create a new repository. We will use this repository to link our function app/s source code to.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Function-CICD/assets/ghrepo01.png)

I have called my repository **_Demo-Azure-Functions_**

## Prepare Local Requirements

As mentioned at the beginning of this post we will now install and run a few pre-requirements on the machine we will be working and developing our function code on.

Install the following tools:

- [Install Azure Function Core Tools](https://github.com/Azure/azure-functions-core-tools#installing)
- [Install VSCode](https://code.visualstudio.com/download)
- [Install Azure Functions extension for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-azurefunctions)
- [Install C# extension for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=ms-dotnettools.csharp)

## Clone GitHub Function repository

With all our tools now installed we can now clone our GitHub function repository to our local machine:

![image.gif]()
