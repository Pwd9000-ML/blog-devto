---
title: Manage and maintain GitHub with Terraform
published: true
description: Manage and maintain GitHub with Terraform using the GitHub Provider
tags: 'githubactions, github, terraform, devops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Terraform-Provider/assets/main04.png'
canonical_url: null
id: 1152676
---

## Overview

In todays post we will take a look at one of the core components of Terraform called [Providers](https://www.terraform.io/language/providers). More specifically we will be looking at using the [GitHub Provider](https://registry.terraform.io/providers/integrations/github/latest/docs) to manage various aspects of GitHub using Terraform.

Firstly what is a terraform provider? **Providers** are simply **plugins** used in **Terraform** that are a logical abstraction of an upstream API responsible for understanding API interactions and exposing resources. They are used **to implement resource types.** At the time of this writing there are more than **2300 providers** to choose from and still increasing daily!

Some [popular providers](https://registry.terraform.io/browse/providers) you may already know about or even be using are cloud platform providers such as the [AzureRM Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs) for example.

However, in this post we will be looking at a specific terraform provider you may have not known about, the [GitHub Provider](https://registry.terraform.io/providers/integrations/github/latest/docs). We will create a basic terraform configuration and use this provider to manage **GitHub resources**, by creating a **GitHub repository** and configure a **branch protection rule** on our repo's **default branch**, all through IaC (Infrastructure as Code), pretty awesome!

## Pre-requisites

To get started you'll need:

- A GitHub account / Organisation
- A Personal Access Token (PAT) - See [creating a personal access token](https://docs.github.com/en/enterprise-server@3.4/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token).
- A Code editor such as [VSCode](https://code.visualstudio.com/download)
- [Terraform](https://www.terraform.io/downloads)

The minimum permission scopes required on the PAT token for this demo are: `"repo"`, `"read:repo_hook"`, `"read:org"`, `"read:discussion"` and `"delete_repo"`:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Terraform-Provider/assets/PAT.png)

**NOTE:** PAT tokens are only displayed once and are sensitive, so ensure they are kept safe.

## Terraform Configuration

These terraform config files can also be found on the following [github repository](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2022-GitHub-Terraform-Provider/code).

### Variables

```hcl
### Variables.tf ###

variable "token" {
  type        = string
  description = "Specifies the GitHub PAT token or `GITHUB_TOKEN`"
  sensitive   = true
}
```

### Main

```hcl
### Main.tf ###

terraform {
  required_version = "~> 1.2.0"
  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> 4.0"
    }
  }
}

provider "github" {
  token = var.token # or `GITHUB_TOKEN`
}

#Create and initialise a public GitHub Repository with MIT license and a Visual Studio .gitignore file (incl. issues and wiki)
resource "github_repository" "repo" {
  name               = "Pwd9000-Demo-Repo-2022"
  description        = "My awesome codebase"
  visibility         = "public"
  has_issues         = true
  has_wiki           = true
  auto_init          = true
  license_template   = "mit"
  gitignore_template = "VisualStudio"
}

#Set default branch 'master'
resource "github_branch_default" "master" {
  repository = github_repository.repo.name
  branch     = "master"
}

#Create branch protection rule to protect the default branch. (Use "github_branch_protection_v3" resource for Organisation rules)
resource "github_branch_protection" "default" {
  repository_id                   = github_repository.repo.id
  pattern                         = github_branch_default.master.branch
  require_conversation_resolution = true
  enforce_admins                  = true

  required_pull_request_reviews {
    required_approving_review_count = 1
  }
}
```

## Usage

1. Clone or copy the files in [this path](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2022-GitHub-Terraform-Provider/code) to a local directory and open a command prompt.
2. Amend the .tfvars file with desired variables or token (Keep your tokens safe).

**BUILD:**

```hcl
terraform init
terraform plan -out deploy.tfplan
terraform apply deploy.tfplan
```

**DESTROY:**

```hcl
terraform plan -destroy -out destroy.tfplan
terraform apply destroy.tfplan
```

As you can see the terraform configuration we just ran using the [GitHub Provider](https://registry.terraform.io/providers/integrations/github/latest/docs) created a repository and also configured our **branch protection rule** on the specified **default branch:**

### Repository

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Terraform-Provider/assets/repo.png)

### Branch protection rule

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Terraform-Provider/assets/branch.png)

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Terraform-Provider/assets/rule.png)

We have only scratched the surface of what this **terraform provider** can do and if you are interested to see what other resources can be built and managed in GitHub using this provider head over to the official [GitHub Provider](https://registry.terraform.io/providers/integrations/github/latest/docs) documentation.

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my published [Github](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2022-GitHub-Terraform-Provider/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
