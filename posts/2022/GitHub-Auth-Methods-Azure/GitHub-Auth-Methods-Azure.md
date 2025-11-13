---
title: GitHub Actions authentication methods for Azure
published: true
description: GitHub Actions authentication methods for Azure
tags: 'github, azure, devops, githubactions'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Auth-Methods-Azure/assets/main0.png'
canonical_url: null
id: 1177675
date: '2022-08-27T15:37:53Z'
---

## Overview

When you work with **GitHub Actions** and start to write and develop automation **workflows** you will sometimes need to connect your **workflows** to different platforms, such as a **cloud provider** for example, to allow your **workflows** access and permissions to perform actions on the cloud provider. Thus you will need to **connect** and **authenticate** your GitHub Actions **workflows** with the cloud provider somehow.

Today we will look at two ways you can do this with **Azure**.

In both methods we will create what is known as an [app registration/service principal](https://docs.microsoft.com/en-us/azure/active-directory/develop/app-objects-and-service-principals?wt.mc_id=DT-MVP-5004771), assigning permissions to the principal and link the principal with GitHub to allow your action **workflows** to authenticate and perform relevant tasks in **Azure**.

**NOTE:** If you are familiar with using **Azure DevOps** and **Azure pipelines**, this is synonymous to creating a [service connection](https://docs.microsoft.com/en-us/azure/devops/pipelines/library/service-endpoints?wt.mc_id=DT-MVP-5004771) for your pipelines. **GitHub Actions workflows** are synonymous to **Azure multi-stage YAML Pipelines**.

## Method 1 - Client and Secret (Legacy)

The first method we will look at is an older legacy method that uses a `'Client'` and `'Secret'` approach to authenticate.

### 1. Create Service Principal credentials

For this method I will use the following PowerShell script; ['Create-SP.ps1'](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2022/GitHub-Auth-Methods-Azure/code?wt.mc_id=DT-MVP-5004771/Create-SP.ps1) to create an **Azure AD App & Service Principal**.

```powershell
### Create-SP.ps1 ###
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

**NOTE:** The service principal will provide your GitHub Actions workflow, **Contributor** access to the **Subscription**. Feel free to change the RBAC `'role'` and `'scopes'` as necessary in the provided script.

Copy the JSON object as we will add this as a **GitHub Secret**. You will only need the sections with the `"clientId"`, `"clientSecret"`, `"subscriptionId"`, and `"tenantId"` values:

```JSON
{
  "clientId": "<GUID>",
  "clientSecret": "<PrincipalSecret>",
  "subscriptionId": "<GUID>",
  "tenantId": "<GUID>"
}
```

The main drawback of using this method to create a service principal for **GitHub** is that the principals **client secret** is only valid for **1 year**, and has to be managed and rotated frequently for security reasons, and will also have to be updated in your **GitHub** account manually, which can become a cumbersome administration task.

You can rotate the secret of the service principal by navigating to **'App registrations'** in **'Azure Active Directory (AAD)'** and finding the App we just created.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Auth-Methods-Azure/assets/aad01.png)

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Auth-Methods-Azure/assets/aad02.png)

We will discuss later why using a passwordless approach with Open ID Connect (OIDC) is a much better option.

### 2. Create a GitHub Actions Secret

Next create a **GitHub Secret** on your **GitHub repository** using the copied JSON object Service Principal credentials from the previous step:

In the GitHub UI, navigate to your repository and select **'Settings'** -> **'Secrets'** -> **'Actions'**:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Auth-Methods-Azure/assets/ghsec01.png)

Select **New repository secret** to add the following secrets:

| **Secret** | **Value** |
| --- | --- |
| `AZURE_CREDENTIALS` | The entire JSON output from the service principal creation step |

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Auth-Methods-Azure/assets/ghsec02.png)

### 3. Authenticate GitHub Actions workflows with Azure

Now that we have a **GitHub Secret** called `'AZURE_CREDENTIALS'` that contains our **Azure Service Principal credentials**, we can consume this secret inside of our **workflows** to authenticate and log into **Azure**.

Here is an example workflow that will authenticate to Azure and show all resource groups on the subscription as part of the workflow run: [authenticate-azure.yml](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2022/GitHub-Auth-Methods-Azure/code?wt.mc_id=DT-MVP-5004771/authenticate-azure.yml).

```yml
name: Authenticate Azure
on:
  workflow_dispatch:
  pull_request:
    branches:
      - master

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository
        uses: actions/checkout@v3.6.0

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

**NOTE:** The `'Run az commands'` step will display the Azure account as well as a list of all resource groups.

## Method 2 - Open ID Connect(OIDC) (Modern)

In this section we will look at a newer, more modern way to link **GitHub Actions** to **Azure**, whereby no client secrets are needed.

We will be using **federated credentials** with **Open ID connect (OIDC)**. One of the main benefits of using **OIDC** is that there are no passwords or client secrets to manage or maintain and uses an `'identity'` driven approach to authenticate.

### 1. Create Service Principal

As before we will require an AAD App and Service Principal.

You can use the following PowerShell script; ['Create-SP-OIDC.ps1'](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2022/GitHub-Auth-Methods-Azure/code?wt.mc_id=DT-MVP-5004771/Create-SP-OIDC.ps1) to create an **Azure AD App & Service Principal** with **federated GitHub Action credentials**.

```powershell
### Create-SP-OIDC.ps1 ###
# Log into Azure
Az login

# Show current subscription (use 'Az account set' to change subscription)
Az account show

# variables
$subscriptionId = $(az account show --query id -o tsv)
$appName = "GitHub-projectName-Actions-OIDC"
$RBACRole = "Contributor"

$githubOrgName = "Pwd9000-ML"
$githubRepoName = "RandomStuff"
$githubBranch = "master"

# Create AAD App and Principal
$appId = $(az ad app create --display-name $appName --query appId -o tsv)
az ad sp create --id $appId

# Create federated GitHub credentials (Entity type 'Branch')
$githubBranchConfig = [PSCustomObject]@{
    name        = "GH-[$githubOrgName-$githubRepoName]-Branch-[$githubBranch]"
    issuer      = "https://token.actions.githubusercontent.com"
    subject     = "repo:" + "$githubOrgName/$githubRepoName" + ":ref:refs/heads/$githubBranch"
    description = "Federated credential linked to GitHub [$githubBranch] branch @: [$githubOrgName/$githubRepoName]"
    audiences   = @("api://AzureADTokenExchange")
}
$githubBranchConfigJson = $githubBranchConfig | ConvertTo-Json
$githubBranchConfigJson | az ad app federated-credential create --id $appId --parameters "@-"

# Create federated GitHub credentials (Entity type 'Pull Request')
$githubPRConfig = [PSCustomObject]@{
    name        = "GH-[$githubOrgName-$githubRepoName]-PR"
    issuer      = "https://token.actions.githubusercontent.com"
    subject     = "repo:" + "$githubOrgName/$githubRepoName" + ":pull_request"
    description = "Federated credential linked to GitHub Pull Requests @: [$githubOrgName/$githubRepoName]"
    audiences   = @("api://AzureADTokenExchange")
}
$githubPRConfigJson = $githubPRConfig | ConvertTo-Json
$githubPRConfigJson | az ad app federated-credential create --id $appId --parameters "@-"

### Additional federated GitHub credential entity types are 'Tag' and 'Environment' (see: https://docs.microsoft.com/en-us/azure/active-directory/develop/workload-identity-federation-create-trust?pivots=identity-wif-apps-methods-azcli#github-actions-example?wt.mc_id=DT-MVP-5004771) ###

# Assign RBAC permissions to Service Principal (Change as necessary)
$appId | foreach-object {

    # Permission 1 (Example)
    az role assignment create `
        --role $RBACRole `
        --assignee $_ `
        --subscription $subscriptionId

    # Permission 2 (Example)
    #az role assignment create `
    #    --role "Reader and Data Access" `
    #    --assignee "$_" `
    #    --scope "/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.Storage/storageAccounts/$storageName"
}
```

Notice that the script creates **federated GitHub Action credentials** on the **AAD App**, you can view them or add more by navigating to **'App registrations'** in **'Azure Active Directory (AAD)'** and finding the App we just created.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Auth-Methods-Azure/assets/aad03.png)

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Auth-Methods-Azure/assets/aad04.png)

Notice that there are no client secrets on the AAD App.

Instead, the script created two federated GitHub Action credentials, one using entity type of `'Branch'` linked to my repositories `'master;` branch, and one entity type of `'pull request'` linked to my repository for any actions triggered by a **'Pull Request (PR)'**

You can add more by clicking on `'+ Add credential'`.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Auth-Methods-Azure/assets/aad05.png)

Select `'GitHub Actions deploying Azure resources'` for the federated credential scenario.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Auth-Methods-Azure/assets/aad06.png)

There are four entity types for **Github action federated credentials**. They are `'Environment'`, `'Branch'`, `'Pull Request'` and `'Tag'`.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Auth-Methods-Azure/assets/aad07.png)

Depending on what entity type you select, will automatically construct the `'Subject identifier'`, this value is used to establish a connection between your **GitHub Actions workflow** and **Azure Active Directory**. The value is generated from the GitHub details entered.

When the GitHub Actions workflow requests the Microsoft identity platform to exchange a GitHub token for an access token, the values in the federated identity credential are checked against the provided GitHub token. Before Azure will grant an access token, the request must match the conditions defined in the `'Subject identifier'`.

- For Jobs tied to an **environment** use: `repo:<Organization/Repository>:environment:<Name>`.
- For Jobs not tied to an environment, include the **ref path** of the **branch/tag** based on the **ref path** used for triggering the workflow: `repo:<Organization/Repository>:ref:<ref path>`. For example, `repo:myOrg/myRepo:ref:refs/heads/myBranch` or `repo:myOrg/myRepo:ref:refs/tags/myTag`.
- For workflows triggered by a **pull request** event use: `repo:<Organization/Repository>:pull-request`.

You can see more examples on the official [Microsoft documentation](https://docs.microsoft.com/en-us/azure/active-directory/develop/workload-identity-federation-create-trust?pivots=identity-wif-apps-methods-azcli#github-actions-example?wt.mc_id=DT-MVP-5004771).

Grab the `'CLIENT_ID'` of the AAD application as we will need it in the next step.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Auth-Methods-Azure/assets/aad08.png)

### 2. Create GitHub Actions Secrets

Next create the following **GitHub Secrets** on your **GitHub repository**.

In the GitHub UI, navigate to your repository and select **'Settings'** -> **'Secrets'** -> **'Actions'**:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Auth-Methods-Azure/assets/ghsec01.png)

Select **New repository secret** to add the following secrets:

| **Secret** | **Value** |
| --- | --- |
| `AZURE_CLIENT_ID` | The AAD Application (client) ID created in the previous step |
| `AZURE_TENANT_ID` | The Azure Directory (tenant) ID |
| `AZURE_SUBSCRIPTION_ID` | The Azure subscription ID |

**NOTE:** There is no password/secret required.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Auth-Methods-Azure/assets/ghsec03.png)

### 3. Authenticate GitHub Actions workflows with Azure (OIDC)

Now that you have **federated credentials** as well as **GitHub Secrets** configured, you can now configure your workflows to use **OIDC tokens** to authenticate and log into **Azure**.

To update your workflows for OIDC, you will need to make two changes to your YAML:

- Add a `permissions` setting with [id-token: write](https://docs.github.com/en/actions/security-guides/automatic-token-authentication#permissions-for-the-github_token) for the token.
- Use the [azure/login](https://github.com/Azure/login) action to exchange the OIDC token (JWT) for a cloud access token.

Here is an example workflow that will authenticate to Azure and show all resource groups on the subscription as part of the workflow run: [authenticate-azure-oidc.yml](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2022/GitHub-Auth-Methods-Azure/code?wt.mc_id=DT-MVP-5004771/authenticate-azure-oidc.yml).

```yml
name: Run Azure Login with OIDC
on:
  workflow_dispatch:
  pull_request:
    branches:
      - master

permissions:
  id-token: write
  contents: read

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - name: 'Az CLI login using OIDC'
        uses: azure/login@v1
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - name: 'Run az commands'
        run: |
          az account show
          az group list
```

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Auth-Methods-Azure/assets/test02.png)

**NOTE:** The `'Run az commands'` step will display the Azure account as well as a list of all resource groups.

Notice the **GitHub Actions** step we are using to log into Azure:

```yml
- name: 'Az CLI login'
uses: azure/login@v1
with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

Also notice that the `'permissions'` on workflow uses `'id-token: write'`. You won't be able to request the OIDC JWT ID token if the permissions setting for id-token is set to `'read'` or `'none'`.

```yml
permissions:
  id-token: write
  contents: read
```

If you only need to fetch an OIDC token for a single job, then this permission can also be set within a job. For example:

```yml
jobs:
  job1:
    runs-on: ubuntu-latest

    permissions:
      id-token: write

    steps:
      - uses: actions/stale@v5
```

## Conclusion

As you can see, it is pretty easy to set up authentication between your **GitHub Actions** and **Azure**. I would highly recommend adopting the newer, **Open ID Connect (OIDC)** method if you aren't using that already as it is a lot more convenient not having to manage and maintain passwords/secrets of your Azure service principals and GitHub secrets manually.

OIDC is a better security option as it is an identity driven, passwordless authentication method that doesn't require frequent rotation or expiration of Azure service principal passwords/secrets.

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my published [GitHub](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2022/GitHub-Auth-Methods-Azure/code?wt.mc_id=DT-MVP-5004771) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [X](https://x.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
