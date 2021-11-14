---
title: Automate Azure Service Bus SAS tokens with Github
published: false
description: Github - Actions - Automate Service Bus SAS tokens
tags: 'actionshackathon21, security, azure, github'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Github-Rotate-ServiceBus-SAS/assets/main-sb.png'
canonical_url: null
id: 897066
---

## Overview

In todays tutorial I will demonstrate how to use powerShell in Github Actions to automate Azure Service Bus SAS tokens to generate short lived usable tokens with a validity period of 10 minutes and securely store the newly generated SAS tokens inside of an Azure Key Vault ready for consumption.

We will create an [Azure Service Bus](https://docs.microsoft.com/en-gb/azure/service-bus-messaging/service-bus-messaging-overview) and [Key Vault](https://docs.microsoft.com/en-gb/azure/key-vault/general/overview) and a single **reusable** github workflow to handle our SAS token requests as well as a service principal / Azure identity to fully automate everything. For the purpose of this demonstration we will also have a main workflow that is triggered manually. Our main workflow, when triggered, will first call our **reusable** github workflow that will generate our temporary SAS token that will only be valid for 10 minutes and store the SAS token inside of the key vault (The token validity period can be adjusted based on your needs or requirement). Our main workflow will then retrieve the SAS token from the key vault and send the message through to our service bus queue.

This means that whenever we need to call our service bus we can now generate a temporary SAS token to call our Azure service bus using a **reusable** GitHub workflow to generate our token for us and we can access the token securely from key vault using a different process or even a different github workflow.

Lets take a look at a sample use case flow diagram of how this would look like:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Github-Rotate-ServiceBus-SAS/assets/flowdiag001.png)

**Note:** Maintaining Service Bus SAS tokens using an Azure key vault is particularly useful for teams who maintain secrets management and need to ensure that only relevant users, principals and processes can access secrets from a secure managed location and also be rotated on a regular basis. Azure key vaults are also particularly useful for security or ops teams who maintain secrets management, instead of giving other teams access to our deployment repositories in Github, teams who look after deployments no longer have to worry about giving access to other teams in order to manage secrets as secrets management will be done from an Azure key vault which nicely separates roles of responsibility when spread across different teams.

### Protecting secrets in github

[Github Secrets](https://docs.github.com/en/actions/reference/encrypted-secrets) is a great way that will allow us to store sensitive information in our organization, repository, or repository environments. In fact we will set up a github secret later in this tutorial that will allow us to authenticate to Azure.

Even though this is a great feature to be able to have secrets management in Github, you may be looking after many repositories all with different secrets, this can become an administrative overhead when secrets or keys need to be rotated on a regular basis for best security practice, that's where [Azure key vault](https://docs.microsoft.com/en-gb/azure/key-vault/general/overview) can also be utilized as a central source for all your secret management in your GitHub workflows.

### What do we need to start generating Service Bus SAS tokens?

For the purpose of this demo and so you can follow along, I will set up the Azure environment with all the relevant resources described below.

1. **Azure key vault:** This will be where we centrally store, access and manage all our Service Bus SAS tokens.
2. **Service Bus Namespace:** We will create a service Bus Namespace and Queue.
3. **Azure AD App & Service Principal:** This is what we will use to authenticate to Azure from our github workflows.
4. **Github repository:** This is where we will keep all our source code and workflows.

### Create an Azure key vault

**NOTE:** A complete script for all the steps/Pre-Reqs described in building the environment can be found on my [GitHub code page](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/Github-Rotate-ServiceBus-SAS/code/Pre-Reqs.ps1)

For this step I will be using Azure CLI using a powershell console. First we will log into Azure by running:

```powershell
az login
```

Next we will set some variables:

```powershell
#Set variables
$randomInt = Get-Random -Maximum 9999
$subscriptionId = $(az account show --query "id" --output tsv)
$resourceGroupName = "Actions-Service-Bus-Demo"
$location = "UKSouth"
$keyVaultName = "secrets-vault$randomInt"
$nameSpaceName = "githubactions"
$queueName = "queue01"
$policyName = "myauthrule"
$currentUser = $(az ad signed-in-user show --query "objectId" --output tsv)
```

Next we will create a `resource group` and `key vault` by running:

```powershell
#Create ResourceGroup and Key Vault
az group create --name $resourceGroupName -l $location
az keyvault create --name $keyVaultName --resource-group $resourceGroupName --location $location --enable-rbac-authorization

#Grant Key Vault Creator/Current User [Key Vault Secrets Officer]
az role assignment create --assignee-object-id "$currentUser" `
    --role "Key Vault Secrets Officer" `
    --scope "/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.KeyVault/vaults/$keyVaultName" `
    --assignee-principal-type "User"
```

As you see above we use the option `--enable-rbac-authorization`. The reason for this is because our `current logged in user` as well as our `service principal` used by our github workflow we will create later, will access this key vault using the RBAC permission model. We also grant the key vault creator, in our case the `current logged in user` [Key Vault Secrets Officer](https://docs.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#key-vault-secrets-officer) access to the key vault as we will store our service bus policy primary key in the key vault.

### Create an Azure Service Bus

Next we will create a `Service Bus Namespace` and `Queue` by running:

```powershell
#Create Service Bus and Queue (and policy with Send and Listen rights)
az servicebus namespace create --resource-group $resourceGroupName --name $nameSpaceName --location $location --sku "Basic"
az servicebus queue create --resource-group $resourceGroupName --namespace-name $nameSpaceName --name $queueName
az servicebus namespace authorization-rule create --resource-group $resourceGroupName --namespace-name $nameSpaceName --name $policyName --rights "Send" "Listen"

#Retrieve and save primary key of new policy to key vault (will be used later as a GH Secret in GH workflow)
$policyPrimaryKey = az servicebus namespace authorization-rule keys list --resource-group $resourceGroupName --namespace-name $nameSpaceName --name $policyName --query "primaryKey" --output tsv
az keyvault secret set --vault-name $keyVaultName --name "$($policyName)PrimaryKey" --value $policyPrimaryKey
```

You will notice that our Service Bus has a Policy with only `Send` and `Listen` configured and our policies `Primary Key` will be saved in our key vault.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Github-Rotate-ServiceBus-SAS/assets/sb1.png) ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Github-Rotate-ServiceBus-SAS/assets/sb2.png)

### Create an Azure AD App & Service Principal

Next we will create our `Azure AD App` by running the following in a powershell console window:

```powershell
# a name for our azure ad app
$appName="gitHubActionsVaultUser"

# create Azure AD app
az ad app create --display-name $appName --homepage "http://localhost/$appName"
```

Next we will retrieve the App ID and set it to a powershell variable `$appId`

```powershell
# get the app id
$appId=$(az ad app list --display-name $appName --query [].appId -o tsv)
```

Now that we have our `appId` we can create our service principal that we will use to authenticate our GitHub workflow with Azure and also give our principal the correct `Role Based Access Control (RBAC)` permissions on our key vault we created earlier. We will give our principal the RBAC/IAM role: [Key Vault Secrets Officer](https://docs.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#key-vault-secrets-officer) because we want our workflow to be able to retrieve `secret keys` and also set secrets for our `Service Bus SAS tokens`.

```PowerShell
#Create Service Principal to be used as GH Secret credential to authenticate to Azure (Make note of JSON output on this step)
az ad sp create-for-rbac --name $appId `
    --role "Key Vault Secrets Officer" `
    --scopes /subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.KeyVault/vaults/$keyVaultName `
    --sdk-auth
```

The above command will output a JSON object with the role assignment credentials that provide access to your key vault. Copy this JSON object for later. You will only need the sections with the `clientId`, `clientSecret`, `subscriptionId`, and `tenantId` values:

```JSON
{
  "clientId": "<GUID>",
  "clientSecret": "<PrincipalSecret>",
  "subscriptionId": "<GUID>",
  "tenantId": "<GUID>"
}
```

### Configure our GitHub repository

Next we will configure our Github repository and Github workflow. My Github repository is called `Azure-Service-Bus-SAS-Management`. You can also take a look or even use my github repository as a template [HERE](https://github.com/Pwd9000-ML/Azure-Service-Bus-SAS-Management).

Remember at the beginning of this post I mentioned that we will create a github secret, we will now create this secret on our repository which will be used to authenticate our Github workflow to Azure when it's triggered.

1. In [GitHub](https://github.com), browse your repository.

2. Select Settings > Secrets > New repository secret.

3. Paste the JSON object output from the Azure CLI command we ran earlier into the secret's value field. Give the secret the name `AZURE_CREDENTIALS`.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Github-Rotate-ServiceBus-SAS/assets/githubAzureCredentials1.png)

Because we will have two workflows in this demo we will create our **reusable** workflow first called `new-service-bus-sas-token.yaml` then we will create our main workflow that will send a message to our Service bus called `main.yaml`.

### Configure our GitHub workflows

Now create a folder in the repository called `.github` and underneath another folder called `workflows`. In the workflows folder we will create a YAML file called `new-service-bus-sas-token.yaml`. The YAML file can also be accessed [HERE](https://github.com/Pwd9000-ML/Azure-Service-Bus-SAS-Management/blob/master/.github/workflows/new-service-bus-sas-token.yaml).

```yaml

```

**Note:** The only fields that needs to be updated for the workflow to be use din your environment are shown below:

```yaml
## code/new-service-bus-sas-token.yaml#L7-L11

env:
  KEY_VAULT_NAME: secrets-vault7839
  SB_NAMESPACE: githubactions
  SB_POLICY_NAME: myauthrule
  SB_POLICY_KEY_NAME: myauthrulePrimaryKey
```

The above YAML workflow has a special trigger as shown below, which will only run when called by another GitHub workflow.

```yaml
on: [workflow_call]
```

Now onto our main workflow file. In the same workflows folder we will create a second YAML file called `main.yaml`. The YAML file can also be accessed [HERE](https://github.com/Pwd9000-ML/Azure-Service-Bus-SAS-Management/blob/master/.github/workflows/main.yaml).

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my [Github](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/Github-Rotate-ServiceBus-SAS/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}
