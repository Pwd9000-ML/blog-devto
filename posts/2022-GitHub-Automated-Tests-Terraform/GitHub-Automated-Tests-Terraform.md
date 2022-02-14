---
title: Automated Terraform Tests for Azure using GitHub Actions
published: false
description: Automate Terraform Module Test and Release on the public terraform registry using GitHub Actions
tags: 'githubactions, Terraform, IaC, Automation'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Automated-Tests-Terraform/assets/main1.png'
canonical_url: null
id: 988582
series: Using Terraform on GitHub
---

### Overview

This tutorial uses examples from the following GitHub project [Terraform module repository - Dynamic Subnets](https://github.com/Pwd9000-ML/terraform-azurerm-dynamic-subnets).

In the previous tutorial on this blog series **Using Terraform on GitHub**, we looked at how to [automate terraform module releases on the public registry using GitHub](https://dev.to/pwd9000/automate-terraform-module-releases-on-the-public-registry-using-github-4775). In todays tutorial we will build on the same topic but take a look at how we can also perform full end to end automation that includes:  

- Automated dependency checks for Terraform modules using GitHub **dependabot**.
- Triggering an automated Terraform test when **dependabot** opens a Pull Request (PR) on the version change.
- Test if the terraform code changes in the PR will work.  
- If all tests are successful automatically merge the PR.
- Once the PR is merged automatically create a new release of the public module on the public Terraform registry.

### Getting started

If you look at the following GitHub project: [Terraform module repository - Dynamic Subnets](https://github.com/Pwd9000-ML/terraform-azurerm-dynamic-subnets), you will 

###

I hope you have enjoyed this post and have learned something new. You can find the code samples used in this blog post on my GitHub project [Terraform module repository - Dynamic Subnets](https://github.com/Pwd9000-ML/terraform-azurerm-dynamic-subnets). :heart:

If you are interested in checking out my public terraform modules on the registry here they are:

- [AZURE - Dynamic Subnets](https://registry.terraform.io/modules/Pwd9000-ML/dynamic-subnets/azurerm/latest)
- [AZURE - Secure Backend](https://registry.terraform.io/modules/Pwd9000-ML/secure-backend/azurerm/latest)

I will be adding a few more cool modules on the public registry in due course.

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
