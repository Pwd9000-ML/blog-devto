---
title: Terraform - Selective configuration with 'lookup()'
published: false
description: DevOps - Terraform - Selective configuration with 'lookup()'
tags: 'terraform, azure, iac, azuredevops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-DevOps-Terraform-Lookup-Function/assets/main-tf-tips.png'
canonical_url: null
id: 1050533
series: Terraform Pro Tips
---

## Overview

This tutorial uses examples from the following GitHub project: [Azure Terraform Deployments](https://github.com/Pwd9000-ML/Azure-Terraform-Deployments).  

In todays tutorial we will take a look at an interesting Terraform function called [lookup()](https://www.terraform.io/language/functions/lookup).  

The `lookup()` function can be used to lookup a particular value inside of a `map`, given its `key` and if the given key does not exist, the given `default` value is returned instead:  

```hcl
lookup(map, key, default)
```

### Example

```sh
$ lookup({a="hello", b="world"}, "a", "what?")
"hello"

$ lookup({a="hello", b="world"}, "b", "what?")
"world"

$ lookup({a="hello", b="world"}, "c", "what?")
"what?"
```

So how can this be useful in Infrastructure As Code (IaC)?  

Well this allows us to be more creative and granular with Terraform configurations by allowing us to create multiple configurations for different scenarios and be able to select what scenario or configuration we want to deploy. Let's take a look at a real world example.  

## Real world example

Say for example we have to create Azure cloud resources for multiple sites of our organization. In the following example we will use **Site A** and **Site B** as two separate sites for our Org.


###################
Say we have a variable with four `storage accounts` we want to create, but we only want to configure `private endpoints` on certain storage accounts. We could create an extra object `key` item called `requires_private_endpoint` like in the following example:

```hcl
## variables ##

variable "storage_config" {
  type = list(object({
    name                      = string
    account_kind              = string
    account_tier              = string
    account_replication_type  = string
    access_tier               = string
    enable_https_traffic_only = bool
    is_hns_enabled            = bool
    requires_private_endpoint = bool
  }))
  default = [
    #V2 Storage (hot) without private endpoint
    {
      name                      = "pwd9000v2sa001"
      account_kind              = "StorageV2"
      account_tier              = "Standard"
      account_replication_type  = "LRS"
      enable_https_traffic_only = true
      access_tier               = "Hot"
      is_hns_enabled            = false
      requires_private_endpoint = false
    },
    #V2 Storage (cool) without private endpoint
    {
      name                      = "pwd9000v2sa002"
      account_kind              = "StorageV2"
      account_tier              = "Standard"
      account_replication_type  = "LRS"
      enable_https_traffic_only = true
      access_tier               = "Cool"
      is_hns_enabled            = false
      requires_private_endpoint = false
    },
    #ADLS2 Storage with private endpoint enabled
    {
      name                      = "pwd9000adls2sa001"
      account_kind              = "BlockBlobStorage"
      account_tier              = "Premium"
      account_replication_type  = "ZRS"
      enable_https_traffic_only = false
      access_tier               = "Hot"
      is_hns_enabled            = true
      requires_private_endpoint = true
    },
    #ADLS2 Storage without private endpoint
    {
      name                      = "pwd9000adls2sa002"
      account_kind              = "BlockBlobStorage"
      account_tier              = "Premium"
      account_replication_type  = "ZRS"
      enable_https_traffic_only = false
      access_tier               = "Hot"
      is_hns_enabled            = true
      requires_private_endpoint = false
    }
  ]
}
```

We can then create all four storage accounts with the following resource config:

```hcl
## storage resources ##

resource "azurerm_resource_group" "RG" {
  name     = "example-resources"
  location = "uksouth"
}

resource "azurerm_storage_account" "SAS" {
  for_each = { for n in var.storage_config : n.name => n }

  #Implicit dependency from previous resource
  resource_group_name = azurerm_resource_group.RG.name
  location            = azurerm_resource_group.RG.location

  #values from variable storage_config objects
  name                      = each.value.name
  account_kind              = each.value.account_kind
  account_tier              = each.value.account_tier
  account_replication_type  = each.value.account_replication_type
  access_tier               = each.value.access_tier
  enable_https_traffic_only = each.value.enable_https_traffic_only
  is_hns_enabled            = each.value.is_hns_enabled
}
```

In the following resource block we can now configure private endpoints, but we will only do so for storage accounts that have an object `"key"` of `"requires_private_endpoint"` set to `"true"` like in the following resource config:

```hcl
## private endpoint resources ##

resource "azurerm_private_endpoint" "SASPE" {
  for_each            = toset([for pe in var.storage_config : pe.name if pe.requires_private_endpoint == true])
  name                = "${each.value}-pe"
  location            = azurerm_resource_group.RG.location
  resource_group_name = azurerm_resource_group.RG.name
  subnet_id           = data.azurerm_subnet.data_subnet.id

  private_service_connection {
    name                           = "${each.value}-pe-sc"
    private_connection_resource_id = azurerm_storage_account.SAS[each.value].id
    is_manual_connection           = false
    subresource_names              = ["dfs"]
  }
}
```

If you take a closer look at the `for_each` in the `azurerm_private_endpoint` resource we are using the filter there as follow:

`for_each = toset([for pe in var.storage_config : pe.name if pe.requires_private_endpoint == true])`

This `for` loop will filter and return a set of storage account names that we can use to loop the resource creation of the private endpoints for the selected storage accounts. The storage account name values will be represented by `each.value` that matches the filter: `requires_private_endpoint == true`.

So in the example above, all four storage accounts will be created:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-DevOps-Terraform-Filter-With-For/assets/storage.png)

But only one storage account was configured to have private endpoints enabled, namely storage account: `pwd9000adls2sa001`

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-DevOps-Terraform-Filter-With-For/assets/pe.png)

I hope you have enjoyed this post and have learned something new. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
