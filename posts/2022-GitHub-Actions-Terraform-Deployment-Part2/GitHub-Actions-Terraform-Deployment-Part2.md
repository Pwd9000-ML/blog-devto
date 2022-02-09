---
title: Multi environment AZURE deployments with Terraform and GitHub (Part 2)
published: true
description: Enterprise scale multi environment Azure deployments using Terraform and Github Actions.
tags: 'terraform, iac, github, azuredevops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part2/assets/main.png'
canonical_url: null
id: 969349
series: Using Terraform on GitHub
date: '2022-01-27T10:18:59Z'
---

### Overview

This tutorial uses examples from the following GitHub demo project [template repository](https://github.com/Pwd9000-ML/Azure-Terraform-Deployments).

Welcome to part 2 of my series on **Using Terraform on GitHub**. In [part 1](https://dev.to/pwd9000/multi-environment-azure-deployments-with-terraform-and-github-2450) of this series we looked at how to build enterprise scale multi environment infrastructure deployments in **Azure** using a **non-monolithic** approach, to construct and simplify complex terraform deployments into simpler manageable work streams, that can be updated independently, increase build time, and reduce duplicate workflow code by utilizing **reusable GitHub workflows**.

Recently I decided to create two public **GitHub Actions** on the GitHub Actions marketplace called **[Terraform Plan for AZURE](https://github.com/marketplace/actions/terraform-plan-for-azure)** and **[Terraform Apply for AZURE](https://github.com/marketplace/actions/terraform-apply-for-azure)**. So in this part of the series I will show how you can use the public marketplace actions instead of reusable workflows.

### Pre-Requisites

The pre-requisites we need to start using terraform on Github is exactly the same as in [part 1](https://dev.to/pwd9000/multi-environment-azure-deployments-with-terraform-and-github-2450) of this series. I would recommend going through [part 1](https://dev.to/pwd9000/multi-environment-azure-deployments-with-terraform-and-github-2450) first, and follow the same steps for 1-3.

We are going to perform the following steps:

1. **Create Azure Resources (Terraform Backend):** (Optional) We will first create a few resources that will host our terraform backend state configuration. We will need a Resource Group, Storage Account and KeyVault. We will also create an **Azure Active Directory App & Service Principal** that will have access to our Terraform backend and subscription in Azure. We will link this Service Principal with our GitHub project and workflows later in the tutorial.
2. **Create a GitHub Repository:** We will create a GitHub project and set up the relevant secrets and (optional) GitHub environments that we will be using. The project will host our workflows and terraform configurations.
3. **Create Terraform Modules (Modular):** We will set up a few terraform ROOT modules. Separated and modular from each other (non-monolithic).
4. **Create GitHub Workflows using marketplace Actions:** After we have our repository and terraform ROOT modules configured we will create a workflow and configure multi-stage deployments using public marketplace actions to run and deploy resources in Azure based on our terraform ROOT Modules.

## Steps 1 to 3

Refer to [part 1](https://dev.to/pwd9000/multi-environment-azure-deployments-with-terraform-and-github-2450) of this series.

## 4. Create GitHub Workflows using marketplace Actions

In the root of our repository we create a folder/path called `.github/workflows`. This folder/path will contain our [GitHub Action Workflows](https://docs.github.com/en/actions/learn-github-actions/understanding-github-actions).

If you are following this tutorial based on the demo project [template repository](https://github.com/Pwd9000-ML/Azure-Terraform-Deployments), you will notice that the folder contains a `YAML` workflow called [./.github/workflows/Marketplace_Example.yml].

Let's take a closer look at this workflow:

- **[Marketplace_Example.yml](https://github.com/Pwd9000-ML/Azure-Terraform-Deployments/blob/master/.github/workflows/Marketplace_Example.yml)**:

```yml
# I have created public github marketplace actions (plan and apply) as well that can be used as shown in this example.
#Plan: https://github.com/marketplace/actions/terraform-plan-for-azure
#Apply: https://github.com/marketplace/actions/terraform-apply-for-azure

name: 'Marketplace-Example'
on:
  workflow_dispatch:
  pull_request:
    branches:
      - master

jobs:
  ##### PLAN A DEPLOYMENT #####
  Plan_Dev_Deploy:
    runs-on: ubuntu-latest
    if: ${{ github.actor != 'dependabot[bot]' }}
    environment: null #(Optional) If using GitHub Environments
    steps:
      - name: Checkout
        uses: actions/checkout@v2

      - name: Dev TF Plan Deploy
        uses: Pwd9000-ML/terraform-azurerm-plan@v1.2.0
        with:
          path: 01_Foundation ## (Optional) Specify path TF module relevant to repo root. Default="."
          plan_mode: deploy ## (Optional) Specify plan mode. Valid options are "deploy" or "destroy". Default="deploy"
          tf_version: latest ## (Optional) Specifies version of Terraform to use. e.g: 1.1.0 Default="latest"
          tf_vars_file: config-dev.tfvars ## (Required) Specifies Terraform TFVARS file name inside module path.
          tf_key: foundation-dev ## (Required) AZ backend - Specifies name that will be given to terraform state file and plan artifact
          enable_TFSEC: true ## (Optional) Enable TFSEC IaC scans (Private repo requires GitHub enterprise). Default=false
          az_resource_group: TF-Core-Rg ## (Required) AZ backend - AZURE Resource Group hosting terraform backend storage acc
          az_storage_acc: tfcorebackendsa ## (Required) AZ backend - AZURE terraform backend storage acc
          az_container_name: ghdeploytfstate ## (Required) AZ backend - AZURE storage container hosting state files
          arm_client_id: ${{ secrets.ARM_CLIENT_ID }} ## (Required - Actions Secrets) ARM Client ID
          arm_client_secret: ${{ secrets.ARM_CLIENT_SECRET }} ## (Required - Actions Secrets) ARM Client Secret
          arm_subscription_id: ${{ secrets.ARM_SUBSCRIPTION_ID }} ## (Required - Actions Secrets) ARM Subscription ID
          arm_tenant_id: ${{ secrets.ARM_TENANT_ID }} ## (Required - Actions Secrets) ARM Tenant ID
          github_token: ${{ secrets.GITHUB_TOKEN }} ## (Required) Needed to comment output on PR's. ${{ secrets.GITHUB_TOKEN }} already has permissions

  ##### APPLY DEPLOY #####
  Apply_Dev_Deploy:
    needs: Plan_Dev_Deploy
    runs-on: ubuntu-latest
    environment: Development #(Optional) If using GitHub Environments
    steps:
      - name: Dev TF Deploy
        if: ${{ github.actor != 'dependabot[bot]' }}
        uses: Pwd9000-ML/terraform-azurerm-apply@v1.2.0
        with:
          plan_mode: deploy ## (Optional) Specify plan mode. Valid options are "deploy" or "destroy". Default="deploy"
          tf_version: latest ## (Optional) Specifies version of Terraform to use. e.g: 1.1.0 Default="latest"
          tf_key: foundation-dev ## (Required) Specifies name of the terraform state file and plan artifact to download
          az_resource_group: TF-Core-Rg ## (Required) AZ backend - AZURE Resource Group hosting terraform backend storage acc
          az_storage_acc: tfcorebackendsa ## (Required) AZ backend - AZURE terraform backend storage acc
          az_container_name: ghdeploytfstate ## (Required) AZ backend - AZURE storage container hosting state files
          arm_client_id: ${{ secrets.ARM_CLIENT_ID }} ## (Required - Actions Secrets) ARM Client ID
          arm_client_secret: ${{ secrets.ARM_CLIENT_SECRET }} ## (Required - Actions Secrets) ARM Client Secret
          arm_subscription_id: ${{ secrets.ARM_SUBSCRIPTION_ID }} ## (Required - Actions Secrets) ARM Subscription ID
          arm_tenant_id: ${{ secrets.ARM_TENANT_ID }} ## (Required - Actions Secrets) ARM Tenant ID

  ##### PLAN A DESTROY #####
  Plan_Dev_Destroy:
    needs: Apply_Dev_Deploy
    runs-on: ubuntu-latest
    if: ${{ github.actor != 'dependabot[bot]' }}
    environment: null #(Optional) If using GitHub Environments
    steps:
      - name: Checkout
        uses: actions/checkout@v2

      - name: Dev TF Plan Destroy
        uses: Pwd9000-ML/terraform-azurerm-plan@v1.2.0
        with:
          path: 01_Foundation ## (Optional) Specify path TF module relevant to repo root. Default="."
          plan_mode: destroy ## (Optional) Specify plan mode. Valid options are "deploy" or "destroy". Default="deploy"
          tf_version: latest ## (Optional) Specifies version of Terraform to use. e.g: 1.1.0 Default="latest"
          tf_vars_file: config-dev.tfvars ## (Required) Specifies Terraform TFVARS file name inside module path.
          tf_key: foundation-dev ## (Required) AZ backend - Specifies name that will be given to terraform state file and plan artifact
          enable_TFSEC: false ## (Optional) Enable TFSEC IaC scans (Private repo requires GitHub enterprise). Default=false
          az_resource_group: TF-Core-Rg ## (Required) AZ backend - AZURE Resource Group hosting terraform backend storage acc
          az_storage_acc: tfcorebackendsa ## (Required) AZ backend - AZURE terraform backend storage acc
          az_container_name: ghdeploytfstate ## (Required) AZ backend - AZURE storage container hosting state files
          arm_client_id: ${{ secrets.ARM_CLIENT_ID }} ## (Required - Actions Secrets) ARM Client ID
          arm_client_secret: ${{ secrets.ARM_CLIENT_SECRET }} ## (Required - Actions Secrets) ARM Client Secret
          arm_subscription_id: ${{ secrets.ARM_SUBSCRIPTION_ID }} ## (Required - Actions Secrets) ARM Subscription ID
          arm_tenant_id: ${{ secrets.ARM_TENANT_ID }} ## (Required - Actions Secrets) ARM Tenant ID
          github_token: ${{ secrets.GITHUB_TOKEN }} ## (Required) Needed to comment output on PR's. ${{ secrets.GITHUB_TOKEN }} already has permissions

  ##### APPLY DESTROY #####
  Apply_Dev_Destroy:
    needs: Plan_Dev_Destroy
    runs-on: ubuntu-latest
    environment: Development #(Optional) If using GitHub Environments
    steps:
      - name: Dev TF Destroy
        if: ${{ github.actor != 'dependabot[bot]' }}
        uses: Pwd9000-ML/terraform-azurerm-apply@v1.2.0
        with:
          plan_mode: destroy ## (Optional) Specify plan mode. Valid options are "deploy" or "destroy". Default="deploy"
          tf_version: latest ## (Optional) Specifies version of Terraform to use. e.g: 1.1.0 Default="latest"
          tf_key: foundation-dev ## (Required) Specifies name of the terraform state file and plan artifact to download
          az_resource_group: TF-Core-Rg ## (Required) AZ backend - AZURE Resource Group hosting terraform backend storage acc
          az_storage_acc: tfcorebackendsa ## (Required) AZ backend - AZURE terraform backend storage acc
          az_container_name: ghdeploytfstate ## (Required) AZ backend - AZURE storage container hosting state files
          arm_client_id: ${{ secrets.ARM_CLIENT_ID }} ## (Required - Actions Secrets) ARM Client ID
          arm_client_secret: ${{ secrets.ARM_CLIENT_SECRET }} ## (Required - Actions Secrets) ARM Client Secret
          arm_subscription_id: ${{ secrets.ARM_SUBSCRIPTION_ID }} ## (Required - Actions Secrets) ARM Subscription ID
          arm_tenant_id: ${{ secrets.ARM_TENANT_ID }} ## (Required - Actions Secrets) ARM Tenant ID
```

As you can see this workflow has four `jobs:`, `Plan_Dev_Deploy`, `Apply_Dev_Deploy`, `Plan_Dev_Destroy`, `Apply_Dev_Destroy`. You will also notice that each job calls the marketplace actions with `uses:` in a `steps:` argument.

You will also see that the `APPLY` jobs: `Apply_Dev_Deploy:` and `Apply_Dev_Destroy` job has a special `needs:` argument which means, the apply job requires the plan job to successfully run first and create the terraform plan, as it will use the `PLAN` created to perform the `APPLY`. (The plan is actually uploaded into the workflow as an artifact which will either contain a deployment plan called `deploy_plan.tfplan` if `plan_mode: "deploy"` is used, or a destroy plan called `destroy_plan.tfplan` if `plan_mode: "destroy"` is used. The apply job will download and apply the `PLAN` artifact from the workflow artifacts and run the relevant plan based on the `plan_mode`)

Additionally on the `Apply` jobs, if you use **[GitHub Environments](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment#creating-an-environment)** you can also link the job using the `environment:` argument and apply approvals by using **[Environment Protection Rules](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment#environment-protection-rules)**.

Input parameters are passed into each of the actions using the `with:` argument. Lets take a look at each actions available inputs.

## PLAN Action Inputs

**[Terraform Plan for AZURE](https://github.com/marketplace/actions/terraform-plan-for-azure)**

This action will connect to a remote Terraform backend in Azure, creates a terraform plan and uploads plan as a workflow artifact. (Additionally TFSEC IaC scanning can be enabled).

| Input | Required | Description | Default |
| --- | --- | --- | --- |
| `path` | FALSE | Specify path to Terraform module relevant to repo root. | "." |
| `plan_mode` | FALSE | Specify plan mode. Valid options are `deploy` or `destroy`. | "deploy" |
| `tf_version` | FALSE | Specifies the Terraform version to use. | "latest" |
| `tf_vars_file` | TRUE | Specifies Terraform TFVARS file name inside module path. | N/A |
| `tf_key` | TRUE | AZ backend - Specifies name that will be given to terraform state file and plan artifact | N/A |
| `enable_TFSEC` | FALSE | Enable IaC TFSEC scan, results are posted to GitHub Project Security Tab. (Private repos require GitHub enterprise). | FALSE |
| `az_resource_group` | TRUE | AZ backend - AZURE Resource Group name hosting terraform backend storage account | N/A |
| `az_storage_acc` | TRUE | AZ backend - AZURE terraform backend storage account name | N/A |
| `az_container_name` | TRUE | AZ backend - AZURE storage container hosting state files | N/A |
| `arm_client_id` | TRUE | The Azure Service Principal Client ID | N/A |
| `arm_client_secret` | TRUE | The Azure Service Principal Secret | N/A |
| `arm_subscription_id` | TRUE | The Azure Subscription ID | N/A |
| `arm_tenant_id` | TRUE | The Azure Service Principal Tenant ID | N/A |
| `github_token` | TRUE | Specify GITHUB TOKEN, only used in PRs to comment outputs such as `plan`, `fmt`, `init` and `validate`. `${{ secrets.GITHUB_TOKEN }}` already has permissions, but if using own token, ensure repo scope. | N/A |

In both examples the terraform plan will be created and is compressed and published to the workflow as an artifact using the same name of the inputs `[plan_mode]-[tf_key]`:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part2/assets/artifact1.png)

As mentioned earlier, the artifacts will either contain a deployment plan called `deploy_plan.tfplan` if `plan_mode: "deploy"` is used, or a destroy plan called `destroy_plan.tfplan` if `plan_mode: "destroy"` is used.

The terraform apply action will download and apply the plan inside of the artifact created by the plan action using the same `[plan_mode]-[tf_key]` and will start a deploy or destroy action based on the `plan_mode`.

**NOTE:** If `enable_TFSEC` is set to `true` on plan stage, Terraform IaC will be scanned using TFSEC and results are published to the GitHub Project `Security` tab:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part2/assets/tfsec.png)

If using a private repository, GitHub enterprise is needed when enabling TFSEC. However if a public repository is used, code analysis is included and TFSEC can be enabled on public repositories without the need for a GitHub enterprise account.

Also note that if the `PLAN` action is used in the context of a Pull Request (PR) the output will be added as a comment on the PR. (Requires a valid GITHUB TOKEN as input with `github_token`) Additionally failures on `fmt`, `init` and `validate` will also added to the PR. e.g.:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part2/assets/pr.png)

## APPLY Action Inputs

**[Terraform Apply for AZURE](https://github.com/marketplace/actions/terraform-apply-for-azure)**

This action will download a Terraform plan workflow artifact created by `Pwd9000-ML/terraform-azurerm-plan` and apply with an AZURE backend configuration.

| Input | Required | Description | Default |
| --- | --- | --- | --- |
| `plan_mode` | FALSE | Specify plan mode. Valid options are `deploy` or `destroy`. | "deploy" |
| `tf_version` | FALSE | Specifies the Terraform version to use. | "latest" |
| `tf_key` | TRUE | Specifies name of the terraform state file and plan artifact to download | N/A |
| `az_resource_group` | TRUE | AZ backend - AZURE Resource Group name hosting terraform backend storage account | N/A |
| `az_storage_acc` | TRUE | AZ backend - AZURE terraform backend storage account name | N/A |
| `az_container_name` | TRUE | AZ backend - AZURE storage container hosting state files | N/A |
| `arm_client_id` | TRUE | The Azure Service Principal Client ID | N/A |
| `arm_client_secret` | TRUE | The Azure Service Principal Secret | N/A |
| `arm_subscription_id` | TRUE | The Azure Subscription ID | N/A |
| `arm_tenant_id` | TRUE | The Azure Service Principal Tenant ID | N/A |

The terraform apply action will download and apply the plan inside of the artifact created by the plan action using the same `[plan_mode]-[tf_key]` and apply the relevant plan based on which `plan_mode` was used in the creation of the plan artifact.

## Conclusion

That's all there is to it. So following the same pattern shown in this series you can now further expand your **Terraform** deployments in a modular, structured, non-monolithic way, by making more modules in separate paths e.g `./03_ect_ect` and for each deployment you can use my public **marketplace Actions** to plan and also apply your configuration. Or if you prefer using **re-usable workflows** you can also see how to do that in [part 1](https://dev.to/pwd9000/multi-environment-azure-deployments-with-terraform-and-github-2450) of this series.

I hope you have enjoyed this post and have learned something new. You can find the code samples used in this blog post on my [Github](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2022-GitHub-Actions-Terraform-Deployment-Part1/code) page. You can also look at the demo project or even create your own projects and workflows from the demo project [template repository](https://github.com/Pwd9000-ML/Azure-Terraform-Deployments). :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
