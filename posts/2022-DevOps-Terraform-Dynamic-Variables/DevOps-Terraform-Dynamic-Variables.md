---
title: Terraform - Creating dynamic variables using locals
published: false
description: DevOps - Terraform - Dynamic Variables
tags: 'terraform, azure, iac, azuredevops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-DevOps-Terraform-Dynamic-Variables/assets/main-tf-tips.png'
canonical_url: null
id: 1030720
series: Terraform Pro Tips
---

## Overview

This tutorial uses examples from the following GitHub project: [Azure Terraform Deployments](https://github.com/Pwd9000-ML/Azure-Terraform-Deployments).

In todays tutorial we will look at an interesting use case example whereby we will be creating a dynamic Terraform variable using [locals](https://www.terraform.io/language/values/locals) and a [for loop](https://www.terraform.io/language/expressions/for).

Let's take a moment to talk about the use case before going into the code. We will use Terraform to build the following:

- Resource Group
- Virtual network
- App Service Plan
- App Insights
- VNET integrated App Service
- Azure Container Registry (ACR)

Some Azure PaaS services (such an ACR) has networking features called **Firewalls and Virtual networks** which gives us the ability to configure allowed public network access where we can define **Firewall IP whitelist** rules or allow only **selected networks** access, in order to limit network connectivity to the PaaS service.

By default an ACR is public accepts connections over the internet from hosts on any network. So we will as part of the Terraform configuration block all access to the ACR and use the **Firewall IP whitelist** to only allow the outbound IPs of our VNET integrated **App service**. In addition we will also provide a list that contains **custom IP ranges** we can set which will represent the on premises public IPs of the company to also be included on the **Firewall IP whitelist** of the ACR.

**IMPORTANT:** ACR `network_rule_set_set` can only be specified for a **Premium** Sku.

Since we are building all of this with IaC using Terraform the question is how can we allow all the **possible outbound IPs** of our VNET integrated **App Service** to be whitelisted on the **ACR** if the outbound IPs of the App Service will not be known to us until the App Service is deployed?

This is where I will demonstrate how we can achieve this using **Dynamic Variables** to dynamically create the IP whitelist in Terraform using **locals**.

## App Service (VNET integrated)

In the following demo [configuration](https://github.com/Pwd9000-ML/Azure-Terraform-Deployments/tree/master/04_App_Acr). Let's take a closer look at the App service configuration and VNET integration:

### App Service resource ([appservices.tf](https://github.com/Pwd9000-ML/Azure-Terraform-Deployments/blob/master/04_App_Acr/appservices.tf))

```hcl
## appservices.tf ##
resource "azurerm_app_service" "APPSVC" {
  name                = var.appsvc_name
  location            = azurerm_resource_group.RG.location
  resource_group_name = azurerm_resource_group.RG.name
  app_service_plan_id = azurerm_app_service_plan.ASP.id
  https_only          = true

  identity {
    type = "SystemAssigned"
  }

  site_config {
    acr_use_managed_identity_credentials = true
    ftps_state                           = "FtpsOnly"
    linux_fx_version                     = var.asp_kind == "linux" ? local.linux_fx_version : null
    vnet_route_all_enabled               = var.vnet_route_all_enabled
  }

  app_settings = lookup(local.app_settings, "linux_app_settings", null)
}
```

### VNET integration resource ([appservices.tf](https://github.com/Pwd9000-ML/Azure-Terraform-Deployments/blob/master/04_App_Acr/appservices.tf))

**NOTE:** Outbound IPs will only become available once the VNET integration resource has been created.

```hcl
## appservice.tf ##
resource "azurerm_app_service_virtual_network_swift_connection" "azure_vnet_connection" {
  count          = var.vnet_integ_required == true ? 1 : 0
  app_service_id = azurerm_app_service.APPSVC.id
  subnet_id      = azurerm_subnet.SUBNETS["App-Service-Integration-Subnet"].id
}
```

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-DevOps-Terraform-Dynamic-Variables/assets/vint.png)

### Azure Container Registry (ACR) resource ([acr.tf](https://github.com/Pwd9000-ML/Azure-Terraform-Deployments/blob/master/04_App_Acr/acr.tf))

```hcl
## acr.tf ##
resource "azurerm_container_registry" "ACR" {
  name                = var.acr_name
  location            = azurerm_resource_group.RG.location
  resource_group_name = azurerm_resource_group.RG.name
  sku                 = var.acr_sku
  admin_enabled       = var.acr_admin_enabled

  dynamic "identity" {
    for_each = var.acr_requires_identity == true ? [1] : []
    content {
      type = "SystemAssigned"
    }
  }

  dynamic "georeplications" {
    for_each = var.acr_sku == "Premium" ? var.acr_georeplications_configuration : []
    content {
      location                = georeplications.value.location
      zone_redundancy_enabled = georeplications.value.zone_redundancy_enabled
    }
  }

  ## Need Premium SKU to use the following config ##
  dynamic "network_rule_set" {
    for_each = local.acr_fw_rules != null ? local.acr_fw_rules : []
    content {
      default_action = network_rule_set.value.default_action
      dynamic "ip_rule" {
        for_each = network_rule_set.value["ip_rules"] != [] ? network_rule_set.value["ip_rules"] : []
        content {
          action   = ip_rule.value["action"]
          ip_range = ip_rule.value["ip_range"]
        }
      }

      dynamic "virtual_network" {
        for_each = network_rule_set.value["virtual_network_subnets"] != [] ? network_rule_set.value["virtual_network_subnets"] : []
        content {
          action    = virtual_network.value["action"]
          subnet_id = virtual_network.value["subnet_id"]
        }
      }
    }
  }

}
```

As you can see from the above resource block that is building out the ACR notice the dynamic block called `network_rule_set`:

```hcl
## acr.tf ##
## Need Premium SKU to use the following config ##
dynamic "network_rule_set" {
  for_each = local.acr_fw_rules != null ? local.acr_fw_rules : []
  content {
    default_action = network_rule_set.value.default_action
    dynamic "ip_rule" {
      for_each = network_rule_set.value["ip_rules"] != [] ? network_rule_set.value["ip_rules"] : []
      content {
        action   = ip_rule.value["action"]
        ip_range = ip_rule.value["ip_range"]
      }
    }

    dynamic "virtual_network" {
      for_each = network_rule_set.value["virtual_network_subnets"] != [] ? network_rule_set.value["virtual_network_subnets"] : []
      content {
        action    = virtual_network.value["action"]
        subnet_id = virtual_network.value["subnet_id"]
      }
    }
  }
}
```

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my [Github](https://github.com/Pwd9000-ML/Azure-Terraform-Deployments/tree/master/04_App_Acr) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
