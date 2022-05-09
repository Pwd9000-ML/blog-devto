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

Lets start by creating a resource group and a windows dotnet function app in our Azure subscription. For this step I have written a PowerShell script using Azure CLI. You can also find ths script on my [GitHub repository]()

```powershell
#Log into Azure
az login

# Setup Variables.
$randomInt = Get-Random -Maximum 9999
$subscriptionId=$(az account show --query id -o tsv)
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
    --runtime-version "6.0" `
    --functions-version "4" `
    --assign-identity
```

