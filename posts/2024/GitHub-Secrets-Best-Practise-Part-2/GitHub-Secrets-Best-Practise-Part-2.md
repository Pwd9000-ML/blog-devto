---
title: Integrating Azure Key Vault for Secrets with GitHub Action Workflows - Part 2
published: false
description: Best Practices for Managing Sensitive Information in a GitHub Workflow
tags: 'github, git, devops, devsecops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/GitHub-Secrets-Best-Practise-Part-2/assets/main-gh-tips.png'
canonical_url: null
id: 1925352
series: GitHub Pro Tips
---

## Managing Sensitive Information in a GitHub Workflow

Welcome to **Part 2** of this 2-Part series where we explore different ways for managing sensitive information in **[GitHub workflows](https://docs.github.com/en/actions/using-workflows/about-workflows?wt.mc_id=DT-MVP-5004771)**. In this part we look at how we can use **[Azure Key Vault](https://learn.microsoft.com/en-us/azure/key-vault/general/basic-concepts?wt.mc_id=DT-MVP-5004771)** as a secure **Secrets** store and how to integrate your GitHub Workflows with Key Vault for retrieving **Secrets**, to enhanced security and for more flexible centralised management of your **GitHub Secrets**.

I recommend reading **[Part 1](https://dev.to/pwd9000/best-practices-for-using-github-secrets-part-1-596f)** of the series where we explore the best practices for managing sensitive information in **[GitHub workflows](https://docs.github.com/en/actions/using-workflows/about-workflows?wt.mc_id=DT-MVP-5004771)** using **[GitHub Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#about-secrets?wt.mc_id=DT-MVP-5004771)** natively in the GitHub Website UI and giving a general overview and feel for **GitHub Secrets** and why you would want to make use of them.

Let's jump straight in and see how we can integrate **Azure Key Vault** with **GitHub**.

## Integrating Azure Key Vault with GitHub Workflows

**[Azure Key Vault](https://learn.microsoft.com/en-us/azure/key-vault/general/basic-concepts?wt.mc_id=DT-MVP-5004771)** is a cloud service for securely storing and accessing secrets. Integrating it with GitHub Action Workflows provides an extra layer of security and more flexibility for managing your secrets.

One of the biggest benefits of using **Azure Key Vault** is that it allows you to store your secrets in a centralised location, separate from your codebase, apart from **[Organization Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-an-organization?wt.mc_id=DT-MVP-5004771)**, it addresses the limitation with **[Repository Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository?wt.mc_id=DT-MVP-5004771)** where secrets have to be set in each unique repository which can make secrets management or rotation cumbersome.

To name a few more benefits of using **Secrets** in **GitHub** with **Azure Key Vault** is that they can be accessed by multiple repositories and workflows, secret rotation can be managed centrally, access to secrets can be controlled using **Azure RBAC**, secrets history can also be maintained for auditing purposes and previous versions of secrets can be restored if needed.

There are a few things we need first to integrate **Azure Key Vault** with **GitHub Workflows**:

### Prerequisites

- GitHub repository.
- Azure Subscription.
- Azure Key Vault.
- Azure Service Principal with access to the Key Vault.

### Step-by-Step Integration Example

At the time of writing and for the purposes of the example to follow the following tools were used to prepare the prerequisites for the integration:

- **Windows** operating system.
- **[GitHub CLI](https://github.com/cli/cli/releases?wt.mc_id=DT-MVP-5004771) v2.52.0** to create a **GitHub repository**.
- **[Azure CLI](https://github.com/Azure/azure-cli/releases?wt.mc_id=DT-MVP-5004771) v2.62.0** to create an **Azure Key Vault**, **Secrets** and supporting resources.

In the following example we will integrate an **Azure Key Vault** with a **GitHub Actions workflow**, by integrating **Azure** with a **GitHub Repository** using a federated/passwordless **service principal** (identity) to access an **Azure Storage Account** as part of the workflow execution and using the **Storage Account Key** stored as a **secret** in the **Key Vault** to create a **Storage Container** and copy a **Blob file** into the created container.

**1. Set Up Azure Key Vault:**

Once you have a suitable **Azure Subscription**, we will create a **Resource Group**, **Key Vault**, **Storage Account** and then store the Storage Account Key inside of the Key Vault as a secret, which we will later retrieve and use in our GitHub Actions workflow:

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

As you can see we have created a new **GitHub repository** called `Integration-Test-Repo` and initialised it with a **README.md** file.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/GitHub-Secrets-Best-Practise-Part-2/assets/1-github-repo.png)

Now that we have our **GitHub repository** set up, we can move on to the next step to integrate it with our **Azure Key Vault**.

**3. Configure Azure Service Principal:**

Next we will create a federated service principal (passwordless) in **[Azure Entra ID](https://learn.microsoft.com/en-us/entra/fundamentals/whatis?wt.mc_id=DT-MVP-5004771)** and grant it access to the Key Vault. We will integrate this service principal (identity) to access the Key Vault from our GitHub Actions workflow later on:

```pwsh
# Set variables
$subscriptionId = $(az account show --query id -o tsv)
$resourceGroupName = "ghSecretsRg" # Resource Group Name where Key Vault is located
$keyVaultName = "ghSecretsVault4089" # Key Vault Name to access
$appName = "GitHub-projectName-Actions-OIDC" # App Registration Name
$RBACRole = "Key Vault Secrets User" # RBAC Role to apply

$githubOrgName = "Pwd9000-ML" # GitHub Organization/User Name
$githubRepoName = "Integration-Test-Repo" # GitHub Repository Name
$githubBranch = "master" # GitHub Branch Name

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

# Assign RBAC permissions on Service Principal to access KeyVault (Change as necessary)
$appId | foreach-object {

    # Permission 1 (Example)
    az role assignment create `
        --role $RBACRole `
        --assignee $_ `
        --scope "/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.KeyVault/vaults/$keyVaultName"

    # Permission 2 (Example)
    #az role assignment create `
    #    --role "Reader and Data Access" `
    #    --assignee "$_" `
    #    --scope "/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.Storage/storageAccounts/$storageName"
}
```

As you ca see we have created a service principal in **Azure Entra ID** called `GitHub-projectName-Actions-OIDC`.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/GitHub-Secrets-Best-Practise-Part-2/assets/1-service-principal.png)

Note that the service principal is federated with **GitHub** credentials for my created repository on **Branch** and **Pull Request** entity types.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/GitHub-Secrets-Best-Practise-Part-2/assets/1-service-principal-cred.png)

Also note that the service principal has been granted access to the **Key Vault** with the **Key Vault Secrets User** role.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/GitHub-Secrets-Best-Practise-Part-2/assets/1-service-principal-access.png)

The last step to integrate the **Service Principal** with our **GitHub Repository** we will need to add the **Application ID** of the **Service Principal** as well as our **Azure Tenant ID** and **Azure Subscription ID** as **GitHub Secrets** into our repository. Since the **Service Principal** is federated/passwordless with **GitHub** credentials, we do not have to add any **Client Secret**.

Navigate to your **GitHub Repository** and go to the **Settings** tab, then click on **Secrets and variables** and add the following **GitHub Secrets**:

- **AZURE_CLIENT_ID**: The **Application ID** of the federated **Service Principal**.
- **AZURE_TENANT_ID**: The **Azure Tenant ID** of your **Azure Subscription**.
- **AZURE_SUBSCRIPTION_ID**: The **Azure Subscription ID** of your **Azure Subscription**.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/GitHub-Secrets-Best-Practise-Part-2/assets/1-github-secrets.png)

**NOTE:** You can also check this previous blog post I wrote for more information about federated access between Azure and GitHub and other mechanisms and ways for integration between Azure and GitHub: **[GitHub Actions authentication methods for Azure](https://dev.to/pwd9000/bk-1iij)**

**3. Access Azure Key Vault in GitHub Actions:**

That is it for the setup and configuration of the **Azure Key Vault** and the **Service Principal**. Now we can utilise the federated **Service Principal** to access the **Key Vault** from our **GitHub Actions Workflow**.

Let's test this by creating a simple **GitHub Actions workflow** file in our repository to access the **Key Vault secret** we created earlier called `StorageAccountKey`. We will retrieve the Storage Account Key from the Key Vault and use it in our workflow to create a new storage container and copy a file into the storage container:

[keyvault-integration-test.yml](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2024/GitHub-Secrets-Best-Practise-Part-2/assets?wt.mc_id=DT-MVP-5004771/keyvault-integration-test.yml)

```yml
name: Azure Key Vault Integration Test

on: [push]

permissions:
  id-token: write
  contents: read

jobs:
  access-key-vault:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Log in to Azure using federated Service Principal
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - name: Retrieve secret from Key Vault
        id: get-secret-sa-key
        uses: azure/cli@v2
        with:
          azcliversion: latest
          inlineScript: |
            # Variables  
            KEY_VAULT_NAME=ghSecretsVault4089  
            SECRET_NAME=StorageAccountKey  

            # Retrieve secret from Key Vault  
            STORAGE_KEY=$(az keyvault secret show --name $SECRET_NAME --vault-name $KEY_VAULT_NAME --query value -o tsv)

            # Create a container in Azure Storage Account using the secret
            az storage container create --name "ghrepocontainer" --account-name "ghsecsa4089" --account-key "$STORAGE_KEY"

            # Copy a text file saying "Hello World" to the container
            echo "Hello World" > hello.txt
            az storage blob upload --container-name "ghrepocontainer" --file hello.txt --name hello.txt --account-name "ghsecsa4089" --account-key "$STORAGE_KEY"        

            # You can also set the retrieved secret as an output for use in subsequent steps in the workflow  
            echo "::set-output name=secret_value::$STORAGE_KEY"

      - name: Use the retrieved secret in another step (example)
        uses: azure/cli@v2
        with:
          azcliversion: latest
          inlineScript: |
            # Use the secret output from the previous step
            # WARNING! Output secret to workflow log just as an example for the purposes of this demonstration 
            echo "The secret value is: ${{ steps.get-secret-sa-key.outputs.secret_value }}"
```

Note that after running the workflow above:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/GitHub-Secrets-Best-Practise-Part-2/assets/1-github-actions.png)

The **Storage Account Key** was retrieved from the **Key Vault** and used to create a new storage container called `ghrepocontainer`:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/GitHub-Secrets-Best-Practise-Part-2/assets/1-azure-storage.png)

We also used the same retrieved **Storage Account Key** to upload a file called `hello.txt` to the storage container:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/GitHub-Secrets-Best-Practise-Part-2/assets/1-azure-storage-file.png)

**NOTE:** As you can see from the example above we can also optionally set the retrieved secret as an output for use in subsequent steps in the workflow using this syntax: `echo "::set-output name=secret_value::$STORAGE_KEY"`. We can then use the output secret in another step in the workflow using this syntax: `${{ steps.get-secret-sa-key.outputs.secret_value }}` as you can see in this step:

```yml
- name: Use the retrieved secret in another step (example)
  uses: azure/cli@v2
  with:
    azcliversion: latest
    inlineScript: |
      # Use the secret output from the previous step
      # WARNING! Output secret to workflow log just as an example for the purposes of this demonstration 
      echo "The secret value is: ${{ steps.get-secret-sa-key.outputs.secret_value }}"
```

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/GitHub-Secrets-Best-Practise-Part-2/assets/1-github-actions-output.png)

## Conclusion

Managing sensitive information securely is vital for any DevOps workflow. By using **GitHub Secrets**, but by integrating Azure Key Vault, you can ensure that your secrets are stored and accessed securely and managed centrally. This provides an extra layer of security and more flexibility for managing your secrets.

Always follow best practices and avoid common pitfalls to maintain the security and integrity of your applications.

I hope you have enjoyed this post and have learned something new. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
