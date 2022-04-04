---
title: Terraform - Filter results using FOR loops.
published: false
description: DevOps - Terraform - Filter with FOR
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
- **Filter:** Filter only on desired items in combination with `if` expression.
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

This will return a set of `app_names` that have the objects key `"app_require_feature"` set to true

```txt$ terraform apply
Outputs:

result = ["App3"]
```

## Real world example

Let's take a real world usage case where we would need such a `for` construct to filter and only configure something based on certain criteria.



I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my [Github](https://github.com/Pwd9000-ML/Azure-Terraform-Deployments/tree/master/04_App_Acr) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
