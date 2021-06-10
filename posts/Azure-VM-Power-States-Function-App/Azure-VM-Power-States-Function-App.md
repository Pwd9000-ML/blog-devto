---
title: Power virtual machines ON or OFF using Azure functions
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

## How to control Azure virtual machines power states using an Azure function

Today we will look at how we can create a function app using PowerShell as the code base, that will allow us to check the power state of a virtual machine or stop/start a virtual machine by passing a URL request or a JSON body via a HTTP trigger to the function app.  

To get everything ready I will be using Azure CLI using a powershell console. First we will log into Azure by running:

```powershell
az login
```

Next we will create a `resource group`, `storage account`, `app service plan` and `function app` by running:

```powershell
# Function app and storage account names must be unique.
$randomInt = Get-Random -Maximum 9999
$resourceGroupName = "VmPowerFunction"
$storageName = "vmpowersa$randomInt"
$functionAppName = "vmpowerfunc$randomInt"
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

**Note:** In this tutorial we are using a [`Consumption`](https://docs.microsoft.com/en-us/azure/azure-functions/consumption-plan) app service plan and not a [`dedicated`](https://docs.microsoft.com/en-us/azure/azure-functions/dedicated-plan) or [`premium`](https://docs.microsoft.com/en-us/azure/azure-functions/functions-premium-plan?tabs=portal) plan as this will be sufficient enough for our function app. You can however change the plan if needed.

Next we will enable the function app with a `system assigned` [`managed identity`](https://docs.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/overview) so that we can permission our function app against the virtual machines we will be maintaining. Under the function app `settings` pane select `Identity` and enable the `system assigned` setting to be `ON` and save the setting:

![managedIdentity](./assets/managedIdentity.png)

With the Managed Identity now created, we can add a Role assignment and permissions (IAM) to the Subscription or Resource Group where our Vms reside. We will also give the function app the role `Virtual Machine Contributor` because we only want the app to be able to check the status of a VM and the ability to either stop or start a VM. On the same `settings` pane where we set the `identity` you will now see a new setting called `Permissions`. Click on `Azure Role Assignments` and add the relevant permissions at the resource group scope where the Vms resides.  
**Note:** You can also add the role assignment permissions via `IAM` at a desired scope such as at a management group or subscription scope.  

![managedIdentity2](./assets/managedIdentity2.png)

![managedIdentity3](./assets/managedIdentity3.png)

If you check the `IAM` permissions now under the scope we added the role assignment, you should see the `IAM` permission for our function app:  

![managedIdentity4](./assets/managedIdentity4.png)

Now we will configure our function app with the powershell code and triggers to finalize the solution.  
Under the `Functions` pane click `Add` with the following settings:  

![functionadd](./assets/functionadd.png)  

**Development Enviornment:** `Develop in portal`  
**Select a template:** `HTTP trigger`  
**New Function:** `VmPowerState`  
**Authorization level:** `Function`  

Next under `Code + Test` copy the following powershell code:  

```txt
// code/vmPowerFunction.ps1

```
