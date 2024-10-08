---
title: Dynamic terraform deployments using DevOps replace tokens
published: true
description: DevOps - Terraform - Replace Tokens
tags: 'terraform, azure, iac, azuredevops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/DevOps-Replace-Tokens/assets/main-rep.png'
canonical_url: null
id: 802801
date: '2021-08-26T07:36:30Z'
---

## Replace tokens

Replace tokens is a DevOps extension that can be installed into your DevOps Organisation from the Azure DevOps [marketplace](https://marketplace.visualstudio.com/items?itemName=qetza.replacetokens), simply put it is an Azure Pipelines extension that replace tokens in files with variable values. Today we will look at how we can use this Devops extension working with a terraform HCL code base, to dynamically deploy infrastructure hosted on Azure based on environments defined as variables in DevOps using terraform.

## Installing Replace Tokens

Before we can use replace tokens we have to install it into our Devops Organisation from the [marketplace](https://marketplace.visualstudio.com/items?itemName=qetza.replacetokens).

Go to DevOps Organisation Settings and select the **Extensions** tab followed by **Browse marketplace** and search for **Replace tokens**. In addition also install the terraform extension called **Terraform** by Microsoft DevLabs as we will use this later on to use terraform tasks in our DevOps pipeline.

![ado_task](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/DevOps-Replace-Tokens/assets/ado_task.png)

## Project layout and objective

For this tutorial we will write a simple terraform configuration that will deploy a resource group, but we will use the **replace tokens task** to manipulate our configuration file to deploy 3 different resource groups based on environment. For example `Infra-dev-Rg`, `Infra-uat-Rg` and `Infra-prod-Rg`. I have set up a new project in my organisation called **DynamicTerraform**, I also created a repository called **Infrastructure**. Inside of my repository I have created the following paths:

- `/terraform-azurerm-resourcegroup` This location will be my root path used to store the main terraform configuration files which will be used to deploy a simple resource group.
- `/terraform-azurerm-resourcegroup/pipelines` This location will be used to store and configure yaml deployment pipelines for the resources in my root path.
- `/terraform-azurerm-resourcegroup/pipelines/variables` This location will be used to store and configure yaml variable template files used for my pipelines.
- `/terraform-azurerm-resourcegroup/pipelines/task_groups` This location will be used to store and configure yaml tasks/steps used in my pipelines.

Any additional future resources can be created in new root paths e.g.: `/terraform-azurerm-resourceX`, `/terraform-azurerm-resourceY`, `/terraform-azurerm-resourceZ` etc... For this tutorial we will just be using `/terraform-azurerm-resourcegroup` to deploy multiple resource groups dynamically based on an environment e.g. `dev`, `uat` and `prod`. This is what the DevOps project layout looks like:

![repo_layout](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/DevOps-Replace-Tokens/assets/repo_layout.png)

## Terraform Configuration

As a pre-requisite I have also pre-created an Azure DevOps [service connection](https://docs.microsoft.com/en-us/azure/devops/pipelines/library/service-endpoints?view=azure-devops&tabs=yaml#create-a-service-connection/?wt.mc_id=DT-MVP-5004771) that will be used to allow my pipelines to access Azure via the terraform task we installed earlier, and I also pre-created an Azure storage account which will act as my terraform [backend](https://www.terraform.io/docs/language/settings/backends/azurerm.html) to safely store my terraform state files in.

Under my repo path: `/terraform-azurerm-resourcegroup/`, I have created the following three terraform files:

1. **main.tf** (Main terraform configuration file)

   ```hcl
   # code/terraform-azurerm-resourcegroup/main.tf

   ##################################################
   # Terraform Config                               #
   ##################################################
   terraform {
     required_version = ">= ~{terraformVersion}~"

     backend "azurerm" {
       resource_group_name  = "~{terraformBackendRG}~"
       storage_account_name = "~{terraformBackendSA}~"
       container_name       = "tfstate"
       key                  = "infra_~{environment}~_rg.tfstate"
     }

     required_providers {
       azurerm = {
         source  = "hashicorp/azurerm"
         version = "~> 2.73"
       }
     }
   }

   provider "azurerm" {
     features {}
     skip_provider_registration = true
   }

   ##################################################
   # RESOURCES                                      #
   ##################################################
   resource "azurerm_resource_group" "resource_group" {
     name     = var.resource_group_name
     location = var.location
     tags     = var.tags
   }
   ```

   **NOTE:** In the terraform configuration you will notice the following values: `~{terraformVersion}~`, `~{terraformBackendRG}~`, `~{terraformBackendSA}~` and `~{environment}~`, we will be dynamically changing the values inside of `~{ }~` with values from our pipeline variable file later on in this tutorial using **replace tokens**.

2. **variables.tf** (Terraform variable definition file)

   ```hcl
   # code/terraform-azurerm-resourcegroup/variables.tf

   variable "resource_group_name" {
     type        = string
     description = "Specifies the name of the resource group that will be created."
   }

   variable "location" {
     type        = string
     description = "The location/region where Azure resource will be created."
   }

   variable "tags" {
     type        = map(any)
     description = "Specifies a map of tags to be applied to the resources created."
   }

   ```

3. **resourcegroup.auto.tfvars** (Terraform variables which will be dynamically changed by replace tokens task)

   ```hcl
   # code/terraform-azurerm-resourcegroup/resourcegroup.auto.tfvars

   resource_group_name = "Infra-~{environment}~-Rg"
   location            = "~{location}~"
   tags = {
     terraformDeployment = "true"
     Environment         = "~{environment}~"
   }
   ```

   **NOTE:** In the **TFVARS** configuration file you will notice the following values: `~{environment}~` and `~{location}~`, we will be dynamically changing the values inside of `~{ }~` with values from our pipeline variable file later on in this tutorial using **replace tokens**.

## DevOps Pipeline Variable files

Under my repo path: `/terraform-azurerm-resourcegroup/pipelines/variables/`, I have created the following four yaml variable template files:

1. **common_vars.yml** (Declares variables that will be used in all pipelines).

   ```yml
   # code/terraform-azurerm-resourcegroup/pipelines/variables/common_vars.yml

   variables:
     #Terraform Config + backend
     - name: terraformVersion
       value: '1.0.5'

     - name: terraformBackendRG
       value: 'TF-Core-Rg'

     - name: terraformBackendSA
       value: 'tfcorebackendsa'

     #Variables used for service connection
     - name: AzureServiceConnection
       value: 'TF-Terraform-SP'

     - name: rootDirName
       value: 'terraform-azurerm-resourcegroup'
   ```

2. **dev_vars.yml** (Declares variables that will be used in DEV specific pipeline).

   ```yml
   # code/terraform-azurerm-resourcegroup/pipelines/variables/dev_vars.yml

   variables:
     #Development Variables
     - name: environment
       value: 'dev'

     - name: location
       value: 'uksouth'
   ```

3. **uat_vars.yml** (Declares variables that will be used in UAT specific pipeline).

   ```yml
   # code/terraform-azurerm-resourcegroup/pipelines/variables/uat_vars.yml

   variables:
     #UAT Variables
     - name: environment
       value: 'uat'

     - name: location
       value: 'uksouth'
   ```

4. **prod_vars.yml** (Declares variables that will be used in PROD specific pipeline).

   ```yml
   # code/terraform-azurerm-resourcegroup/pipelines/variables/prod_vars.yml

   variables:
     #Production Variables
     - name: environment
       value: 'prod'

     - name: location
       value: 'ukwest'
   ```

**NOTE:** You will notice that the variable **names** in each yaml template are aligned with the values used on the terraform configuration files earlier: `~{environment}~`, `~{location}~`, `~{terraformBackendRG}~`, `~{terraformBackendSA}~`. Also note that our production variable file has a different location specified: `ukwest`.

## DevOps Pipelines

Under my repo path: `/terraform-azurerm-resourcegroup/pipelines/`, I have created the following three yaml pipelines (one for each environment):

1. **dev_deployment.yml** (Deploy dev RG - Pipeline)

   ```yml
   # code/terraform-azurerm-resourcegroup/pipelines/dev_deployment.yml

   name: Deployment-Dev-RG-$(Rev:rr)
   trigger: none

   variables:
     - template: variables/common_vars.yml
     - template: variables/dev_vars.yml

   stages:
     - stage: TF_DEPLOY_DEV_RG
       displayName: Deploy Dev ResourceGroup
       dependsOn: []
       jobs:
         - deployment: TF_Deploy_Dev_Rg
           displayName: Terraform - Dev - RG
           pool:
             name: Azure Pipelines
             vmImage: windows-latest
           workspace:
             clean: all
           environment: Infra-Dev
           strategy:
             runOnce:
               deploy:
                 steps:
                   - checkout: self
                   ### Run common terraform deploy steps
                   - template: task_groups/tf_deploy_tasks.yml
                     parameters:
                       terraformVersion: ${{ variables.terraformVersion }}
                       rootDirName: ${{ variables.rootDirName }}
                       AzureServiceConnection: ${{ variables.AzureServiceConnection }}
                       terraformBackendRG: ${{ variables.terraformBackendRG }}
                       terraformBackendSA: ${{ variables.terraformBackendSA }}
                       environment: ${{ variables.environment }}
   ```

2. **uat_deployment.yml** (Deploy uat RG - Pipeline)

   ```yml
   # code/terraform-azurerm-resourcegroup/pipelines/uat_deployment.yml

   name: Deployment-UAT-RG-$(Rev:rr)
   trigger: none

   variables:
     - template: variables/common_vars.yml
     - template: variables/uat_vars.yml

   stages:
     - stage: TF_DEPLOY_UAT_RG
       displayName: Deploy Uat ResourceGroup
       dependsOn: []
       jobs:
         - deployment: TF_Deploy_Uat_Rg
           displayName: Terraform - Uat - RG
           pool:
             name: Azure Pipelines
             vmImage: windows-latest
           workspace:
             clean: all
           environment: Infra-Uat
           strategy:
             runOnce:
               deploy:
                 steps:
                   - checkout: self
                   ### Run common terraform deploy steps
                   - template: task_groups/tf_deploy_tasks.yml
                     parameters:
                       terraformVersion: ${{ variables.terraformVersion }}
                       rootDirName: ${{ variables.rootDirName }}
                       AzureServiceConnection: ${{ variables.AzureServiceConnection }}
                       terraformBackendRG: ${{ variables.terraformBackendRG }}
                       terraformBackendSA: ${{ variables.terraformBackendSA }}
   ```

3. **prod_deployment.yml** (Deploy prod RG - Pipeline)

   ```yml
   # code/terraform-azurerm-resourcegroup/pipelines/prod_deployment.yml

   name: Deployment-Prod-RG-$(Rev:rr)
   trigger: none

   variables:
     - template: variables/common_vars.yml
     - template: variables/prod_vars.yml

   stages:
     - stage: TF_DEPLOY_PROD_RG
       displayName: Deploy Prod ResourceGroup
       dependsOn: []
       jobs:
         - deployment: TF_Deploy_Prod_Rg
           displayName: Terraform - Prod - RG
           pool:
             name: Azure Pipelines
             vmImage: windows-latest
           workspace:
             clean: all
           environment: Infra-Prod
           strategy:
             runOnce:
               deploy:
                 steps:
                   - checkout: self
                   ### Run common terraform deploy steps
                   - template: task_groups/tf_deploy_tasks.yml
                     parameters:
                       terraformVersion: ${{ variables.terraformVersion }}
                       rootDirName: ${{ variables.rootDirName }}
                       AzureServiceConnection: ${{ variables.AzureServiceConnection }}
                       terraformBackendRG: ${{ variables.terraformBackendRG }}
                       terraformBackendSA: ${{ variables.terraformBackendSA }}
   ```

## DevOps Pipelines - Task group

Under my repo path: `/terraform-azurerm-resourcegroup/pipelines/task_groups/`, I have created the following common yaml tasks/steps template which defines common steps that will be used in each pipeline:

```yml
# code/terraform-azurerm-resourcegroup/pipelines/task_groups/tf_deploy_tasks.yml

parameters:
  terraformVersion:
  rootDirName:
  AzureServiceConnection:
  terraformBackendRG:
  terraformBackendSA:
  environment:

steps:
  ### Install Terraform Version from commom_vars
  - task: TerraformInstaller@0
    inputs:
      terraformVersion: ${{ parameters.terraformVersion }}

  ### replace tokens in tf and tfvars.
  - task: qetza.replacetokens.replacetokens-task.replacetokens@3
    displayName: 'Replace tokens in tfvars and tf'
    inputs:
      rootDirectory: '$(System.DefaultWorkingDirectory)'
      targetFiles: |
        ${{ parameters.rootDirName }}\*.tf
        ${{ parameters.rootDirName }}\*.tfvars
            encoding: 'utf-8'
      actionOnMissing: 'warn'
      keepToken: false
      tokenPrefix: '~{'
      tokenSuffix: '}~'

  ### Terraform Init
  - task: TerraformTaskV2@2
    displayName: Terraform Init
    inputs:
      provider: 'azurerm'
      command: 'init'
      workingDirectory: '$(System.DefaultWorkingDirectory)/${{ parameters.rootDirName }}'
      backendServiceArm: '${{ parameters.AzureServiceConnection }}'
      backendAzureRmResourceGroupName: '${{ parameters.terraformBackendRG }}'
      backendAzureRmStorageAccountName: '${{ parameters.terraformBackendSA }}'
      backendAzureRmContainerName: 'tfstate'
      backendAzureRmKey: 'Infra_${{ parameters.environment }}_rg.tfstate'

  ### Terraform Plan
  - task: TerraformTaskV2@2
    displayName: Terraform Plan
    inputs:
      provider: 'azurerm'
      command: 'plan'
      workingDirectory: '$(System.DefaultWorkingDirectory)/${{ parameters.rootDirName }}'
      commandOptions: '--out=$(System.DefaultWorkingDirectory)/${{ parameters.rootDirName }}/plan.tfplan'
      environmentServiceNameAzureRM: '${{ parameters.AzureServiceConnection }}'

  ### Terraform Apply
  - task: TerraformTaskV2@2
    displayName: Terraform Apply
    inputs:
      provider: 'azurerm'
      command: 'apply'
      workingDirectory: '$(System.DefaultWorkingDirectory)/${{ parameters.rootDirName }}'
      environmentServiceNameAzureRM: '${{ parameters.AzureServiceConnection }}'
```

Note that the replace tokens task is defined and configured to replace the variables we defined within the **tokenPrefix: `~{`** and **tokenSuffix: `}~`** as you can see below:

```yml
### replace tokens in tf and tfvars.
- task: qetza.replacetokens.replacetokens-task.replacetokens@3
  displayName: 'Replace tokens in tfvars and tf'
  inputs:
    rootDirectory: '$(System.DefaultWorkingDirectory)'
    targetFiles: |
      ${{ parameters.rootDirName }}\*.tf
      ${{ parameters.rootDirName }}\*.tfvars
          encoding: 'utf-8'
    actionOnMissing: 'warn'
    keepToken: false
    tokenPrefix: '~{'
    tokenSuffix: '}~'
```

Now we can configure each pipeline, which will consume its own corresponding variable template file as well as a common variable template file, but use the same terraform configuration code to dynamically deploy the same resource group but each having its own state file, name and tags dynamically.

![pipelines](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/DevOps-Replace-Tokens/assets/pipelines.png)

Also remember to set the environments in Azure DevOps as shown on each of our yaml pipelines e.g.:

```yml
# code/terraform-azurerm-resourcegroup/pipelines/dev_deployment.yml#L21-L21

environment: Infra-Dev
```

![environments](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/DevOps-Replace-Tokens/assets/environments.png)

After each pipeline has been run, you will notice that our terraform configuration was dynamically changed each time with the **replace tokens task**, replacing the values on our **TF** and **TFVARS** files.

![replace_token](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/DevOps-Replace-Tokens/assets/replace_token.png)

You'll also see the each resource group have been dynamically created.

![rg_dep](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/DevOps-Replace-Tokens/assets/rg_dep.png)

**NOTE:** Remember we changed location to be in the UK West region on our variable template file for prod.

Also note that each of the deployments have their own unique state file based on the environment as depicted on each of the yaml pipelines and declared in the variable files e.g.:

```yml
# code/terraform-azurerm-resourcegroup/pipelines/dev_deployment.yml#L58-L58

backendAzureRmKey: 'Infra_${{ variables.environment }}_rg.tfstate'
```

![state](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/DevOps-Replace-Tokens/assets/state.png)

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my [GitHub](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2021/DevOps-Replace-Tokens/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [X/Twitter](https://x.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
