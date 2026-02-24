---
title: Automate Terraform Module Releases on the public registry using GitHub Actions
published: true
description: Automate Terraform Module Releases on the public terraform registry using GitHub Actions
tags: 'github, terraform, githubactions, devops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Automate-Terraform-Registry/assets/main3.png'
id: 3020585
series: Terraform Registry
date: '2025-11-13T17:11:59Z'
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
  required_version = ">= 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 3.0"
    }
  }
}
```

**NOTE:** Using `>=` constraints allows more flexibility for module consumers while ensuring minimum version requirements are met.

We will set up dependabot by creating a special folder at the root of the repository called `.github` and inside that folder create a `YAML` file called [dependabot.yml](https://github.com/Pwd9000-ML/terraform-azurerm-dynamic-subnets/blob/master/.github/dependabot.yml):

```yaml
# To get started with Dependabot version updates, you'll need to specify which
# package ecosystems to update and where the package manifests are located.
# Please see the documentation for all configuration options:
# https://docs.github.com/en/code-security/dependabot/working-with-dependabot/dependabot-options-reference

version: 2
updates:
  - package-ecosystem: 'terraform' # See documentation for possible values
    directory: '/' # Location of package manifests
    schedule:
      interval: 'daily'
    # Optional: Limit number of open PRs for version updates
    open-pull-requests-limit: 5
    # Optional: Add labels to PRs
    labels:
      - 'dependencies'
      - 'terraform'
    # Optional: Add reviewers
    reviewers:
      - 'pwd9000'
    # Optional: Add assignees
    assignees:
      - 'pwd9000'
    # Optional: Customise commit message prefix
    commit-message:
      prefix: 'chore'
      include: 'scope'
```

Once the dependabot `YAML` file has been created and committed to the repository, you will notice that it automatically opened a Pull-Request for me, showing me that my provider version is out of date:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Automate-Terraform-Registry/assets/pr1.png)

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Automate-Terraform-Registry/assets/pr2.png)

Now we can decide whether we want to accept this version bump or not by either accepting and merging the pull request or cancelling and closing the pull request. As you can also see the schedule interval is set to `daily` which means **dependabot** will check everyday to see if there are any new terraform provider versions released and automatically open a pull request if there is. Pretty neat!

### Automate Releases - Terraform Registry

Say for example we take this version change (or any changes and improvements on our module), and after testing the changes on our module we want to create a new public release version of our module on the public **[Terraform Registry](https://registry.terraform.io/)**.

**NOTE:** I have written a public **GitHub marketplace Action** called: [Terraform Tests for AZURE](https://github.com/marketplace/actions/terraform-tests-for-azure) to do automated tests. Check it out.

After testing to perform a release we will create a **workflow**.

**Security Note:** It's recommended to use minimal permissions for GitHub Actions workflows. We'll add explicit permissions to our workflow.

Under the `.github` directory we will create a new folder called `workflows` and in this folder we will create another `YAML` file called: [push-tf-registry.yml](https://github.com/Pwd9000-ML/terraform-azurerm-dynamic-subnets/blob/master/.github/workflows/push-tf-registry.yml).

```yml
### This workflow can be used to manually create new release versions from a tag push using e.g. VSCODE ###
name: Release to terraform public registry

on:
  push:
    tags:
      - 'v*.*.*' # More specific pattern for semantic versioning

permissions:
  contents: write # Required for creating releases

jobs:
  Release:
    name: Release
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4.2.2 # Updated to latest version
      - uses: ncipollo/release-action@v1.14.0 # Updated to latest version
        with:
          generateReleaseNotes: true
          name: 'v${{ github.ref_name }}'
          token: ${{ secrets.GITHUB_TOKEN }}
```

This workflow will trigger on a tag push and create a **GitHub Release**. As per the [documented process](https://www.terraform.io/registry/modules/publish#releasing-new-versions) for creating a new release on the public terraform registry we have to use a valid semantic version, optionally prefixed with a v.

Example of valid tags are: v1.0.1 and 0.9.4. To publish a new module, you must already have at least one tag created.

To release a new version, create and push a new tag with the proper format. The webhook will notify the registry of the new version and it will appear on the registry usually in less than a minute.

The current version of my public module is `version = 1.0.3`:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Automate-Terraform-Registry/assets/pre.png)

This corresponds with the current release on the **GitHub** repository hosting the module:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Automate-Terraform-Registry/assets/pre2.png)

With the **GitHub workflow** set up, Let's create a new tag and push that to our repository on GitHub. The workflow will trigger and create a new release for us automatically, so let's try it out.

![image.gif](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Automate-Terraform-Registry/assets/tag.gif)

After creating the tag `1.0.4` and pushing the tag to the remote repository. Notice that the workflow has triggered and ran, creating a new release automatically using the tag version number:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Automate-Terraform-Registry/assets/work.png)

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Automate-Terraform-Registry/assets/rel.png)

**NOTE:** The **GitHub Action** that creates the release has an input setting: `generateReleaseNotes: true`, so the release notes have also been created for us dynamically.

As you can see the new version is also now published on the **Terraform Registry**

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Automate-Terraform-Registry/assets/rel2.png)

That's it, now we can automatically let **Dependabot** take care of our terraform provider versioning and create pull requests automatically when new provider versions are released.

Additionally we also have a really straight forward easy way to create new releases of our own module by simply creating a valid semantic version number as a tag and then push that tag to our remote repository where the **GitHub Workflow** will create a release for us based on the semantic version tag.

As an added bonus, I also added another section onto the **Dependabot** config file to also regularly check the **GitHub Actions** used in the workflow called: `ncipollo/release-action@v1` and `actions/checkout@v4` so when new versions of these actions come out, **Dependabot** will also let me know that I can update my workflow actions (I've also changed my Dependency scans to run on a specific weekday and time as shown below).

```yml
version: 2
updates:
  - package-ecosystem: 'terraform'
    directory: '/' # Location of package manifests
    schedule:
      interval: 'weekly'
      day: 'sunday'
      time: '09:00'
      timezone: 'Europe/London'
    open-pull-requests-limit: 5
    labels:
      - 'dependencies'
      - 'terraform'
    reviewers:
      - 'pwd9000'
    assignees:
      - 'pwd9000'
    commit-message:
      prefix: 'chore'
      prefix-development: 'fix'
      include: 'scope'
    # Optional: Ignore specific versions or version ranges
    ignore:
      - dependency-name: 'hashicorp/azurerm'
        versions: ['2.x', '3.0.0']
    # Optional: Allow specific dependency updates
    allow:
      - dependency-type: 'all'
    # Optional: Target branch for PRs (default is the default branch)
    target-branch: 'main'
    # Optional: Milestone to set on PRs
    milestone: 1
    # Optional: Prefix for PR branch names
    pull-request-branch-name:
      separator: '-'

  - package-ecosystem: 'github-actions'
    # Workflow files stored in the
    # default location of `.github/workflows`
    directory: '/' # Location of package manifests
    schedule:
      interval: 'weekly'
      day: 'friday'
      time: '09:00'
      timezone: 'Europe/London'
    open-pull-requests-limit: 5
    labels:
      - 'dependencies'
      - 'github-actions'
    # Optional: Group updates together
    groups:
      github-actions:
        patterns:
          - 'actions/*'
        update-types:
          - 'minor'
          - 'patch'
```

### Advanced Dependabot Configuration

For more complex scenarios, you can leverage additional Dependabot features:

#### Grouping Dependencies

Starting with Dependabot version 2, you can group related updates together:

```yml
groups:
  terraform-providers:
    patterns:
      - 'hashicorp/*'
      - 'azure/*'
    update-types:
      - 'minor'
      - 'patch'
```

#### Vendor or Cache Dependencies

For ecosystems that support it, you can specify vendoring:

```yml
vendor: true # For ecosystems like Go
```

#### Rebase Strategy

Control how Dependabot handles rebasing:

```yml
rebase-strategy: 'auto' # Options: auto, disabled
```

#### Versioning Strategy

Specify how to update manifest files:

```yml
versioning-strategy: 'increase' # Options: auto, increase, increase-if-necessary, lockfile-only, widen
```

#### Security Updates Configuration

Enable or disable security updates:

```yml
enable-beta-ecosystems: true # For beta ecosystem support
insecure-external-code-execution: 'deny' # Options: allow, deny
```

#### Custom Registry Configuration

For private registries or custom sources:

```yml
registries:
  - terraform-private:
      type: 'terraform-registry'
      url: 'https://my-private-registry.com'
      token: '${{secrets.REGISTRY_TOKEN}}'
```

Note: When using custom registries, ensure the token is properly configured in your repository secrets.

These additional options provide fine-grained control over how Dependabot manages your dependencies, allowing you to customise the automation to fit your team's workflow perfectly.

### Troubleshooting Common Issues

#### Module Not Appearing on Terraform Registry

- Ensure your repository name follows the format: `terraform-<PROVIDER>-<NAME>`
- Verify the webhook is properly configured in your GitHub repository settings
- Check that your tags follow semantic versioning (e.g., v1.0.0, 1.0.0)

#### Dependabot PRs Not Being Created

- Verify the `.github/dependabot.yml` file is in the default branch
- Check repository settings to ensure Dependabot is enabled
- Review the Dependabot logs in the repository's Insights > Dependency graph > Dependabot

#### Release Workflow Failures

- Ensure the `GITHUB_TOKEN` has appropriate permissions
- Verify tag format matches the workflow trigger pattern
- Check that previous releases don't have conflicting names

### Best Practices

1. **Version Constraints**: Use flexible version constraints (`>=`) in modules to avoid forcing specific versions on consumers
2. **Testing**: Always test module changes before creating a new release
3. **Documentation**: Keep your README and examples updated with each release
4. **Security**: Regularly review and merge Dependabot security updates
5. **Semantic Versioning**: Follow semantic versioning strictly:
   - MAJOR version for incompatible API changes
   - MINOR version for backwards-compatible functionality additions
   - PATCH version for backwards-compatible bug fixes

### Fully Automated Testing and Release on changes to IaC

Check out the next blog post on this series: **Using Terraform on GitHub** that shows how to perform fully automated integration test when **Dependabot** opens a PR. Followed by automatically merging that pull request if all tests have finished successfully and then also as a last step automatically deploy a new release/version and pushing that to the Terraform registry: [Automated Terraform Tests for Azure using GitHub Actions](https://dev.to/pwd9000/automated-terraform-tests-for-azure-using-github-actions-4349)

I hope you have enjoyed this post and have learned something new. You can find the code samples used in this blog post on my GitHub project [Terraform module repository - Dynamic Subnets](https://github.com/Pwd9000-ML/terraform-azurerm-dynamic-subnets). :heart:

If you are interested in checking out my public terraform modules for azure, including some cool modules like **OpenAI-Service**, **OpenAI-Private-ChatGpt**, **Custom Role Definitions** and **Sonarqube ACI**, you can find them on the public terraform registry:

- [Pwd9000-ML - Public Terraform Registry Modules](https://registry.terraform.io/search/modules?namespace=Pwd9000-ML)

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [X](https://x.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-pwd9000/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
