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

### Overview

All the code used in this tutorial can be found on my GitHub project: [docker-github-runner-windows](https://github.com/Pwd9000-ML/docker-github-runner-windows) or [docker-github-runner-linux](https://github.com/Pwd9000-ML/docker-github-runner-linux).

Welcome to Part 4 of my series: **Self Hosted GitHub Runner containers on Azure**.

In the previous part of this series, we looked at how we can use CI/CD in **GitHub** using **GitHub Actions** to **build** our docker containers and then **push** the docker images to an **Azure Container Registry (ACR)** we created in **Azure**.

Following on from the previous part we will now look at how we can use [Azure Container Instances (ACI)](https://docs.microsoft.com/en-us/azure/container-instances/container-instances-overview) to run images from the remote registry.

I will cover two scenarios, first how we can run self hosted **GitHub runner** as as an **Azure Container Instances (ACI)** from our images using using **Azure-CLI**, and second how we can use CI/CD workflows in **GitHub** using **GitHub Actions** to deploy our ACIs.

### Pre-Requisites

Things we will need are:

- Create an ACI deployment Resource Group
- Grant access to our **Service Principal** we created in the previous step to create ACIs

For this step I will use a PowerShell script, [Prepare-RBAC-ACI.ps1](https://github.com/Pwd9000-ML/docker-github-runner-linux/blob/master/Azure-Pre-Reqs/Prepare-RBAC-ACI.ps1) running **Azure-CLI**, to create a **Resource Group** and grant access to our **GitHub Service Principal App**.

```powershell
#Log into Azure
#az login

# Setup Variables.
$aciResourceGroupName = "Demo-ACI-GitHub-Runners-RG"
$appName="GitHub-ACI-Deploy" #Previously created Service Principal (See part 3 of blog series)
$region = "uksouth"

# Create a resource group to deploy ACIs to
az group create --name "$aciResourceGroupName" --location "$region"
$aciRGId = az group show --name "$aciResourceGroupName" --query id --output tsv

# Create AAD App and Service Principal and assign to RBAC Role to ACI deployment RG
az ad sp list --display-name $appName --query [].appId -o tsv | ForEach-Object {
    az role assignment create --assignee "$_" `
        --role "Contributor" `
        --scope "$aciRGId"
    }
```

As you can see the script has created an empty resource group called: **Demo-ACI-GitHub-Runners-RG**, and gave our GitHub service principal **Contributor** access over the resource group.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part4/assets/rg.png)

### Deploy ACI - Azure-CLI

Next we will deploy a self hosted GitHub runner as an **Azure Container Instance (ACI)** using **Azure-CLI**.

Get the relevant image details from the **Azure Container Registry**:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part4/assets/acr-lin02.png)

For this step I will use a PowerShell script, [Deploy-ACI.ps1](https://github.com/Pwd9000-ML/docker-github-runner-linux/blob/master/Azure-Pre-Reqs/Deploy-ACI.ps1)

```powershell
#az login

#Variables
$randomInt = Get-Random -Maximum 9999
$aciResourceGroupName = "Demo-ACI-GitHub-Runners-RG" #Resource group created to deploy ACIs
$aciName = "gh-runner-linux-$randomInt" #ACI name (unique)
$acrLoginServer = "registryName.azurecr.io" #The login server name of the ACR (all lowercase). Example: _myregistry.azurecr.io_
$acrUsername = "servicePrincipalClientId" #The `clientId` from the JSON output from the service principal creation (See part 3 of blog series)
$acrPassword = "servicePrincipalClientSecret" #The `clientSecret` from the JSON output from the service principal creation (See part 3 of blog series)
$image = "$acrLoginServer/pwd9000-github-runner-lin:2.293.0" #image reference to pull
$pat = "githubPAT" #GitHub PAT token
$githubOrg = "Pwd9000-ML" #GitHub Owner
$githubRepo = "docker-github-runner-linux" #GitHub repository to register self hosted runner against
$osType = "Linux" #Use "Windows" if image is Windows OS

az container create --resource-group "$aciResourceGroupName" `
    --name "$aciName" `
    --image "$image" `
    --registry-login-server "$acrLoginServer" `
    --registry-username "$acrUsername" `
    --registry-password "$acrPassword" `
    --environment-variables GH_TOKEN="$pat" GH_OWNER="$githubOrg" GH_REPOSITORY="$githubRepo" `
    --os-type "$osType"
```

**NOTE:** Remember when we ran our docker containers in part one and two of this series we had to pass in some **environment variables** using the `'-e'` option to specify the **PAT (Personal Access Token)**, **GitHub Organisation** and **Repository** to register the runner against. We pass these values in using the `'--environment-variables'` parameter as show above.

See [creating a personal access token](https://docs.github.com/en/enterprise-server@3.4/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) on how to create a GitHub PAT token. PAT tokens are only displayed once and are sensitive, so ensure they are kept safe.

The minimum permission scopes required on the PAT token to register a self hosted runner are: `"repo"`, `"read:org"`:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part4/assets/PAT.png)

**Tip:** I recommend only using short lived PAT tokens and generating new tokens whenever new agent runner registrations are required.

After running this command, under the GitHub repository settings, you will see a new self hosted GitHub runner. (This is our **Azure Container Instance**):

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part4/assets/gh-aci.png)

You will also see the ACI under the resource group we created earlier:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part4/assets/rg02.png)

You can simply re-run the above script to add more runners and ACIs. To stop and remove the ACI container you can run:

```powershell
az container delete --resource-group $aciResourceGroupName --name $aciName
```

Next we will look at how we can use CI/CD in GitHub to deploy ACIs using **GitHub Actions**

### Deploy ACI - GitHub CI/CD

Because we have our repository already set up with the relevant **Service Principal** and **GitHub Secrets**:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part4/assets/ghsec03.png)

We can create a **GitHub Workflow** to deploy our **Azure Container Instances**.
