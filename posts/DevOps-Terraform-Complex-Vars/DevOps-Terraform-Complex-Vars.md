---
title: Terraform - Complex Variable Types
published: true
description: DevOps - Terraform - Complex Variable Types
tags: 'tutorial, azure, productivity, devops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/DevOps-Terraform-Complex-Vars/assets/main-tf.png'
canonical_url: null
id: 849831
date: '2021-10-03T14:55:03Z'
---

## Terraform Variables

When creating a terraform configuration, you have to configure and declare [Input Variables](https://www.terraform.io/docs/language/values/variables.html). Input variables serve as parameters for a Terraform module and resources, allowing aspects of the module to be customized without altering the module's own source code, and allowing modules to be shared between different configurations.

The Terraform language uses the following types for its values:

- `string`: a sequence of Unicode characters representing some text, like "hello".
- `number`: a numeric value. The number type can represent both whole numbers like 15 and fractional values like 6.283185.
- `bool`: a boolean value, either true or false. bool values can be used in conditional logic.
- `list` (or `tuple`): a sequence of values, like `["one", "two"]`. Elements in a list or tuple are identified by consecutive whole numbers, starting with zero.
- `map` (or `object`): a group of values identified by named labels, like `{name = "Mabel", age = 52}`.

Strings, numbers, and bools are sometimes called _primitive_ types. Lists/tuples and maps/objects are sometimes called _complex_ types, _structural_ types, or _collection_ types.

## Using Primitive Variable Types

In the following example we create a basic Azure Resource Group and we declare each resource argument with it's own separate variable using _Primitive_ types:

```hcl
#main.tf
resource "azurerm_resource_group" "demo_rg" {
  count    = var.create_rg ? 1 : 0
  name     = var.name
  location = var.location
}
```

Each variable is declared separately:

```hcl
#variables.tf
variable "create_rg" {
    type = bool
    default = false
}

variable "name" {
    type = string
    default = "Default-RG-Name"
}

variable "location" {
    type = string
    default = "uksouth"
}
```

As you can see from the above example each resource argument is declared using a _primitive_ variable type.

## Using Complex Variable Types

In the following example we create an Azure Resource Group and two storage accounts, but instead of declaring each variable individually using _primitive_ types we will use **Collections** using _complex_ types. We will create our Resource Group by using a single complex variable called `rg_config` and we will create our storage account/s using a single complex variable list of objects called `storage_config`.

As you can see from the following variable declaration, we are only declaring each resources values using a _complex_ variable type of **Object** (Resource Group config) and **List Object** (List of Storage Account configs):

```hcl
#// code/variables.tf#L1-L20
#Resource Group Config - Object
variable "rg_config" {
  type = object({
    create_rg = bool
    name      = string
    location  = string
  })
}

#Storage Account Config - List of Objects (Each object represents a storage config)
variable "storage_config" {
  type = list(object({
    name                      = string
    account_kind              = string
    account_tier              = string
    account_replication_type  = string
    access_tier               = string
    enable_https_traffic_only = bool
    min_tls_version           = string
    is_hns_enabled            = bool
  }))
}
```

**NOTE:** Because we are using variable objects we can just reference and lookup each key of the relevant object passed in to obtain the corresponding configuration value e.g. `var.config.key`:

```hcl
#// code/resources.tf#L6-L32
resource "azurerm_resource_group" "demo_rg" {
  count    = var.rg_config.create_rg ? 1 : 0
  name     = var.rg_config.name
  location = var.rg_config.location
  tags     = { Purpose = "Demo-RG", Automation = "true" }
}

resource "azurerm_storage_account" "sas" {
  count = length(var.storage_config)

  #Implicit dependency from previous resource
  resource_group_name = azurerm_resource_group.demo_rg[0].name
  location            = azurerm_resource_group.demo_rg[0].location

  #values from variable config object
  name                      = var.storage_config[count.index].name
  account_kind              = var.storage_config[count.index].account_kind
  account_tier              = var.storage_config[count.index].account_tier
  account_replication_type  = var.storage_config[count.index].account_replication_type
  access_tier               = var.storage_config[count.index].access_tier
  enable_https_traffic_only = var.storage_config[count.index].enable_https_traffic_only
  min_tls_version           = var.storage_config[count.index].min_tls_version
  is_hns_enabled            = var.storage_config[count.index].is_hns_enabled

  #Apply tags
  tags = { Purpose = "Demo-sa-${count.index + 1}", Automation = "true" }
}
```

Because we are now using a **list of objects** as the variable for storage accounts, each storage account we want to create can be configured on our **TFVARS** file as an object inside its own block, and so we can simply add additional object blocks into our **TFVARS** to build `one` or `many` storage accounts, each with different configs:

```hcl
#// code/common.auto.tfvars.tf#L1-L30
#Resource Group Config - Object Values
rg_config = {
  create_rg = true
  name      = "Demo-Terraform-RG"
  location  = "uksouth"
}

#Storage Account Configs - List of Objects Values
storage_config = [
  #Storage Account 1 (Object1): StorageV2
  {
    name                      = "pwd9000v2sa001"
    account_kind              = "StorageV2"
    account_tier              = "Standard"
    account_replication_type  = "LRS"
    min_tls_version           = "TLS1_2"
    enable_https_traffic_only = true
    access_tier               = "Cool"
    is_hns_enabled            = false
  },
  #Storage Account 2 (object2): Azure Data Lake Storage V2 (ADLS2)
  {
    name                      = "pwd9000adls2sa001"
    account_kind              = "BlockBlobStorage"
    account_tier              = "Premium"
    account_replication_type  = "ZRS"
    min_tls_version           = "TLS1_2"
    enable_https_traffic_only = false
    access_tier               = "Hot"
    is_hns_enabled            = true
  }
]
```

As you can see from the last example, using complex variable types and making our configurations more object oriented can offer much greater flexibility and granularity in terraform deployments.

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my [Github](https://github.com/Pwd9000-ML/blog-devto/tree/master/posts/DevOps-Terraform-Complex-Vars/code) page. :heart:

### _Author_

{% user pwd9000 %}

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) \ :penguin: [Twitter](https://twitter.com/pwd9000) \ :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)
