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

So how can this be useful in Infrastructure as Code (IaC)?

It allows us to be more creative and granular with Terraform configurations by allowing us to create multiple configurations for different scenarios and be able to select what scenario or configuration we want to deploy. Let's take a look at a real world example of this.

## Real world example

The example code used in the following section can also be found here: [05_lookup_demo](https://github.com/Pwd9000-ML/Azure-Terraform-Deployments/tree/master/05_lookup_demo).

Say for example we have to create Azure cloud resources for multiple sites of our organization. In the following example we will use **Site A** in _UK South_ and **Site B** in _UK West_ as two separate sites for our Org.

We start off by creating a list of sites in a variable for **siteA** and **siteB**:

```hcl
## variables.tf ##

variable "site_names" {
  type        = list(string)
  default     = ["siteA", "siteB"]
  description = "Provide a list of all Contoso site names - Will be mapped to local var 'site_configs'"
}
```

Next we create a `locals` variable called `site_configs`, a `map` configuration containing child `maps` for each of the sites we want to set certain criteria against:

```hcl
## local.tf ##

locals {
  site_configs = {
    siteA = {
      resource_group_name = "Demo-Inf-SiteA-RG"
      location            = "UKSouth"
      allowed_ips         = ["8.8.8.8", "8.8.8.9"]
    },
    siteB = {
      resource_group_name = "Demo-Inf-SiteB-RG"
      location            = "UKWest"
      allowed_ips         = ["7.7.7.7", "7.7.7.8"]
    }
  }
}
```

So for our first set of resources we will deploy azure resource groups for each of our sites:

```hcl
## storage_resources.tf ##

resource "azurerm_resource_group" "RGS" {
  for_each = toset(var.site_names)
  name     = lookup(local.site_configs[each.value], "resource_group_name", null)
  location = lookup(local.site_configs[each.value], "location", null)
}
```

Notice that we are using a `for_each` loop using the list we created earlier with our site names, **siteA** and **siteB**. The `lookup()` function is then used to lookup the corresponding `key` for each site config inside of our `site_configs` locals variable map, that corresponds to **siteA** and **siteB**.

As you can see each Azure resource group was created for each site in the locations we defined in our `local` variable for _UK South_ and _UK West_:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-DevOps-Terraform-Lookup-Function/assets/rgs.png)

Next we will create a few storage accounts for each of our sites. We have a variable called `storage_config` which is a list of objects where each object represents a storage account configuration. But notice that one of the keys of each storage config/object has a `key` called `site_name`.

```hcl
## config-dev.tfvars ##

storage_config = [
  #V2 Storage - SiteA
  {
    name                      = "pwd9000v2sitea"
    account_kind              = "StorageV2"
    account_tier              = "Standard"
    account_replication_type  = "LRS"
    enable_https_traffic_only = true
    access_tier               = "Hot"
    is_hns_enabled            = false
    site_name                 = "siteA"
  },
  #ADLS2 Storage - SiteA
  {
    name                      = "pwd9000dfssitea"
    account_kind              = "BlockBlobStorage"
    account_tier              = "Premium"
    account_replication_type  = "ZRS"
    enable_https_traffic_only = true
    access_tier               = "Hot"
    is_hns_enabled            = true
    site_name                 = "siteA"
  },
  #V2 Storage - SiteB
  {
    name                      = "pwd9000v2siteb"
    account_kind              = "StorageV2"
    account_tier              = "Standard"
    account_replication_type  = "LRS"
    enable_https_traffic_only = false
    access_tier               = "Hot"
    is_hns_enabled            = false
    site_name                 = "siteB"
  }
]
```

This `site_name` corresponds with the local variable maps `key` of each of the `site_configs` maps:

```hcl
## local.tf ##

locals {
  site_configs = {
    siteA = {
      resource_group_name = "Demo-Inf-SiteA-RG"
      location            = "UKSouth"
      allowed_ips         = ["8.8.8.8", "8.8.8.9"]
    },
    siteB = {
      resource_group_name = "Demo-Inf-SiteB-RG"
      location            = "UKWest"
      allowed_ips         = ["7.7.7.7", "7.7.7.8"]
    }
  }
}
```

Notice that when we are building out the storage accounts for each of the sites we can now lookup the `network_rules` to apply to each of our storage accounts that corresponds to the allowed IPs for that site using the `lookup()` function `ip_rules = lookup(local.site_configs[each.value.site_name], "allowed_ips", null)` as shown below:

```hcl
resource "azurerm_storage_account" "SAS" {
  for_each = { for n in var.storage_config : n.name => n }

  #Implicit dependency from previous resource
  resource_group_name = azurerm_resource_group.RGS[each.value.site_name].name
  location            = azurerm_resource_group.RGS[each.value.site_name].location

  #values from variable storage_config objects
  name                      = "${lower(each.value.name)}${random_integer.sa_num.result}"
  account_kind              = each.value.account_kind
  account_tier              = each.value.account_tier
  account_replication_type  = each.value.account_replication_type
  access_tier               = each.value.access_tier
  enable_https_traffic_only = each.value.enable_https_traffic_only
  is_hns_enabled            = each.value.is_hns_enabled

  #Lookup allowed ips
  network_rules {
    default_action = "Deny"
    ip_rules       = lookup(local.site_configs[each.value.site_name], "allowed_ips", null)
  }
}

resource "random_integer" "sa_num" {
  min = 0001
  max = 9999
}
```

As you can see **Site A** storage accounts are set with allowed IPs of `allowed_ips = ["8.8.8.8", "8.8.8.9"]`.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-DevOps-Terraform-Lookup-Function/assets/sa_sitea.png)  
![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-DevOps-Terraform-Lookup-Function/assets/ip_sitea.png)

And **Site B** storage accounts are set with allowed IPs of `allowed_ips = ["7.7.7.7", "7.7.7.8"]`

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-DevOps-Terraform-Lookup-Function/assets/sa_siteb.png)  
![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-DevOps-Terraform-Lookup-Function/assets/ip_siteb.png)

I hope you have enjoyed this post and have learned something new. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
