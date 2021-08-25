---
title: Dynamic terraform deployments using DevOps replace tokens
published: false
description: DevOps - Terraform - Replace Tokens
tags: 'tutorial, azure, productivity, devops'
cover_image: assets/main.jpg
canonical_url: null
id: 802801
---

## Replace tokens

Replace tokens is a DevOps extension that can be installed into your DevOps Organisation from the Azure DevOps [marketplace](https://marketplace.visualstudio.com/items?itemName=qetza.replacetokens), simply put it is an Azure Pipelines extension that replace tokens in files with variable values. Today we will look at how we can use this Devops extension working with a terraform HCL code base, to dynamically deploy infrastructure hosted on Azure based on environments defined as variables using terraform.

## Installing Replace Tokens

Before we can use replace tokens we have to install it into our Devops Organisation from the [marketplace](https://marketplace.visualstudio.com/items?itemName=qetza.replacetokens).  

Go to your DevOps Organisation Settings and select the **Extensions** tab followed by **Browse marketplace** and search for **Replace tokens**. In addition we will also install the terraform extension called **Terraform** by Microsoft DevLabs.

![ado_task](./assets/ado_task.jpg)

## Project layout and objective

For this tutorial we will write a simple terraform configuration that will deploy a resource group, but we will use the **replace tokens task** to manipulate our configuration file to deploy 3 different resource groups based on environment. For example `Infra-Dev-Rg`, `Infra-Uat-Rg` and `Infra-Prod-Rg`. I have set up a new project in my organisation called **DynamicTerraform**, I also created a repository called **Infrastructure**. Inside of my repository I have created the following paths:

- `\pipelines` Here we will configure our yaml deployment pipeline.
- `\pipelines\variables` Here we will create a yaml based variable file for our pipeline
- `\terraform-azurerm-resourcegroup` Here we will have our main HCL coe base which will be used to deploy a simple resource group

Any additional future resources can be created in new paths e.g.: `\terraform-azurerm-resourceX\`, `\terraform-azurerm-resourceY\`, `\terraform-azurerm-resourceZ\` etc... For this tutorial we will just be using `\terraform-azurerm-resourcegroup\` to deploy resource groups.

![repo_layout](./assets/repo_layout.jpg)

## Terraform Configuration

As a pre-req I have also pre-created an Azure DevOps [service connection](https://docs.microsoft.com/en-us/azure/devops/pipelines/library/service-endpoints?view=azure-devops&tabs=yaml#create-a-service-connection) that will be used to allow my pipeline to access Azure via the terraform task we installed earlier, and I also pre-created an Azure storage account which will act as my terraform [backend](https://www.terraform.io/docs/language/settings/backends/azurerm.html) to safely store my terraform state in.  

Under my repo path: `\terraform-azurerm-resourcegroup\`, I have created the following three terraform files:

1. main.tf

    ```hcl
    ##################################################
    # Terraform Config + PROVIDERS                   #
    ##################################################
    terraform {
      required_version = ">= 1.0.5"

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

    **NOTE:** If you look at the our terraform backend configuration you will notice the following: `~{terraformBackendRG}~`, `~{terraformBackendSA}~` and `~{environment}~`, we will be dynamically changing the values inside of `~{ }~` with values from our pipeline variable file later on in this tutorial using **replace tokens**.

2. variables.tf

    ```hcl
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

3. resourcegroup.auto.tfvars

    ```hcl
    resource_group_name = "Infra-~{environment}~-Rg"
    location            = "~{location}~"
    tags = {
      terraformDeployment = "true"
      Environment         = "~{environment}~"
    }
    ```

    **NOTE:** Again, if you look at the our **tfvars** configuration you will notice the following: `~{environment}~` and `~{location}~`, we will be dynamically changing the values inside of `~{ }~` with values from our pipeline variable file later on in this tutorial using **replace tokens**.

## DevOps Pipeline Variable file

Under my repo path: `\pipelines\variables`, I have created the following three yaml variable template files:

1. dev_vars.yml

    ```yml
    ```

2. uat_vars.yml

    ```yml
    ```

3. prod_vars.yml

    ```yml
    ```

**NOTE:** You will notice that my variable **names** in each yaml template are aligned with the values I used on my terraform configuration files: `~{environment}~`, `~{location}~`, `~{terraformBackendRG}~`, `~{terraformBackendSA}~`.

## DevOps Pipeline

Under my repo path: `\pipelines`, I have created the following three yaml pipelines:

1. dev_deployment.yml

    ```yml
    ```

2. uat_deployment.yml

    ```yml
    ```

3. prod_deployment.yml

    ```yml
    ```

Now we can set up each pipeline, which will consume its corresponding variable template file and use the same terraform code to dynamically deploy the same resource group but each having its own state file, name and tags.

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my [Github](https://github.com/Pwd9000-ML/blog-devto/tree/master/posts/DevOps-Replace-Tokens/code) page. :heart:

### _Author_

{% user pwd9000 %}
