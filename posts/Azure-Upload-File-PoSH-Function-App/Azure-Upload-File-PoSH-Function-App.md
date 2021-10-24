---
title: Upload Files to Azure Storage using a PowerShell Function App
published: false
description: Azure - Function App file uploader
tags: 'tutorial, powershell, productivity, azure'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Azure-Upload-File-PoSH-Function-App/assets/main-cover.png'
canonical_url: null
id: 874213
---

## Overview

With Hacktober 2021 coming to an end soon, I thought I would share with you a little experiment I did using an Azure serverless Function App with Powershell as the code base. The idea was to create an easy to use, reusable `File Uploader API` that would allow someone to upload a file to an Azure Storage Account blob container by posting a HTTP request.

The HTTP request would be a JSON body and only requires the file name and the file Content/data in a serialized Base64 string. The PowerShell Function App would then deserialize the base64 string into a temporary file, rename and copy the file as a blob into a storage account container called `fileuploads`.

## Set everything up automatically

To stage and setup the entire environment for my API automatically I wrote a PowerShell script using AZ CLI, that would build and configure all the things I would need to start work on my function. There was one manual step however I will cover a bit later on. But for now you can find the script I used on my [github code](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/Azure-Upload-File-PoSH-Function-App/code) page called `setup_environment.ps1`.

First we will log into Azure by running:

```powershell
az login
```

After logging into Azure and selecting the subscription comes the script that will set everything up:

```powershell
# Setup Variables.
$randomInt = Get-Random -Maximum 9999
$subscriptionId = (get-azcontext).Subscription.Id
$resourceGroupName = "Function-App-Storage2"
$storageName = "storagefuncsa$randomInt"
$functionAppName = "storagefunc$randomInt"
$region = "uksouth"
$secureStore = "securesa$randomInt"
$secureContainer = "fileuploads"

# Create a resource resourceGroupName
az group create --name "$resourceGroupName" --location "$region"

# Create an azure storage account for secure store (uploads)
az storage account create `
    --name "$secureStore" `
    --location "$region" `
    --resource-group "$resourceGroupName" `
    --sku "Standard_LRS" `
    --kind "StorageV2" `
    --https-only true `
    --min-tls-version "TLS1_2"

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
  "SEC_STOR_RGName=$resourceGroupName"
  "SEC_STOR_StorageAcc=$secureStore"
  "SEC_STOR_StorageCon=$secureContainer"
)

az functionapp config appsettings set `
    --name "$functionAppName" `
    --resource-group "$resourceGroupName" `
    --settings @settings

# Authorize the operation to create the container - Signed in User (Storage Blob Data Contributor Role)
az ad signed-in-user show --query objectId -o tsv | foreach-object {
    az role assignment create `
        --role "Storage Blob Data Contributor" `
        --assignee "$_" `
        --scope "/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.Storage/storageAccounts/$secureStore"
    }

#Create Upload container in secure store
Start-Sleep -s 30
az storage container create `
    --account-name "$secureStore" `
    --name "$secureContainer" `
    --auth-mode login

#Assign Function System MI permissions to Storage account(Read) and container(Write)
$functionMI = $(az resource list --name $functionAppName --query [*].identity.principalId --out tsv)| foreach-object {
    az role assignment create `
        --role "Reader and Data Access" `
        --assignee "$_" `
        --scope "/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.Storage/storageAccounts/$secureStore" `

    az role assignment create `
        --role "Storage Blob Data Contributor" `
        --assignee "$_" `
        --scope "/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.Storage/storageAccounts/$secureStore/blobServices/default/containers/$secureContainer"
    }
```

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my [Github](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/Azure-Upload-File-PoSH-Function-App/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}
