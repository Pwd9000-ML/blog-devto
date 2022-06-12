---
title: Running Docker based GitHub runner containers on Azure Container Instances (ACI)
published: false
description: Running Docker based GitHub runner containers on Azure Container Instances (ACI)
tags: 'github, azure, aci, containers'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part4/assets/main.png'
canonical_url: null
id: 1107073
series: Self Hosted GitHub Runner containers on Azure
---

notes::

We will then use **GitHub Actions** to deploy a running instance of our self hosted **GitHub runner** as as an [Azure Container Instances (ACI)](https://docs.microsoft.com/en-us/azure/container-instances/container-instances-overview).

Previous script:

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
