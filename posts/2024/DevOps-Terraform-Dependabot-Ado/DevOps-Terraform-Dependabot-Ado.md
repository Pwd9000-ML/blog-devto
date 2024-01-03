---
title: Terraform - Keep dependencies up to date with Dependabot (Azure DevOps version)
published: false
description: Terraform - How to keep dependencies up to date with Dependabot and Azure DevOps
tags: 'terraform, Dependabot, iac, AzureDevOps'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/DevOps-Terraform-Dependabot-Ado/assets/main-tf-tips.png'
canonical_url: null
id: 1715663
series: Terraform Pro Tips
---

## Previously

If you are interested to see how to do the same thing described in this post but in **GitHub** instead, feel free to check out my previous post: [Automate Terraform Module Releases on the public registry using GitHub](https://dev.to/pwd9000/automate-terraform-module-releases-on-the-public-registry-using-github-4775)  

## Overview

In this post we will look at how you can automate and maintain your terraform module versioning using a dependency management tool originally ported from the **GitHub Security Toolset** called **[Dependabot](https://marketplace.visualstudio.com/items?itemName=tingle-software.dependabot)** but used in **Azure DevOps** instead, and how the tool can easily help to update your terraform module dependencies to the latest version using **Azure DevOps pipelines**.

**Dependabot** is an invaluable tool for managing **Terraform** infrastructure-as-code projects. It helps maintain your Terraform modules at their latest versions. It systematically scans your `*.tf` files, identifies dependencies (i.e., modules and Terraform providers), and checks for any new updates or releases available.

When **Dependabot** identifies an outdated Terraform module or provider, it automatically creates a pull request in your version control system with the updated version, we will look how to set this automated check and **Pull Requests** up using **Azure DevOps Pipelines**. These pull requests include change logs and compatibility scores, just like any other Dependabot update.

This automated process ensures your infrastructure's configuration is always up-to-date and reduces the risks associated with outdated modules or providers. Furthermore, Dependabot simplifies the process of managing multiple dependencies, making it significantly effortless and more efficient for developers to maintain a healthy Terraform codebase.  

### Getting Started

To integrate **Dependabot** with our **Azure DevOps repos**, we need to install [this extension](https://marketplace.visualstudio.com/items?itemName=tingle-software.dependabot) by Tingle Software. You can find it in the Azure DevOps Extension Marketplace by searching for **"Dependabot"**. Go to your **"Organization Settings"** in Azure DevOps and see if you have this extension installed. If not, please install it before moving on.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/DevOps-Terraform-Dependabot-Ado/assets/market.png)  

### Setting up Dependabot

Once the extension is installed, we can now set up **Dependabot** for our **Azure DevOps** repos to scan for **Terraform** dependencies. Go to your **"Azure DevOps Project"** and locate the Git repo you want to set up **Dependabot** for.  

Add a configuration file stored at `.github/dependabot.yml` conforming to the [official spec](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file).  

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/DevOps-Terraform-Dependabot-Ado/assets/market.png)  

In my case the content of the file is as follows:  

```yaml
version: 2
updates:
  - package-ecosystem: "terraform" 
    directory: "/"
    schedule:
      interval: "daily"
```

The above configuration file will scan for **Terraform** dependencies and will only check the root of my repository code where my terraform `*.tf` files are located for my module.  

Notice the `versions.tf` file in the root of my repository, this file is used to pin the version of the **Terraform** provider I am using in my module, in this case the **AzureRM** provider.  

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/DevOps-Terraform-Dependabot-Ado/assets/market.png)  

```hcl
terraform {
  required_version = ">= 1.6.6"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.55.0"
    }
  }
}
```




### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
