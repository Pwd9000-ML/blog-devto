---
title: Terraform - Filter results using 'for' loops
published: false
description: DevOps - Terraform - Filter with 'for'
tags: 'terraform, azure, iac, azuredevops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-DevOps-Terraform-Filter-With-For/assets/main-tf-tips.png'
canonical_url: null
id: 1044248
series: Terraform Pro Tips
---

## Overview

In todays tutorial we will take a look at a fairly common question I often get from the community and it is around how to filter results in Terraform or even if it is possible. We will also look at a real world usage example so that we can see how and when we would use filters in Terraform.

**Filtering** in Terraform can be achieved using [for loop](https://www.terraform.io/language/expressions/for) expressions. Though `for` loop constructs in terraform performs looping, it can also be used for manipulating data structures such as the following to name a few:

- **Transform:** Changing the data structure.
- **Filter:** Filter only on desired items in combination with an `if` expression.
- **Group:** Group elements together in a new `list` by key.

## Filtering results

Let's take a look at the following example variable where we have a list of applications:

```hcl
variable "apps" {
  type = list(object({
    app_name            = string
    app_kind            = string
    app_require_feature = bool
  }))
  default = [
    {
      app_name            = "App1"
      app_kind            = "Linux"
      app_require_feature = false
    },
    {
      app_name            = "App2"
      app_kind            = "Linux"
      app_require_feature = false
    },
    {
      app_name            = "App3"
      app_kind            = "Windows"
      app_require_feature = true
    },
    {
      app_name            = "App4"
      app_kind            = "Windows"
      app_require_feature = false
    }
  ]
}
```

Say you want to filter only on `app_require_feature = true` you could write a `for` loop with an `if` expression like in the following local variable:

```hcl
locals {
  apps_that_require_feature = toset([for each in var.apps : each.app_name if each.app_require_feature == true])
}

output "result" {
  value = local.apps_that_require_feature
}
```

This will return a set of `app_names` that have the objects key `"app_require_feature"` set to `true`

```sh
$ terraform apply
Outputs:

result = ["App3"]
```

So let's say you want to filter the same variable but this time you want to only see the apps that are `windows`, you could write a `for` loop with an `if` expression like in the following local variable:

```hcl
locals {
  windows_apps = toset([for each in var.apps : each.app_name if each.app_kind == "windows"])
}

output "result2" {
  value = local.windows_apps
}
```

This will return a set of `app_names` that have the objects key `"app_kind"` set to `"windows"`

```sh
$ terraform apply
Outputs:

result2 = ["App3", "App4"]
```

## Real world example

Let's take a real world usage case where we would need such a `for` construct to filter and only configure something based on certain criteria.

Say we have a variable with three `storage accounts` we want to create, but we only want to configure `private endpoints` on certain storage accounts. We could create an extra object `key` item called `requires_private_endpoint` like in the following example:

````hcl
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
    #V2 Storage without private endpoint
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
    #V2 Storage with private endpoint
    {
      name                      = "pwd9000v2sa002"
      account_kind              = "StorageV2"
      account_tier              = "Standard"
      account_replication_type  = "LRS"
      enable_https_traffic_only = true
      access_tier               = "Cool"
      is_hns_enabled            = false
      requires_private_endpoint = true
    },
    #ADLS2 Storage with private endpoint
    {
      name                      = "pwd9000adls2sa001"
      account_kind              = "BlockBlobStorage"
      account_tier              = "Premium"
      account_replication_type  = "ZRS"
      enable_https_traffic_only = false
      access_tier               = "Hot"
      is_hns_enabled            = true
      requires_private_endpoint = true
    }
  ]
}
```

We can then create all three storage accounts with the following resource config:

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
````

In the following resource block we can now configure private endpoints, but we will only do so for storage accounts that have an object `key` of `requires_private_endpoint` set to `true` like in the following resource config:

```hcl
## private endpoint resources ##

resource "azurerm_private_endpoint" "SASPE" {
  for_each            = toset([for pe in var.storage_config : pe.name if pe.requires_private_endpoint == true])
  name                = "${each.value.name}-pe"
  location            = azurerm_resource_group.RG.location
  resource_group_name = azurerm_resource_group.RG.name
  subnet_id           = data.azurerm_subnet.data_subnet.id

  private_service_connection {
    name                           = "${each.value.name}-pe-sc"
    private_connection_resource_id = azurerm_storage_account.SAS[each.value.name].id
    is_manual_connection           = false
  }
```

If you take a closer look at the `for_each` in the `azurerm_private_endpoint` resource we are using the filter there as follow: `for_each = toset([for pe in var.storage_config : pe.name if pe.requires_private_endpoint == true])`.  

Thus we can then use selected list(object)/storage config keys as shown by the `each.value.xxxx` config to specify the values used to create private endpoints for selected storage accounts only.

I hope you have enjoyed this post and have learned something new. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
