---
title: Terraform - Understanding Implicit and Explicit Dependencies
published: false
description: DevOps - Terraform - Understanding Implicit and Explicit Dependencies
tags: 'terraform, azure, iac, devops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/DevOps-Terraform-Implicit-Explicit-Dependency/assets/main-tf-tips.png'
canonical_url: null
id: 1761018
series: Terraform Pro Tips
---

## Overview

When working with Terraform, it is important to understand the difference between **implicit** and **explicit** dependencies. This is important as it can help you to understand how Terraform creates the **dependency graph** and how it determines the order in which resources are created.  

## What Are Dependencies in Terraform?

Dependencies in Terraform dictate the order in which resources are created, updated, or destroyed. Terraform automatically determines dependencies between your resources, ensuring that they are managed in the correct sequence.  

## Implicit Dependencies

Implicit dependencies are automatically discovered by Terraform by analysing resource attributes. When one resource refers to another using interpolation syntax, Terraform recognises this as a dependency.  

In other words, implicit dependencies in Terraform are created when one resource property references another resource's property or output. Terraform uses these references to automatically determine the order of resource creation.  

Consider this example involving an Azure virtual network and a subnet:  

```hcl
resource "azurerm_resource_group" "example" {
  name     = "example-resources"
  location = "East US"
}

resource "azurerm_virtual_network" "example_vnet" {
  name                = "example-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
}

resource "azurerm_subnet" "example_subnet" {
  name                 = "example-subnet"
  resource_group_name  = azurerm_resource_group.example.name
  virtual_network_name = azurerm_virtual_network.example_vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}
```

In this example, the `azurerm_subnet` resource has an implicit dependency on the `azurerm_virtual_network` resource. This is because the `virtual_network_name` property of the `azurerm_subnet` resource references the `name` property of the `azurerm_virtual_network` resource. Terraform automatically recognises this and creates the dependency.  

## Explicit Dependencies

Sometimes, however, the relationship between resources is not captured by direct references. In these instances, you can use the `depends_on` attribute to create an explicit dependency.  

Explicit dependencies should only be defined when Terraform can't automatically infer the required order for resource creation, or when specific provisioning steps are necessary before or after a resource is deployed.

Let's illustrate an explicit dependency in a scenario where an Azure App Service depends on certain configuration settings that are applied via an Azure CLI script after the creation of an Azure Key Vault.  

Here's a simple Terraform configuration demonstrating this relationship:  

```hcl
resource "azurerm_resource_group" "example_rg" {
  name     = "example-resources"
  location = "West Europe"
}

resource "azurerm_key_vault" "example_kv" {
  name                        = "exampleKeyVault"
  location                    = azurerm_resource_group.example_rg.location
  resource_group_name         = azurerm_resource_group.example_rg.name
  tenant_id                   = "00000000-0000-0000-0000-000000000000"
  sku_name                    = "standard"

  soft_delete_enabled         = true
  purge_protection_enabled    = false
}

resource "null_resource" "example_kv_settings" {
  # Dummy example of an Azure CLI script command that sets configuration in the Key Vault
  provisioner "local-exec" {
    command = "echo Configuring Key Vault Settings"
  }

  # Explicitly state that the Key Vault settings should be applied after the Key Vault is created
  depends_on = [ azurerm_key_vault.example_kv ]
}

resource "azurerm_app_service" "example_app_service" {
  name                = "example-appservice"
  location            = azurerm_resource_group.example_rg.location
  resource_group_name = azurerm_resource_group.example_rg.name
  app_service_plan_id = azurerm_app_service_plan.example_asp.id

  # Explicitly state the dependency on the Key Vault settings to ensure these are set before creating the App Service
  depends_on = [ null_resource.example_kv_settings ]
}

resource "azurerm_app_service_plan" "example_asp" {
  name                = "example-asp"
  location            = azurerm_resource_group.example_rg.location
  resource_group_name = azurerm_resource_group.example_rg.name

  sku {
    tier = "Standard"
    size = "S1"
  }
}
```

In the above example:

1. `azurerm_resource_group.example_rg` creates a resource group.
2. `azurerm_key_vault.example_kv` creates the Azure Key Vault.
3. `null_resource.example_kv_settings` represents a hypothetical Azure CLI script that configures settings in the Key Vault (replaced with an echo command for simplicity). The `depends_on` ensures the Key Vault is in place before the configuration script runs.
4. `azurerm_app_service_plan.example_asp` sets up the required App Service Plan.
5. `azurerm_app_service.example_app_service` creates the App Service with a `depends_on` pointing to `null_resource.example_kv_settings`. This explicit dependency ensures that the App Service is only provisioned after the Key Vault settings have been applied by the script.

By using `depends_on`, we establish an explicit dependency chain: Resource Group -> Key Vault -> Key Vault Settings -> App Service. This ensures the resources are provisioned in the correct order, even though the dependencies aren't apparent from the resource attributes alone.  

## When to Use Implicit vs. Explicit Dependencies

Implicit dependencies should be your first go-to in Terraform since they are automatically detected, and Terraform handles the ordering for you. However, there are cases when Terraform cannot discern the right order, or you have custom steps in your provisioning process which can warrant the use of explicit dependencies with the `depends_on` attribute.  

To minimise potential issues:  

- Rely mostly on implicit dependencies through resource attribute references.
- Only use explicit dependencies when necessary, and keep them to a minimum to avoid tightly coupled architecture.
- Always document why an explicit dependency is required to help other developers understand the rationale behind it.

## Conclusion

Grasping the concept of implicit and explicit dependencies and applying that knowledge to Azure resources with Terraform will lead to smoother deployments and a more robust infrastructure.  

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
