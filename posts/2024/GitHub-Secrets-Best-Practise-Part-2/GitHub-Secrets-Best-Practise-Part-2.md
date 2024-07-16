---
title: Integrating Azure Key Vault with GitHub Secrets and Workflows - Part 2
published: false
description: Best Practices for Managing Sensitive Information in a GitHub Workflow
tags: 'github, git, devops, devsecops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/GitHub-Secrets-Best-Practise-Part-2/assets/main-gh-tips.png'
canonical_url: null
id: 1925352
series: GitHub Pro Tips
---

## Overview - Managing Sensitive Information in a GitHub Workflow

Welcome to **`Part 2`** of a 2-Part series where we'll explore more ways for managing sensitive information in your **[GitHub workflows](https://docs.github.com/en/actions/using-workflows/about-workflows?wt.mc_id=DT-MVP-5004771)** by using **[Azure Key Vault](https://learn.microsoft.com/en-us/azure/key-vault/general/basic-concepts?wt.mc_id=DT-MVP-5004771)** and how to integrate your GitHub Workflows with Azure Key Vault for using **Secrets** to enhanced security and centralised management of your **Secrets**.

I recommend you read **`Part 1`** of this series where we explored the best practices for managing sensitive information in your **[GitHub workflows](https://docs.github.com/en/actions/using-workflows/about-workflows?wt.mc_id=DT-MVP-5004771)** by using **[GitHub Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#about-secrets?wt.mc_id=DT-MVP-5004771)** using the GitHub Website UI and giving a general overview and feel for **GitHub Secrets** and why you would want to use them.

Let's jump straight into it and explore how we can integrate **Azure Key Vault** with our **GitHub Workflows**.

## Integrating Azure Key Vault with GitHub Workflows

**[Azure Key Vault](https://learn.microsoft.com/en-us/azure/key-vault/general/basic-concepts?wt.mc_id=DT-MVP-5004771)** is a cloud service for securely storing and accessing secrets. Integrating it with GitHub Actions provides an extra layer of security and a more flexibility for managing your secrets.

One of the biggest benefits of using **Azure Key Vault** is that it allows you to store your secrets in a centralised location, separate from your codebase, apart from **[Organization Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-an-organization?wt.mc_id=DT-MVP-5004771)**, it addresses the limitation with **[Repository Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository?wt.mc_id=DT-MVP-5004771)** where secrets have to be set in each unique repository which can make secrets management or rotation cumbersome.

Let's take a look at how you can integrate **Azure Key Vault** with your **GitHub Workflows**:

### Prerequisites

- GitHub repository.
- Azure Subscription.
- Azure Key Vault.
- Azure Service Principal with access to the Key Vault.

### Step-by-Step Integration Example

At the time of writing for the purposes of the following example on a **Windows** operating system, we will use **[GitHub CLI](https://github.com/cli/cli/releases?wt.mc_id=DT-MVP-5004771) v2.52.0** to create a **GitHub repository** and **[Azure CLI](https://github.com/Azure/azure-cli/releases?wt.mc_id=DT-MVP-5004771) v2.62.0** to create an **Azure Key Vault** and store an **Azure Storage Account Key** in it. We will then integrate the **Key Vault** with our **GitHub Actions workflow** with a service principal (identity) to access the storage account secret key securely during the actions workflow execution.

**1. Set Up Azure Key Vault:**

For the example below we will create a Key Vault and store a Storage Account Key in it which we will later access in our GitHub Actions workflow:

```pwsh
  # Set variables
  $randomInt = Get-Random -Maximum 9999
  $subscriptionId = $(az account show --query "id" --output tsv)
  $resourceGroupName = "ghSecretsRg"
  $location = "UKSouth"
  $keyVaultName = "ghSecretsVault$randomInt"
  $storageAccountName = "ghsecsa$randomInt"
  $currentUser = $(az ad signed-in-user show --query "id" --output tsv)

  # Create Resource Group
  az group create --name "$resourceGroupName" --location "$location"

  # Create Key Vault
  az keyvault create --name "$keyVaultName" --resource-group "$resourceGroupName" --location "$location"

  # Authorize the operation to create the tracker table - Signed in User
  az role assignment create --assignee-object-id "$currentUser" `
    --role "Key Vault Secrets Officer" `
    --scope "/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.KeyVault/vaults/$keyVaultName" `
    --assignee-principal-type "User"

  # Create a storage account and store the key in Key Vault (Example)
  az storage account create --name "$storageAccountName" --resource-group "$resourceGroupName" --location "$location" --sku Standard_LRS

  # Fetch and store a Storage Account Key in Key Vault
  $storageKey = az storage account keys list --account-name "$storageAccountName" --resource-group "$resourceGroupName" --query "[0].value" --output tsv
  az keyvault secret set --vault-name "$keyVaultName" --name "StorageAccountKey" --value "$storageKey"
```

As you can see we have securely created an **Azure Key Vault** and stored our **Storage Account Key** in it.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/GitHub-Secrets-Best-Practise-Part-2/assets/1-key-vault.png)

**2. Configure Azure Service Principal:**

Next we will create a federated service principal (passwordless) in **[Azure Entra ID](https://learn.microsoft.com/en-us/entra/fundamentals/whatis?wt.mc_id=DT-MVP-5004771)** and grant it access to the Key Vault. We will integrate this service principal (identity) to access the Key Vault from our GitHub Actions workflow:

**NOTE:** You can also check this earlier blog post I wrote on other mechanisms and ways for integrating identities between Azure and GitHub: **[GitHub Actions authentication methods for Azure](https://dev.to/pwd9000/bk-1iij)**

**3. Store Service Principal Credentials in GitHub Secrets:**

**4. Access Azure Key Vault in GitHub Actions:**

## Conclusion

Managing sensitive information securely is vital for any DevOps workflow. By using **GitHub Secrets** and integrating Azure Key Vault, you can ensure that your secrets are stored and accessed securely. Always follow best practices and avoid common pitfalls to maintain the security and integrity of your applications.

I hope you have enjoyed this post and have learned something new. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
