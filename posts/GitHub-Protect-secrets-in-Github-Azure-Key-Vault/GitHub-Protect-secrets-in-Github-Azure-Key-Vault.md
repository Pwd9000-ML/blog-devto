---
title: Protect secrets in Github with Azure Key Vault
published: false
description: A tutorial on how to protect secrets used in Github using Azure key vault
tags: 'tutorial, devops, github, azure'
cover_image: assets/maincover1.png
canonical_url: null
id: 698968
---

## :bulb: How to protect secrets in Github with Azure Key Vault

### Overview

Today we are going to look at how we can secure secrets that we are using in our Github source control by utilizing Azure Key Vault.  
When you deploy resources in Azure using Github workflows you need the ability to authenticate to Azure, you may also need to sometimes use passwords, secrets, API keys or connection strings in your source code in order to pass through some configuration of the deployment which needs to be set during the deployment. So how do we protect these sensitive pieces of information that our deployment needs and ensure that they are not in our source control when we start our deployment?  

There are a few ways to handle this. One way is to use [Github Secrets](https://docs.github.com/en/actions/reference/encrypted-secrets). This is a great way that will allow you to store sensitive information in your organization, repository, or repository environments. In fact we will set up a github secret later in this tutorial to authenticate to Azure. Even though this is a great feature to be able to have secrets management in Github, you may be looking after many repositories all with different secrets, this can become an administrative overhead when secrets or keys need to be rotated on a regular basis for best security practice.  

This is where [Azure key vault](https://docs.microsoft.com/en-gb/azure/key-vault/general/overview) can be utilized as a central source for all our secret management in our GitHub workflows.  

**Note:** Azure key vaults are also particularly useful for security or ops teams who maintain secrets management, instead of giving other teams access to our deployment repositories in Github teams who look after deployments no longer have to worry about giving access to other teams in order to manage secrets as secrets management will be done from an Azure key vault which nicely separates roles of responsibility when spread across different teams.  

### What do we need?

1. **Azure key vault:**
    This will be where we manage all our secrets we are going to use in our Github source control.  
2. **Azure AD App & Service Principal:**
    This is what we will use to authenticate to Azure from our github workflows
3. **Github repository:**
    This is where we are keeping our source control and Github workflows

### Create an Azure Key Vault

For this step I will be using Azure CLI using a powershell console. First we will log into Azure by running:  

```powershell
az login
```

Next we will create a `resource group` and `key vault` by running:

```powershell
az group create --name "Github-Assets" -l "UKSouth"
az keyvault create --name "github-secrets-vault" --resource-group "Github-Assets" --location "UKSouth"
```

You can also create an Azure key vault by using the Azure portal. Check this [link](https://docs.microsoft.com/en-us/azure/key-vault/general/quick-create-portal).  

### Create an Azure AD App & Service Principal

Next we will create our `Azure AD App` by running:

```powershell
# a name for our azure ad app
$appName="GitHubSecretsUser"

# create Azure AD app
az ad app create --display-name $appName --homepage "http://localhost/$appName" --identifier-uris "http://localhost/$appName"
```

Next we will retrieve the App ID and set it to a powershell variable `$appId`

```powershell
# get the app id
$appId=$(az ad app list --display-name $appName --query [].appId -o tsv)
```

Now that we have our App Id we can create our service principal and also give our principal the correct `Role Based Access Control (RBAC)` permissions on our key vault we created earlier. We will give our principal the RBAC/IAM role: `Key Vault Secrets User`

```powershell
$subscriptionId=$(az account show --query id -o tsv) # You can change this value t the subscription ID where the key vault resides
$resourceGroup="Github-Assets"
$keyVaultName="github-secrets-vault"

az ad sp create-for-rbac --name $appId `
    --role "Key Vault Secrets User" `
    --scopes /subscriptions/$subscriptionId/resourceGroups/$resourceGroup/providers/Microsoft.KeyVault/vaults/$keyVaultName `
    --sdk-auth
```

The above command will output a JSON object with the role assignment credentials that provide access to your key vault. Copy this JSON object for later. You will only need the sections with the `clientId`, `clientSecret`, `subscriptionId`, and `tenantId` values:

```JSON
{
  "clientId": "<GUID>",
  "clientSecret": "<PrincipalSecret>",
  "subscriptionId": "<GUID>",
  "tenantId": "<GUID>",
}
```

### Configure our GitHub repository

### _Author_

Marcel.L - pwd9000@hotmail.co.uk