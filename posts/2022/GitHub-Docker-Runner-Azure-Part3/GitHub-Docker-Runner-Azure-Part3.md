---
title: Build Docker based GitHub runner containers on Azure Container Registry (ACR)
published: true
description: Build Docker based GitHub runner containers on Azure Container Registry (ACR)
tags: 'github, azure, acr, containers'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Docker-Runner-Azure-Part3/assets/main.png'
canonical_url: null
id: 1107072
series: Self Hosted GitHub Runner containers on Azure
date: '2022-06-15T08:21:55Z'
---

### Overview

All the code used in this tutorial can be found on my GitHub project: [docker-github-runner-windows](https://github.com/Pwd9000-ML/docker-github-runner-windows) or [docker-github-runner-linux](https://github.com/Pwd9000-ML/docker-github-runner-linux).

Welcome to Part 3 of my series: **Self Hosted GitHub Runner containers on Azure**.

In part one and two of this series, we looked at how we can create **windows** and **linux** container images using docker and then running our self hosted **GitHub runners** as containers on a Virtual Machine running docker.

As in the first two parts of this series, instead of preparing a Virtual Machine with docker, we are going to use CI/CD in **GitHub** using **GitHub Actions** to **build** our docker containers, as well as scanning the container for any **vulnerabilities** using **Trivy** before **pushing** the docker images to a **registry** we will create and host in **Azure** called [Azure Container Registry (ACR)](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-intro/?wt.mc_id=DT-MVP-5004771).

In part 4 of this blog series we will cover how we can use **Azure Container Instances (ACI)** to run images from the remote registry hosted in **Azure**.

### Pre-Requisites

We will need to prepare a few things first. You can clone and use my GitHub repositories [docker-github-runner-windows](https://github.com/Pwd9000-ML/docker-github-runner-windows) or [docker-github-runner-linux](https://github.com/Pwd9000-ML/docker-github-runner-linux), or simply follow along these steps.

Things we will need are:

- An Azure Container Registry (ACR)
- A GitHub Account and repository linked with Azure

### Set up an Azure Container Registry (ACR)

For this step I will use a PowerShell script, [Deploy-ACR.ps1](https://github.com/Pwd9000-ML/docker-github-runner-windows/blob/master/Azure-Pre-Reqs/AzureContainerRegistry/Deploy-ACR.ps1) running **Azure-CLI**, to create a **Resource Group** and an **Azure Container Registry** where we can push docker images to:

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

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Docker-Runner-Azure-Part3/assets/acr01.png)

Make a note of the **Login Server FQDN** from the newly created ACR as we will use this value later in a **GitHub Secret** for pushing images to the ACR:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Docker-Runner-Azure-Part3/assets/acr02.png)

### Configure GitHub repository and link with Azure

Next we will configure a **Service Principal** to link our **GitHub repository** and **workflows** with **Azure**.

We will grant the principal access to the **Azure Container Registry** to allow us to build and push images to the ACR.

For this step I will use a PowerShell script, [Prepare-RBAC-ACR.ps1](https://github.com/Pwd9000-ML/docker-github-runner-windows/blob/master/Azure-Pre-Reqs/AzureContainerRegistry/Prepare-RBAC-ACR.ps1) running **Azure-CLI**. This script will:

- Create a **Service Principal** which we can link with our **GitHub repository**
- Grant Pull/Push access over the **Azure Container Registry (ACR)** we created earlier

```powershell
#Log into Azure
#az login

# Setup Variables. (provide your ACR name)
$appName = "GitHub-ACI-Deploy"
$acrName = "<ACRName>"

# Create AAD App and Service Principal and assign to RBAC Role to push and pull images from ACR
$acrId = az acr show --name "$acrName" --query id --output tsv
az ad sp create-for-rbac --name $appName `
    --role "AcrPush" `
    --scopes "$acrId" `
    --sdk-auth
```

In the script above, the `'az ad sp create-for-rbac'` command will create an AAD app & service principal and will output a JSON object containing the credentials of the service principal:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Docker-Runner-Azure-Part3/assets/rbac.png)

Copy this JSON object as we will add this as a **GitHub Secret**. You will only need the sections with the `clientId`, `clientSecret`, `subscriptionId`, and `tenantId` values:

```JSON
{
  "clientId": "<GUID>",
  "clientSecret": "<PrincipalSecret>",
  "subscriptionId": "<GUID>",
  "tenantId": "<GUID>"
}
```

**NOTE:** I named my Service principal App **GitHub-ACI-Deploy**. We have `'AcrPush'` permissions on our **Service Principal** which will allow us to **Pull** and **Push** images to the ACR:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Docker-Runner-Azure-Part3/assets/rbac03.png)

Next we will copy that JSON object Service Principal credentials, as well as a few other **GitHub Secrets** to our **GitHub repository**:

- In the GitHub UI, navigate to your repository and select **Settings** > **Secrets** > **Actions**:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Docker-Runner-Azure-Part3/assets/ghsec01.png)

- Select **New repository secret** to add the following secrets:

| **Secret** | **Value** |
| --- | --- |
| `AZURE_CREDENTIALS` | The entire JSON output from the service principal creation step |
| `REGISTRY_LOGIN_SERVER` | The login server name of the ACR (all lowercase). Example: _myregistry.azurecr.io_ |
| `REGISTRY_USERNAME` | The `clientId` from the JSON output from the service principal creation |
| `REGISTRY_PASSWORD` | The `clientSecret` from the JSON output from the service principal creation |

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Docker-Runner-Azure-Part3/assets/ghsec03.png)

**NOTE:** Make sure to also save these **GitHub Secrets** inside of a key vault for later use as we will be using the same values to deploy **Azure Container Instances** in the next blog post in this series.

### Build and Push docker image to ACR

With all the repository secrets now set up, we will be creating a **GitHub workflow** to build our docker image, scan the image for any vulnerabilities and also push our image to the **Azure Container Registry** using a few **GitHub Actions**.

**NOTE:** Vulnerability scanning using trivy is only available on **Linux** containers at the moment.

In parts one and two of this blog series we created some scripts and a **dockerfile** inside of a folder and then built the docker images on our windows 11 machine using **Docker-Desktop** and **Docker-Compose**.

But now with these scripts and docker files in source control inside of a **GitHub repository** ([windows repo](https://github.com/Pwd9000-ML/docker-github-runner-windows) / [linux repo](https://github.com/Pwd9000-ML/docker-github-runner-linux)), we can use **GitHub Actions** to build the images instead using CI/CD.

Create a new workflow under the GitHub repository that contains the dockerfile:

You can use this: [Windows_Container_Workflow](https://github.com/Pwd9000-ML/docker-github-runner-windows/blob/master/.github/workflows/dockerBuildAcr-Win.yml) for **Windows containers**.

```yml
name: Windows_Container_Workflow

on:
  workflow_dispatch:

env:
  RUNNER_VERSION: 2.293.0

jobs:
  build-and-push:
    runs-on: windows-latest
    steps:
      # checkout the repo
      - name: 'Checkout GitHub Action'
        uses: actions/checkout@main

      - name: 'Login via Azure CLI'
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: 'Build and push image'
        uses: azure/docker-login@v1
        with:
          login-server: ${{ secrets.REGISTRY_LOGIN_SERVER }}
          username: ${{ secrets.REGISTRY_USERNAME }}
          password: ${{ secrets.REGISTRY_PASSWORD }}
      - run: |
          docker build --build-arg RUNNER_VERSION=${{ env.RUNNER_VERSION }} -t ${{ secrets.REGISTRY_LOGIN_SERVER }}/pwd9000-github-runner-win:${{ env.RUNNER_VERSION }} .
          docker push ${{ secrets.REGISTRY_LOGIN_SERVER }}/pwd9000-github-runner-win:${{ env.RUNNER_VERSION }}
```

Or you can use this: [Linux_Container_Workflow](https://github.com/Pwd9000-ML/docker-github-runner-linux/blob/master/.github/workflows/dockerBuildAcr-Lin.yml) for **Linux containers** that includes vulnerability scanning.

```yml
name: Linux_Container_Workflow

on:
  workflow_dispatch:

env:
  RUNNER_VERSION: 2.293.0

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      # checkout the repo
      - name: 'Checkout GitHub Action'
        uses: actions/checkout@main

      - name: 'Login via Azure CLI'
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: 'Build GitHub Runner container image'
        uses: azure/docker-login@v1
        with:
          login-server: ${{ secrets.REGISTRY_LOGIN_SERVER }}
          username: ${{ secrets.REGISTRY_USERNAME }}
          password: ${{ secrets.REGISTRY_PASSWORD }}
      - run: |
          docker build --build-arg RUNNER_VERSION=${{ env.RUNNER_VERSION }} -t ${{ secrets.REGISTRY_LOGIN_SERVER }}/pwd9000-github-runner-lin:${{ env.RUNNER_VERSION }} .

      - name: 'Vulnerability scan container image with Trivy'
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ secrets.REGISTRY_LOGIN_SERVER }}/pwd9000-github-runner-lin:${{ env.RUNNER_VERSION }}
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'

      - name: Upload Trivy scan results to GitHub Security tab
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

      - name: 'Push container image to ACR'
        uses: azure/docker-login@v1
        with:
          login-server: ${{ secrets.REGISTRY_LOGIN_SERVER }}
          username: ${{ secrets.REGISTRY_USERNAME }}
          password: ${{ secrets.REGISTRY_PASSWORD }}
      - run: |
          docker push ${{ secrets.REGISTRY_LOGIN_SERVER }}/pwd9000-github-runner-lin:${{ env.RUNNER_VERSION }}
```

Notice that our trigger is set to `on: workflow_dispatch:`. This allows us to trigger the build manually.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Docker-Runner-Azure-Part3/assets/run.png)

**NOTE:** This workflow will build a self hosted GitHub runner container image using a runner version specified with an environment variable `env: RUNNER_VERSION: 2.293.0`. The image will also be tagged with the runner version when created and pushed to the ACR in the following step:

```yml
#Windows
- run: |
    docker build --build-arg RUNNER_VERSION=${{ env.RUNNER_VERSION }} -t ${{ secrets.REGISTRY_LOGIN_SERVER }}/pwd9000-github-runner-win:${{ env.RUNNER_VERSION }} .
    docker push ${{ secrets.REGISTRY_LOGIN_SERVER }}/pwd9000-github-runner-win:${{ env.RUNNER_VERSION }}
```

or on the linux workflow:

```yml
#Linux
- run: |
    docker build --build-arg RUNNER_VERSION=${{ env.RUNNER_VERSION }} -t ${{ secrets.REGISTRY_LOGIN_SERVER }}/pwd9000-github-runner-lin:${{ env.RUNNER_VERSION }} .
    docker push ${{ secrets.REGISTRY_LOGIN_SERVER }}/pwd9000-github-runner-lin:${{ env.RUNNER_VERSION }}
```

You can see the latest runner agent versions here: [GitHub Runner Releases](https://github.com/actions/runner/releases)

After triggering the workflow, the build can take a few minutes to complete. After completion you will see the docker image was pushed in to the **Azure Container Registry**:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Docker-Runner-Azure-Part3/assets/acr-win01.png)

You can also see more information on how to use the image:

### Windows runner

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Docker-Runner-Azure-Part3/assets/acr-win02.png)

### Linux runner

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Docker-Runner-Azure-Part3/assets/acr-lin02.png)

### Container security - Vulnerability Scan

You may have noticed that the CI/CD workflow used to **build** and **push** the **Linux** container image to the **Azure Container Registry** also scans the image for any vulnerabilities using a open source tool by **AquaSecurity** called [Trivy](https://aquasecurity.github.io/trivy/v0.28.1/) using these steps:

```yml
- name: 'Vulnerability scan container image with Trivy'
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ secrets.REGISTRY_LOGIN_SERVER }}/pwd9000-github-runner-lin:${{ env.RUNNER_VERSION }}
    format: 'sarif'
    output: 'trivy-results.sarif'
    severity: 'CRITICAL,HIGH'

- name: Upload Trivy scan results to GitHub Security tab
  uses: github/codeql-action/upload-sarif@v2
  with:
    sarif_file: 'trivy-results.sarif'
```

Notice that the scan results are published on the GitHub repository **Security** tab:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Docker-Runner-Azure-Part3/assets/vuln.png)

You have to have [GitHub code scanning](https://docs.github.com/en/code-security/code-scanning/automatically-scanning-your-code-for-vulnerabilities-and-errors/about-code-scanning) enabled on your repository to use this functionality and is free with GitHub **public** repositories. You can however still use **Trivy** to scan containers without GitHub code scanning enabled, by using a workflow like in this example:

```yml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'docker.io/my-organization/my-app:${{ github.sha }}'
    format: 'table'
    exit-code: '1'
    ignore-unfixed: true
    vuln-type: 'os,library'
    severity: 'CRITICAL,HIGH'
```

**NOTE:** The above example will display the results on the workflow run logs in **table format**, and can also output the results to a file if needed. This method can also be used to stop the workflow and interrupt the push of the image to the ACR based on the `'exit-code'` parameter.

For more information on using **Trivy** to scan your container images for public/private and with/without Code Scanning enabled on the GitHub repository, you can see the documentation here: [Trivy Usage](https://github.com/aquasecurity/trivy-action#trivy-action)

With our images now hosted on a remote registry in **Azure** (ACR), in the next part of this series we will look at how we can pull the images from the registry and run our self hosted GitHub runners on **Azure Container Instances (ACI)**.

I hope you have enjoyed this post and have learned something new. You can find the code samples used in this blog post on my GitHub project: [docker-github-runner-windows](https://github.com/Pwd9000-ML/docker-github-runner-windows) or [docker-github-runner-linux](https://github.com/Pwd9000-ML/docker-github-runner-linux). :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [X](https://x.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
