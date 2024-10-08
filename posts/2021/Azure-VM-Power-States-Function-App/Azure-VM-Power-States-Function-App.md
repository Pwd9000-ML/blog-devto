---
title: Power virtual machines ON or OFF using Azure functions
published: true
description: Azure - Function App to control VM power states
tags: 'azurefunctions, azure, serverless, powershell'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/Azure-VM-Power-States-Function-App/assets/main-cover.png'
canonical_url: null
id: 724451
date: '2021-06-10T17:57:09Z'
---

## What is an Azure function?

Azure Functions is a cloud service available on-demand that provides all the continually updated infrastructure and resources needed to run your applications. You focus on the pieces of code that matter most to you, and Functions handles the rest. Functions provides serverless compute for Azure. You can use Functions to build web APIs, respond to database changes, process IoT streams, manage message queues, and more.

{% youtube 8-jz5f_JyEQ %}

For more details on Azure Functions have a look at the [Microsoft Documentation](https://docs.microsoft.com/en-us/azure/azure-functions/functions-overview/?wt.mc_id=DT-MVP-5004771).

## How to control Azure virtual machines power states using an Azure function

Today we will look at how we can create a function app using PowerShell Core as the code base, that will allow us to check the power state of a virtual machine or stop/start a virtual machine by passing a URL request via a HTTP trigger to the function app.

To get everything ready I will be using Azure CLI in a powershell console. First we will log into Azure by running:

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
    --runtime-version "7.2" `
    --functions-version "4"
```

**Note:** In this tutorial we are using a [`Consumption`](https://docs.microsoft.com/en-us/azure/azure-functions/consumption-plan/?wt.mc_id=DT-MVP-5004771) app service plan and not a [`dedicated`](https://docs.microsoft.com/en-us/azure/azure-functions/dedicated-plan/?wt.mc_id=DT-MVP-5004771) or [`premium`](https://docs.microsoft.com/en-us/azure/azure-functions/functions-premium-plan?tabs=portal) plan. You can however change the plan if needed as the consumption plan may take a bit of time to start up once we start using it. But for the purposes of this tutorial and use case this plan will be sufficient enough for our function.

After the function app has been deployed we have to change the `requirements.psd1` file on our function to allow the `AZ` PowerShell module inside of our function by uncommenting the following.

Navigate to the Function App's **'App files'** and select the dropdown `requirements.psd1`, uncomment the line that says `'Az' = '8.*'`:

```powershell
# This file enables modules to be automatically managed by the Functions service.
# See https://aka.ms/functionsmanageddependency for additional information.
#
@{
    # For latest supported version, go to 'https://www.powershellgallery.com/packages/Az'.
    # To use the Az module in your function app, please uncomment the line below.
    'Az' = '8.*'
}
```

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/Azure-VM-Power-States-Function-App/assets/app01.png)

**NOTE:** After making this change for the first time, it can take up to one hour for the **AZ PowerShell module** to be fully installed on the Function App runtime, but this is a one of process and will allow AZ cmdlets to be used inside the Function App code.

Next we will enable the function app with a `system assigned` [`managed identity`](https://docs.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/overview/?wt.mc_id=DT-MVP-5004771) so that we can permission our function app against the virtual machines we will be maintaining. Under the function app `settings` pane select `Identity` and enable the `system assigned` setting to be `ON` and save the setting:

![managedIdentity](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/Azure-VM-Power-States-Function-App/assets/managedIdentity.png)

With the Managed Identity now created, we can add a Role assignment and permissions (IAM) to the Subscription or Resource Group where our Vms reside. We will also give the function app the role `Virtual Machine Contributor` because we only want the app to be able to check the status of a VM and the ability to either stop or start a VM. On the same `settings` pane where we set the `identity` you will now see a new setting called `Permissions`. Click on `Azure Role Assignments` and add the relevant permissions at the resource group scope where the Vms resides.  
**Note:** You can also add the role assignment permissions via `IAM` at a desired scope such as at a management group or subscription scope.

![managedIdentity2](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/Azure-VM-Power-States-Function-App/assets/managedIdentity2.png)

![managedIdentity3](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/Azure-VM-Power-States-Function-App/assets/managedIdentity3.png)

If you check the `IAM` permissions now under the scope we added the role assignment, you should see the `IAM` permission for our function app:

![managedIdentity4](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/Azure-VM-Power-States-Function-App/assets/managedIdentity4.png)

Now we will configure our function app with the powershell code and triggers to finalize the solution.  
Under the `Functions` pane click `Add` with the following settings:

![functionadd](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/Azure-VM-Power-States-Function-App/assets/functionadd.png)

**Development Environment:** `Develop in portal`  
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
        Throw "ERROR! VM [$VMName] not found. Please check if the 'Subscription ID', 'Resource Group Name' or 'VM name' is correct and exists."
    }
    [string]$Message = "Virtual machine [$VMName] status: " + $vmStatus.statuses[-1].displayStatus
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

Here is also a [Link](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2021/Azure-VM-Power-States-Function-App/code) to the function code.

Next we will create a proxy URL, copy the `Get function URL`:

![funcUrl](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/Azure-VM-Power-States-Function-App/assets/funcUrl.png)

Navigate back to the `Functions` pane and select `Proxies`, then select `Add` with the following settings:

![funcProxy2](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/Azure-VM-Power-States-Function-App/assets/funcProxy2.png)

**Name:** `PowerAction`  
**Route template:** `/{Action}/{Context}/{ResourceGroupName}/{VMName}`  
**Allowed HTTP methods:** `GET`  
**Backend URL:** `<function URL>`

**Request override**  
**HTTP method:** `POST`

Add the following **Query** parameters:

| Name              | Value               |
| ----------------- | ------------------- |
| Action            | {Action}            |
| Context           | {Context}           |
| ResourceGroupName | {ResourceGroupName} |
| VMName            | {VMName}            |

Now we can use a normal web browser to test our function app. Copy the proxy URL we just created: `https://functionappname.azurewebsites.net/{Action}/{Context}/{ResourceGroupName}/{VMName}` into a web browser and replace the query parameters with any of the following:

`Action` = This value can be `stop`, `start` or `status`.  
`Context` = This value should be the subscription ID where our VMs reside and our function apps identity has permission.  
`ResourceGroupName` = This value should be the name of the resource group where the VMs reside.  
`VMName` = The name of our VM we want to perform action against.

For example to check the `Status` of a VM `MyWebServer01` you could put this in your browser:  
`https://functionappname.azurewebsites.net/status/259b6576-0000-0000-0000-000000000000/ResourceGroup223/MyWebServer01`

To stop and de-allocate the VM `MyWevServer01` you could change the `{Action}` parameter to `Stop`:  
`https://functionappname.azurewebsites.net/stop/259b6576-0000-0000-0000-000000000000/ResourceGroup223/MyWebServer01`

Similarly you could also start a VM by changing the `{Action}` to `Start`.

![testFunc](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/Azure-VM-Power-States-Function-App/assets/testFunc.gif)

## Securing function apps

For the purposes of this tutorial be aware that the proxy URL we created to check the status, stop and start our VMs will be able to be run by anyone who knows the function app URL, subscription ID, Resource Group Name and VM Names. I would recommend securing the function app by following some of these [Function App Security recommendations](https://docs.microsoft.com/en-us/azure/architecture/serverless-quest/functions-app-security/?wt.mc_id=DT-MVP-5004771) as well as [Securing Azure Functions](https://docs.microsoft.com/en-us/azure/azure-functions/security-concepts/?wt.mc_id=DT-MVP-5004771).

A very quick and effective way as well to limit access to our URL is to only allow a specific IP or range of IPs to access our URL.  
Navigate to the function app `settings` pane and select `Networking`:

![funcSec1](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/Azure-VM-Power-States-Function-App/assets/funcSec1.png)

Next select `Access Restrictions` and add a rule to allow your IP:

![funcSec02](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/Azure-VM-Power-States-Function-App/assets/funcSec02.png)

By default this will block all inbound connections to our Proxy URL with the exception to our excluded IP. Now if anyone else tries to access the function they will be unable to.

![funcSec3](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/Azure-VM-Power-States-Function-App/assets/funcSec3.png)

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my [GitHub](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2021/Azure-VM-Power-States-Function-App/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [X/Twitter](https://x.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
