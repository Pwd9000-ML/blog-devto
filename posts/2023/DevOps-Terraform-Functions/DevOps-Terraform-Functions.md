---
title: Terraform - Fun with Functions
published: false
description: DevOps - Terraform - Fun with Terraform Functions
tags: 'terraform, azure, iac, devops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/DevOps-Terraform-Functions/assets/main-tf-tips.png'
canonical_url: null
id: 1323886
series: Terraform Pro Tips
---

## Overview

In todays tutorial we will take a look at [Terraform functions](https://developer.hashicorp.com/terraform/language/functions) and how we can use them in a few real world examples, and boy are there many functions to get creative and have fun with.

But what are they?  
When writing **Infrastructure as Code**, you may come across certain complexities or maybe you want to improve or simplify your code by using **Terraform functions**. You can even use functions to guardrail and safeguard your code from platform related limitations. (For example character limitations or case sensitivity when building certain resources in a cloud provider like **Azure**).

Functions are expressions to transform and combine values in order to manipulate these values to be used in other ways. Functions can also be nested within each other.

Most **Terraform functions** follow a common syntax, for example:

```hcl
<FUNCTION NAME>(<ARGUMENT 1>, <ARGUMENT 2>)
```

## Example

**NOTE:** You can use `terraform console` in a command prompt to run any of the function examples shown later, or to test your own function logic.

Say for example you want to provision an **Azure storage account** using **Terraform**. As you may know, storage account names in **Azure** have certain [name rules and character limitations](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/resource-name-rules).  
The **length** of a storage account name must be between **3-24** characters, and can only be **lowercase letters and numbers**.

Take this example of provisioning a storage account in **Azure**:

```hcl
variable "storage_account_name" {
  type        = string
  description = "Specifies Storage account name"
  default     = "MySuperCoolStorageAccountName9000"
}

resource "azurerm_storage_account" "example" {
  name                     = var.storage_account_name
  resource_group_name      = "MyRgName9000"
  location                 = "uksouth"
  account_tier             = "Standard"
  account_replication_type = "LRS"
}
```

As you can see from the above example the storage account name provided by the **default** value in the variable **'storage_account_name'** is: `'MySuperCoolStorageAccountName9000'`

Because of the [provider limitations](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/resource-name-rules), if the **default** value is used in the deployment, this resource creation would fail.

So how can we safeguard that the default value, or any value that is provided will always work?  
You guessed it, we can use **Terraform functions**.

So we will use two functions namely, **['substr'](https://developer.hashicorp.com/terraform/language/functions/substr)** and **['lower'](https://developer.hashicorp.com/terraform/language/functions/substr)**:

Lets look at each function:

- `substr` extracts a substring from a given string by offset and (maximum) length. Usage: `substr(string, offset, length)`
- `lower` converts all cased letters in the given string to lowercase. Usage: `lower(string)`

So lets test this using terraform console:

```hcl
$ substr("MySuperCoolStorageAccountName9000", 0, 24)
"MySuperCoolStorageAccoun"
```

The result **'MySuperCoolStorageAccoun'** has now been truncated to only **24 characters**, but this would still fail because there are still **uppercase characters** present. Let's nest this inside the **'lower'** function:

```hcl
$ lower(substr("MySuperCoolStorageAccountName9000", 0, 24))
"mysupercoolstorageaccoun"
```

This is much better! The storage account will now be provisioned by simply amending our original terraform code as follow:

```hcl
variable "storage_account_name" {
  type        = string
  description = "Specifies Storage account name"
  default     = "MySuperCoolStorageAccountName9000"
}

resource "azurerm_storage_account" "example" {
  name                     = lower(substr(var.storage_account_name, 0, 24))
  resource_group_name      = "MyRgName9000"
  location                 = "uksouth"
  account_tier             = "Standard"
  account_replication_type = "LRS"
}
```

But what if we want to improve this even more, by making the value always work, but always be **unique** as well?  
Maybe we can shorten the name a bit more using **'subsr'** and then add a unique random string?  
As you thought, yes we can!!!

Let's look at another special function called **['uuid'](https://developer.hashicorp.com/terraform/language/functions/uuid)**:

- `uuid` generates a unique identifier string. Usage: `uuid()`

So lets test this using terraform console:

```hcl
$ uuid()
"908b8d83-f33e-aa2e-7318-8232077dfe10"
```

Firstly, let's shorten our storage account name down to **18 characters**:

```hcl
$ lower(substr("MySuperCoolStorageAccountName9000", 0, 18))
"mysupercoolstorage"
```

Then we care left with **6 characters** that we can generate a random identifier string, that would act as a **suffix**, we can combine the **'uuid'** function with the **'substr'** function to get the following result:

```hcl
$ substr(uuid(), 0, 6)
"e807be"
```

Now, you may be wondering?, how can we combine our original function: `lower(substr("MySuperCoolStorageAccountName9000", 0, 18))` with the unique suffix: `substr(uuid(), 0, 6)`?

You guessed it, there is a function we can use!!!

Let's look at the function called **['join'](https://developer.hashicorp.com/terraform/language/functions/join)**:

- `join` produces a string by concatenating together all elements of a given **list** of strings with the given delimiter. Usage: `join(separator, list)`

So as a basic example join can combine two strings in the following way:

```hcl
$ join("", ["StringA", "StringB"])
"StringAStringB"
```

Let's now apply this now to our storage account name and unique suffix:

```hcl
$ join("", [lower(substr("MySuperCoolStorageAccountName9000", 0, 18)), substr(uuid(), 0, 6)])
"mysupercoolstoraged29fc5"
```

Viola! We now have a randomly generated storage account name, that will always be unique and not be limited to character and case limitations for our storage account/s.

Let's run this function a few times to see the results:

```hcl
$ join("", [lower(substr("MySuperCoolStorageAccountName9000", 0, 18)), substr(uuid(), 0, 6)])
"mysupercoolstoraged29fc5"

$ join("", [lower(substr("MySuperCoolStorageAccountName9000", 0, 18)), substr(uuid(), 0, 6)])
"mysupercoolstorage3b39e2"

$ join("", [lower(substr("MySuperCoolStorageAccountName9000", 0, 18)), substr(uuid(), 0, 6)])
"mysupercoolstoragefe9d25"

$ join("", [lower(substr("MySuperCoolStorageAccountName9000", 0, 18)), substr(uuid(), 0, 6)])
"mysupercoolstorage716b99"
```

Lastly, let's apply this to our original code:

```hcl
variable "storage_account_name" {
  type        = string
  description = "Specifies Storage account name"
  default     = "MySuperCoolStorageAccountName9000"
}

resource "azurerm_storage_account" "example" {
  name                     = join("", [lower(substr(var.storage_account_name, 0, 18)), substr(uuid(), 0, 6)])
  resource_group_name      = "MyRgName9000"
  location                 = "uksouth"
  account_tier             = "Standard"
  account_replication_type = "LRS"
}
```

## Bonus example

If you are used to provisioning resources in the cloud on **Azure** you'll know that each resource has a resource ID.  
Here is a fun little function that I have used in the past to get the last element of any resource ID, usually the name of the resource, without fail:

```hcl
#Basic Example
$ element(split("/", "/x/y/z"), length(split("/", "/x/y/z"))-1)
"z"

#Resource Group name based of resource ID
$ element(split("/", "/subscriptions/829efd7e-aa80-4c0d-9c1c-7aa2557f8e07/resourceGroups/MSDO-Lab-ADO"), length(split("/", "/subscriptions/829efd7e-aa80-4c0d-9c1c-7aa2557f8e07/resourceGroups/MSDO-Lab-ADO"))-1)
"MSDO-Lab-ADO"

#VNET name based of resource ID
$ element(split("/", "/subscriptions/829efd7e-aa80-4c0d-9c1c-7aa2557f8e07/resourceGroups/Pwd9000-EB-Network/providers/Microsoft.Network/virtualNetworks/UKS-EB-VNET"), length(split("/", "/subscriptions/829efd7e-aa80-4c0d-9c1c-7aa2557f8e07/resourceGroups/Pwd9000-EB-Network/providers/Microsoft.Network/virtualNetworks/UKS-EB-VNET"))-1)
"UKS-EB-VNET"
```

Lets take a closer look at the functions in use here and how we combine and nest them.

## Conclusion

As mentioned there are so many cool **Terraform functions** out there to make your code even better and more robust!  
Go check out the [official documentation](https://developer.hashicorp.com/terraform/language/functions) for more details.

I hope you have enjoyed this post and have learned something new. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
