---
title: Terraform - Understanding Dynamic Blocks
published: false
description: DevOps - Terraform - Understanding Dynamic Blocks
tags: 'terraform, azure, iac, devops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/DevOps-Terraform-Dynamic-Block/assets/main-tf-tips.png'
canonical_url: null
id: 1744700
series: Terraform Pro Tips
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

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
