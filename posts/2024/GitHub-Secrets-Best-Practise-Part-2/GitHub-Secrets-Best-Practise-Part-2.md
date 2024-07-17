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

Welcome to **Part 2** of this 2-Part series where we explore different ways for managing sensitive information in **[GitHub workflows](https://docs.github.com/en/actions/using-workflows/about-workflows?wt.mc_id=DT-MVP-5004771)**. In this part we look at how we can use **[Azure Key Vault](https://learn.microsoft.com/en-us/azure/key-vault/general/basic-concepts?wt.mc_id=DT-MVP-5004771)** as a secure **Secrets** store and how to integrate your GitHub Workflows with Key Vault for retrieving **Secrets**, to enhanced security and for more flexible centralised management of your **GitHub Secrets**.  

I recommend reading **Part 1** of the series where we explore the best practices for managing sensitive information in **[GitHub workflows](https://docs.github.com/en/actions/using-workflows/about-workflows?wt.mc_id=DT-MVP-5004771)** using **[GitHub Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#about-secrets?wt.mc_id=DT-MVP-5004771)** natively in the GitHub Website UI, giving a general overview and feel for **GitHub Secrets** and why you would want to use them.  

Let's jump straight into it and see how we can integrate **Azure Key Vault** with **GitHub**.

## Integrating Azure Key Vault with GitHub Workflows

**[Azure Key Vault](https://learn.microsoft.com/en-us/azure/key-vault/general/basic-concepts?wt.mc_id=DT-MVP-5004771)** is a cloud service for securely storing and accessing secrets. Integrating it with GitHub Action Workflows provides an extra layer of security and more flexibility for managing your secrets.

One of the biggest benefits of using **Azure Key Vault** is that it allows you to store your secrets in a centralised location, separate from your codebase, apart from **[Organization Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-an-organization?wt.mc_id=DT-MVP-5004771)**, it addresses the limitation with **[Repository Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository?wt.mc_id=DT-MVP-5004771)** where secrets have to be set in each unique repository which can make secrets management or rotation cumbersome.

There are a few things we need first to integrate **Azure Key Vault** with **GitHub Workflows**:

### Prerequisites

- GitHub repository.
- Azure Subscription.
- Azure Key Vault.
- Azure Service Principal with access to the Key Vault.

### Step-by-Step Integration Example

At the time of writing for the purposes of the following example on a **Windows** operating system, we will use **[GitHub CLI](https://github.com/cli/cli/releases?wt.mc_id=DT-MVP-5004771) v2.52.0** to create a **GitHub repository** and **[Azure CLI](https://github.com/Azure/azure-cli/releases?wt.mc_id=DT-MVP-5004771) v2.62.0** to create an **Azure Key Vault** and store an **Azure Storage Account Key** in it. We will then integrate the **Key Vault** with our **GitHub Actions workflow** with a service principal (identity) to access the storage account secret key securely during the actions workflow execution.

**1. Set Up Azure Key Vault:**

Once you have a suitable **Azure Subscription**, for the example below we will create a **Resource Group**, **Key Vault**, **Storage Account** and then store the Storage Account Key inside of the Key Vault as a secret, which we will later access in our GitHub Actions workflow:

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

  # Set RBAC access to the operation for maintaining secrets - grant signed in user access
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

As you can see we have securely created an **Azure Key Vault** and stored our **Storage Account Key** in it as a secret.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/GitHub-Secrets-Best-Practise-Part-2/assets/1-key-vault.png)

**2. Create a GitHub Repository (Optional):**  

For the purposes of this example we will use the **GitHub CLI** to create a new repository and initialise it with a README.md file, but you can also skip this step if you already have a repository you would like to integrate with **Azure Key Vault**:  

```pwsh
# Authenticate to GitHub
gh auth login

# Create a new repository
gh repo create "Integration-Test-Repo" --public --description "Azure Key Vault Integrated Test Repository"

# Clone the new repository (Replace <your-username> with your actual GitHub username.)
git clone "https://github.com/<your-username>/Integration-Test-Repo.git"
cd "Integration-Test-Repo"
  
# Create a new file and add content  
echo "# Key Vault Integration Test Repo" > README.md  
  
# Add the file to the staging area  
git add README.md  
  
# Commit the file  
git commit -m "Initial commit"  
  
# Push the changes to GitHub (If you are not using the main branch, replace 'main' with your branch name. e.g. 'master')
git push origin main  
```

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/GitHub-Secrets-Best-Practise-Part-2/assets/1-github-repo.png)

Now that we have our **GitHub repository** set up, we can move on to the next step to integrate it with our **Azure Key Vault**.  

**3. Configure Azure Service Principal:**

Next we will create a federated service principal (passwordless) in **[Azure Entra ID](https://learn.microsoft.com/en-us/entra/fundamentals/whatis?wt.mc_id=DT-MVP-5004771)** and grant it access to the Key Vault. We will integrate this service principal (identity) to access the Key Vault from our GitHub Actions workflow:  

```pwsh

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

### Additional federated GitHub credential entity types are 'Tag' and 'Environment' (see: https://docs.microsoft.com/en-us/azure/active-directory/develop/workload-identity-federation-create-trust?pivots=identity-wif-apps-methods-azcli#github-actions-example) ###

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
