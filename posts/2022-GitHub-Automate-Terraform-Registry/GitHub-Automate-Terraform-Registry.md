---
title: Automate Terraform Module Releases on the public registry using GitHub
published: true
description: Automate Terraform Module Releases on the public terraform registry using GitHub Actions
tags: 'githubactions, Terraform, IaC, Automation'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Automate-Terraform-Registry/assets/main1.png'
canonical_url: null
id: 979002
date: '2022-02-05T15:38:50Z'
series: Using Terraform on GitHub
---

### Overview

This tutorial uses examples from the following GitHub project [Terraform module repository - Dynamic Subnets](https://github.com/Pwd9000-ML/terraform-azurerm-dynamic-subnets).

If you enjoy creating public terraform modules for the community like I do, and host them on the public terraform registry. You will enjoy todays tutorial. We will be covering how you can automate and maintain your terraform module versioning using **GitHub dependabot** and also automate your module releases and pushing versioned releases to the public **Terraform registry** using **GitHub Actions**.

### Getting started

Anyone can publish and share modules on the [Terraform Registry](https://registry.terraform.io/) for free. In this tutorial I wont be going into detail on how to create your account, linking it with your GitHub repository and doing the initial push to the registry.

This initial process is fairly well documented on HashiCorps tutorial on: [How to publish modules to the registry](https://www.terraform.io/registry/modules/publish). It is a fairly easy and frictionless process.

In this tutorial we are going to focus more on maintaining an existing module and how to automate releasing new versions using **GitHub Actions**. We will also look at how we can automatically update the provider versions (dependencies) used inside of the terraform module using a great feature of GitHub called **Dependabot**.

### Enable Dependabot

Dependabot is a service built into GitHub that helps you update your dependencies automatically, so you can spend less time updating dependencies and more time building. Dependabot even includes checks for version updates for **terraform providers** inside of your configuration files which we will look at today.

Check out this list of **[package-ecosystems](https://docs.github.com/en/code-security/supply-chain-security/keeping-your-dependencies-updated-automatically/configuration-options-for-dependency-updates#package-ecosystem)** that's supported.

One key benefit is that dependency updates might contain security vulnerability fixes, bug fixes etc and manually keeping track of updates or updating them when a newer version is available is a lot of hassle. This is where **Dependabot** can help by automatically raising a Pull Request whenever there is a newer version of a dependency.

In my [Terraform module repository - Dynamic Subnets](https://github.com/Pwd9000-ML/terraform-azurerm-dynamic-subnets), I have a terraform file called [versions.tf](https://github.com/Pwd9000-ML/terraform-azurerm-dynamic-subnets/blob/master/versions.tf):

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

We will set up dependabot by creating a special folder at the root of the repository called `.github` and inside that folder create a `YAML` file called [dependabot.yml](https://github.com/Pwd9000-ML/terraform-azurerm-dynamic-subnets/blob/master/.github/dependabot.yml):

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

**NOTE:** The package-ecosystem is `terraform` and the `versions.tf` file is at the root of the project repository, which is represented by the directory: `"/"`

Once the dependabot `YAML` file has been created and committed to the repository, you will notice that it automatically opened a Pull-Request for me, showing me that my provider version is out of date:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Automate-Terraform-Registry/assets/pr1.png)

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Automate-Terraform-Registry/assets/pr2.png)

Now we can decide whether we want to accept this version bump or not by either accepting and merging the pull request or cancelling and closing the pull request. As you can also see the schedule interval is set to `daily` which means **dependabot** will check everyday to see if there are any new terraform provider versions released and automatically open a pull request if there is. Pretty neat!

### Automate Releases - Terraform Registry

Say for example we take this version change (or any changes and improvements on our module), and after testing the changes on our module we want to create a new public release version of our module on the public **[Terraform Registry](https://registry.terraform.io/)**.

**NOTE:** I have written a public **GitHub marketplace Action** called: [Terraform Tests for AZURE](https://github.com/marketplace/actions/terraform-tests-for-azure) to do automated tests. Check it out.

After testing to perform a release we will create a **workflow**.

Under the `.github` directory we will create a new folder called `workflows` and in this folder we will create another `YAML` file called: [push-tf-registry.yml](https://github.com/Pwd9000-ML/terraform-azurerm-dynamic-subnets/blob/master/.github/workflows/push-tf-registry.yml).

```yml
### This workflow can be used to manually create new release versions from a tag push using e.g. VSCODE ###
on:
  push:
    tags:
      - '*'

name: Release to terraform public registry
jobs:
  Release:
    name: Release
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: ncipollo/release-action@v1
        with:
          generateReleaseNotes: true
          name: 'v${{ github.ref_name }}'
          token: ${{ secrets.GITHUB_TOKEN }}
```

This workflow will trigger on a tag push and create a **GitHub Release**. As per the [documented process](https://www.terraform.io/registry/modules/publish#releasing-new-versions) for creating a new release on the public terraform registry we have to use a valid semantic version, optionally prefixed with a v.

Example of valid tags are: v1.0.1 and 0.9.4. To publish a new module, you must already have at least one tag created.

To release a new version, create and push a new tag with the proper format. The webhook will notify the registry of the new version and it will appear on the registry usually in less than a minute.

The current version of my public module is `version = 1.0.3`:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Automate-Terraform-Registry/assets/pre.png)

This corresponds with the current release on the **GitHub** repository hosting the module:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Automate-Terraform-Registry/assets/pre2.png)

With the **GitHub workflow** set up, Let's create a new tag and push that to our repository on GitHub. The workflow will trigger and create a new release for us automatically, so let's try it out.

![image.gif](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Automate-Terraform-Registry/assets/tag.gif)

After creating the tag `1.0.4` and pushing the tag to the remote repository. Notice that the workflow has triggered and ran, creating a new release automatically using the tag version number:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Automate-Terraform-Registry/assets/work.png)

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Automate-Terraform-Registry/assets/rel.png)

**NOTE:** The **GitHub Action** that creates the release has an input setting: `generateReleaseNotes: true`, so the release notes have also been created for us dynamically.

As you can see the new version is also now published on the **Terraform Registry**

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Automate-Terraform-Registry/assets/rel2.png)

That's it, now we can automatically let **Dependabot** take care of our terraform provider versioning and create pull requests automatically when new provider versions are released.

Additionally we also have a really straight forward easy way to create new releases of our own module by simply creating a valid semantic version number as a tag and then push that tag to our remote repository where the **GitHub Workflow** will create a release for us based on the semantic version tag.

As an added bonus, I also added another section onto the **Dependabot** config file to also regularly check the **GitHub Actions** used in the workflow called: `ncipollo/release-action@v1` and `actions/checkout@v2` so when a new versions of these actions come out, **Dependabot** will also let me know that I can update my workflow actions.

```yml
version: 2
updates:
  - package-ecosystem: 'terraform' # See documentation for possible values
    directory: '/' # Location of package manifests
    schedule:
      interval: 'daily'

  - package-ecosystem: 'github-actions' # See documentation for possible values
    directory: '/' # Location of package manifests
    schedule:
      interval: 'daily'
```

### Fully Automated Testing and Release on changes to IaC

Check out the next blog post on this series: **** to show how to do fully automated integration test when **Dependabot** opens a PR. Followed by automatically merging the pull request once all tests have finished and then also as a last step automatically deploy a new release/version and pushing that to the Terraform registry:  

[Automated Terraform Tests for Azure using GitHub Actions](https://dev.to/pwd9000/automated-terraform-tests-for-azure-using-github-actions-4349)

I hope you have enjoyed this post and have learned something new. You can find the code samples used in this blog post on my GitHub project [Terraform module repository - Dynamic Subnets](https://github.com/Pwd9000-ML/terraform-azurerm-dynamic-subnets). :heart:

If you are interested in checking out my public terraform modules on the registry here they are:

- [AZURE - Dynamic Subnets](https://registry.terraform.io/modules/Pwd9000-ML/dynamic-subnets/azurerm/latest)
- [AZURE - Secure Backend](https://registry.terraform.io/modules/Pwd9000-ML/secure-backend/azurerm/latest)

I will be adding a few more cool modules on the public registry in due course.

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
