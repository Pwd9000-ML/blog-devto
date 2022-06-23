---
title: Run Docker based GitHub runner containers on Azure Container Apps (ACA)
published: false
description: Running Docker based GitHub runner containers on Azure Container Apps (ACA)
tags: 'github, azure, docker, containers'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part5/assets/main.png'
canonical_url: null
id: 1111853
series: Self Hosted GitHub Runner containers on Azure
---

### Overview

All the code used in this tutorial can be found on my GitHub project: [docker-github-runner-windows](https://github.com/Pwd9000-ML/docker-github-runner-windows) or [docker-github-runner-linux](https://github.com/Pwd9000-ML/docker-github-runner-linux).

Welcome to Part 5 of my series: **Self Hosted GitHub Runner containers on Azure**.

In the previous part of this series, we looked at how we can use **Azure-CLI** or CI/CD workflows in **GitHub** using **GitHub Actions** to **run** self hosted **GitHub runner** docker containers as **Azure Container instances (ACI)** in **Azure** from a remote **container registry** also hosted in Azure (ACR).

Following on from the previous part we will now look at how we can use [Azure Container Apps (ACA)](https://docs.microsoft.com/en-gb/azure/container-apps/overview) to run images from the remote registry instead and also demonstrate how we can automatically scale our self hosted GitHub runners up and down based on load/demand, using **Kubernetes Event-driven Autoscaling (KEDA)**.

### Pre-Requisites

Things we will need before we can deploy container apps:

- Azure Container Apps deployment Resource Group (Optional)
- Grant access to our GitHub **Service Principal** created in [Part3](https://dev.to/pwd9000/storing-docker-based-github-runner-containers-on-azure-container-registry-acr-4om3) of this blog series on the Resource Group to create ACAs (Optional)
- Log Analytics Workspace to link with Azure Container Apps (Optional)
- An Azure Container Apps environment

For this step I will use a PowerShell script, [Prepare-ACA.ps1](https://github.com/Pwd9000-ML/docker-github-runner-linux/blob/master/Azure-Pre-Reqs/Prepare-ACA.ps1) running **Azure-CLI**, to create a **Resource Group**, **Log Analytics Workspace** and an **Azure Container Apps Environment**.

```powershell
#Log into Azure
#az login

#Add container app extension to Azure-CLI
az extension add --name containerapp

# Setup Variables.
$randomInt = Get-Random -Maximum 9999
$region = "uksouth"
$acaResourceGroupName = "Demo-ACA-GitHub-Runners-RG"
$acaEnvironment = "gh-runner-aca-env-$randomInt"
$acaLaws = "$acaEnvironment-laws"
$appName = "GitHub-ACI-Deploy" #Previously created Service Principal (See part 3 of blog series)

# Create a resource group to deploy ACA
az group create --name "$acaResourceGroupName" --location "$region"
$acaRGId = az group show --name "$acaResourceGroupName" --query id --output tsv

#Create Log Analytics Workspace for ACA
az monitor log-analytics workspace create --resource-group "$acaResourceGroupName" --workspace-name "$acaLaws"
$acaLawsId = az monitor log-analytics workspace show -g $acaResourceGroupName -n $acaLaws --query customerId --output tsv
$acaLawsKey = az monitor log-analytics workspace get-shared-keys -g $acaResourceGroupName -n $acaLaws --query primarySharedKey --output tsv

#Create ACA Environment
az containerapp env create --name "$acaEnvironment" `
    --resource-group "$acaResourceGroupName" `
    --logs-workspace-id "$acaLawsId" `
    --logs-workspace-key "$acaLawsKey" `
    --location "$region"

# Grant AAD App and Service Principal Contributor to ACI deployment RG
az ad sp list --display-name $appName --query [].appId -o tsv | ForEach-Object {
    az role assignment create --assignee "$_" `
        --role "Contributor" `
        --scope "$acaRGId"
    }
```

As you can see the script has created a resource group called: **Demo-ACA-GitHub-Runners-RG**, containing the **Azure Container Apps Environment** linked with a **Log Analytics Workspace**.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part5/assets/rg.png)

**NOTE**: Ensure that the GitHub **Service Principal** also has **AcrPush** permissions on the **Azure Container Registry (ACR)**. See [Part3](https://dev.to/pwd9000/storing-docker-based-github-runner-containers-on-azure-container-registry-acr-4om3) of this series, or you can use the following PowerShell snippet:

```powershell
#Log into Azure
#az login

# Setup Variables. (provide your ACR name)
$appName="GitHub-ACI-Deploy"
$acrName="<ACRName>"
$region = "uksouth"

# Create AAD App and Service Principal and assign to RBAC Role to push and pull images from ACR
$acrId = az acr show --name "$acrName" --query id --output tsv
az ad sp create-for-rbac --name $appName `
    --role "AcrPush" `
    --scopes "$acrId" `
    --sdk-auth
```

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part5/assets/rbac03.png)

### Deploy self hosted GitHub Runner Container Apps

With the pre-requirements complete, we will do the following to run and scale our self hosted GitHub runners inside of the **Container Apps Environment**:

- Create a self hosted GitHub runner container app inside of the container app environment
- Create an ACA auto scaling rule
- Test out our runners and dynamic scaling capabilities

I have prepared the following PowerShell script using **Azure-CLI** to deploy the **Container App**: [Deploy-ACA.ps1](https://github.com/Pwd9000-ML/docker-github-runner-linux/blob/master/Azure-Pre-Reqs/Deploy-ACA.ps1).

```powershell
#Log into Azure
#az login

#Add container app extension to Azure-CLI
az extension add --name containerapp

# Setup Variables.
$randomInt = Get-Random -Maximum 9999
$region = "uksouth"
$acaResourceGroupName = "Demo-ACA-GitHub-Runners-RG"
$acaEnvironment = "gh-runner-aca-env-$randomInt"
$acaLaws = "$acaEnvironment-laws"

# Create a resource group to deploy ACA
az group create --name "$acaResourceGroupName" --location "$region"

#Create Log Analytics Workspace for ACA
az monitor log-analytics workspace create --resource-group "$acaResourceGroupName" --workspace-name "$acaLaws"
$acaLawsId = az monitor log-analytics workspace show -g $acaResourceGroupName -n $acaLaws --query customerId --output tsv
$acaLawsKey = az monitor log-analytics workspace get-shared-keys -g $acaResourceGroupName -n $acaLaws --query primarySharedKey --output tsv

#Create ACA Environment
az containerapp env create --name "$acaEnvironment" `
    --resource-group "$acaResourceGroupName" `
    --logs-workspace-id "$acaLawsId" `
    --logs-workspace-key "$acaLawsKey" `
    --location "$region"
```

That concludes this five part series where we took a deep dive in detail on how to implement **Self Hosted GitHub Runner containers on Azure**.

I hope you have enjoyed this post and have learned something new. You can find the code samples used in this blog post on my GitHub project: [docker-github-runner-windows](https://github.com/Pwd9000-ML/docker-github-runner-windows) or [docker-github-runner-linux](https://github.com/Pwd9000-ML/docker-github-runner-linux). :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
