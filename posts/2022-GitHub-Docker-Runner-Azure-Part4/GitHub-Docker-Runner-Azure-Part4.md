---
title: Run Docker based GitHub runner containers on Azure Container Instances (ACI)
published: true
description: Run Docker based GitHub runner containers on Azure Container Instances (ACI)
tags: 'github, azure, aci, containers'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part4/assets/main.png'
canonical_url: null
id: 1107073
series: Self Hosted GitHub Runner containers on Azure
date: '2022-06-17T08:00:45Z'
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
- Grant access to our GitHub **Service Principal** created in Part3 of this blog series on the **Resource Group** to create ACIs

For this step I will use a PowerShell script, [Prepare-RBAC-ACI.ps1](https://github.com/Pwd9000-ML/docker-github-runner-linux/blob/master/Azure-Pre-Reqs/Prepare-RBAC-ACI.ps1) running **Azure-CLI**, to create a **Resource Group** and grant access to our **GitHub Service Principal App** we created in the previous blog post (Part 3).

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

# Grant AAD App and Service Principal Contributor to ACI deployment RG
az ad sp list --display-name $appName --query [].appId -o tsv | ForEach-Object {
    az role assignment create --assignee "$_" `
        --role "Contributor" `
        --scope "$aciRGId"
    }
```

As you can see the script has created an empty resource group called: **Demo-ACI-GitHub-Runners-RG**, and gave our GitHub service principal **Contributor** access over the resource group.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part4/assets/rg.png)  

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

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part4/assets/rbac03.png)  

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

Because we have our repository already set up with the relevant **Service Principal** and **GitHub Secrets** from the previous blog post:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part4/assets/ghsec03.png)

We can create a **GitHub Workflow** to deploy our **Azure Container Instances**. [deployACI-Lin.yml](https://github.com/Pwd9000-ML/docker-github-runner-linux/blob/master/.github/workflows/deployACI-Lin.yml)

```yaml
name: Deploy_GHRunner_Linux_ACI

on:
  workflow_dispatch:

env:
  RUNNER_VERSION: 2.293.0
  ACI_RESOURCE_GROUP: 'Demo-ACI-GitHub-Runners-RG'
  ACI_NAME: 'gh-runner-linux-01'
  DNS_NAME_LABEL: 'gh-lin-01'
  GH_OWNER: 'Pwd9000-ML'
  GH_REPOSITORY: 'docker-github-runner-linux' #Change here to deploy self hosted runner ACI to another repo.

jobs:
  deploy-gh-runner-aci:
    runs-on: ubuntu-latest
    steps:
      # checkout the repo
      - name: 'Checkout GitHub Action'
        uses: actions/checkout@main

      - name: 'Login via Azure CLI'
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: 'Deploy to Azure Container Instances'
        uses: 'azure/aci-deploy@v1'
        with:
          resource-group: ${{ env.ACI_RESOURCE_GROUP }}
          image: ${{ secrets.REGISTRY_LOGIN_SERVER }}/pwd9000-github-runner-lin:${{ env.RUNNER_VERSION }}
          registry-login-server: ${{ secrets.REGISTRY_LOGIN_SERVER }}
          registry-username: ${{ secrets.REGISTRY_USERNAME }}
          registry-password: ${{ secrets.REGISTRY_PASSWORD }}
          name: ${{ env.ACI_NAME }}
          dns-name-label: ${{ env.DNS_NAME_LABEL }}
          environment-variables: GH_TOKEN=${{ secrets.PAT_TOKEN }} GH_OWNER=${{ env.GH_OWNER }} GH_REPOSITORY=${{ env.GH_REPOSITORY }}
          location: 'uksouth'
```

The workflow above mainly uses the `'azure/aci-deploy@v1'` **GitHub** Action. You can also set parameters such as `'cpu: 1'` and `'memory: 0.1'` to spec out the container instance. Check out the documentation of this extension here: [ACI deploy GitHub Action](https://github.com/Azure/aci-deploy#github-action-for-deploying-to-azure-container-instances).

**NOTE:** I have added the custom PAT token as a GitHub Secret on the repository: `'GH_TOKEN=${{ secrets.PAT_TOKEN }}'`:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part4/assets/PAT02.png)

We can manually trigger and run the workflow:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part4/assets/aci02.png)

After the workflow has run you should see the self hosted GitHub runner against the repository you specified in the workflow environment variables:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part4/assets/node.png)

You will also be able to see the ACI created under the resource group we created earlier:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part4/assets/aci-rg.png)

To stop and remove the ACI container you can run the following **Azure-CLI** command:

```powershell
az container delete --resource-group $aciResourceGroupName --name $aciName
```

We have successfully deployed self hosted GitHub runners using **Azure Container Instances**. In the next part of this series we will look at how we can run and automatically scale our self hosted GitHub runners up and down based on load/demand, using **Azure Container Apps (ACA)** utilizing **Kubernetes Event-driven Autoscaling (KEDA)**.

I hope you have enjoyed this post and have learned something new. You can find the code samples used in this blog post on my GitHub project: [docker-github-runner-windows](https://github.com/Pwd9000-ML/docker-github-runner-windows) or [docker-github-runner-linux](https://github.com/Pwd9000-ML/docker-github-runner-linux). :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
