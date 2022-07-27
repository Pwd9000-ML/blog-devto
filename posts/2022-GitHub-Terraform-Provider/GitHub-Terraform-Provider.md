---
title: Manage and maintain GitHub with Terraform
published: false
description: Manage and maintain GitHub with Terraform using the GitHub Provider
tags: 'githubactions, github, terraform, devops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Terraform-Provider/assets/main04.png'
canonical_url: null
id: 1152676
---

## Overview

In todays tutorial we will take a look at one of the core building blocks of Terraform called [Providers](https://www.terraform.io/language/providers). More specifically we will be looking at using the [GitHub Provider](https://registry.terraform.io/providers/integrations/github/latest/docs) to manage various aspects of GitHub using Terraform.

**Providers** are **plugins** used in **Terraform** and are a logical abstraction of an upstream API responsible for understanding API interactions and exposing resources. They are used **to implement resource types.** At the time of this writing there are more than **2300 providers** to choose from and still increasing!

Some [popular providers](https://registry.terraform.io/browse/providers) you may already know about or even already be using are cloud based terraform providers such as the [AzureRM Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs).

However as mentioned, in this post we will be looking at a terraform provider you may have not known about, the [GitHub Provider](https://registry.terraform.io/providers/integrations/github/latest/docs). We will create a basic terraform configuration and use this provider to manage **GitHub resources**, by creating a GitHub repository set a default branch and configure a branch protection policy, all through IaC (Infrastructure as Code), pretty awesome!

## Conclusion

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my published [Github](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2022-GitHub-Function-CICD/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
