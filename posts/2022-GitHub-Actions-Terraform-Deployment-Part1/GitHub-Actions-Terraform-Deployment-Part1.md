---
title: Multi environment AZURE deployments with Terraform and GitHub
published: false
description: Enterprise scale multi environment Azure deployments using Terraform and Github reusable workflows.
tags: 'terraform, iac, github, azuredevops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/assets/main.png'
canonical_url: null
id: 963996
---

### Overview

I have been wanting to do a tutorial to demonstrate how to perform large scale terraform deployments in Azure using a **non-monolithic** approach. I have seen so many large deployments fall into this same trap of using one big **monolithic** configuration when doing deployments at scale. Throwing everything into one unwieldy configuration can be troublesome for many reasons. To name a few:

- Making a small change can potentially break something much larger somewhere else in the configuration unintentionally.
- Build time aka `terraform plan/apply` is increased. A tiny change can take a long time to run as the entire state is checked.
- It can become cumbersome and complex for a team or team member to understand the entire code base.
- Module and provider versioning and dependencies can be fairly confusing to debug in this paradigm.
- It becomes unmanageable, risky and time consuming to plan and implement any changes.

There's also many blogs and tutorials out there on how to integrate **Terraform** with DevOps **CI/CD** processes using Azure DevOps. So I decided to share with you today how to use **Terraform** with **GitHub** instead.

In this tutorial we will use **GitHub reusable workflows** and **GitHub environments** to build enterprise scale multi environment infrastructure deployments in **Azure** using a **non-monolithic** approach, to construct and simplify complex terraform deployments into simpler manageable work streams, that can be updated independently, increase build time, and reduce duplicate workflow code by utilizing **reusable GitHub workflows**.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/assets/mainwf.png)

Things you will get out of this tutorial:

- Learn about **GitHub reusable workflows**.
- Learn how to integrate terraform deployments with **CI/CD** using **GitHub**.
- Learn how to deploy resources in **AZURE** at scale.
- Learn about **multi-stage** deployments and approvals using **GitHub Environments**.

Hopefully you can even utilize these concepts in your own organization to build **AZURE** Infrastructure at scale in your own awesome cloud projects.

### Pre-Requisites

To start things off we will build a few pre-requisites that is needed to integrate our **GitHub** project and workflows with **AZURE** before we can start building resources.

We are going to perform the following steps:

1. **Create Azure Resources (Terraform Backend):** (Optional) We will first create a few resources that will host our terraform backend state configuration. We will need a Resource Group, Storage Account and KeyVault. We will also create an **Azure Active Directory App & Service Principal** that will have access to our Terraform backend and subscription in Azure. We will link this Service Principal with our GitHub project and workflows later in the tutorial.
2. **Create a GitHub Repository:** We will create a GitHub project and set up the relevant secrets and environments that we will be using. The project will host our workflows and terraform configurations.
3. **Create Terraform Modules (Modular):** We will set up a few terraform ROOT modules. Separated and modular from each other (non-monolithic).
4. **Create GitHub Workflows:** After we have our repository and terraform ROOT modules configured we will create our reusable workflows and configure multi-stage deployments to run and deploy resources in Azure based on our terraform ROOT Modules.

## 1. Create Azure resources (Terraform Backend)

To set up the resources that will act as our Terraform backend, I wrote a PowerShell script using AZ CLI that will build and configure everything and store the relevant details/secrets we need to link our GitHub project in a key vault. You can find the script on my [github code](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/code) page called [AZ-GH-TF-Pre-Reqs.ps1](https://github.com/Pwd9000-ML/blog-devto/blob/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/code/AZ-GH-TF-Pre-Reqs.ps1).

First we will log into Azure by running:

```powershell
az login
```

After logging into Azure and selecting the subscription, we can run the script that will create all the pre-requirements we'll need:

```powershell
## code/AZ-GH-TF-Pre-Reqs.ps1

#Log into Azure
#az login

# Setup Variables.
$randomInt = Get-Random -Maximum 9999
$subscriptionId = (get-azcontext).Subscription.Id
$resourceGroupName = "Demo-Terraform-Core-Backend-RG"
$storageName = "tfcorebackendsa$randomInt"
$kvName = "tf-core-backend-kv$randomInt"
$appName="tf-core-github-SPN$randomInt"
$region = "uksouth"

# Create a resource resourceGroupName
az group create --name "$resourceGroupName" --location "$region"

# Create a Key Vault (RBAC mode)
az keyvault create `
    --name "$kvName" `
    --resource-group "$resourceGroupName" `
    --location "$region" `
    --enable-rbac-authorization

# Authorize the operation to create a few secrets - Signed in User (Key Vault Secrets Officer)
az ad signed-in-user show --query objectId -o tsv | foreach-object {
    az role assignment create `
        --role "Key Vault Secrets Officer" `
        --assignee "$_" `
        --scope "/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.KeyVault/vaults/$kvName"
    }

# Create an azure storage account - Terraform Backend Storage Account
az storage account create `
    --name "$storageName" `
    --location "$region" `
    --resource-group "$resourceGroupName" `
    --sku "Standard_LRS" `
    --kind "StorageV2" `
    --https-only true `
    --min-tls-version "TLS1_2"

# Create Terraform Service Principal and assign RBAC Role on Key Vault
$spnJSON = az ad sp create-for-rbac --name $appName `
    --role "Key Vault Secrets Officer" `
    --scopes /subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.KeyVault/vaults/$kvName

# Save new Terraform Service Principal details to key vault for later use
$spnObj = $spnJSON | ConvertFrom-Json
foreach($object_properties in $spnObj.psobject.properties) {
    If ($object_properties.Name -eq "appId") {
        $null = az keyvault secret set --vault-name $kvName --name "ARM-CLIENT-ID" --value $object_properties.Value
    }
    If ($object_properties.Name -eq "password") {
        $null = az keyvault secret set --vault-name $kvName --name "ARM-CLIENT-SECRET" --value $object_properties.Value
    }
    If ($object_properties.Name -eq "tenant") {
        $null = az keyvault secret set --vault-name $kvName --name "ARM-TENANT-ID" --value $object_properties.Value
    }
}
$null = az keyvault secret set --vault-name $kvName --name "ARM-SUBSCRIPTION-ID" --value $subscriptionId

# Assign additional RBAC role to Terraform Service Principal Subscription as Contributor
az ad sp list --display-name $appName --query [].appId -o tsv | ForEach-Object {
    az role assignment create --assignee "$_" `
        --role "Contributor" `
        --subscription $subscriptionId
    }
```

Lets take a closer look, step-by-step what the above script does as part of setting up the Terraform backend environment.

1. Create a resource group called `Demo-Terraform-Core-Backend-RG`, containing an Azure key vault and storage account. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/assets/prereqs1.png)
2. Create an **AAD App and Service Principal** that has access to the key vault and the subscription. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/assets/spn.png) ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/assets/rbac.png)
3. The **AAD App and Service Principal** details are saved inside the key vault. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/assets/secrets.png)

## 2. Create a GitHub Repository

For this step I actually created a [template repository](https://github.com/Pwd9000-ML/Azure-Terraform-Deployments) that contains everything to get started. Feel free to create your repository from my template by selecting `Use this template`. (Optional)

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/assets/ghtemplate1.png)

After creating the GitHub repository there are a few things we do need to set on the repository before we can start using it.

1. Add the secrets that was created in the `Key Vault` step above, into the newly created GitHub repository as **[Repository Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets#creating-encrypted-secrets-for-a-repository)**

   ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/assets/ghsecrets.png)

2. Create the following **[GitHub Environments](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment#creating-an-environment)**. Or environments that matches your own requirements. In my case these are: `Development`, `UserAcceptanceTesting`, `Production`. Note that GitHub environments are available on public repos, but for private repos you will need GitHub Enterprise.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/assets/ghenv.png)

Also note that on my **Production** environment I have set a **Required Reviewer**. This will basically allow me to set explicit reviewers that have to physically approve deployments to the **Production** environment. To learn more about approvals see [Environment Protection Rules](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment#environment-protection-rules).

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/assets/ghprotect.png)

**NOTE:** You can also configure **GitHub Secrets** at the **Environment** scope if you have separate Service Principals or even separate Subscriptions in Azure for each **Environment**. (Example: Your Development resources are in subscription A and your Production resources are in Subscription B). See [Creating encrypted secrets for an environment](https://docs.github.com/en/actions/security-guides/encrypted-secrets#creating-encrypted-secrets-for-an-environment) for details.

## 3. Create Terraform Modules (Modular)

Now that our repository is all configured and ready to go, we can start to create some modular terraform configurations, or in other words separate independent deployment configurations based on ROOT terraform modules. If you look at the [Demo Repository](https://github.com/Pwd9000-ML/Demo-Repo-TF-Azure) you will see that on the root of the repository I have paths/folders that are numbered e.g. **./01_Foundation** and **./02_Storage**.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/assets/tfmods.png)

These paths each contain a terraform ROOT module, which consists of a **collection** of items that can **independently** be configured and deployed. You do not have to use the same naming/numbering as I have chosen, but the idea is to understand that these paths/folders each represent a unique independent modular terraform configuration that consists of a collection of resources that we want to deploy independently.

So in this example:

- **path:** `./01_Foundation` contains the terraform ROOT module/configuration of an Azure Resource Group and key vault.
- **path:** `./02_Storage` contains the terraform ROOT module/configuration for one General-V2 and one Data Lake V2 Storage storage account.

**NOTE:** You will also notice that each ROOT module contains 3x separate TFVARS files: `config-dev.tfvars`, `config-uat.tfvars` and `config-prod.tfvars`. Each representing an environment. This is because each of my environments will use the same configuration: `foundation_resources.tf`, but may have slightly different configuration values or naming.  

Example: The **Development** resource group name will be called `Demo-Infra-Dev-Rg`, whereas the **Production** resource group will be called `Demo-Infra-Prod-Rg`.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/assets/tffoundation.png)

## 4. Create GitHub Workflows

Next we will create a special folder/path structure in the root of our repository called `.github/workflows`. This folder/path will contain our **[GitHub Action Workflows](https://docs.github.com/en/actions/learn-github-actions/understanding-github-actions)**.  

You will notice that there are **numbered** workflows: `./.github/workflows/01_Foundation.yml` and `./.github/workflows/02_Storage.yml`, these are **caller** workflows. Each caller workflow represents a terraform module and is named the same as the **path** containing the ROOT terraform module as described in the section above. There are also 2x **[GitHub Reusable Workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows)** called `./.github/workflows/az_tf_plan.yml` and `./.github/workflows/az_tf_apply.yml`.

Let's take a closer look at the reusable workflows:

- **az_tf_plan.yml**:  

This workflow is a reusable workflow to plan a terraform deployment, create an artifact and upload that artifact to workspace artifacts for consumption.

```yml
## code/az_tf_plan.yml

### Reusable workflow to plan terraform deployment, create artifact and upload to workspace artifacts for consumption ###
name: "Build_TF_Plan"
on:
  workflow_call:
    inputs:
      path:
        description: 'Specifies the path of the root terraform module.'
        required: true
        type: string
      tf_version:
        description: 'Specifies version of Terraform to use. e.g: 1.1.0 Default=latest.'
        required: false
        type: string
        default: latest
      az_resource_group:
        description: 'Specifies the Azure Resource Group where the backend storage account is hosted.'
        required: true
        type: string
      az_storage_acc:
        description: 'Specifies the Azure Storage Account where the backend state is hosted.'
        required: true
        type: string
      az_container_name:
        description: 'Specifies the Azure Storage account container where backend Terraform state is hosted.'
        required: true
        type: string
      tf_key:
        description: 'Specifies the Terraform state file name for this plan.'
        required: true
        type: string
      gh_environment:
        description: 'Specifies the GitHub deployment environment.'
        required: false
        type: string
        default: null
      tf_vars_file:
        description: 'Specifies the Terraform TFVARS file.'
        required: true
        type: string
    secrets:
      arm_client_id:
        description: 'Specifies the Azure ARM CLIENT ID.'
        required: true
      arm_client_secret:
        description: 'Specifies the Azure ARM CLIENT SECRET.'
        required: true
      arm_subscription_id:
        description: 'Specifies the Azure ARM SUBSCRIPTION ID.'
        required: true
      arm_tenant_id:
        description: 'Specifies the Azure ARM TENANT ID.'
        required: true

jobs:
  build-plan:
    runs-on: ubuntu-latest
    environment: ${{ inputs.gh_environment }}
    defaults:
      run:
        shell: bash
        working-directory: ${{ inputs.path }}
    env:
      STORAGE_ACCOUNT: ${{ inputs.az_storage_acc }}
      CONTAINER_NAME: ${{ inputs.az_container_name }}
      RESOURCE_GROUP: ${{ inputs.az_resource_group }}
      TF_KEY: ${{ inputs.tf_key }}.tfstate
      TF_VARS: ${{ inputs.tf_vars_file }}
      ###AZURE Client details###
      ARM_CLIENT_ID: ${{ secrets.arm_client_id }}
      ARM_CLIENT_SECRET: ${{ secrets.arm_client_secret }}
      ARM_SUBSCRIPTION_ID: ${{ secrets.arm_subscription_id }}
      ARM_TENANT_ID: ${{ secrets.arm_tenant_id }}
  
    steps:
      - name: Checkout
        uses: actions/checkout@v2

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v1.3.2
        with:
          terraform_version: ${{ inputs.tf_version }}

      - name: Terraform Format
        id: fmt
        run: terraform fmt --check

      - name: Terraform Init
        id: init
        run: terraform init --backend-config="storage_account_name=$STORAGE_ACCOUNT" --backend-config="container_name=$CONTAINER_NAME" --backend-config="resource_group_name=$RESOURCE_GROUP" --backend-config="key=$TF_KEY"
      
      - name: Terraform Validate
        id: validate
        run: terraform validate

      - name: Terraform Plan
        id: plan
        run: terraform plan --var-file=$TF_VARS --out=plan.tfplan
        continue-on-error: true

      - name: Terraform Plan Status
        if: steps.plan.outcome == 'failure'
        run: exit 1

      - name: Compress TF Plan artifact
        run: zip -r ${{ inputs.tf_key }}.zip ./*

      - name: Upload Artifact
        uses: actions/upload-artifact@v2
        with:
          name: "${{ inputs.tf_key }}"
          path: "${{ inputs.path }}/${{ inputs.tf_key }}.zip"
          retention-days: 5
```

**NOTE:** The reusable workflow can only be triggered by another workflow, aka the **caller** workflows. We can see this by the `on:` trigger called `workflow_call:`.

```yml
## code/az_tf_plan.yml#L3-L4

on:
  workflow_call:
```

As you can see the reusable workflow can be given specific **inputs** when called by the **caller** workflow. Notice that one of the inputs are called **path:** which we can use to specify the path of the ROOT terraform module that we want to plan and deploy.  

| Inputs | Required | Description | Default |
|--------|----------|-------------|---------|
| path | True | Specifies the path of the root terraform module. | - |
| tf_version | False | Specifies version of Terraform to use. e.g: 1.1.0 Default=latest. | latest |
| az_resource_group | True | Specifies the Azure Resource Group where the backend storage account is hosted. | - |
| az_storage_acc | True | Specifies the Azure Storage Account where the backend state is hosted. | - |
| az_container_name | True | Specifies the Azure Storage account container where backend Terraform state is hosted. | - |
| tf_key | True | Specifies the Terraform state file name for this plan. | - |
| gh_environment | False | Specifies the GitHub deployment environment. | null |
| tf_vars_file | True | Specifies the Terraform TFVARS file. | - |

We aso need to pass some secrets from the **caller** to the **reusable workflow**. This is the details of our Service Principal we created to have access in Azure and is linked with our **GitHub Repository Secrets** we configured earlier.  

| Secret | Required | Description |
|--------|----------|-------------|
| arm_client_id | True | Specifies the Azure ARM CLIENT ID. |
| arm_client_secret | True | Specifies the Azure ARM CLIENT SECRET. |
| arm_subscription_id | True | Specifies the Azure ARM SUBSCRIPTION ID. |
| arm_tenant_id | True | Specifies the Azure ARM TENANT ID. |

This workflow when called will perform the following steps:  

- Check out the code repository and set the path context given as input to the path containing the terraform module.
- Install and use the version of terraform as per the input.
- Format check the terraform module code.
- Initialize the terraform module in the given path.
- Validate the terraform module in the given path.
- Create a terraform plan based on the given TFVARS file specified at input.
- Compress the plan artifacts.
- Upload the compressed plan as a workflow artifact.

- **az_tf_apply.yml**:  

This workflow is a reusable workflow to download a terraform artifact built by `az_tf_plan.yml` and apply the artifact/plan (Deploy the planned terraform configuration).

```yml
## code/az_tf_apply.yml

### Reusable workflow to download terraform artifact built by `az_tf_plan` and apply the artifact/plan ###
name: "Apply_TF_Plan"
on:
  workflow_call:
    inputs:
      path:
        description: 'Specifies the path of the root terraform module.'
        required: true
        type: string
      tf_version:
        description: 'Specifies version of Terraform to use. e.g: 1.1.0 Default=latest.'
        required: false
        type: string
        default: latest
      az_resource_group:
        description: 'Specifies the Azure Resource Group where the backend storage account is hosted.'
        required: true
        type: string
      az_storage_acc:
        description: 'Specifies the Azure Storage Account where the backend state is hosted.'
        required: true
        type: string
      az_container_name:
        description: 'Specifies the Azure Storage account container where backend Terraform state is hosted.'
        required: true
        type: string
      tf_key:
        description: 'Specifies the Terraform state file name for this plan.'
        required: true
        type: string
      gh_environment:
        description: 'Specifies the GitHub deployment environment.'
        required: false
        type: string
        default: null
      tf_vars_file:
        description: 'Specifies the Terraform TFVARS file.'
        required: true
        type: string
    secrets:
      arm_client_id:
        description: 'Specifies the Azure ARM CLIENT ID.'
        required: true
      arm_client_secret:
        description: 'Specifies the Azure ARM CLIENT SECRET.'
        required: true
      arm_subscription_id:
        description: 'Specifies the Azure ARM SUBSCRIPTION ID.'
        required: true
      arm_tenant_id:
        description: 'Specifies the Azure ARM TENANT ID.'
        required: true

jobs:
  apply-plan:
    runs-on: ubuntu-latest
    environment: ${{ inputs.gh_environment }}
    defaults:
      run:
        shell: bash
        working-directory: ${{ inputs.path }}
    env:
      STORAGE_ACCOUNT: ${{ inputs.az_storage_acc }}
      CONTAINER_NAME: ${{ inputs.az_container_name }}
      RESOURCE_GROUP: ${{ inputs.az_resource_group }}
      TF_KEY: ${{ inputs.tf_key }}.tfstate
      TF_VARS: ${{ inputs.tf_vars_file }}
      ###AZURE Client details###
      ARM_CLIENT_ID: ${{ secrets.arm_client_id }}
      ARM_CLIENT_SECRET: ${{ secrets.arm_client_secret }}
      ARM_SUBSCRIPTION_ID: ${{ secrets.arm_subscription_id }}
      ARM_TENANT_ID: ${{ secrets.arm_tenant_id }}
  
    steps:
      - name: Download Artifact
        uses: actions/download-artifact@v2
        with:
          name: ${{ inputs.tf_key }}
          path: ${{ inputs.path }}

      - name: Decompress TF Plan artifact
        run: unzip ${{ inputs.tf_key }}.zip

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v1.3.2
        with:
          terraform_version: ${{ inputs.tf_version }}

      - name: Terraform Init
        id: init
        run: terraform init --backend-config="storage_account_name=$STORAGE_ACCOUNT" --backend-config="container_name=$CONTAINER_NAME" --backend-config="resource_group_name=$RESOURCE_GROUP" --backend-config="key=$TF_KEY"

      - name: Terraform Apply
        run: terraform apply --var-file=$TF_VARS --auto-approve
```

The **inputs** and **secrets** are the same as our previous **reusable workflow** which created the terraform plan.  

| Inputs | Required | Description | Default |
|--------|----------|-------------|---------|
| path | True | Specifies the path of the root terraform module. | - |
| tf_version | False | Specifies version of Terraform to use. e.g: 1.1.0 Default=latest. | latest |
| az_resource_group | True | Specifies the Azure Resource Group where the backend storage account is hosted. | - |
| az_storage_acc | True | Specifies the Azure Storage Account where the backend state is hosted. | - |
| az_container_name | True | Specifies the Azure Storage account container where backend Terraform state is hosted. | - |
| tf_key | True | Specifies the Terraform state file name for this plan. | - |
| gh_environment | False | Specifies the GitHub deployment environment. | null |
| tf_vars_file | True | Specifies the Terraform TFVARS file. | - |

| Secret | Required | Description |
|--------|----------|-------------|
| arm_client_id | True | Specifies the Azure ARM CLIENT ID. |
| arm_client_secret | True | Specifies the Azure ARM CLIENT SECRET. |
| arm_subscription_id | True | Specifies the Azure ARM SUBSCRIPTION ID. |
| arm_tenant_id | True | Specifies the Azure ARM TENANT ID. |

This workflow when called will perform the following steps:  

- Download the terraform plan (workflow artifact).
- Decompress the terraform plan (workflow artifact).
- Install and use the version of terraform as per the input.
- Re-initialize the terraform module.
- Apply the terraform configuration based on the terraform plan and values in the TFVARS file.



I hope you have enjoyed this post and have learned something new. You can find the code samples used in this blog post on my [Github](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}
