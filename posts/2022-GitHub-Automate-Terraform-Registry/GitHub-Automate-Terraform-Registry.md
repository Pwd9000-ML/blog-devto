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

Dependabot is a service built into GitHub that helps you update your dependencies automatically, so you can spend less time updating dependencies and more time building. Dependabot even includes checks for version updates for **terraform providers** inside of your configuration files which we will look at today.

Check out this list of **[package-ecosystems](https://docs.github.com/en/code-security/supply-chain-security/keeping-your-dependencies-updated-automatically/configuration-options-for-dependency-updates#package-ecosystem)** that's supported.

One key benefit is that dependency updates might contain security vulnerability fixes, bug fixes etc and manually keeping track of updates or updating them when a newer version is available is a lot of hassle. This is where **Dependabot** can help by automatically raising a Pull Request whenever there is a newer version of a dependency.

In my [Terraform module repository - Dynamic Subnets](https://github.com/Pwd9000-ML/terraform-azurerm-dynamic-subnets), I have a terraform file called `versions.tf`:

```hcl
terraform {
  required_version = "~> 1.1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 2.62.0"
    }
  }
}
```

We will set up dependabot by creating a special folder at the root of the project called `.github` and inside that folder create a `YAML` file called `dependabot.yml`:

```yaml
# To get started with Dependabot version updates, you'll need to specify which
# package ecosystems to update and where the package manifests are located.
# Please see the documentation for all configuration options:
# https://help.github.com/github/administering-a-repository/configuration-options-for-dependency-updates

version: 2
updates:
  - package-ecosystem: 'terraform' # See documentation for possible values
    directory: '/' # Location of package manifests
    schedule:
      interval: 'daily'
```

**NOTE:** The package-ecosystem is `terraform` and the `versions.tf` file is at the root of my project repository, which is represented bt the directory `"/"`

Once the dependabot `YAML` file has been created and committed to the repository, you will notice that it automatically opened a Pull-Request for me, showing me that my provider version is out of date:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Automate-Terraform-Registry/assets/pr1.png)

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Automate-Terraform-Registry/assets/pr2.png)

Now we can decide whether we want to accept this version bump or not by either accepting and merging the pull request or cancelling and closing the pull request. As you can also see the schedule interval is set to `daily` which means dependabot will check everyday to see if there are any new terraform provider versions released and automatically open a pull request if there is. Pretty neat!

### Automate push to Terraform Registry

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
