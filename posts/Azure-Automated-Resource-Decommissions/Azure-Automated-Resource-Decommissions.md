---
title: Automate Azure Resource Decommissions (with tracking)
published: false
description: Azure - Automate Azure Resource Decommissions
tags: 'azurefunctions, azure, serverless, automation'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/Azure-Automated-Resource-Decommissions/assets/main_img.png'
canonical_url: null
id: 930485
---

## Overview

Today we are going to look at a common use case around resource management in Azure, how to manage our resource decommissions more effectively, and even having the ability for our users to self serve a resource decommission by simply using an Azure tag, and also be able to track decommissions or failed decommissions using a tracker table **(Azure table storage)**.

We can ease the management of handling our resource decommissions by simply using **[Tags](https://docs.microsoft.com/en-us/azure/azure-resource-manager/management/tag-resources?tabs=json)** and automate the decommission process using an Azure serverless **[Function App](https://docs.microsoft.com/en-us/azure/azure-functions/functions-overview)** with **Powershell** as the code base set on a daily run trigger. We will also utilize the **[Funtion Apps](https://docs.microsoft.com/en-us/azure/azure-functions/functions-overview)** own storage account to create two **tables**. One called **Tracker** to track successful decommissions by **resource ID** and date of decommission, and also a table called **Failed** in which we will track failed decommissions. Say for example if a resource had a resource lock on it or some sort of other failure that does not allow our automation to successfully complete the decommission task.

So in this demo I will be using a **[Resource Tag](https://docs.microsoft.com/en-us/azure/azure-resource-manager/management/tag-resources?tabs=json)** called **Decommission**. The value will be a date format of **dd/MM/yyyy**.

| Tag Key      | Tag Value  |
| ------------ | ---------- |
| Decommission | dd/MM/yyyy |

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-Automated-Resource-Decommissions/assets/date_Tag.png)

The idea is simple, place the **Decommission** tag on the **resource** OR **resource group** that you would like to decommission as well as the date that you want that decommission to take place on. The function app will run on a daily **Cron** schedule and search resources/resource groups that are tagged with the **Decommission** key and evaluate based on the given **Date** value whether the decommission should be initiated or not, and also track the decommission by recording the event into an Azure **Storage Account Table** with the resource ID and date of the successful/failed decommission, so that we can track and audit our automated events.

## Pre-Requisites

To set up everything we need for our function app I wrote a PowerShell script using AZ CLI, that would build and configure all the things needed. There was one manual step however I will cover a bit later on. But for now you can find the script I used on my [github code](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/Azure-Automated-Resource-Decommissions/code) page called [Azure-Pre-Reqs.ps1](https://github.com/Pwd9000-ML/blog-devto/blob/main/posts/Azure-Automated-Resource-Decommissions/code/Azure-Pre-Reqs.ps1).  

First we will log into Azure by running:  

```powershell
az login
```

After logging into Azure and selecting the subscription, we can run the script that will create all the resources and set the environment up:  

```powershell
## code/Azure-Pre-Reqs.ps1

#Log into Azure
#az login

# Setup Variables.
$randomInt = Get-Random -Maximum 9999
$subscriptionId = (get-azcontext).Subscription.Id
$resourceGroupName = "Automated-Resource-Decommissioning"
$storageName = "decomfuncsa$randomInt"
$tableName = "Tracker"
$tablePartition = "Decommissioned"
$functionAppName = "decomfunc$randomInt"
$region = "uksouth"
$scopes = "$subscriptionId" #Array of Subscriptions that will be covered by automate decommissioning e.g: "$subscriptionId1, $subscriptionId2"

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
    --runtime "powershell" `
    --runtime-version "7.0" `
    --functions-version "3" `
    --assign-identity

#Configure Function App environment variables:
$settings = @(
  "Function_Scopes=$scopes"  
  "Function_RGName=$resourceGroupName"
  "Function_SaActName=$storageName"
  "Function_TableName=$tableName"
  "Function_TablePartition=$tablePartition"
)

$settings | foreach-object {
    az functionapp config appsettings set --name "$functionAppName" --resource-group "$resourceGroupName" --settings """$_"""
}

# Authorize the operation to create the tracker table - Signed in User
az ad signed-in-user show --query objectId -o tsv | foreach-object {
    az role assignment create `
        --role "Reader and Data Access" `
        --assignee "$_" `
        --scope "/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.Storage/storageAccounts/$storageName"

    az role assignment create `
        --role "Storage Table Data Contributor" `
        --assignee "$_" `
        --scope "/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.Storage/storageAccounts/$storageName"
    }

#Create Tracker Table in Function storage acc
Start-Sleep -s 15
$storageKey = az storage account keys list -g $resourceGroupName -n $storageName --query [0].value -o tsv
az storage table create `
    --account-name "$storageName" `
    --account-key "$storageKey" `
    --name "$tableName" `

#Create Table in Function storage to track failed decommissions
az storage table create `
    --account-name "$storageName" `
    --account-key "$storageKey" `
    --name "Failed" `

#Assign Function System MI permissions to Storage account(Read) and table(Write) and contributor to subscription to be able to do decommissions
$functionMI = $(az resource list --name $functionAppName --query [*].identity.principalId --out tsv)| foreach-object {
    az role assignment create `
        --role "Reader and Data Access" `
        --assignee "$_" `
        --scope "/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.Storage/storageAccounts/$storageName" `

    az role assignment create `
        --role "Storage Table Data Contributor" `
        --assignee "$_" `
        --scope "/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.Storage/storageAccounts/$storageName/tableServices/default/tables/blogs"

    az role assignment create `
        --role "Contributor" `
        --assignee "$_" `
        --subscription "$subscriptionId"
    }
```

Lets take a closer look, step-by-step what the above script does as part of setting up the environment.

1. Create a resource group called `Automated-Resource-Decommissioning`. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-Automated-Resource-Decommissions/assets/rg.png)
2. Create an azure storage account for the function app. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-Automated-Resource-Decommissions/assets/funcsa.png)
3. Create a PowerShell Function App with `SystemAssigned` managed identity, `consumption` app service plan and `insights`. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-Automated-Resource-Decommissions/assets/func.png) ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-Automated-Resource-Decommissions/assets/funcmi1.png)
4. Configure Function App environment variables. (Will be consumed inside of function app later). ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-Automated-Resource-Decommissions/assets/funcappsettings1.png)
5. Create `Tracker` and `Failed` storage tables in the function apps storage account. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-Automated-Resource-Decommissions/assets/satabbles1.png)
6. Assign Function App `SystemAssigned` managed identity permissions to Storage account(Read), table(Write) and subscription(Contributor). ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-Automated-Resource-Decommissions/assets/sarbac1.png) ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-Automated-Resource-Decommissions/assets/subrbac1.png)
7. Remember I mentioned earlier there is one manual step. In the next step we will change the `requirements.psd1` file on our function to allow the `AZ` module inside of our function by uncommenting the following, as well as adding a module to be installed called `AzTable`  

```powershell
# This file enables modules to be automatically managed by the Functions service.
# See https://aka.ms/functionsmanageddependency for additional information.
#
@{
    # For latest supported version, go to 'https://www.powershellgallery.com/packages/Az'. 
    # To use the Az module in your function app, please uncomment the line below.
    'Az' = '7.*'
    'AzTable' = '2.*'
}
```

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-Automated-Resource-Decommissions/assets/manual1.png)

**NOTE:** Remember to save the manual change we made on `requirements.psd1` above. That is it, our environment is set up and in the next section we will configure the function to run automated decommissions and schedule a timer.
