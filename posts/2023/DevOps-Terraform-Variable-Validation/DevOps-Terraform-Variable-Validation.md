---
title: Terraform - Variable Validation
published: true
description: DevOps - Terraform - Enhancing Infrastructure-as-Code Development using Variable Validation
tags: 'terraform, azure, iac, azuredevops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/DevOps-Terraform-Variable-Validation/assets/main-tf-tips.png'
canonical_url: null
id: 1573291
series: Terraform Pro Tips
date: '2023-08-28T08:06:42Z'
---

## Overview

Today we will discuss an interesting feature of Terraform by taking a closer look at **[variable validation rules](https://developer.hashicorp.com/terraform/language/values/variables#custom-validation-rules)** inside **terraform variables**.

```hcl
variable "fruit" {
  type        = string
  description = "What fruit to pick?"
  default     = "apple"

  validation {
    condition     = can(regex("^(lemon|apple|mango|banana|cherry)$", var.fruit))
    error_message = "Invalid fruit selected, only allowed fruits are: 'lemon', 'apple', 'mango', 'banana', 'cherry'. Default 'apple'"
  }
}
```

The above example **validates** the `fruit` variable against a set of predefined fruits. An input that matches the regex pattern passes the validation. If any invalid fruit is passed, the error message quickly informs the users about the allowed values.

**Terraform's** consistent updates have always aimed to make **infrastructure-as-code (IaC)** development more efficient, secure, and error-free. One of these updates, the addition of a **validation capability** for **input variables**, has significantly improved this IaC tool's robustness.

This blog post will demystify **Terraform validation**, discussing its utility and providing practical examples using the Azure platform.

## Understanding Terraform Variable Validation

Terraform's variable validation helps ensure the values assigned to variables meet specific criteria defined in advance. Introduced in version 0.13, this feature allows you to provide custom `validation` rules for your input variables. Validation is essentially added as a validation block within the variable declaration, and it uses a condition to determine whether a value is acceptable.

There are two key components in a variable validation block - the `condition` that expresses the criteria a value must meet, and an error `message` to alert the user if the value doesn't pass the check. The condition is a boolean expression. When the condition is false, Terraform produces an error displaying the custom message.

### The Importance of Terraform Variable Validation

Terraform variable validation brings four key advantages to IaC developers:

1. **Greater Consistency:** With variable validation, you ensure that acceptable input values adhere to specific standards. This fosters uniformity across each infrastructure deployment.

2. **Error Reduction:** By flagging erroneous or unacceptable variable inputs, the tool drastically reduces errors that might arise during the 'terraform apply' phase.

3. **Enhanced Security:** By validating inputs adequately, developers can avoid potential security vulnerabilities resulting from insecure or dangerous variable input.

4. **Improved Developer Experience:** Validation improves user experience by quickly catching errors and guiding users towards acceptable values, accelerating the development process.

## Variable Validation In Action: Azure Platform Examples

Let's dive into some practical use cases of variable validation with Azure infrastructure deployments.

For instance, when creating a virtual machine, if a user wants to choose their known operating system, we define a terraform variable and validate whether the input falls within our accepted values:

```hcl
variable "os_type" {
  description = "Operating System to use for the VM"

  validation {
    condition     = contains(["Windows", "Linux"], var.os_type)
    error_message = "The os_type must be either 'Windows' or 'Linux'."
  }
}
```

In the example above, we utilize the `contains` function to validate whether the `os_type` falls within `[Windows, Linux]`. If a user enters an OS type out of this list, Terraform will display the error message, preventing potential confusion or failure in deployments.

Similarly, you might want to implement a naming convention for a **resource group** in Azure. For example, the name must always start with a **'rg-'** prefix. Terraform validation can assist here:

```hcl
variable "resource_group_name" {
  description = "Name of the resource group"

  validation {
    condition     = can(regex("^rg-", var.resource_group_name))
    error_message = "The resource group name must start with 'rg-'."
  }
}
```

Our `condition` uses a regular expression to test whether the given resource group name starts with **'rg-'**. If not, Terraform prompts the user with the specified `error_message`.

Let's take a look at one more example. The following example demonstrates another use case for Terraform's variable validation, when working with private DNS records and validating the record type. This code sample ensures that only valid DNS record types are specified when deploying resources:

```hcl
variable "private_dns_record_type" {
  type        = string
  description = "value of the private dns record type, only allowed options are 'A', 'AAAA', 'CNAME', 'MX', 'PTR', 'SRV', 'TXT'"
  default     = "A"

  validation {
    condition     = can(regex("^(A|AAAA|CNAME|MX|PTR|SRV|TXT)$", var.private_dns_record_type))
    error_message = "Invalid value for private_dns_record_type, only allowed options are: 'A', 'AAAA', 'CNAME', 'MX', 'PTR', 'SRV', 'TXT'"
  }
}
```

The above `variable` block is a stricter example where it validates the `private_dns_record_type` against a set of predefined DNS record types. An input that matches the regex pattern passes the validation. If any invalid DNS record type is passed, the error message quickly informs the users about the allowed values.

This variable validation can then be used in the resource block as follows to create a corresponding private DNS record for that type for example:

```hcl
#A record example
resource "azurerm_private_dns_a_record" "private_dns_a_record" {
  count               = var.private_dns_record_type == "A" ? 1 : 0
  name                = lower(var.private_dns_record_name)
  resource_group_name = var.resource_group_name
  ttl                 = var.private_dns_record_ttl
  zone_name           = var.private_dns_zone_name
  records             = var.private_dns_record_value
  tags                = var.tags
}
```

or

```hcl
#CNAME record example
resource "azurerm_private_dns_cname_record" "private_dns_cname_record" {
  count               = var.private_dns_record_type == "CNAME" ? 1 : 0
  name                = lower(var.private_dns_record_name)
  resource_group_name = var.resource_group_name
  ttl                 = var.private_dns_record_ttl
  zone_name           = var.private_dns_zone_name
  record              = var.private_dns_record_value
  tags                = var.tags
}
```

The resource blocks above creates an Azure Private DNS **'A'** or **'CNAME'** record, but only if the `private_dns_record_type` variable is **"A"** or **"CNAME"** for example. If the DNS record type doesn't fit that criteria of the validation, count equals 0, and Terraform won't create this record type. This approach ensures the correct DNS record gets created based on the initially validated variable and avoids unnecessary or inaccurate resources.

By integrating variable validation in your Terraform configurations like this, you enhance the **accuracy and predictability** of your deployments. With this advanced feature, you'll be able to manage resources more effectively on platforms like Azure.

## Conclusion

In summary, **variable validation** enhances Terraform's robustness as an IaC tool by **reducing errors**, **improving security**, and fostering a **consistent**, developer-friendly experience. Our examples on the Azure platform demonstrate how you can avoid complications by ensuring variable inputs align with your requirements during the infrastructure setup process. As you continue to build with Terraform, consider this feature to help bolster your code's reliability and your infrastructure's integrity.

I hope you have enjoyed this post and have learned something new. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
