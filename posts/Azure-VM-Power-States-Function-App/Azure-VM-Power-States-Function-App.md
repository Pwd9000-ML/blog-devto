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

```powershell
#// code/vmPowerFunction.ps1

using namespace System.Net

# Input bindings are passed in via param block.
param($request, $TriggerMetadata)

#Set default value
$status = 200

Try{
    # Write to the Azure Functions log stream.
    Write-Output "PowerShell HTTP trigger function processed a request."

    # Interact with query parameters or the body of the request.
    Write-Output ($request | ConvertTo-Json -depth 99)

    $ResourceGroupName = $request.query.ResourceGroupName
    $VMName = $request.query.VMName
    $Context =  $request.query.Context
    $Action = $request.query.Action
    
    $null = Connect-AzAccount -Identity
    $null = Set-AzContext $Context

    $vmStatus = Get-AzVM -ResourceGroupName $ResourceGroupName -Name $VMName -Status
    Write-output $vmStatus
    If(-not ($vmStatus)){
        $status = 404
        Throw 'ERROR! VM not found'
    }
    [string]$Message = "Virtual machine status: " + $vmStatus.statuses[-1].displayStatus
    Switch($Action){
        'start'{
            If($vmStatus.statuses[-1].displayStatus -ne 'VM running'){
                Start-AzVM -ResourceGroupName $ResourceGroupName -Name $VMName -Verbose
                [string]$message += '... Virtual machine is now starting'
            }
            Else{
                [string]$message += '... Virtual machine is already running'
            }
        }
        'stop'{
            If($vmStatus.statuses[-1].displayStatus -ne 'VM deallocated'){
                Stop-AzVM -ResourceGroupName $ResourceGroupName -Name $VMName -Force -Verbose
                [string]$message += '... Virtual machine is stopping'
            }
            Else{
                [string]$message += '... Virtual machine is already deallocated'
            }
        }
        'status'{
            [string]$message
        }
        default{
            [string]$message += ". $($request.query.action) is outside of the allowed actions. Only allowed actions are: 'start', 'stop', 'status'"
            $status = 400
        }
    }
}
Catch{
    [string]$message += $_
}

Write-output $message

# Associate values to output bindings by calling 'Push-OutputBinding'.
Push-OutputBinding -Name Response -Value (
    [HttpResponseContext]@{
        StatusCode = $status
        body = [string]$message
        headers = @{ "content-type" = "text/plain" }
    }
)
```

Next we will create a proxy URL, copy the `Get function URL`:  

![funcUrl](./assets/funcUrl.png)  

Navigate back to the `Functions` pane and select `Proxies`, then select `Add` with the following settings:

![funcProxy2](./assets/funcProxy2.png)

**Name:** `PowerAction`  
**Route template:** `/{Action}/{Context}/{ResourceGroupName}/{VMName}`  
**Allowed HTTP methods:** `GET`  
**Backend URL:** `<function URL>`  

**Request override**  
**HTTP method:** `POST`  

Add the following **Query** parameters:  
`Action: {Action}`  
`Context: {Context}`  
`ResourceGroupName: {ResourceGroupName}`  
`VMName: {VMName}`  
