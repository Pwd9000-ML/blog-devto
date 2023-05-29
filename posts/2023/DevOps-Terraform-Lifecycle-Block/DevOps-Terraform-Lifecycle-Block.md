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

This tutorial uses examples from the following GitHub

### Example

It allows us to be mo

## Real world example

The example code

We start off by creating a list of sites in a variable for **siteA** and **siteB**:

```hcl
## variables.tf ##

variable "site_names" {
  type        = list(string)
  default     = ["siteA", "siteB"]
  description = "Provide a list of all Contoso site names - Will be mapped to local var 'site_configs'"
}
```

As you can see the Terraform `lookup()` function can be quite useful in cases where we have multiple sites or different configs and having the ability match and correlate different configurations for different scenarios.

I hope you have enjoyed this post and have learned something new. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
