---
title: Terraform - Keep dependencies up to date with Dependabot (Azure DevOps version)
published: true
description: Terraform - How to keep dependencies up to date with Dependabot and Azure DevOps
tags: 'terraform, Dependabot, iac, AzureDevOps'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/DevOps-Terraform-Dependabot-Ado/assets/main-tf-tips.png'
canonical_url: null
id: 1715663
series: Terraform Pro Tips
date: '2024-01-03T14:52:42Z'
---

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/DevOps-Terraform-Dependabot-Ado/assets/springclean24.png)

## Previously

If you are interested to see how to do the same thing described in this post but in **GitHub** instead, feel free to check out my previous post: [Automate Terraform Module Releases on the public registry using GitHub](https://dev.to/pwd9000/automate-terraform-module-releases-on-the-public-registry-using-github-4775)

## Overview

In this post we will look at how you can automate and maintain your terraform module versioning using a dependency management tool originally ported from the **GitHub Security Toolset** called **[Dependabot](https://marketplace.visualstudio.com/items?itemName=tingle-software.dependabot)** but used in **Azure DevOps** instead, and how the tool can easily help to update your terraform module dependencies to the latest version using **Azure DevOps pipelines**.

**Dependabot** is an invaluable tool for managing **Terraform** infrastructure-as-code projects. It helps maintain your Terraform modules at their latest versions. It systematically scans your `*.tf` files, identifies dependencies (i.e., modules and Terraform providers), and checks for any new updates or releases available.

When **Dependabot** identifies an outdated Terraform module or provider, it automatically creates a pull request in your version control system with the updated version, we will look how to set this automated check and **Pull Requests** up using **Azure DevOps Pipelines**. These pull requests include change logs and release notes of the updated provider version, just like any other Dependabot update.

This automated process ensures your infrastructure's configuration is always up-to-date and reduces the risks associated with outdated modules or providers. Furthermore, Dependabot simplifies the process of managing multiple dependencies, making it significantly effortless and more efficient for developers to maintain a healthy Terraform codebase.

### Getting Started

To integrate **Dependabot** with our **Azure DevOps repos**, we need to install [the Dependabot extension](https://marketplace.visualstudio.com/items?itemName=tingle-software.dependabot) by Tingle Software. You can find it in the Azure DevOps Extension Marketplace by searching for **"Dependabot"**. Go to your **"Organization Settings"** in Azure DevOps and see if you have this extension installed. If not, please install it before moving on.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/DevOps-Terraform-Dependabot-Ado/assets/market.png)

### Repository Permissions

In order for **Dependabot** to create a **pull request**, you need to grant some permissions to your repository's `Project Collection Build Service (OrgName)`.

Go to your project **settings** and select the **repositories** option. Find the repo where your **Terraform code** is located and click on the **security tab**. Then, add a user called `Project collection build service (YourOrgName)` and give it the following permissions:

- **Bypass policies when pushing**
- **Contribute**
- **Contribute to pull request**
- **Create Branch**
- **Create Tag**
- **Force Push**

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/DevOps-Terraform-Dependabot-Ado/assets/permission.png)

### Setting up Dependabot

Once the extension is installed and permissions are set, we can now set up **Dependabot** for our **Azure DevOps** repos to scan for **Terraform** dependencies using an **Azure DevOps Pipeline**. Go to your **"Azure DevOps Project"** and locate the Git repo you want to set up **Dependabot** for.

Add a configuration file stored at `.github/dependabot.yml` conforming to the [official spec](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file?wt.mc_id=DT-MVP-5004771).

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/DevOps-Terraform-Dependabot-Ado/assets/dep.png)

### dependabot.yml

```yaml
version: 2
updates:
  - package-ecosystem: 'terraform'
    directory: '/'
    schedule:
      interval: 'daily'
```

The above configuration file will scan for **Terraform** dependencies and will only check the root of my repository code where my terraform `*.tf` files are located for my module.

Notice the `versions.tf` file in the root of my repository, this file is used to pin the version of the **Terraform** provider I am using in my module, in this case the **AzureRM** provider. The current version is `3.55.0` and **Dependabot** will check if there is a newer version available and will create a **pull request** if there is a newer version available.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/DevOps-Terraform-Dependabot-Ado/assets/version.png)

### versions.tf

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

### Setting up the pipeline

Now that we have our **Dependabot** configuration file in place, we can now set up our **Azure DevOps Pipeline** to run the **Dependabot** scan. Go to your **Azure DevOps Project** and create a new **Pipeline**. Select your **Git repo** and choose the **Starter Pipeline** template or copy the following code into a `yaml` file to be used. I will be using the following **YAML** pipeline for this example:

```yaml
trigger: none # Disable CI trigger

schedules:
  - cron: '0 2 * * *' # daily at 2am UTC
    always: true # run even when there are no code changes
    branches:
      include:
        - dev
    batch: true
    displayName: Daily

stages:
  - stage: CheckDependencies
    displayName: 'Check Dependencies'
    jobs:
      - job: Dependabot
        displayName: 'Run Dependabot'
        pool:
          vmImage: 'ubuntu-latest' # Only Ubuntu and MacOS is supported at this time
        steps:
          - task: dependabot@1
            displayName: 'Run Dependabot'
```

The above pipeline will run the **Dependabot** scan daily at 2am UTC and will only run against the `dev` branch. The pipeline will run on an **Ubuntu** agent and will use the **Dependabot** task that will use our configuration file to scan for **Terraform** dependencies.

Note that the **Dependabot** task is currently only supported on **Ubuntu** and **MacOS** agents, so if you are using **Windows** agents, you will need to change your pipeline to use **Ubuntu** or **MacOS** agents instead.

Notice that after the pipeline runs, a **pull request** is created with the updated version of the **AzureRM** provider from `3.55.0` to `3.85.0`:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/DevOps-Terraform-Dependabot-Ado/assets/pr.png)

It also includes a **change log** and a nice **overview** for the new version:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/DevOps-Terraform-Dependabot-Ado/assets/overview.png)

You can also inspect the **pull request** to see the **difference** between the old and new version of the `versions.tf` file:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/DevOps-Terraform-Dependabot-Ado/assets/diff2.png)

### Conclusion

**Dependabot** is a great tool to help you keep your **Terraform** dependencies up to date and it is very easy to set up and use, or to schedule dependency checks using a simple **pipeline** with a cron job as shown in this post. It is also very flexible and can be used with **GitHub** or **Azure DevOps**.

Not only can it be used to keep your **Terraform** dependencies up to date, but it also supports other package ecosystems such as **npm**, **NuGet**, **Maven**, **Docker**, **Composer**, **Cargo**, **pip**, **Yarn** and so forth. Check out the full list of supported package ecosystems [here](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file#package-ecosystem?wt.mc_id=DT-MVP-5004771).

I hope you found this post useful and if you have any questions or comments, please get in touch with me on **[Twitter](https://twitter.com/pwd9000)** or **[LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)**.

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
