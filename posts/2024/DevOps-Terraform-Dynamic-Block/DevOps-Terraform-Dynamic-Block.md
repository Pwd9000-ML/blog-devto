---
title: Terraform - Understanding Dynamic Blocks
published: true
description: 'Learn how to use Terraform dynamic blocks to generate repeatable nested configurations, with practical Azure examples and real-world use cases.'
tags: 'terraform, azure, tutorial, devops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/DevOps-Terraform-Dynamic-Block/assets/main-tf-tips.png'
canonical_url: null
id: 1744700
series: Terraform Pro Tips
date: '2024-01-29T15:54:00Z'
---

## Overview

In the complex world of infrastructure management, simplicity and reusability are key to maintaining sanity. This is where Terraform shines, offering a suite of advanced syntax and features to streamline the way you define and deploy resources in the cloud.

Today, we focus on **dynamic blocks** - a powerful feature that introduces greater flexibility and dynamism into your Terraform configurations. I'll walk you through various scenarios and show you how dynamic blocks can make a substantial difference in managing Azure resources and we will also look at a few real world uses cases and scenarios with a few examples using the **AzureRM provider**.

## Understanding Dynamic Blocks

Dynamic blocks let you generate nested block configurations within resources or data structures dynamically. They are particularly useful when the configuration of a resource involves repeated nested blocks whose number and content may vary based on input variables or external data.

In Terraform, a dynamic block consists of two parts: the `dynamic` keyword followed by the name of the nested block, and a `content` block that defines the structure of the dynamic block. Inside this `content` block, you reference iterator objects to assign values:

```hcl
resource "provider_resource" "example" {

  argument = "value"
  # ... other arguments ...

  dynamic "argument_block_name" {
    for_each = var.collection # or expression
    content {
      # Block content
    }

  }
}
```

## Scenario 1: Azure Network Security Group with Variable Rules

Imagine you need to create a network security group in Azure with a varying number of security rules that can change over time. Instead of hardcoding each rule, you can use a `dynamic block` to generate these rules from a variable:

```hcl
variable "security_rules" {
  description = "A list of security rules"
  type = list(object({
    name                     = string
    priority                 = number
    direction                = string
    access                   = string
    protocol                 = string
    source_port_range        = string
    destination_port_range   = string
    source_address_prefix    = string
    destination_address_prefix = string
  }))
  default = [
    {
      name                     = "allow-ssh"
      priority                 = 100
      direction                = "Inbound"
      access                   = "Allow"
      protocol                 = "Tcp"
      source_port_range        = "*"
      destination_port_range   = "22"
      source_address_prefix    = "*"
      destination_address_prefix = "VirtualNetwork"
    },
    // ... more rules ...
  ]
}

resource "azurerm_network_security_group" "example" {
  name                = "example-nsg"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name

  dynamic "security_rule" {
    for_each = var.security_rules

    content {
      name                       = security_rule.value.name
      priority                   = security_rule.value.priority
      direction                  = security_rule.value.direction
      access                     = security_rule.value.access
      protocol                   = security_rule.value.protocol
      source_port_range          = security_rule.value.source_port_range
      destination_port_range     = security_rule.value.destination_port_range
      source_address_prefix      = security_rule.value.source_address_prefix
      destination_address_prefix = security_rule.value.destination_address_prefix
    }
  }
}
```

In this scenario, dynamic blocks iterate over the `var.security_rules` list object, creating security rules based on its content. This dynamic approach keeps your code DRY (Don't Repeat Yourself) by avoiding repetitive block definitions.

## Scenario 2: Tagging Azure Resources Dynamically

Tagging resources is critical for cost tracking, compliance, and management. However, not every resource may share the same set of tags. Using dynamic blocks can conditionally add tags based on the context.

```hcl
variable "common_tags" {
  type = map(string)
  default = {
    Environment = "Development"
    Owner       = "Infrastructure Team"
  }
}

variable "extra_tags" {
  type = map(string)
  default = {
    Project = "Phoenix"
    Tier    = "Backend"
  }
}

resource "azurerm_resource_group" "example" {
  name     = "example-resources"
  location = "West Europe"

  dynamic "tag" {
    for_each = merge(var.common_tags, var.extra_tags)

    content {
      key   = tag.key
      value = tag.value
    }
  }
}
```

In this example, the resource group is tagged with a **merged** set of common and extra tags. Using dynamic blocks, you can easily combine these tags and apply them flexibly without having to declare each tag separately, simplifying the management of resource metadata. As you can see in the example, the `for_each` expression uses a `merge` function that combines the two maps into a single map.

## Scenario 3: Conditional DNS Zone Groups with Private Endpoint

Let's take a look at a few more advanced scenarios using conditions and expressions. In this example, we will create a private DNS zone group with a private endpoint.

```hcl
variable "private_dns_zone_group" {
  type = list(object({
    enabled              = bool
    name                 = string
    private_dns_zone_ids = list(string)
  }))
  default = [
    {
      enabled              = true
      name                 = "privatelink.vaultcore.azure.net"
      private_dns_zone_ids = [<DNS ZONE ID>]
    }
  ]
  description = "List of private dns zone groups to associate with the private endpoint."
}

resource "azurerm_private_endpoint" "private_endpoint" {

  # ... other arguments ...

  dynamic "private_dns_zone_group" {
    for_each = [for each in var.private_dns_zone_group :
      {
        name                 = each.name
        private_dns_zone_ids = each.private_dns_zone_ids
        enabled              = each.enabled
      } if each.enabled == true
    ]
    content {
      name                 = private_dns_zone_group.value.name
      private_dns_zone_ids = private_dns_zone_group.value.private_dns_zone_ids
    }
  }
}
```

In this example, the `for_each` argument is used to iterate over the `var.private_dns_zone_group` list. For each item in the list, it creates a new map with `name`, `private_dns_zone_ids`, and `enabled` keys if `enabled` is `true`.

The `content` block then uses these values to create a new `private_dns_zone_group` block for each item in the `for_each` list. The `private_dns_zone_group.value.name` and `private_dns_zone_group.value.private_dns_zone_ids` expressions refer to the current item in the `for_each` list.

This dynamic block allows us to create a flexible number of `private_dns_zone_group` blocks based on the input variable, which can be incredibly useful when dealing with complex infrastructure setups.

## Scenario 4: Conditional Azure Virtual Network Subnets

Suppose you are managing an Azure Virtual Network that needs to support multiple subnets. Each subnet has specific requirements and might only be necessary under certain conditions. This could be driven by environment types, features toggling, or specific compliance needs.

Here's how you can use dynamic blocks with a condition to selectively create subnets:

```hcl
variable "subnets" {
  description = "A map of subnets with their properties and a creation condition"
  type = map(object({
    address_prefixes = list(string)
    create_subnet    = bool
  }))
  default = {
    subnet1 = {
      address_prefixes = ["10.0.1.0/24"]
      create_subnet    = true
    },
    subnet2 = {
      address_prefixes = ["10.0.2.0/24"]
      create_subnet    = false // This can be driven by your specific conditions
    }
    // ...other subnets...
  }
}

resource "azurerm_virtual_network" "example" {
  name                = "example-network"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name

  dynamic "subnet" {
    # We are using the for each to iterate only over subnets that should be created.
    for_each = {
      for s_name, s_details in var.subnets : s_name => s_details
      if s_details.create_subnet
    }

    content {
      name           = subnet.key
      address_prefix = subnet.value.address_prefixes[0]
      // It’s common for the first item of the address_prefixes to be used,
      // or integrate further logic to handle multiple prefixes.
    }
  }
}
```

In this example, the `for_each` expression has been augmented with a conditional. The iteration now only includes subnet configurations where the `create_subnet` attribute is set to `true`. As a result, despite the `var.subnets` variable containing multiple definitions, only those explicitly marked for creation are acted upon - `subnet1` in this case, while `subnet2` is ignored.

Using this pattern, you can fine-tune your Terraform configurations to respond dynamically not just to the contents of variables, but also to the logical conditions your infrastructure setup may require.

## Conclusion

**Dynamic blocks** enhanced with **conditional logic** are among Terraform's most potent features for crafting maintainable and adaptable **Infrastructure as Code** in **Azure**. Leveraging the power of dynamic blocks with conditions gives you the ability to construct intricate IaC configurations that are both powerful and elegant. By carefully combining these advanced **Terraform** features, your Azure templates will become more modular, less error-prone, and far easier to extend as your Azure landscapes evolve.

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [X](https://x.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-pwd9000/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
