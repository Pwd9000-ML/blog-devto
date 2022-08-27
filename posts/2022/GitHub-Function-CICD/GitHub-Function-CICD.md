---
title: Implement CI/CD with GitHub - Deploy Azure Functions
published: true
description: Implementing CI/CD with GitHub by automating Azure Function deployment
tags: 'githubactions, azuredevops, github, azurefunctions'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Function-CICD/assets/main.png'
canonical_url: null
id: 1051702
date: '2022-05-11T09:47:24Z'
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

Lets start by creating a resource group and a windows dotnet function app in our Azure subscription. For this step I have written a PowerShell script using Azure CLI. You can also find ths script on my [GitHub repository](https://github.com/Pwd9000-ML/blog-devto/blob/main/posts/2022/GitHub-Function-CICD/code/Azure-Pre-Reqs.ps1).

```powershell
#Log into Azure
az login

# Setup Variables.
$randomInt = Get-Random -Maximum 9999
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

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Function-CICD/assets/func.png)

**NOTE:** We have only created our **Function App** at this stage, we do not have any Functions yet. We will create our first function later on in this tutorial with GitHub.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Function-CICD/assets/func02.png)

## Create a GitHub repository

Next up head over to your GitHub account and create a new repository. We will use this repository to link our function app/s source code to.  
I have called my repository **_Demo-Azure-Functions_**

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Function-CICD/assets/ghrepo01.png)

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
   ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Function-CICD/assets/clone01.png)

2. Open VSCode and navigate to the **Command Palette** ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Function-CICD/assets/clone02.png)

3. In the command palette type clone and click on **Git:clone** ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Function-CICD/assets/clone03.png)

4. Paste in the copied **clone URL** and select a folder you want to clone the repository to. (**Note:** The repo will be cloned to a sub folder in the folder you selected, the name of this sub folder will match the repo name and will contain all your repo files.) ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Function-CICD/assets/clone04.png)

## Link Azure Function App with GitHub Repository

Next we will create an empty folder inside of our locally cloned repository. This folder will represent our **Function App**:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Function-CICD/assets/folder.png)

**NOTE:** I have called my folder in my repo the same name as the name I have given to my Azure Function App we created earlier; **demofunc6144**.

Now we will create our first function inside of the folder using the **Azure Functions extension for Visual Studio Code** we installed earlier.

In VSCode you will see the extension installed on the left side of the screen. Click on the extension and select **Create New Project**:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Function-CICD/assets/proj01.png)

This will then open the **Command Palette** again, browse to and select the empty folder we created representing our **Function App**:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Function-CICD/assets/proj02.png)

The **Command Palette** will now present you with some options, select the following:

1. Select a language: **C#** ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Function-CICD/assets/proj03.png)

2. Select a .NET runtime: **.NET 6** ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Function-CICD/assets/proj04.png)

3. Select a template for your project's first function: **HTTP trigger** ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Function-CICD/assets/proj05.png)

4. Give the function a name: **MyFirstDotnetFunction** ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Function-CICD/assets/proj06.png)

5. Provide a namespace: **My.Function** ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Function-CICD/assets/proj07.png)

6. Select appropriate access rights: **Anonymous/Function/Admin** ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Function-CICD/assets/proj08.png)

Once the above process has completed, notice that now we have a **C#** function app template in our folder **demofunc6144** we can start working on straight away. Because this code is also now in our local **git repository** we can ensure that our code is always managed through source control.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Function-CICD/assets/proj09.png)

Save and commit the the changes, then push the new function to the remote **GitHub repository**:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Function-CICD/assets/proj10.png)

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Function-CICD/assets/proj11.png)

## Deploy Function App

Now we have a fully integrated workspace we can use to create and develop **Functions** for our Function App. But we have not set up any CI/CD yet.

This brings us to the last step, automating the deployment of our **Functions** with CI/CD using **GitHub Actions**

1. Navigate back to the **Function App** hosted in Azure that we created earlier in this tutorial and go to **Deployment Center**: ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Function-CICD/assets/depl01.png)

2. Select Source **GitHub** and set the **Org**, **Repo** and **Branch** we created and hit **Save**. (**NOTE:** You will be asked to link your GitHub account if you are performing this step for the very first time): ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Function-CICD/assets/depl02.png)

**NOTE:** You can also manage the **Publish Profile** from the above step.

When you **save** on the configuration above, you will notice that on the **GitHub repository** there is a new automation workflow that is automatically created as well as a new repository secret.

The workflow will be located in a special folder called **.github/workflows** that is automatically created by Azure:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Function-CICD/assets/work01.png)

In my case the workflow was called **master_decomfunc6144.yml**:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Function-CICD/assets/work02.png)

Let's take a closer look at this workflow:

```yml
name: Build and deploy dotnet core app to Azure Function App - demofunc6144

on:
  push:
    branches:
      - master
    paths:
      - 'demofunc6144/**'
  workflow_dispatch:

env:
  AZURE_FUNCTIONAPP_PACKAGE_PATH: 'demofunc6144' # set this to the path to your web app project, defaults to the repository root
  DOTNET_VERSION: '6.0.x' # set this to the dotnet version to use

jobs:
  build-and-deploy:
    runs-on: windows-latest
    steps:
      - name: 'Checkout GitHub Action'
        uses: actions/checkout@v2

      - name: Setup DotNet ${{ env.DOTNET_VERSION }} Environment
        uses: actions/setup-dotnet@v1
        with:
          dotnet-version: ${{ env.DOTNET_VERSION }}

      - name: 'Resolve Project Dependencies Using Dotnet'
        shell: pwsh
        run: |
          pushd './${{ env.AZURE_FUNCTIONAPP_PACKAGE_PATH }}'
          dotnet build --configuration Release --output ./output
          popd

      - name: 'Run Azure Functions Action'
        uses: Azure/functions-action@v1
        id: fa
        with:
          app-name: 'demofunc6144'
          slot-name: 'Production'
          package: '${{ env.AZURE_FUNCTIONAPP_PACKAGE_PATH }}/output'
          publish-profile: ${{ secrets.AZUREAPPSERVICE_PUBLISHPROFILE_AD8BBBC377A040C480EB918BC04CE61C }}
```

**NOTE:** I have added the workflow trigger to only trigger on my **master** branch and for any changes made under the folder/repo path **demofunc6144**. The **workflow_dispatch:** trigger allows us to additionally trigger and run the automation workflow manually.

```yml
#Trigger
on:
  push:
    branches:
      - master
    paths:
      - 'demofunc6144/**'
  workflow_dispatch:
```

Also note that I have changed the environment variables for the function app package path to **demofunc6144**

```yml
#Environment variables
env:
  AZURE_FUNCTIONAPP_PACKAGE_PATH: 'demofunc6144' # set this to the path to your web app project, defaults to the repository root
  DOTNET_VERSION: '6.0.x' # set this to the dotnet version to use
```

Let's take a look at what this automation workflow will do when it is triggered:

```yml
jobs:
  build-and-deploy:
    runs-on: windows-latest
    steps:
      - name: 'Checkout GitHub Action'
        uses: actions/checkout@v2

      - name: Setup DotNet ${{ env.DOTNET_VERSION }} Environment
        uses: actions/setup-dotnet@v1
        with:
          dotnet-version: ${{ env.DOTNET_VERSION }}

      - name: 'Resolve Project Dependencies Using Dotnet'
        shell: pwsh
        run: |
          pushd './${{ env.AZURE_FUNCTIONAPP_PACKAGE_PATH }}'
          dotnet build --configuration Release --output ./output
          popd

      - name: 'Run Azure Functions Action'
        uses: Azure/functions-action@v1
        id: fa
        with:
          app-name: 'demofunc6144'
          slot-name: 'Production'
          package: '${{ env.AZURE_FUNCTIONAPP_PACKAGE_PATH }}/output'
          publish-profile: ${{ secrets.AZUREAPPSERVICE_PUBLISHPROFILE_AD8BBBC377A040C480EB918BC04CE61C }}
```

The above job has 4 steps:

1. The code is checked out onto the GitHub runner.
2. The version of .NET we specified in the environment variables will be installed on the GitHub runner.
3. The Azure Function is built and packaged.
4. The Function is deployed to the Azure Function App, **demofunc6144** using the **publish-profile** of the Function App:

```yml
publish-profile: ${{ secrets.AZUREAPPSERVICE_PUBLISHPROFILE_AD8BBBC377A040C480EB918BC04CE61C }}
```

Note that the **Publish Profile** is actually stored as a GitHub Action Secret, this was also automatically created by Azure as part of the workflow YAML file:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Function-CICD/assets/sec01.png)

**NOTE:** This Actions Secret is basically the contents of the Function Apps **Publish Profile File** which can be downloaded and re-added if ever needed manually:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Function-CICD/assets/pub01.png)

Let's trigger this workflow manually and deploy our function into the Azure Function App. In GitHub navigate to Actions, select the workflow and then **Run Workflow**:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Function-CICD/assets/run01.png)

After the workflow has run, we can now see our Function in the Function App on Azure.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Function-CICD/assets/fin01.png)

## Conclusion

That's all there is to it, now we have successfully integrated our function app development lifecycle using source control with Git and GitHub and have the ability to automatically deploy our Functions using CI/CD workflows with GitHub Actions.

We can simply create additional folders for any new Function Apps along with a corresponding YAML workflow linked to deploy functions created for the relevant Function Apps in Azure.

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my published [Github](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2022/GitHub-Function-CICD/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
