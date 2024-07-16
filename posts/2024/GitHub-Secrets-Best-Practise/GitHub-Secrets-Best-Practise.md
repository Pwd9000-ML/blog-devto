---
title: Securing Your GitHub Workflows - Best Practices for Using GitHub Secrets
published: false
description: Best Practices for Managing Sensitive Information in a GitHub Workflow
tags: 'github, git, devops, devsecops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/GitHub-Secrets-Best-Practise/assets/main-gh-tips.png'
canonical_url: null
id: 1924247
series: GitHub Pro Tips
---

## Overview - Managing Sensitive Information in a GitHub Workflow

In today's fast-paced development environment, automation is key. However, this often requires the handling of **sensitive information** such as **API keys**, **credentials**, and other **secrets**. Managing these securely is crucial to avoid unauthorised access and data breaches.

In this blog post, we'll explore best practices for managing sensitive information in your **[GitHub workflows](https://docs.github.com/en/actions/using-workflows/about-workflows?wt.mc_id=DT-MVP-5004771)** by using **[GitHub Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#about-secrets?wt.mc_id=DT-MVP-5004771)**, and also how we can go further by storing **Secrets** securely in **[Azure Key Vault](https://learn.microsoft.com/en-us/azure/key-vault/general/basic-concepts?wt.mc_id=DT-MVP-5004771)**, integrating your GitHub Workflows with **Azure Key Vault** for enhanced security.

### Why Secure Handling of Sensitive Information is Crucial

What is the purpose of **GitHub Secrets** you may wonder, and why do you even want to use them?

The reason is simple, exposing sensitive information in **git** code repositories can lead to severe consequences such as **unauthorised access**, **data breaches**, and possible leak of sensitive or **private information** which can lead to **reputational damage**. Properly managing this information ensures the security and integrity of your applications and data.

### Common Pitfalls to Avoid

When managing sensitive information in your workflows, there are some common pitfalls to avoid:

1. **Hardcoding Secrets:** Never hardcode secrets in your codebase. Always use **[GitHub Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#about-secrets?wt.mc_id=DT-MVP-5004771)** or secret management tools such as **[Azure Key Vault](https://learn.microsoft.com/en-us/azure/key-vault/general/basic-concepts?wt.mc_id=DT-MVP-5004771)**.
2. **Improper Access Control:** Ensure that only necessary workflows and users have access to secrets.
3. **Exposing Secrets in Logs:** Be cautious not to print secrets in logs, as logs can be accessed by unauthorised users.

## Using GitHub Secrets

**[GitHub Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#about-secrets?wt.mc_id=DT-MVP-5004771)** allow you to securely store sensitive information and access it in your workflows. These secrets are encrypted and only exposed to selected workflows. Let's take a look at how you can get started with **GitHub Secrets** and how to set them up in your workflows.

1. **Navigate to Your Repository:**  
   1.1. Go to your GitHub repository.  
   1.2. Click on `Settings`.  
   ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/GitHub-Secrets-Best-Practise/assets/1-settings.png)

2. **Access Secrets:**  
   2.1. In the left sidebar, click on `Secrets and variables` under the `Security` section.  
   2.2. Notice that you have options for `Actions`, `Codespaces` and `Dependabot`.  
   ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/GitHub-Secrets-Best-Practise/assets/1-secrets.png)  
   2.3. Because we are working with GitHub Workflows, we will focus on `Actions`. But also know that you can use these secrets in other areas of your repository as well, such as inside of your **Codespaces** or for **Dependabot** specific workflows.  
   For more information on using **Secrets** in **Codespaces** check out: **[Codespaces Secrets](https://docs.github.com/en/codespaces/managing-your-codespaces/managing-your-account-specific-secrets-for-github-codespaces?wt.mc_id=DT-MVP-5004771)**, and for using **Secrets** in **Dependabot** check out: **[Dependabot Secrets](https://docs.github.com/en/code-security/dependabot/working-with-dependabot/automating-dependabot-with-github-actions#accessing-secrets?wt.mc_id=DT-MVP-5004771)**.

3. **Add a New Secret:**  
   3.1. Click on `New repository secret`.  
   ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/GitHub-Secrets-Best-Practise/assets/1-add-secret.png)  
   **Note:** that you can set up **[Environment Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-an-environment?wt.mc_id=DT-MVP-5004771)**, **[Organization Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-an-organization?wt.mc_id=DT-MVP-5004771)** and **[Repository Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository?wt.mc_id=DT-MVP-5004771)** as well as **[variables](https://docs.github.com/en/actions/learn-github-actions/variables?wt.mc_id=DT-MVP-5004771)** for use in your workflows.  
   3.2. Provide a `Name` and `Value` for your secret.  
   3.3. Click `Add secret`.  
   ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/GitHub-Secrets-Best-Practise/assets/2-add-secret.png) Once the `Secret` is added, it is encrypted and cannot be viewed again. You can only update or delete the secret.  
   ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/GitHub-Secrets-Best-Practise/assets/3-add-secret.png)

### Example: Using GitHub Secrets in a Workflow

Secrets can be accessed in your workflows using the `${{ secrets.SECRET_NAME }}` syntax. Here's an example of how to use GitHub Secrets in a GitHub Actions workflow:

```yaml
name: CI/CD Pipeline

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Use Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '14'

      - name: Install Dependencies
        run: npm install

      - name: Run Tests
        run: npm test

      - name: Deploy
        env:
          API_KEY: ${{ secrets.API_KEY }}
        run: |
          echo "Deploying with API Key: $API_KEY"  
          # Insert your deployment script here
```

In the above example, `API_KEY` is a secret stored in GitHub Secrets. It is accessed using `${{ secrets.API_KEY }}` within the workflow.

## Integrating Azure Key Vault with GitHub Workflows

What if you want to take your security to the next level and store your secrets in a more secure location? **[Azure Key Vault](https://learn.microsoft.com/en-us/azure/key-vault/general/basic-concepts?wt.mc_id=DT-MVP-5004771)** is a cloud service for securely storing and accessing secrets. Integrating it with GitHub Actions provides an extra layer of security and flexibility for managing your secrets.

One of the biggest benefits of using **Azure Key Vault** is that it allows you to store your secrets in a centralised location, separate from your codebase, apart from **[Organization Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-an-organization?wt.mc_id=DT-MVP-5004771)**, it addresses the limitation with **[Repository Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository?wt.mc_id=DT-MVP-5004771)** where secrets have to be set in each unique repository which can make secrets management or rotation cumbersome.

Let's take a look at how you can integrate **Azure Key Vault** with your GitHub Workflows:

### Prerequisites

- Azure Subscription.
- Azure Key Vault.
- GitHub repository.

### Step-by-Step Integration

**1. Set Up Azure Key Vault:**

We will use Azure CLI to create a Key Vault and some secrets. For example below we will create a Key Vault and store a Storage Account Key in it which we will later access in our GitHub Actions workflow:

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

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/GitHub-Secrets-Best-Practise/assets/1-key-vault.png)

**2. Configure Azure Service Principal:**

Next we will create a federated service principal (passwordless) in **[Azure Entra ID](https://learn.microsoft.com/en-us/entra/fundamentals/whatis?wt.mc_id=DT-MVP-5004771)** and grant it access to the Key Vault. We will integrate this service principal (identity) to access the Key Vault from our GitHub Actions workflow:

```bash
  az ad sp create-for-rbac --name "myServicePrincipal" --role "Contributor" --scopes /subscriptions/{subscription-id}/resourceGroups/myResourceGroup
```

Note down the `appId`, `password`, and `tenant`. We will need this information to configure the GitHub Secrets later so that the service principal can access the Key Vault from our GitHub Actions workflow.

You can also check this earlier post I wrote on how to create a federated service principal for passwordless integration between Azure and GitHub Actions Workflows using Open ID Connect (OIDC): **[GitHub Actions authentication methods for Azure](https://dev.to/pwd9000/bk-1iij)**

**3. Store Service Principal Credentials in GitHub Secrets:**

Add the following secrets to your GitHub repository. This is so that the workflow we will set up later can access Azure and the Key Vault:

`AZURE_CLIENT_ID`: `appId` from the service principal  
`AZURE_CLIENT_SECRET`: `password` from the service principal  
`AZURE_TENANT_ID`: `tenant` from the service principal  
`AZURE_KEY_VAULT`: Name of your Azure Key Vault

**4. Access Azure Key Vault in GitHub Actions:**

Use the Azure Key Vault action to retrieve secrets in your workflow:

```yaml
name: CI/CD Pipeline

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Use Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '14'

      - name: Install Dependencies
        run: npm install

      - name: Run Tests
        run: npm test

      - name: Retrieve Secrets from Azure Key Vault
        uses: azure/secrets-store@v1
        with:
          method: 'keyvault'
          azure-client-id: ${{ secrets.AZURE_CLIENT_ID }}
          azure-client-secret: ${{ secrets.AZURE_CLIENT_SECRET }}
          azure-tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          keyvault-name: ${{ secrets.AZURE_KEY_VAULT }}
          secrets: |
            MySecret

      - name: Deploy
        env:
          API_KEY: ${{ steps.retrieve-secrets.outputs.MySecret }}
        run: |
          echo "Deploying with API Key: $API_KEY"  
          # Insert your deployment script here
```

In the above example, the `azure/secrets-store` action is used to retrieve the `MySecret` secret from Azure Key Vault. The secret is then used in the deployment step.

## Conclusion

Managing sensitive information securely is vital for any DevOps workflow. By using **GitHub Secrets** and integrating Azure Key Vault, you can ensure that your secrets are stored and accessed securely. Always follow best practices and avoid common pitfalls to maintain the security and integrity of your applications.

I hope you have enjoyed this post and have learned something new. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
