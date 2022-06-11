---
title: Running Docker based GitHub runner containers on Azure Container Instances (ACI)
published: false
description: Running Docker based GitHub runner containers on Azure Container Instances (ACI)
tags: 'github, azure, docker, containers'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part3/assets/main.png'
canonical_url: null
id: 1107072
series: Self Hosted Docker GitHub Runners on Azure
---

### Overview

All the code used in this tutorial can be found on my GitHub project: [docker-github-runner-windows](https://github.com/Pwd9000-ML/docker-github-runner-windows) or [docker-github-runner-linux](https://github.com/Pwd9000-ML/docker-github-runner-linux).

Welcome to Part 3 of my series: **Self Hosted Docker GitHub Runners on Azure**.

In part one and two of this series, we looked at how we can create **windows** and **linux** container images using docker and then running our self hosted **GitHub runners** as containers on a Virtual Machine running docker.

In this part, we will look at how we can utilize **Azure** to store and run our containers in the cloud using **Azure Container Registry (ACR)** to store images and **Azure Container Instances (ACI)** to run our self hosted GitHub runners, without the need of a Virtual Machine running docker.

Part four will cover how we can use **Azure Container Apps (ACA)** instead of **Azure Container Instances (ACI)**.

As in the first two parts of this series, instead of preparing a Virtual Machine with docker, we are going to use automation and CI/CD in **GitHub** using **GitHub Actions** to **build** our docker containers and then **push** the docker images to a **registry** we will create and host in **Azure** called [Azure Container Registry (ACR)](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-intro).

We will then use **GitHub Actions** to deploy a running instance of our self hosted **GitHub runner** as as an [Azure Container Instances (ACI)](https://docs.microsoft.com/en-us/azure/container-instances/container-instances-overview).

### Pre-Requisites

We will need to prepare a few things first. You can clone and use my GitHub repositories [docker-github-runner-windows](https://github.com/Pwd9000-ML/docker-github-runner-windows) or [docker-github-runner-linux](https://github.com/Pwd9000-ML/docker-github-runner-linux), or simply follow along these steps.

Things we will need are:

- An Azure Container Registry (ACR)
- A GitHub Account and repository linked with Azure

### Set up an Azure Container Registry (ACR)

For this step I will use a PowerShell script, [Deploy-ACR.ps1](https://github.com/Pwd9000-ML/docker-github-runner-windows/blob/master/Azure-Pre-Reqs/Deploy-ACR.ps1) running **Azure-CLI**, to create a **Resource Group** and an **Azure Container Registry** where we can push docker images to:

```powershell
#Log into Azure
#az login

# Setup Variables.
$randomInt = Get-Random -Maximum 9999
$resourceGroupName = "Demo-Azure-Container-Registry"
$region = "uksouth"
$acrName = "pwd9000registry$randomInt"

# Create a resource resourceGroupName
az group create --name "$resourceGroupName" --location "$region"

# Create an ACR (Basic)
az acr create --resource-group "$resourceGroupName" `
    --name "$acrName" `
    --sku "Basic" `
    --admin-enabled "false"
```

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part3/assets/acr01.png)

Make a note of the **Login Server FQDN** from the newly created ACR as we will use this value later to push images to the ACR:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part3/assets/acr02.png)

### Configure GitHub repository and link with Azure

Next we will configure a **Service Principal** to link our **GitHub repository** and **workflows** with **Azure**.

We will grant the principal access to the **Azure Container Registry** to allow us to build and push images to the ACR and also grant permissions to be able to deploy **Azure Container Instances (ACIs)** from the container images hosted on our ACR.

For this step I will use a PowerShell script, [Prepare-RBAC-ACI.ps1](https://github.com/Pwd9000-ML/docker-github-runner-windows/blob/master/Azure-Pre-Reqs/Deploy-ACR.ps1) running **Azure-CLI**.

This script will:

- Create a **Service Principal** which we can link with our **GitHub repository**
- Create an **Azure Container Instance (ACI)** deployment **Resource Group**, where we can deploy ACIs to later on
- Grant relevant access for the **Service Principal** over the ACI deployment **Resource Group**
- Grant Pull/Push access over the **Azure Container Registry (ACR)** we created earlier

```powershell
#Log into Azure
#az login

# Setup Variables.
$aciResourceGroupName = "Demo-ACI-GitHub-Runners-RG"
$appName="GitHub-ACI-Deploy"
$acrName="<ACRName>"
$region = "uksouth"

# Create a resource group to deploy ACIs to
az group create --name "$aciResourceGroupName" --location "$region"
$aciRGId = az group show --name "$aciResourceGroupName" --query id --output tsv

# Create AAD App and Service Principal and assign to RBAC Role to ACI deployment RG
az ad sp create-for-rbac --name $appName `
    --role "Contributor" `
    --scopes "$aciRGId" `
    --sdk-auth

# Assign additional RBAC role to Service Principal to push and pull images from ACR
$acrId = az acr show --name "$acrName" --query id --output tsv
az ad sp list --display-name $appName --query [].appId -o tsv | ForEach-Object {
    az role assignment create --assignee "$_" `
        --role "AcrPush" `
        --scope "$acrId"
    }
```

In the script above, the `'az ad sp create-for-rbac'` command will create an AAD app & service principal and will output a JSON object containing the credentials of the service principal:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part3/assets/rbac.png)

Copy this JSON object as we will add this as a **GitHub Secret**. You will only need the sections with the `clientId`, `clientSecret`, `subscriptionId`, and `tenantId` values:

```JSON
{
  "clientId": "<GUID>",
  "clientSecret": "<PrincipalSecret>",
  "subscriptionId": "<GUID>",
  "tenantId": "<GUID>"
}
```

As you can see we now have an empty resource group where we will deploy **container instances** into later using **GitHub Actions** (I named my Service principal App **GitHub-ACI-Deploy**):

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part3/assets/rbac02.png)

We also have `'AcrPush'` permissions on our **Service Principal** which will allow us to **Pull** and **Push** images to the ACR:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part3/assets/rbac03.png)

Next we will copy that JSON object Service Principal credentials, as well as a few other **GitHub Secrets** to our **GitHub repository**:

1. In the GitHub UI, navigate to your repository and select **Settings** > **Secrets** > **Actions**:

   ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part3/assets/ghsec01.png)

2. Select **New repository secret** to add the following secrets:

| **Secret** | **Value** |
| --- | --- |
| `AZURE_CREDENTIALS` | The entire JSON output from the service principal creation step |
| `REGISTRY_LOGIN_SERVER` | The login server name of the ACR (all lowercase). Example: _myregistry.azurecr.io_ |
| `REGISTRY_USERNAME` | The `clientId` from the JSON output from the service principal creation |
| `REGISTRY_PASSWORD` | The `clientSecret` from the JSON output from the service principal creation |
| `RESOURCE_GROUP` | The name of the resource group we created to deploy our ACIs into |

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part3/assets/ghsec02.png)

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part3/assets/ghsec02.png)
