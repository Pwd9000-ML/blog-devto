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

**NOTE:** We have only created our **Function App** at this stage, we do not have any Functions yet. We will create our first function later on in this tutorial with GitHub.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Function-CICD/assets/func02.png)

## Create a GitHub repository

Next up head over to your GitHub account and create a new repository. We will use this repository to link our function app/s source code to.  
I have called my repository **_Demo-Azure-Functions_**

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Function-CICD/assets/ghrepo01.png)

## Prepare Local Requirements

As mentioned at the beginning of this post we will now install and run a few pre-requirements on the machine we will be working and developing our function code on.

Install the following tools:

- [Install Azure Function Core Tools](https://github.com/Azure/azure-functions-core-tools#installing)
- [Install VSCode](https://code.visualstudio.com/download)
- [Install Azure Functions extension for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-azurefunctions)
- [Install C# extension for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=ms-dotnettools.csharp)

## Clone GitHub Function repository

With all our tools now installed we can now clone our GitHub function repository to our local machine:

1. Copy the **clone URL**  
   ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Function-CICD/assets/clone01.png)

2. Open VSCode and navigate to the **Command Palette** ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Function-CICD/assets/clone02.png)

3. In the command palette type clone and click on **Git:clone** ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Function-CICD/assets/clone03.png)

4. Paste in the copied **clone URL** and select a folder you want to clone the repository to. (**Note:** The repo will be cloned to a sub folder in the folder you selected, the name of this sub folder will match the repo name and will contain all your repo files.) ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Function-CICD/assets/clone04.png)

## Link Azure Function App with GitHub Repository

Next we will create an empty folder inside of our locally cloned repository. This folder will represent our **Function App**:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Function-CICD/assets/folder.png)

**NOTE:** I have called my folder in my repo the same name as the name I have given to my Azure Function App we created earlier; **demofunc6144**.

Now we will create our first function inside of the folder using the **Azure Functions extension for Visual Studio Code** we installed earlier.

In VSCode you will see the extension installed on the left side of the screen. Click on the extension and select **Create New Project**:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Function-CICD/assets/proj01.png)

This will then open the **Command Palette** again, browse to and select the empty folder we created representing our **Function App**:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Function-CICD/assets/proj02.png)

The **Command Palette** will now present you with some options, select the following:

1. Select a language: **C#** ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Function-CICD/assets/proj03.png)

2. Select a .NET runtime: **.NET 6** ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Function-CICD/assets/proj04.png)

3. Select a template for your project;s first function: **HTTP trigger** ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Function-CICD/assets/proj05.png)

4. Give the function a name: **MyFirstDotnetFunction** ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Function-CICD/assets/proj06.png)

5. Provide a namespace: **My.Function** ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Function-CICD/assets/proj07.png)

6. Select appropriate access rights: **Anonymous/Function/Admin** ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Function-CICD/assets/proj08.png)

Once the above process has completed, notice that now we have a **C#** function app template in our folder **demofunc6144** we can straight away start working on. Because this is also in our local **git repository** we can ensure that our code is always managed through source control.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Function-CICD/assets/proj09.png)

Save and commit the the changes, then push the new function to the remote **GitHub repository**:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Function-CICD/assets/proj10.png)

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Function-CICD/assets/proj11.png)

## Deploy Function App

Now we have a fully integrated workspace we can use to create and develop **Functions**. But we have not set up any CI/CD yet.

This brings us to the last step, automating the deployment of our **Functions** with CI/CD using **GitHub Actions**

1. Navigate back to the **Function App** hosted in Azure that we created earlier in this tutorial and got to **Deployment Center**: ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Function-CICD/assets/depl01.png)

2. Select Source **GitHub** and set the **Org**, **Repo** and **Branch** we created and hit **Save**. (**NOTE:** You will be asked to link your GitHub account if you are performing this step for the very first time): ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Function-CICD/assets/depl02.png)

**NOTE:** You can also manage the **Publish Profile** from the above step.

When you **save** the configuration above, you will notice that on the **GitHub repository** there is a new automation workflow that is automatically set up as well as a new repository secret.
