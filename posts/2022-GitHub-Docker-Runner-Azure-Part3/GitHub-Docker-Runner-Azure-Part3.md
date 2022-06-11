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

Part four will focus on how we can use **Azure Container Apps (ACA)** instead of **Azure Container Instances (ACI)** which is the focus of this part.

As in the first two parts of this series, instead of preparing a Virtual Machine with docker, we are going to use automation and CI/CD in **GitHub** using **Actions** to **build** our docker containers and then **push** the docker images to a **registry** we will create in **Azure** called [Azure Container Registry (ACR)](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-intro).

We will then use **GitHub Actions** to deploy a running instance of our self hosted **GitHub runner** as as an [Azure Container Instances (ACI)](https://docs.microsoft.com/en-us/azure/container-instances/container-instances-overview).

### Pre-Requisites

We will need to prepare a few things first. You can also clone and use my GitHub repositories [docker-github-runner-windows](https://github.com/Pwd9000-ML/docker-github-runner-windows) or [docker-github-runner-linux](https://github.com/Pwd9000-ML/docker-github-runner-linux), or simply follow along the following steps.

Things we will need are:

- Azure Container Registry (ACR)
- GitHub Account and repository linked with Azure

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

Next we will configure a **Service Principal** to link our **GitHub repository** with **Azure** and grant the principal relevant access to our **Azure Container Registry** to allow us to push images to the ACR and also permissions over our subscription to be able to deploy **Azure Container Instances (ACIs)** from the images we will host on our ACR.
