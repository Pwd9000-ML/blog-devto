---
title: GitHub authentication methods for Azure
published: false
description: GitHub authentication methods for Azure
tags: 'github, azure, authentication, devsecops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Auth-Methods-Azure/assets/main0.png'
canonical_url: null
id: 1177675
date: '2022-08-27T15:37:53Z'
---

## Overview

When you're working with **GitHub Actions** and start to write and develop automation **workflows** you will sometimes need to connect your **workflow** to different platforms, such as a **cloud provider** for example, to allow your **workflows** access and permissions to perform actions on the cloud provider. Thus you will need to **connect** and **authenticate** your **workflows** with the cloud provider.

Today we will look at two ways you can do this with **Azure**, a popular Microsoft cloud provider.

In both methods we will create what is known as an [app registration/service principal](https://docs.microsoft.com/en-us/azure/active-directory/develop/app-objects-and-service-principals), assigning permissions to the principal and link the principal with GitHub to allow your **workflows** to authenticate and perform relevant tasks in **Azure**.

**NOTE:** If you are familiar with using **Azure DevOps** and **Azure pipelines**, this is synonymous to creating a [service connection](https://docs.microsoft.com/en-us/azure/devops/pipelines/library/service-endpoints?view=azure-devops&tabs=yaml) for your pipelines.

## Method 1 - Client and Secret (Legacy)

The first method we will look at is an older legacy method that uses a `'Client'` and `'Secret'` approach to authenticate.

### 1. Create Service Principal credentials

For this method I will use the following [PowerShell script](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2022/GitHub-Auth-Methods-Azure/code/Create-SP.ps1) to create an **Azure AD App & Service Principal**.

```powershell
# Log into Azure
Az login

# Show current subscription (use 'Az account set' to change subscription)
Az account show

# variables
$subscriptionId=$(az account show --query id -o tsv)
$appName="GitHub-projectName-Actions"
$RBACRole="Contributor"

# Create AAD App and Service Principal and assign RBAC Role
az ad sp create-for-rbac --name $appName `
    --role $RBACRole `
    --scopes /subscriptions/$subscriptionId `
    --sdk-auth
```

In the script above, the `'az ad sp create-for-rbac'` command will create an AAD app & service principal and will output a JSON object containing the credentials of the service principal:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Auth-Methods-Azure/assets/rbac.png)

**NOTE:** The service principal will provide your GitHub workflow, **Contributor** access to the **Subscription**. Feel free to change the RBAC `'role'` and `'scopes'` as necessary.

Copy this JSON object as we will add this as a **GitHub Secret**. You will only need the sections with the `"clientId"`, `"clientSecret"`, `"subscriptionId"`, and `"tenantId"` values:

```JSON
{
  "clientId": "<GUID>",
  "clientSecret": "<PrincipalSecret>",
  "subscriptionId": "<GUID>",
  "tenantId": "<GUID>"
}
```

The main drawback of using this legacy method to create a service principal for **GitHub** is that the principals **client secret** is only valid for **1 year**, and has to be managed and rotated frequently for security reasons, and will also have to be updated in your **GitHub** account manually, which can become a cumbersome administration task.

You can rotate the secret of the service principal by navigating to **'App registrations'** in **'Azure Active Directory (AAD)'**.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Auth-Methods-Azure/assets/aad01.png)

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Auth-Methods-Azure/assets/aad02.png)

We will discuss later why using Open ID Connect (OIDC) is a much better option.

### 2. Create a GitHub Actions Secret

Next create a **GitHub Secret** on your **GitHub repository** using the JSON object Service Principal credentials:

In the GitHub UI, navigate to your repository and select **Settings** > **Secrets** > **Actions**:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Auth-Methods-Azure/assets/ghsec01.png)

Select **New repository secret** to add the following secrets:

| **Secret** | **Value** |
| --- | --- |
| `AZURE_CREDENTIALS` | The entire JSON output from the service principal creation step |

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Auth-Methods-Azure/assets/ghsec02.png)

### 3. Authenticate GitHub Actions workflows with Azure

Now that we have a **GitHub Secret** called `'AZURE_CREDENTIALS'` that contains our **Azure Service Principal credentials**, we can consume this secret inside of our **workflows** to authenticate and log into **Azure**.  

Here is an example workflow that will authenticate to Azure and show all resource groups on the subscription as part of th workflow run: [authenticate-azure.yml](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2022/GitHub-Auth-Methods-Azure/code/authenticate-azure.yml).  

```yml
name: Authenticate Azure
on:
  workflow_dispatch:

jobs:
  publish:
    runs-on: windows-latest
    steps:
      - name: Check out repository
        uses: actions/checkout@v2

      - name: 'Log into Azure using github secret AZURE_CREDENTIALS'
        uses: Azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
          enable-AzPSSession: true

      - name: 'Run az commands'
        run: |
          az account show
          az group list
```

Notice the **GitHub Actions** step we are using to log into Azure:  

```yml
- name: 'Log into Azure using github secret AZURE_CREDENTIALS'
uses: Azure/login@v1
with:
    creds: ${{ secrets.AZURE_CREDENTIALS }}
    enable-AzPSSession: true
```

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Auth-Methods-Azure/assets/test01.png)

## Method 2 - Open ID Connect(OIDC) (Modern)

## Conclusion

xxxxxxxx

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my published [GitHub](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2022/GitHub-Auth-Methods-Azure/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
