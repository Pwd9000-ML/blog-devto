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

All the code used in this tutorial can be found on my GitHub project: [docker-github-runner-linux](https://github.com/Pwd9000-ML/docker-github-runner-linux).

Welcome to Part 5 of my series: **Self Hosted GitHub Runner containers on Azure**.

In the previous part of this series, we looked at how we can use **Azure-CLI** or CI/CD workflows in **GitHub** using **GitHub Actions** to **run** self hosted **GitHub runner** docker containers as **Azure Container Instances (ACI)** in **Azure** from a remote **container registry** also hosted in Azure (ACR).

One of the drawbacks of having self hosted agent runners are if no **GitHub Action Workflows** or **Jobs** are running, the GitHub runner will just sit there idle consuming cost, whether that self hosted **GitHub runner** be an ACI or a docker container hosted on a VM.

So following on from the previous part we will look at how we can use [Azure Container Apps (ACA)](https://docs.microsoft.com/en-gb/azure/container-apps/overview) to run images from the remote registry instead and also demonstrate how we can automatically scale our self hosted GitHub runners from **no runners** or **0** up and down based on load/demand, using **Kubernetes Event-driven Autoscaling (KEDA)**.

This will allow us to save costs and only provision **self hosted GitHub runners** only when needed.

**NOTE**: At the time of this writing Azure Container Apps supports:

- Any **_Linux-based_** x86-64 (linux/amd64) container image.
- Containers from any public or private container registry.
- There are no available [KEDA scalers for GitHub runners](https://keda.sh/docs/2.7/scalers/) at the time of this writing.

### Proof of Concept

Because there are no available [KEDA scalers for GitHub runners](https://keda.sh/docs/2.7/scalers/) at the time of this writing, we will use an **Azure Storage Queue** to control the scaling and provisioning of our self hosted **GitHub runners**.

We will create the **Container App Environment** and **Azure Queue**, then create a [Azure Queue KEDA Scale Rule](https://docs.microsoft.com/en-us/azure/container-apps/scale-app#keda-scalers-conversion) that will have a minimum of **0** and maximum of **3** self hosted runner containers.

We will use the **Azure Storage Queue** to associate **GitHub workflows** as queue messages, to provision/scale self hosted runners using an external **GitHub workflow Job** that will signal KEDA to provision a self hosted runner on the fly for us to use on any subsequent **Workflow Jobs** inside of the **Workflow**.

After all subsequent **Workflow Jobs** have finished running, the queue message associated with the workflow will be evicted from the queue and KEDA will scale back down/destroy the self hosted runner container, essentially scaling back down to **0** if there are no other **GitHub workflows** running.

### Pre-Requisites

Things we will need to implement this container app proof of concept:

- Azure Container Apps deployment **Resource Group** (Optional).
- Azure **Container Registry** (ACR) - See [Part3](https://dev.to/pwd9000/storing-docker-based-github-runner-containers-on-azure-container-registry-acr-4om3) of this blog series. (Admin account needs to be enabled).
- **GitHub Service Principal** linked with **Azure** - See [Part3](https://dev.to/pwd9000/storing-docker-based-github-runner-containers-on-azure-container-registry-acr-4om3) of this blog series.
- **Log Analytics Workspace** to link with Azure Container Apps.
- **Azure storage account** and **queue** to be used for scaling with KEDA.
- Azure Container Apps **environment**.
- **Container App** from docker image (self hosted GitHub runner) stored in ACR.

For this step I will use a PowerShell script, [Deploy-ACA.ps1](https://github.com/Pwd9000-ML/docker-github-runner-linux/blob/master/Azure-Pre-Reqs/AzureContainerApps-Queue-Scaler/Deploy-ACA.ps1) running **Azure-CLI**, to create the entire **environment** and **Container App** linked with a target **GitHub Repo** where we will scale runners using KEDA.

```powershell
#Log into Azure
#az login

#Add container app extension to Azure-CLI
az extension add --name containerapp

#Variables (ACA)
$randomInt = Get-Random -Maximum 9999
$region = "uksouth"
$acaResourceGroupName = "Demo-ACA-GitHub-Runners-RG" #Resource group created to deploy ACAs
$acaStorageName = "aca2keda2scaler$randomInt" #Storage account that will be used to scale runners/KEDA queue scaling
$acaEnvironment = "gh-runner-aca-env-$randomInt" #Azure Container Apps Environment Name
$acaLaws = "$acaEnvironment-laws" #Log Analytics Workspace to link to Container App Environment
$acaName = "myghprojectpool" #Azure Container App Name

#Variables (ACR) - ACR Admin account needs to be enabled
$acrLoginServer = "registryname.azurecr.io" #The login server name of the ACR (all lowercase). Example: _myregistry.azurecr.io_
$acrUsername = "acrAdminUser" #The Admin Account `Username` on the ACR
$acrPassword = "acrAdminPassword" #The Admin Account `Password` on the ACR
$acrImage = "$acrLoginServer/pwd9000-github-runner-lin:2.293.0" #Image reference to pull

#Variables (GitHub)
$pat = "ghPatToken" #GitHub PAT token
$githubOrg = "Pwd9000-ML" #GitHub Owner/Org
$githubRepo = "docker-github-runner-linux" #Target GitHub repository to register self hosted runners against
$appName = "GitHub-ACI-Deploy" #Previously created Service Principal linked to GitHub Repo (See part 3 of blog series)

# Create a resource group to deploy ACA
az group create --name "$acaResourceGroupName" --location "$region"
$acaRGId = az group show --name "$acaResourceGroupName" --query id --output tsv

# Create an azure storage account and queue to be used for scaling with KEDA
az storage account create `
    --name "$acaStorageName" `
    --location "$region" `
    --resource-group "$acaResourceGroupName" `
    --sku "Standard_LRS" `
    --kind "StorageV2" `
    --https-only true `
    --min-tls-version "TLS1_2"
$storageConnection = az storage account show-connection-string --resource-group "$acaResourceGroupName" --name "$acaStorageName" --output tsv
$storageId = az storage account show --name "$acaStorageName" --query id --output tsv

az storage queue create `
    --name "gh-runner-scaler" `
    --account-name "$acaStorageName" `
    --connection-string "$storageConnection"

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

# Grant AAD App and Service Principal Contributor to ACA deployment RG + `Storage Queue Data Contributor` on Storage account
az ad sp list --display-name $appName --query [].appId -o tsv | ForEach-Object {
    az role assignment create --assignee "$_" `
        --role "Contributor" `
        --scope "$acaRGId"

    az role assignment create --assignee "$_" `
        --role "Storage Queue Data Contributor" `
        --scope "$storageId"
}

#Create Container App from docker image (self hosted GitHub runner) stored in ACR
az containerapp create --resource-group "$acaResourceGroupName" `
    --name "$acaName" `
    --image "$acrImage" `
    --environment "$acaEnvironment" `
    --registry-server "$acrLoginServer" `
    --registry-username "$acrUsername" `
    --registry-password "$acrPassword" `
    --secrets gh-token="$pat" storage-connection-string="$storageConnection" `
    --env-vars GH_OWNER="$githubOrg" GH_REPOSITORY="$githubRepo" GH_TOKEN=secretref:gh-token `
    --cpu "1.75" --memory "3.5Gi" `
    --min-replicas 0 `
    --max-replicas 3
```

**NOTES:** Before running the above PowerShell script you will need to enable the **Admin Account** on the **Azure Container Registry** and make a note of the `Username` and `Password` as well as the `LoginSever` and `Image reference` as these needs to be passed as variables in the script:

```powershell
#Variables (ACR) - ACR Admin account needs to be enabled
$acrLoginServer = "registryname.azurecr.io" #The login server name of the ACR (all lowercase). Example: _myregistry.azurecr.io_
$acrUsername = "acrAdminUser" #The Admin Account `Username` on the ACR
$acrPassword = "acrAdminPassword" #The Admin Account `Password` on the ACR
$acrImage = "$acrLoginServer/pwd9000-github-runner-lin:2.293.0" #Image reference to pull
```

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part5/assets/acr-admin.png)

You will also need to provide variables for the **GitHub Service Principal/AppName** we created in [Part3](https://dev.to/pwd9000/storing-docker-based-github-runner-containers-on-azure-container-registry-acr-4om3) of the blog series, that is linked with Azure, a **GitHub PAT token** and specify the **Owner** and **Repository** to link with the **Container App**:

```powershell
#Variables (GitHub)
$pat = "ghPatToken" #GitHub PAT token
$githubOrg = "Pwd9000-ML" #GitHub Owner/Org
$githubRepo = "docker-github-runner-linux" #Target GitHub repository to register self hosted runners against
$appName = "GitHub-ACI-Deploy" #Previously created Service Principal linked to GitHub Repo (See part 3 of blog series)
```

See [creating a personal access token](https://docs.github.com/en/enterprise-server@3.4/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) on how to create a GitHub PAT token. PAT tokens are only displayed once and are sensitive, so ensure they are kept safe.

The minimum permission scopes required on the PAT token to register a self hosted runner are: `"repo"`, `"read:org"`:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part5/assets/PAT.png)

**Tip:** I recommend only using short lived PAT tokens and generating new tokens whenever new agent runner registrations are required.

### Let's look at what this script created step-by-step

It created a resource group called: **Demo-ACA-GitHub-Runners-RG**, containing the **Azure Container Apps Environment** linked with a **Log Analytics Workspace**, an **Azure Storage account** and a **Container App** based of a **GitHub runner** image pulled from our **Azure Container Registry**.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part5/assets/rg1.png)

In addition the GitHub **service principal** created in [Part3](https://dev.to/pwd9000/storing-docker-based-github-runner-containers-on-azure-container-registry-acr-4om3) of this series has also been granted access on the Resource Group as **Contributor** and **Storage Queue Data Contributor** on the storage account.

It also created an empty queue for us **(gh-runner-scaler)**, that we will use to associate running **GitHub Workflows** as queue messages once we start running and scaling **GitHub Action Workflows**.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part5/assets/queue.png)

### Container App

Lets take a deeper look into the container app itself.  



### Running and Scaling Workflows

### Conclusion

As you can see it was pretty easy to provision an **Azure Container Apps** environment and create a **Container App** and **KEDA** scale rule using **azure queues** to automatically provision self hosted **GitHub runners** onto a repository of our choice that has **0** or **no** runners at all.

There are a few caveats and pain points I would like to highlight in this proof of concept implementation, and hopefully these will be remediated soon. Once they are, I will create another part to this blog series once the following pain points have been fixed or improved.

**Issue 1**: Azure Container Apps doesn't fully yet allow us to use the **Container Apps system assigned managed identity** to pull images from **Azure Container Registry**. This means that we have to enable the ACRs **Admin Account** in order to provision images from the Azure Container Registry. You can follow this [GitHub issue](https://github.com/microsoft/azure-container-apps/issues/268) regarding this bug.

**Issue 2**: As mentioned earlier, there are no available [KEDA scalers for GitHub runners](https://keda.sh/docs/2.7/scalers/) at the time of this writing. This means that we have to utilise an **Azure Storage Queue** linked with our **GitHub workflow** to provision/scale runners with KEDA using an external **GitHub workflow Job** by sending a queue message with our workflow for KEDA to be signalled to provision a self hosted runner on the fly for us to use in any subsequent **GitHub Workflow Jobs**.

One benefit of this method however is that we can have a minimum container count of **0**, which means we won't ever have any idle runners doing nothing consuming unnecessary costs, thus essentially only paying for self hosted runners when they are actually **running**. This method will only create self hosted GitHub runners based on the **Azure Queue length** essentially associating our workflow run with a queue item.

Once the **GitHub Workflow** finishes it will remove the queue item and KEDA will scale back down to **0** if there are no **GitHub workflows** running.

That concludes this five part series where we took a deep dive in detail on how to implement **Self Hosted GitHub Runner containers on Azure**.

I hope you have enjoyed this post and have learned something new. You can find the code samples used in this blog post on my GitHub project: [docker-github-runner-linux](https://github.com/Pwd9000-ML/docker-github-runner-linux). :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
