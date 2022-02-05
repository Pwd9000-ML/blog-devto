---
title: Automate Terraform Module Releases on the public registry using GitHub
published: false
description: Automate Terraform Module Releases on the public terraform registry using GitHub Actions
tags: 'githubactions, Terraform, IaC, Automation'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Automate-Terraform-Registry/assets/main1.png'
canonical_url: null
id: 979002
---

### Overview

This tutorial uses examples from the following GitHub project [Terraform module repository - Dynamic Subnets](https://github.com/Pwd9000-ML/terraform-azurerm-dynamic-subnets).

If you enjoy creating public terraform modules for the community like I do, and host them on the public terraform registry. You will enjoy todays tutorial. We will be covering how you can automate and maintain your terraform module versioning using **GitHub dependabot** and also automate your module releases and pushing versioned releases to the public **Terraform registry** using **GitHub Actions**.

### Getting started

Anyone can publish and share modules on the [Terraform Registry](https://registry.terraform.io/) for free. In this tutorial I wont be going into detail on how to create your account, linking it with your GitHub repository and doing the initial push to the registry.  

This initial process is fairly well documented on HashiCorps tutorial on: [How to publish modules to the registry](https://www.terraform.io/registry/modules/publish). It is a fairly easy and frictionless process.  

In todays tutorial we are going to focus more on maintaining an existing module and how to automate releasing new versions using **GitHub Actions**. We will also look at how we can automate the Terraform and provider version inside the module using a great feature of HitHub called **GitHub Dependabot**.

### Dependabot

What is it?
### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>