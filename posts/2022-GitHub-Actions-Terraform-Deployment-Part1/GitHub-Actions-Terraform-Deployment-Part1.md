---
title: Multi environment AZURE deployments with Terraform and GitHub
published: true
description: Enterprise scale multi environment Azure deployments using Terraform and Github reusable workflows.
tags: 'terraform, iac, github, azuredevops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/assets/main.png'
canonical_url: null
id: 963996
date: '2022-01-23T15:14:24Z'
---

### Overview

This tutorial uses examples from the following GitHub demo project [template repository](https://github.com/Pwd9000-ML/Azure-Terraform-Deployments).

I have been wanting to do a tutorial to demonstrate how to perform large scale terraform deployments in Azure using a **non-monolithic** approach. I have seen so many large deployments fall into this same trap of using one big **monolithic** configuration when doing deployments at scale. Throwing everything into one unwieldy configuration can be troublesome for many reasons. To name a few:

- Making a small change can potentially break something much larger somewhere else in the configuration unintentionally.
- Build time aka `terraform plan/apply` is increased. A tiny change can take a long time to run as the entire state is checked.
- It can become cumbersome and complex for a team or team members to understand the entire code base.
- Module and provider versioning and dependencies can be fairly confusing to debug in this paradigm and may become restrictive.
- It becomes unmanageable, risky and time consuming to plan and implement any changes.

There's also many blogs and tutorials out there on how to integrate **Terraform** with DevOps **CI/CD** processes using Azure DevOps. So I decided to share with you today how to use **Terraform** with **GitHub** instead.

In this tutorial we will use **GitHub reusable workflows** and **GitHub environments** to build enterprise scale multi environment infrastructure deployments in **Azure** using a **non-monolithic** approach, to construct and simplify complex terraform deployments into simpler manageable work streams, that can be updated independently, increase build time, and reduce duplicate workflow code by utilizing **reusable GitHub workflows**.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/assets/mainwf.png)

Things you will get out of this tutorial:

- Learn about **GitHub reusable workflows**.
- Learn how to integrate terraform deployments with **CI/CD** using **GitHub**.
- Learn how to deploy resources in **AZURE** at scale.
- Learn about **multi-stage** deployments and approvals using **GitHub Environments**.

As an added bonus I have also added IaC security scanning with **TFSEC** to demonstrate IaC security scans and code quality checks as part of the CI/CD process to highlight any Terraform/Azure vulnerabilities or misconfigurations inside of the terraform code. Scan results are published on the GitHub Projects `Security` tab.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/assets/tfsec.png)

Hopefully you can utilize these concepts in your own organization to build **AZURE** Infrastructure at scale and succeed in your own awesome cloud projects.

### Pre-Requisites

To start things off we will build a few pre-requisites that is needed to integrate our **GitHub** project and workflows with **AZURE** before we can start building resources.

We are going to perform the following steps:

1. **Create Azure Resources (Terraform Backend):** (Optional) We will first create a few resources that will host our terraform backend state configuration. We will need a Resource Group, Storage Account and KeyVault. We will also create an **Azure Active Directory App & Service Principal** that will have access to our Terraform backend and subscription in Azure. We will link this Service Principal with our GitHub project and workflows later in the tutorial.
2. **Create a GitHub Repository:** We will create a GitHub project and set up the relevant secrets and (optional) GitHub environments that we will be using. The project will host our workflows and terraform configurations.
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

# Create a Key Vault
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

# Authorize the operation to create the container - Signed in User (Storage Blob Data Contributor Role)
az ad signed-in-user show --query objectId -o tsv | foreach-object {
    az role assignment create `
        --role "Storage Blob Data Contributor" `
        --assignee "$_" `
        --scope "/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.Storage/storageAccounts/$storageName"
    }

#Create Upload container in storage account to store terraform state files
Start-Sleep -s 40
az storage container create `
    --account-name "$storageName" `
    --name "tfstate" `
    --auth-mode login

# Create Terraform Service Principal and assign RBAC Role on Key Vault
$spnJSON = az ad sp create-for-rbac --name $appName `
    --role "Key Vault Secrets Officer" `
    --scopes /subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.KeyVault/vaults/$kvName

# Save new Terraform Service Principal details to key vault
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

# Assign additional RBAC role to Terraform Service Principal Subscription as Contributor and access to backend storage
az ad sp list --display-name $appName --query [].appId -o tsv | ForEach-Object {
    az role assignment create --assignee "$_" `
        --role "Contributor" `
        --subscription $subscriptionId

    az role assignment create --assignee "$_" `
        --role "Storage Blob Data Contributor" `
        --scope "/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.Storage/storageAccounts/$storageName" `
    }

```

Lets take a closer look, step-by-step what the above script does as part of setting up the Terraform backend environment.

1. Create a resource group called `Demo-Terraform-Core-Backend-RG`, containing an Azure key vault and storage account. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/assets/prereqs1.png)
2. Create an **AAD App and Service Principal** that has access to the key vault, backend storage account, container and the subscription. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/assets/spn.png) ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/assets/rbac.png)
3. The **AAD App and Service Principal** details are saved inside the key vault. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/assets/secrets.png)

## 2. Create a GitHub Repository

For this step I actually created a [template repository](https://github.com/Pwd9000-ML/Azure-Terraform-Deployments) that contains everything to get started. Feel free to create your repository from my template by selecting `Use this template`. (Optional)

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/assets/ghtemplate1.png)

After creating the GitHub repository there are a few things we do need to set on the repository before we can start using it.

1. Add the secrets that was created in the `Key Vault` step above, into the newly created GitHub repository as **[Repository Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets#creating-encrypted-secrets-for-a-repository)**  
   ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/assets/ghsecrets.png)
2. This step is **Optional**. Create the following **[GitHub Environments](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment#creating-an-environment)**, or environments that matches your own requirements. In my case these are: `Development`, `UserAcceptanceTesting`, `Production`. You do not have to set up and use **GitHub Environments**, this is optional and is used in this tutorial to demonstrate deployment approvals via **Protection Rules**.

**NOTE:** GitHub environments and Protection Rules are available on public repos, but for private repos you will need GitHub Enterprise.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/assets/ghenv.png)

Note that on the **Production** environment I have configured a **Required Reviewer**. This will basically allow me to set explicit reviewers that have to physically approve deployments to the **Production** environment. To learn more about approvals see [Environment Protection Rules](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment#environment-protection-rules).

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

- **[az_tf_plan.yml](https://github.com/Pwd9000-ML/blog-devto/blob/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/code/az_tf_plan.yml)**:

This workflow is a reusable workflow to plan a terraform deployment, create an artifact and upload that artifact to workflow artifacts for consumption.

```yml
## code/az_tf_plan.yml

### Reusable workflow to plan terraform deployment, create artifact and upload to workflow artifacts for consumption ###
name: 'Build_TF_Plan'
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
        description: 'Specifies the Terraform state file name for this plan. Workflow artifact will use same name.'
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

      - name: Scan IaC - tfsec
        uses: tfsec/tfsec-sarif-action@v0.0.6
        with:
          sarif_file: tfsec.sarif

      - name: Upload SARIF file
        uses: github/codeql-action/upload-sarif@v1
        with:
          sarif_file: tfsec.sarif

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
          name: '${{ inputs.tf_key }}'
          path: '${{ inputs.path }}/${{ inputs.tf_key }}.zip'
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
| --- | --- | --- | --- |
| path | True | Specifies the path of the root terraform module. | - |
| tf_version | False | (Optional) Specifies version of Terraform to use. e.g: 1.1.0 Default=latest. | latest |
| az_resource_group | True | Specifies the Azure Resource Group where the backend storage account is hosted. | - |
| az_storage_acc | True | Specifies the Azure Storage Account where the backend state is hosted. | - |
| az_container_name | True | Specifies the Azure Storage account container where backend Terraform state is hosted. | - |
| tf_key | True | Specifies the Terraform state file name for this plan. Workflow artifact will use same name. | - |
| gh_environment | False | (Optional) Specifies the GitHub deployment environment. Leave this setting out if you do not have GitHub Environments configured. | null |
| tf_vars_file | True | Specifies the Terraform TFVARS file. | - |

We aso need to pass some secrets from the **caller** to the **reusable workflow**. This is the details of our Service Principal we created to have access in Azure and is linked with our **GitHub Repository Secrets** we configured earlier.

| Secret              | Required | Description                              |
| ------------------- | -------- | ---------------------------------------- |
| arm_client_id       | True     | Specifies the Azure ARM CLIENT ID.       |
| arm_client_secret   | True     | Specifies the Azure ARM CLIENT SECRET.   |
| arm_subscription_id | True     | Specifies the Azure ARM SUBSCRIPTION ID. |
| arm_tenant_id       | True     | Specifies the Azure ARM TENANT ID.       |

This workflow when called will perform the following steps:

- Check out the code repository and set the path context given as input to the path containing the terraform module.
- Scan IaC in the path provided for any vulnerabilities or issues (Published to GitHub Security Tab)
- Install and use the version of terraform as per the input.
- Format check the terraform module code.
- Initialize the terraform module in the given path.
- Validate the terraform module in the given path.
- Create a terraform plan based on the given TFVARS file specified at input.
- Compress the plan artifacts.
- Upload the compressed plan as a workflow artifact.

### IaC Security Scanning (TFSEC)

In addition IaC scanning using TFSEC has also been applied to the `PLAN` **reusable workflow**.

Each terraform configuration, when calling the `PLAN` **reusable workflow** will be scanned for any Terraform IaC vulnerabilities and misconfigurations and the results will be published on the GitHub Projects `Security` tab e.g:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/assets/tfsec.png)

The IaC security scan will not stop or FAIL any terraform plan or deployment, but is meant to highlight issues in code that can be looked at and corrected or improved upon.

Let's take a look at our second **reusable workflow**.

- **[az_tf_apply.yml](https://github.com/Pwd9000-ML/blog-devto/blob/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/code/az_tf_apply.yml)**:

This workflow is a reusable workflow to download a terraform artifact built by `az_tf_plan.yml` and apply the artifact/plan (Deploy the planned terraform configuration).

```yml
## code/az_tf_apply.yml

### Reusable workflow to download terraform artifact built by `az_tf_plan` and apply the artifact/plan ###
name: 'Apply_TF_Plan'
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
        description: 'Specifies the Terraform state file name. Workflow artifact will be the same name.'
        required: true
        type: string
      gh_environment:
        description: 'Specifies the GitHub deployment environment.'
        required: false
        type: string
        default: null
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
        run: terraform apply plan.tfplan
```

The **inputs** and **secrets** are almost the same as our previous **reusable workflow** which created the terraform plan.

| Inputs | Required | Description | Default |
| --- | --- | --- | --- |
| path | True | Specifies the path of the root terraform module. | - |
| tf_version | False | (Optional) Specifies version of Terraform to use. e.g: 1.1.0 Default=latest. | latest |
| az_resource_group | True | Specifies the Azure Resource Group where the backend storage account is hosted. | - |
| az_storage_acc | True | Specifies the Azure Storage Account where the backend state is hosted. | - |
| az_container_name | True | Specifies the Azure Storage account container where backend Terraform state is hosted. | - |
| tf_key | True | Specifies the Terraform state file name for this plan. Workflow artifact will be the same name. | - |
| gh_environment | False | (Optional) Specifies the GitHub deployment environment. Leave this setting out if you do not have GitHub Environments configured. | null |

| Secret              | Required | Description                              |
| ------------------- | -------- | ---------------------------------------- |
| arm_client_id       | True     | Specifies the Azure ARM CLIENT ID.       |
| arm_client_secret   | True     | Specifies the Azure ARM CLIENT SECRET.   |
| arm_subscription_id | True     | Specifies the Azure ARM SUBSCRIPTION ID. |
| arm_tenant_id       | True     | Specifies the Azure ARM TENANT ID.       |

This workflow when called will perform the following steps:

- Download the terraform plan (workflow artifact).
- Decompress the terraform plan (workflow artifact).
- Install and use the version of terraform as per the input.
- Re-initialize the terraform module.
- Apply the terraform configuration based on the terraform plan that was created by the previous workflow.

Let's take a look at one of the **caller workflows** next. These workflows will be used to call the **reusable workflows**.

- **[01_Foundation.yml](https://github.com/Pwd9000-ML/blog-devto/blob/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/code/01_Foundation.yml)**:

This workflow is a **Caller** workflow. It will call and trigger a reusable workflow `az_tf_plan.yml` and create a foundational terraform deployment `PLAN` based on the repository `path: ./01_Foundation` containing the terraform ROOT module/configuration of an Azure Resource Group and key vault. The plan artifacts are validated, compressed and uploaded into the workflow artifacts, the caller workflow `01_Foundation` will then call and trigger the second reusable workflow `az_tf_apply.yml` that will download and decompress the `PLAN` artifact and trigger the deployment based on the plan. (Also demonstrated is how to use GitHub Environments to do multi staged environment based deployments with approvals - Optional)

```yml
## code/01_Foundation.yml
name: '01_Foundation'
on:
  workflow_dispatch:
  pull_request:
    branches:
      - master
jobs:
  Plan_Dev:
    #if: github.ref == 'refs/heads/master' && github.event_name == 'pull_request'
    uses: Pwd9000-ML/Azure-Terraform-Deployments/.github/workflows/az_tf_plan.yml@master
    with:
      path: 01_Foundation ## Path to terraform root module (Required)
      tf_version: latest ## Terraform version e.g: 1.1.0 Default=latest (Optional)
      az_resource_group: your-resource-group-name ## AZ backend - AZURE Resource Group hosting terraform backend storage acc (Required)
      az_storage_acc: your-storage-account-name ## AZ backend - AZURE terraform backend storage acc (Required)
      az_container_name: your-sa-container-name ## AZ backend - AZURE storage container hosting state files (Required)
      tf_key: foundation-dev ## AZ backend - Specifies name that will be given to terraform state file and workflow artifact name (Required)
      tf_vars_file: config-dev.tfvars ## Terraform TFVARS (Required)
    secrets:
      arm_client_id: ${{ secrets.ARM_CLIENT_ID }} ## ARM Client ID
      arm_client_secret: ${{ secrets.ARM_CLIENT_SECRET }} ## ARM Client Secret
      arm_subscription_id: ${{ secrets.ARM_SUBSCRIPTION_ID }} ## ARM Subscription ID
      arm_tenant_id: ${{ secrets.ARM_TENANT_ID }} ## ARM Tenant ID

  Deploy_Dev:
    needs: Plan_Dev
    uses: Pwd9000-ML/Azure-Terraform-Deployments/.github/workflows/az_tf_apply.yml@master
    with:
      path: 01_Foundation ## Path to terraform root module (Required)
      tf_version: latest ## Terraform version e.g: 1.1.0 Default=latest (Optional)
      az_resource_group: your-resource-group-name ## AZ backend - AZURE Resource Group hosting terraform backend storage acc (Required)
      az_storage_acc: your-storage-account-name ## AZ backend - AZURE terraform backend storage acc (Required)
      az_container_name: your-sa-container-name ## AZ backend - AZURE storage container hosting state files (Required)
      tf_key: foundation-dev ## AZ backend - Specifies name of the terraform state file and workflow artifact to download (Required)
      gh_environment: Development ## GH Environment. Default=null - (Optional)
    secrets:
      arm_client_id: ${{ secrets.ARM_CLIENT_ID }} ## ARM Client ID
      arm_client_secret: ${{ secrets.ARM_CLIENT_SECRET }} ## ARM Client Secret
      arm_subscription_id: ${{ secrets.ARM_SUBSCRIPTION_ID }} ## ARM Subscription ID
      arm_tenant_id: ${{ secrets.ARM_TENANT_ID }} ## ARM Tenant ID

  Plan_Uat:
    #if: github.ref == 'refs/heads/master' && github.event_name == 'pull_request'
    uses: Pwd9000-ML/Azure-Terraform-Deployments/.github/workflows/az_tf_plan.yml@master
    with:
      path: 01_Foundation
      az_resource_group: your-resource-group-name
      az_storage_acc: your-storage-account-name
      az_container_name: your-sa-container-name
      tf_key: foundation-uat
      tf_vars_file: config-uat.tfvars
    secrets:
      arm_client_id: ${{ secrets.ARM_CLIENT_ID }}
      arm_client_secret: ${{ secrets.ARM_CLIENT_SECRET }}
      arm_subscription_id: ${{ secrets.ARM_SUBSCRIPTION_ID }}
      arm_tenant_id: ${{ secrets.ARM_TENANT_ID }}

  Deploy_Uat:
    needs: [Plan_Uat, Deploy_Dev]
    uses: Pwd9000-ML/Azure-Terraform-Deployments/.github/workflows/az_tf_apply.yml@master
    with:
      path: 01_Foundation
      az_resource_group: your-resource-group-name
      az_storage_acc: your-storage-account-name
      az_container_name: your-sa-container-name
      tf_key: foundation-uat
      gh_environment: UserAcceptanceTesting
    secrets:
      arm_client_id: ${{ secrets.ARM_CLIENT_ID }}
      arm_client_secret: ${{ secrets.ARM_CLIENT_SECRET }}
      arm_subscription_id: ${{ secrets.ARM_SUBSCRIPTION_ID }}
      arm_tenant_id: ${{ secrets.ARM_TENANT_ID }}

  Plan_Prod:
    #if: github.ref == 'refs/heads/master' && github.event_name == 'pull_request'
    uses: Pwd9000-ML/Azure-Terraform-Deployments/.github/workflows/az_tf_plan.yml@master
    with:
      path: 01_Foundation
      tf_version: latest
      az_resource_group: your-resource-group-name
      az_storage_acc: your-storage-account-name
      az_container_name: your-sa-container-name
      tf_key: foundation-prod
      tf_vars_file: config-prod.tfvars
    secrets:
      arm_client_id: ${{ secrets.ARM_CLIENT_ID }}
      arm_client_secret: ${{ secrets.ARM_CLIENT_SECRET }}
      arm_subscription_id: ${{ secrets.ARM_SUBSCRIPTION_ID }}
      arm_tenant_id: ${{ secrets.ARM_TENANT_ID }}

  Deploy_Prod:
    needs: [Plan_Prod, Deploy_Uat]
    uses: Pwd9000-ML/Azure-Terraform-Deployments/.github/workflows/az_tf_apply.yml@master
    with:
      path: 01_Foundation
      az_resource_group: your-resource-group-name
      az_storage_acc: your-storage-account-name
      az_container_name: your-sa-container-name
      tf_key: foundation-prod
      gh_environment: Production
    secrets:
      arm_client_id: ${{ secrets.ARM_CLIENT_ID }}
      arm_client_secret: ${{ secrets.ARM_CLIENT_SECRET }}
      arm_subscription_id: ${{ secrets.ARM_SUBSCRIPTION_ID }}
      arm_tenant_id: ${{ secrets.ARM_TENANT_ID }}
```

Notice that we have multiple `jobs:` in the caller workflow, one job to generate a terraform plan and one job to deploy the plan, per environment.

You will see that each plan job uses the different TFVARS files: `config-dev.tfvars`, `config-uat.tfvars` and `config-prod.tfvars` respectively of each environment, but using the same ROOT module configuration in the **path:** `./01_Foundation/foundation_resources.tf`.  

Each plan job is also linked to a `tf_key` which represents the name of the backend state file as well as the name given to the compressed uploaded workflow artifact containing the terraform plan:  

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/assets/artifact.png)

Each reusable workflows **inputs** are specified on the **caller** workflows `jobs:` using `with:`, and **Secrets** using `secret:`.

(Optional) - You will also note that only the **Deploy** jobs: `Deploy_Dev:`, `Deploy_Uat:`, `Deploy_Prod:`, are linked with an input `gh_environment` which specifies which GitHub environment the job is linked to. Each **Plan** jobs: `Plan_Dev:`, `Plan_Uat:`, `Plan_Prod:`, are not linked to any GitHub Environment.

If you don't use **GitHub Environments** or don't have any set up, you can leave out the input: `gh_environment` completely. The benefits however of using GitHub Environments are **Protection rules**, and also **secrets** at the Environment scope.

Each **Deploy** jobs: `Deploy_Dev:`, `Deploy_Uat:`, `Deploy_Prod:` are also linked with the relevant `needs:` setting of it's corresponding plan. This means that the plan job must be successful before the deploy job can initialize and run. Deploy jobs are also linked with earlier deploy jobs using `needs:` so that **Dev** gets built first and if successful be followed by **Uat**, and if successful followed by **Prod**. However if you remember, we configured a **GitHub Protection Rule** on our Production environment which needs to be approved before it can run.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/assets/mainwf.png)

**NOTE:** if you have been following this tutorial step by step, and used a cloned copy of the [Demo Repository](https://github.com/Pwd9000-ML/Azure-Terraform-Deployments) you will need to update the **caller** workflows: `./.github/workflows/01_Foundation.yml` and `./.github/workflows/02_Storage.yml` with the **inputs** specified under `with:` using the values of your environment.

## Testing

Let's run the workflow: **01_Foundation** and see what happens.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/assets/run.png)

After the run you will see that each plan was created and DEV as well as UAT terraform configurations have been deployed to Azure as per the terraform configuration under `path: ./01_Foundation`:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/assets/run2.png)

After approving **Production** we can see that approval has triggered the production deployment and now we also have a production resource group.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/assets/run3.png)

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/assets/run4.png)

You will notice that each resource group contains a key vault as per our foundation terraform configuration under `path: ./01_Foundation`.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/assets/run5.png)

Let's run the workflow: **02_Storage** and after deploying DEV and UAT, also approve PRODUCTION to run.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/assets/run6.png)

Now you will notice that each of our environments resource groups also contains storage accounts as per the terraform configuration under `path: ./02_Storage`.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/assets/run7.png)

Lastly, if we navigate to the terraform backend storage account, you will see that based on the `tf_key` inputs we gave each of our **caller** workflow `jobs:`, each terraform deployment has its own state file per ROOT module/collection, per environment, which nicely segregates the terraform configuration state files independently from each other.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/assets/state.png)

## Conclusion

Following the same pattern shown in this tutorial you can now further expand your **Terraform** deployments in a modular, structured, non-monolithic way, by making more modules in separate paths e.g `./03_ect_ect` and extend your cloud deployments in more manageable chunks.

You can structure your **Terraform** modules/collections in such a way such as grouping certain resources together that forms a function such as **Foundation** or **Networking** for example, or a certain service such as **Storage** or **Apps**, so that when changes to IaC are needed for a certain function or service in a large scale architecture the changes can be implemented safely and independently.

I hope you have enjoyed this post and have learned something new. You can find the code samples used in this blog post on my [Github](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/code) page. You can also look at the demo project or even create your own projects and workflows from the demo project [template repository](https://github.com/Pwd9000-ML/Azure-Terraform-Deployments). :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}
