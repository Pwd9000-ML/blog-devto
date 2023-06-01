---
title: Terraform - Understanding the Lifecycle Block
published: false
description: DevOps - Terraform - Understanding the Lifecycle Block
tags: 'terraform, azure, iac, azuredevops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/DevOps-Terraform-Lifecycle-Block/assets/main-tf-tips.png'
canonical_url: null
id: 1484553
series: Terraform Pro Tips
---

## Overview

Terraform offers a range of capabilities to handle infrastructure changes in an elegant and controlled manner. One such capability is the **lifecycle** configuration block.

The [lifecycle block](https://developer.hashicorp.com/terraform/language/meta-arguments/lifecycle) provides several meta-arguments to manage how Terraform creates, updates, checks and deletes resources. In this post, we will dive into Terraform's **lifecycle** block and demonstrate its usage with a few examples with **Microsoft Azure resources**.

## Understanding the Lifecycle Block

**Note**: This post was written using **_Terraform (v1.4.x)_**

The **lifecycle** block in Terraform provides control over how a resource is managed. It's a configuration block that is nested within a [resource block](https://developer.hashicorp.com/terraform/language/resources/behavior) and supports four **meta-arguments**:

```hcl
resource "provider_resource" "block" {
  // ... some resource configuration ...

  lifecycle {
    argument = value
  }
}
```

The **lifecycle** block also has an option to configure **custom condition checks** using [preconditions and postconditions](https://developer.hashicorp.com/terraform/language/v1.4.x/expressions/custom-conditions#preconditions-and-postconditions):

```hcl
resource "provider_resource" "block" {
  // ... some resource configuration ...

  lifecycle {
    precondition {
      condition = expression
      error_message = "error(string)"
    }

    postcondition {
      condition = expression
      error_message = "error(string)"
    }
  }
}
```

We will take a closer look at **preconditions and postconditions** a bit later, but let's first look at a few examples using **meta-arguments**:

- create_before_destroy
- prevent_destroy
- ignore_changes
- replace_triggered_by

### 1. Create Before Destroy

**Argument Type**: _Boolean_

In some scenarios, destroying a resource before creating a new one can lead to downtime. To circumvent this, we can set `create_before_destroy` to `true`. This can be particularly useful when working with **Azure Virtual Machines** or **App Services**, where you'd want to minimize downtime.

Here is an example with an Azure Virtual Machine:

```hcl
resource "azurerm_virtual_machine" "example" {
  // ... other configuration ...

  lifecycle {
    create_before_destroy = true
  }
}
```

In this scenario, when an update is required that can't be performed in place, Terraform will first create the replacement VM and then destroy the old one, reducing potential downtime.

### 2. Prevent Destroy

**Argument Type**: _Boolean_

Setting `prevent_destroy` to `true` is a protective measure to prevent **accidental deletion** of **critical resources**. If you attempt to destroy such a resource, Terraform will return an error and stop the operation. This can be useful when working with **Azure SQL Databases**, **Storage Accounts**, or any resource that holds important data.

Here is an example with an Azure SQL Database:

```hcl
resource "azurerm_sql_database" "example" {
  // ... other configuration ...

  lifecycle {
    prevent_destroy = true
  }
}
```

With this configuration, Terraform will prevent the SQL database from being accidentally destroyed.

### 3. Ignore Changes

**Argument Type**: _list of attribute names_

The `ignore_changes` argument is useful when you want to manage certain resource attributes outside of Terraform, or when you want to avoid spurious diffs.

Here is an example with an Azure App Service:

```hcl
resource "azurerm_app_service" "example" {
  // ... other configuration ...

  lifecycle {
    ignore_changes = [
      app_settings,  // Ignore changes to app_settings attribute
    ]
  }
}
```

Say a different team manages an **App Services** `app_settings` for example, you may be provisioning that **App Service**, but the configuration is left up to someone else, or maybe even a different automation all together is taking care of the `app_settings` configuration, and you do not want Terraform to revert, interfere or potentially remove those settings.

In this case, any changes to the `app_settings` of the **App Service** will be ignored by Terraform.

**Tip**: You can also use a special value `all` that will ignore all settings once a resource is provisioned.

```hcl
resource "azurerm_app_service" "example" {
  // ... other configuration ...

  lifecycle {
    ignore_changes = all
  }
}
```

This will provision the resource any any subsequent configuration outside of Terraform will be ignored by Terraform.

### 4. Replace Triggered By

**Argument Type**: _list of resource or attribute references_

The `replace_triggered_by` argument allows you to replace a resource when another resource changes. You can only reference **managed resources** in `replace_triggered_by` expressions. Supply a list of expressions referencing managed resources, instances, or instance attributes.

```hcl
resource "azurerm_sql_database" "example" {
  // ... other configuration ...
}

resource "azurerm_app_service" "example" {
  // ... other configuration ...

  lifecycle {
    replace_triggered_by = [
      azurerm_sql_database.example.id, //Replace `azurerm_app_service` each time `azurerm_sql_database` id changes
    ]
  }
}
```

`replace_triggered_by` allows only resource addresses because the decision is based on the planned actions for all of the given resources, meaning that variables, data sources and modules are not supported.

Plain values such as **local values** or **input variables** do not have planned actions of their own, but you can treat them with a resource-like lifecycle by using them with the **terraform_data** resource type.

## Custom Condition Checks

You can add `precondition` and `postcondition` blocks with a lifecycle block to specify assumptions and guarantees about how resources and data sources operate. The following examples creates a precondition that checks whether the AMI is properly configured.

```hcl
data "azurerm_mssql_server" "example" {
  // ... other configuration ...
}

resource "azurerm_mssql_database" "test" {
  // ... other configuration ...

  lifecycle {
    precondition {
      condition     = data.azurerm_mssql_server.example.version == "12.0"
      error_message = "MSSQL server version incorrect (Needs to be version 12.0)."
    }

    postcondition {
      condition     = self.transparent_data_encryption_enabled == true
      error_message = "The Database must have TDE enabled."
    }
  }
}
```

**NOTE:** The [self object](https://developer.hashicorp.com/terraform/language/expressions/custom-conditions#self-object) above in the `postcondition` block refers to attributes of the instance under evaluation (e.g. the MSSQL database).

You can implement a validation check as either a `postcondition` of the resource producing the data, or as a `precondition` of a resource or output value using the data. To decide which is most appropriate, consider whether the check is representing an assumption or a guarantee.

In our example above:

- **Assumption:** Validate using `preconditions` that the database is being created, is on a **MSSQL server** that is version `12.0`.
- **GUarantee:** Validating using `postcondition` that the **MSSQL database** being created **(SELF)**, has `transparent_data_encryption_enabled` set to `true`.

## Conclusion

Terraform's **lifecycle block** provides a powerful way to control and manage your resources. Whether it's preventing accidental destruction of critical resources, managing zero-downtime updates, or ignoring changes to certain attributes, the lifecycle block offers you the flexibility you need. As always, be sure to test these configurations in a non-production environment before rolling out to production to ensure they work as expected. Happy Terraforming!

I hope you have enjoyed this post and have learned something new. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
