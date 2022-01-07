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

This brings me to this new tutorial I want to share with you today. I was thinking how we can even better the process by also getting an email alert when a resource has been decommissioned or if a decommission has failed, and perhaps including the error message in the alert if it was a failed decommission. So today I will share with you a general guide on how we can utilize a service in Azure called **SendGrid** to send us email notifications from an **Azure Function App**.

This tutorial is only a general guide on how to utilize the **SendGrid** service inside of a **Function App** to send notification emails and does not follow on my previous tutorial. This guide is meant to serve as a supplement to show how to set up the **SendGrid** service and utilize the service in any **Powershell** based **Function App** in any environment, giving the ability to send email notifications to relevant stakeholders.

Feel free to integrate the steps in this tutorial in addition to my previous blog post mentioned above, if you have the additional requirement to be notified by email about resource decommissions. Let's get started.

## What is SendGrid?

[SendGrid](https://docs.sendgrid.com/for-developers/partners/microsoft-azure-2021#create-a-twilio-sendgrid-account) is a third party provider in Azure that provides a cloud-based email service. The service manages various types of email including shipping notifications, friend requests, sign-up confirmations, and email newsletters. It also handles internet service provider (ISP) monitoring, domain keys, sender policy framework (SPF), and feedback loops. Additionally provides link tracking, open rate reporting. It also allows companies to track email opens, unsubscribes, bounces, and spam reports.

Azure offers a variety of **[SendGrid pricing plans](https://sendgrid.com/marketing/sendgrid-services-cro/#pricing-app)**. For the purpose of our use case and this tutorial we will create and use the **FREE** plan which gives us access to the API and also 100 emails/day forever.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-SendGrid-Function-Alerts/assets/sendgrid_free1.png)

## Steps to set up

We are going to need to perform the following steps:

1. **Create Azure resources:** (Optional) We will first create a Resource Group, PowerShell based Function App and KeyVault. This step is optional only for this demo/tutorial.
2. **Create a SendGrid account:** We will create a FREE SendGrid account, activate the account and create a sender identity.
3. **Generate a SendGrid API Key:** We will generate an API Key, store this key in the key vault and consume it in our PowerShell function to authenticate to the SendGrid service.
4. **Create a SendGrid API PowerShell Function:** We will create a PowerShell function to interact with the SendGrid API and service to send an email notification.
5. **Integrate PowerShell Function into Function App:** We will integrate our PowerShell function into our Function App and test.

## 1. Create Azure resources

To set up the function app I wrote a PowerShell script using AZ CLI, that would build and configure the function app to use as a demo for this tutorial. You can find the script I used on my [github code](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/Azure-SendGrid-Function-Alerts/code) page called [Azure-Pre-Reqs.ps1](https://github.com/Pwd9000-ML/blog-devto/blob/main/posts/Azure-SendGrid-Function-Alerts/code/Azure-Pre-Reqs.ps1).

First we will log into Azure by running:

```powershell
az login
```

After logging into Azure and selecting the subscription, we can run the script that will create the function app resources and set the environment up:

```powershell
## code/Azure-Pre-Reqs.ps1

#Log into Azure
#az login

# Setup Variables.
$randomInt = Get-Random -Maximum 9999
$subscriptionId = (get-azcontext).Subscription.Id
$resourceGroupName = "SendGrid-Function-App-Demo"
$storageName = "sgridfuncsa$randomInt"
$functionAppName = "sgridfunc$randomInt"
$kvName = "sgridfunkv$randomInt"
$region = "uksouth"

# Create a resource resourceGroupName
az group create --name "$resourceGroupName" --location "$region"

# Create a Key Vault
az keyvault create `
    --name "$kvName" `
    --resource-group "$resourceGroupName" `
    --location "$region" `
    --enable-rbac-authorization

# Authorize the operation to create a few secrets - Signed in User (Key Vault Secrets Officer)
az ad signed-in-user show --query objectId -o tsv | foreach-object {
    az role assignment create `
        --role "Key Vault Secrets Officer" `
        --assignee "$_" `
        --scope "/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.KeyVault/vaults/$kvName"
    }

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
    --runtime "powershell" `
    --runtime-version "7.0" `
    --functions-version "3" `
    --assign-identity

# Set Key Vault Secrets (secret values are set to 'xxxx', we will update these later after creating SendGrid account)
Start-Sleep -s 15
az keyvault secret set --vault-name "$kvName" --name "sendGridApiKey" --value "xxxx"
az keyvault secret set --vault-name "$kvName" --name "fromAddress" --value "xxxx"

#Configure Function App environment variables:
$settings = @(
  # @Microsoft.KeyVault(SecretUri=https://<key-vault-name>.vault.azure.net/secrets/<secret-name>/<secret-version>)
  # or @Microsoft.KeyVault(SecretUri=https://<key-vault-name>.vault.azure.net/secrets/<secret-name>/) '/' at end means to take latest secret
  "sendGridApiKey=@Microsoft.KeyVault(SecretUri=https://$kvName.vault.azure.net/secrets/sendGridApiKey/)" #from KV
  "fromAddress=@Microsoft.KeyVault(SecretUri=https://$kvName.vault.azure.net/secrets/fromAddress/)" #from KV
)

$settings | foreach-object {
    az functionapp config appsettings set --name "$functionAppName" --resource-group "$resourceGroupName" --settings """$_"""
}

#Assign Function System MI permissions to KV to access secrets
$functionMI = $(az resource list --name $functionAppName --query [*].identity.principalId --out tsv)| foreach-object {
    az role assignment create `
        --role "Key Vault Secrets User" `
        --assignee "$_" `
        --scope "/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.KeyVault/vaults/$kvName"
    }
```

Lets take a closer look, step-by-step what the above script does as part of setting up the function app environment.

1. Create a resource group called `SendGrid-Function-App-Demo`. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-SendGrid-Function-Alerts/assets/rg.png)
2. Create a **PowerShell** Function App with `SystemAssigned` managed identity, `consumption` app service plan, `insights`, a `key vault` and function app `storage account`. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-SendGrid-Function-Alerts/assets/func.png) ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-SendGrid-Function-Alerts/assets/funcmi1.png)
3. Configure Function App environment variables. (Will be consumed inside of function app later). ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-SendGrid-Function-Alerts/assets/funcappsettings1.png)

   **NOTE:** You will see that we are referencing the `fromAddress` and `sendGridApiKey` from our key vault.

4. Assign Function App `SystemAssigned` managed identity permissions to access/read secrets on the key vault. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-SendGrid-Function-Alerts/assets/kvrbac1.png)
5. Create two dummy key vault secrets called `fromAddress` and `sendGridApiKey` which we will update later. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-SendGrid-Function-Alerts/assets/kvsec1.png)

## 2. Create a SendGrid account

Next we will create a SendGrid Account. Go to the **Azure Portal** and search services for **SendGrid** and **create** an account. We will use the **Free** account as mentioned earlier.  

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-SendGrid-Function-Alerts/assets/sgrid_plan.png)

You will need to provide contact details such as your email address and phone number as **SendGrid** is a SaaS service subscription. Shortly after creating the **SendGrid** Azure resource you will receive an activation email on the email address you have provided at creation time.  

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-SendGrid-Function-Alerts/assets/sgrid_activate.png)

After activation you can navigate to the **SendGrid** publisher's site directly from Azure.  

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-SendGrid-Function-Alerts/assets/sgrid_nav.png)

From the dashboard we will proceed to create the **Sender Identity**.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-SendGrid-Function-Alerts/assets/sgrid_sender.png)

**Note:** For the **From Email Address**, verification is required. If the email domain doesn't match one of your authenticated domains, you'll need to verify ownership of the email address before using it as a sender.



I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my [Github](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/Azure-SendGrid-Function-Alerts/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}
