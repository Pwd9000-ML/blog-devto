---
title: Terraform - Understanding Count and For_Each Loops
published: true
description: DevOps - Terraform - Understanding Count and For_Each Loops
tags: 'terraform, tutorial, iac, devops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/DevOps-Terraform-Loops/assets/main-tf-tips.png'
canonical_url: null
id: 1762109
series: Terraform Pro Tips
date: '2024-03-03T17:46:47Z'
---

## Overview

When working with Terraform, you may need to create multiple instances of the same resource. This is where **count** and **for_each** loops come in. These loops allow you to create multiple resources with the same configuration, but with different values. This guide will explain how to use **count** and **for_each** loops in Terraform.

## Count in Terraform

The `count` parameter in Terraform allows you to create a specified number of identical resources. It is an integral part of a resource block that defines how many instances of a particular resource should be created.

Here's an example of how to use `count` in Terraform:

```hcl
resource "azurerm_resource_group" "example" {
  count    = 3
  name     = "resourceGroup-${count.index}"
  location = "East US"
  tags = {
    iteration = "Resource Group number ${count.index}"
  }
}
```

In the example above, we create three identical resource groups in the Azure region "East US" with differing names using the `count` parameter.

## Pros:

- **Simple to use:** The `count` parameter is straightforward for creating multiple instances of a resource.
- **Suitable for homogeneous resources:** When all the resources you're creating are identical except for an identifier, `count` is likely a good fit.

## Cons:

- **Lacks key-based identification:** `count` doesn’t include a way to address a resource with a unique key directly; you have to rely on an index.
- **Immutable:** If you remove an item from the middle of the `count` list, Terraform marks all subsequent resources for recreation which can be disruptive in certain scenarios. For example: Let's say you have a Terraform configuration that manages a fleet of virtual machines in Azure using the `count` parameter. Assume that you initially set the `count` parameter to 5, which provisioned five VMs:

```hcl
resource "azurerm_virtual_machine" "vm" {
  count               = 5
  name                = "vm-${count.index}"
  location            = "East US"
  resource_group_name = azurerm_resource_group.rg.name
  network_interface_ids = [azurerm_network_interface.nic[count.index].id]
  # ... (other configuration details)
}
```

In the above example. Say After some time, you decide that you no longer need the second VM (**"vm-1"**, since **"count.index"** is zero-based). To remove this VM, you might change the `count` to `4` and adjust your resource names or indexes, which might intuitively seem like the correct approach.

The problem arises here: Terraform determines the creation and destruction of resources based on their index. If you simply remove or comment out the definition for **"vm-1"**, Terraform won't know that you specifically want to destroy **"vm-1"**. It would interpret that every VM from index 1 and onward (vm-1, vm-2, vm-3, and vm-4) should be destroyed and recreated because their indices have changed.

This could have several disruptive consequences:

- **Downtime:** Recreating VMs would lead to downtime for the services running on them, which may be unacceptable in a production environment.
- **Data Loss:** If there's local data on the VMs that you haven't backed up, it would be lost when the VMs are destroyed and recreated.
- **IP Changes:** If the VMs are assigned dynamic public IPs, these IPs would change and could cause connectivity issues.
- **Costs:** Destroying and recreating resources might incur unnecessary costs in terms of the compute hours consumed.

To avoid such issues with `count`, you'd want to use `create_before_destroy` [lifecycle rules](https://dev.to/pwd9000/terraform-understanding-the-lifecycle-block-4f6e) or consider whether `for_each` is a better choice for such a scenario because it provides a way to uniquely identify resources without relying on sequence. With `for_each`, each VM would be managed individually, and you could remove a single map entry that corresponds to the unwanted VM, leading to the destruction of only that particular VM without impacting the others.

## For_Each in Terraform

The `for_each` loop in Terraform, used within the `for_each` argument, iterates over a map or a set of strings, allowing you to create resources that correspond to the given elements.

Here's an example of how to use `for_each` in Terraform:

```hcl
resource "azurerm_resource_group" "example" {
  for_each  = toset(["rg-prod", "rg-dev", "rg-test"])
  name      = each.value
  location  = "East US"
  tags = {
    Name = each.value
  }
}

# Alternatively, using a map
resource "azurerm_storage_account" "example" {
  for_each  = {
    prod = "eastus2"
    dev  = "westus"
    test = "centralus"
  }
  name                     = "storage${each.key}"
  resource_group_name      = azurerm_resource_group.example[each.key].name
  location                 = each.value
  account_tier             = "Standard"
  account_replication_type = "GRS"
}
```

In the first example using a **set** of strings, we create resource groups with specific names: **"rg-prod"**, **"rg-dev"**, and **"rg-test"**.  
In the second example using a **map**, we create storage accounts in different locations and with associations to corresponding resource groups.

## Pros:

- **Detailed declaration:** `for_each` provides greater control when creating resources that require specific attributes or configurations.
- **Key-based identification:** Resources created with `for_each` can be directly identified and accessed by their keys, making modifications more manageable.
- **Non-destructive updates:** If you remove an item from the map or set, only that specific resource will be affected.

## Cons:

- **Complexity:** `for_each` is more complex to use than `count` and requires more planning.
- **Requires a set or map:** You must provide a set or map of items to iterate over, which might not be necessary or straightforward for all situations.

## When to Use Count vs. For_each

Both constructs are powerful, but they shine in different situations. Here's a quick reference to determine which to use:

### Use Count when:

- You need to create a fixed number of similar resources.
- Resource differences can be represented by an index.

### Use For_each when:

- You're dealing with a collection of items that have unique identifiers.
- Your resources are not perfectly identical and require individual configurations.
- You plan to make future modifications that should not affect all resources.

## Conclusion

Choosing between `count` and `for_each` largely depends on the scenario at hand. The `count` parameter is excellent for simplicity and when you're dealing with homogenous resources. Meanwhile, `for_each` is perfect for a more controlled resource declaration, offering flexibility and precision especially beneficial in complex infrastructures.

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [X/Twitter](https://x.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
