---
title: Protect secrets in Azure Functions using Key Vault
published: false
description: Azure - Integrate Key Vault with Functions
tags: 'tutorial, azure, productivity, security'
cover_image: assets/key-func-main.png
canonical_url: null
---

## What is an Azure function?

[Azure Functions](https://docs.microsoft.com/en-us/azure/azure-functions/functions-overview) is a cloud service available on-demand that provides all the continually updated infrastructure and resources needed to run your applications. You focus on the pieces of code that matter most to you, and Functions handles the rest. Functions provides serverless compute for Azure. You can use Functions to build web APIs, respond to database changes, process IoT streams, manage message queues, and more.

{% youtube 8-jz5f_JyEQ %}

## What is Azure Key Vault?

[Azure Key Vault](https://docs.microsoft.com/en-us/azure/key-vault/general/overview) is a cloud service that allows us to protect cryptographic keys, certificates (and the private keys associated with certificates), and secrets (such as connection strings and passwords) in the cloud.

## How to integrate Key Vault with Azure Functions

Because Azure functions are serverless pieces of code, there will be cases where we do not want to put any of our secrets (such as passwords or connection strings) into our function code in plain-text. For security reasons we need to protect the secrets we use in our function code to not expose secrets. So today we will look at how we can create a function app using PowerShell Core as the code base, and protect any secrets that we use in our function code with Azure Key Vault by integration.  

To get everything ready I will be using Azure CLI in a powershell console. First we will log into Azure by running:

```powershell
az login
```

Next we will create a `resource group`, `storage account`, `key vault`, `app service plan` and `function app` by running:

```powershell
# Variables - Function app and storage account names must be unique.
$randomInt = Get-Random -Maximum 9999
$resourceGroupName = "KeyVaultFunction"
$functionAppName = "func$randomInt"
$storageName = "sa$functionAppName"
$kvName = "kv$functionAppName"
$region = "uksouth"

# Create a resource resourceGroupName
az group create --name "$resourceGroupName" --location "$region"

# Create an azure storage account
az storage account create `
    --name "$storageName" `
    --location "$region" `
    --resource-group "$resourceGroupName" `
    --sku "Standard_LRS" `
    --kind "StorageV2"

# Create an azure key vault (RBAC model)
az keyvault create `
    --name "$kvName" `
    --resource-group "$resourceGroupName" `
    --location "$region" `
    --enable-rbac-authorization

# Create a Function App
az functionapp create `
    --name "$functionAppName" `
    --storage-account "$storageName" `
    --consumption-plan-location "$region" `
    --resource-group "$resourceGroupName" `
    --os-type "Windows" `
    --runtime "powershell" `
    --runtime-version "7.0" `
    --functions-version "3"
```

Next we will enable the function app with a **system assigned** [managed identity](https://docs.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/overview) so that we can permission our function app to access our key vault. Under the function app **settings** pane select **Identity** and enable the **system assigned** setting to be `ON` and save the setting:

### _Author_

Marcel.L - pwd9000@hotmail.co.uk
