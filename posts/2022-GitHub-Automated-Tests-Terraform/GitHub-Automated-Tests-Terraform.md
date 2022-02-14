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

### Public Marketplace GitHub Actions

I actually wrote a public GitHub action which I will use in this tutorial to demonstrate the automated tests. The Github action we will be using is called: [Terraform Tests for AZURE](https://github.com/marketplace/actions/terraform-tests-for-azure).

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Automated-Tests-Terraform/assets/action.png)

### Dependabot

If you look at the following GitHub project: [Terraform module repository - Dynamic Subnets](https://github.com/Pwd9000-ML/terraform-azurerm-dynamic-subnets), you will see there is a special folder path called `.github` and inside that folder is a `YAML` file called: [dependabot.yml](https://github.com/Pwd9000-ML/terraform-azurerm-dynamic-subnets/blob/master/.github/dependabot.yml).

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
      interval: 'weekly'
```

This dependabot file enables **dependabot** on our **GitHub** project and will check our projects root folder for any terraform files that have provider versions configured and checks if they are the latest version.

We discussed **dependabot** in much more detail on the previous tutorial [automate terraform module releases on the public registry using GitHub](https://dev.to/pwd9000/automate-terraform-module-releases-on-the-public-registry-using-github-4775), so take a look at the previous tutorial for more details on enabling **dependabot**.

### Automated Testing

As we know **dependabot** will automatically open a PR if it detects that a version change is available for our terraform module and also show us the file changes.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Automated-Tests-Terraform/assets/pr.png)

It is important to note that **Dependabot** will only open a PR and nothing else. Normally after a PR has been opened a user will look at the PR, perform a code review, and have to also manually go and test whether the changes in that PR will actually work before merging the PR and then creating a new release using the new version of the code.

What we will do instead is automate the entire process from the moment the PR is opened by **dependabot** by creating a workflow to trigger and run based on the Pull Request event.

**NOTE:** In this tutorial we look at PRs opened by **dependabot**, but the testing action can be used in other contexts as well where a user/developer makes any sort of changes/additions/configs to a module, for example if new resources are added to a module. The same testing GitHub Action: [Terraform Tests for AZURE](https://github.com/marketplace/actions/terraform-tests-for-azure) can also be used in such cases to test if those changes will work.

### Creating the Workflow

In our GitHub project: [Terraform module repository - Dynamic Subnets](https://github.com/Pwd9000-ML/terraform-azurerm-dynamic-subnets), inside of the `.github` folder/path, you will see another folder/path called `workflows`, there is a `YAML` workflow called: [dependency-tests.yml](https://github.com/Pwd9000-ML/terraform-azurerm-dynamic-subnets/blob/master/.github/workflows/dependency-tests.yml).

```yml
### This workflow will run only when Dependabot opens a PR on master ###
### Full integration test is done by doing a plan, build and destroy of config under ./tests/auto_test1 ###
### If tests are successful the PR is automatically merged to master ###
### If the merge was completed the next patch version is released and the patch is bumped and pushed to terraform registry ###

name: 'Automated-Dependency-Tests-and-Release'
on:
  workflow_dispatch:
  pull_request:
    branches:
      - master

jobs:
  # Dependabot will open a PR on terraform version changes, this 'dependabot' job is only used to test TF version changes by running a plan, apply and destroy in sequence.
  dependabot-plan-apply-destroy:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
      issues: write
      actions: read
    if: ${{ github.actor == 'dependabot[bot]' }}
    steps:
      - name: Checkout
        uses: actions/checkout@v2

      - name: Run Dependency Tests - Plan AND Apply AND Destroy
        uses: Pwd9000-ML/terraform-azurerm-tests@v1.0.1
        with:
          test_type: plan-apply-destroy ## (Required) Valid options are "plan", "plan-apply", "plan-apply-destroy". Default="plan"
          path: 'tests/auto_test1' ## (Optional) Specify path to test module to run.
          tf_version: latest ## (Optional) Specifies version of Terraform to use. e.g: 1.1.0 Default="latest"
          tf_vars_file: testing.tfvars ## (Required) Specifies Terraform TFVARS file name inside module path (Testing vars)
          tf_key: tf-mod-tests-dyn-subn ## (Required) AZ backend - Specifies name that will be given to terraform state file and plan artifact (testing state)
          az_resource_group: TF-Core-Rg ## (Required) AZ backend - AZURE Resource Group hosting terraform backend storage account
          az_storage_acc: tfcorebackendsa ## (Required) AZ backend - AZURE terraform backend storage account
          az_container_name: ghdeploytfstate ## (Required) AZ backend - AZURE storage container hosting state files
          arm_client_id: ${{ secrets.ARM_CLIENT_ID }} ## (Required - Dependabot Secrets) ARM Client ID
          arm_client_secret: ${{ secrets.ARM_CLIENT_SECRET }} ## (Required - Dependabot Secrets) ARM Client Secret
          arm_subscription_id: ${{ secrets.ARM_SUBSCRIPTION_ID }} ## (Required - Dependabot Secrets) ARM Subscription ID
          arm_tenant_id: ${{ secrets.ARM_TENANT_ID }} ## (Required - Dependabot Secrets) ARM Tenant ID
          github_token: ${{ secrets.GITHUB_TOKEN }} ## (Required) Needed to comment output on PR's. ${{ secrets.GITHUB_TOKEN }} already has permissions.

  ##### If dependency tests are successful merge the pull request #####
  merge_pr:
    needs: dependabot-plan-apply-destroy
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
      contents: write
    if: ${{ github.actor == 'dependabot[bot]' }}
    steps:
      - name: Dependabot metadata
        id: metadata
        uses: dependabot/fetch-metadata@v1.1.1
        with:
          github-token: '${{ secrets.GITHUB_TOKEN }}'

      - name: Auto-merge PR after tests
        run: gh pr merge --auto --merge "$PR_URL"
        env:
          PR_URL: ${{github.event.pull_request.html_url}}
          GITHUB_TOKEN: ${{secrets.GITHUB_TOKEN}}

  ##### Create and automate new release based on next patch version of releases #####
  release_new_version:
    needs: merge_pr
    runs-on: ubuntu-latest
    permissions:
      contents: write
    if: ${{ github.actor == 'dependabot[bot]' }}
    steps:
      - name: Determine version
        id: version
        uses: zwaldowski/semver-release-action@v2
        with:
          bump: patch
          dry_run: true
          github_token: ${{secrets.GITHUB_TOKEN}}

      - name: Create new release and push to registry
        id: release
        uses: ncipollo/release-action@v1
        with:
          generateReleaseNotes: true
          name: 'v${{ steps.version.outputs.version }}'
          tag: ${{ steps.version.outputs.version }}
          token: ${{ secrets.GITHUB_TOKEN }}
```

This workflow will only trigger if a `Pull Request` is opened on the `master` branch:

```yml
name: 'Automated-Dependency-Tests-and-Release'
on:
  workflow_dispatch:
  pull_request:
    branches:
      - master
```

It consists out of 3 jobs: `dependabot-plan-apply-destroy:`, `merge_pr`, and `release_new_version`. Lets take a closer look at each job.

### dependabot-plan-apply-destroy:

This first job uses my public github action: [Terraform Tests for AZURE](https://github.com/marketplace/actions/terraform-tests-for-azure)

```yml
# Dependabot will open a PR on terraform version changes, this 'dependabot' job is only used to test TF version changes by running a plan, apply and destroy in sequence.
dependabot-plan-apply-destroy:
  runs-on: ubuntu-latest
  permissions:
    pull-requests: write
    issues: write
    actions: read
  if: ${{ github.actor == 'dependabot[bot]' }}
  steps:
    - name: Checkout
      uses: actions/checkout@v2

    - name: Run Dependency Tests - Plan AND Apply AND Destroy
      uses: Pwd9000-ML/terraform-azurerm-tests@v1.0.1
      with:
        test_type: plan-apply-destroy ## (Required) Valid options are "plan", "plan-apply", "plan-apply-destroy". Default="plan"
        path: 'tests/auto_test1' ## (Optional) Specify path to test module to run.
        tf_version: latest ## (Optional) Specifies version of Terraform to use. e.g: 1.1.0 Default="latest"
        tf_vars_file: testing.tfvars ## (Required) Specifies Terraform TFVARS file name inside module path (Testing vars)
        tf_key: tf-mod-tests-dyn-subn ## (Required) AZ backend - Specifies name that will be given to terraform state file and plan artifact (testing state)
        az_resource_group: TF-Core-Rg ## (Required) AZ backend - AZURE Resource Group hosting terraform backend storage account
        az_storage_acc: tfcorebackendsa ## (Required) AZ backend - AZURE terraform backend storage account
        az_container_name: ghdeploytfstate ## (Required) AZ backend - AZURE storage container hosting state files
        arm_client_id: ${{ secrets.ARM_CLIENT_ID }} ## (Required - Dependabot Secrets) ARM Client ID
        arm_client_secret: ${{ secrets.ARM_CLIENT_SECRET }} ## (Required - Dependabot Secrets) ARM Client Secret
        arm_subscription_id: ${{ secrets.ARM_SUBSCRIPTION_ID }} ## (Required - Dependabot Secrets) ARM Subscription ID
        arm_tenant_id: ${{ secrets.ARM_TENANT_ID }} ## (Required - Dependabot Secrets) ARM Tenant ID
        github_token: ${{ secrets.GITHUB_TOKEN }} ## (Required) Needed to comment output on PR's. ${{ secrets.GITHUB_TOKEN }} already has permissions.
```

As you can see we have an `if:` expression to say that the job should only run if the PR was opened by **dependabot**, also note that the action I am using in this job will need the ability to add comments/issues on the Pull Request to display any issues and the plans from the terraform runs.  

To do this a special token called `GITHUB_TOKEN` is needed, by default this token in the context of **dependabot** will be **read-only** and so we can give the token additional permissions as you can see from the following `YAML` code:

```yml
permissions:
  pull-requests: write
  issues: write
  actions: read
if: ${{ github.actor == 'dependabot[bot]' }}
```

**NOTE:** To see what extra permissions can be granted to the `GITHUB_TOKEN` see: [Permissions for the github_token](https://docs.github.com/en/actions/security-guides/automatic-token-authentication#permissions-for-the-github_token)

The automated tests are then run using the action: `uses: Pwd9000-ML/terraform-azurerm-tests@v1.0.1`

The following inputs can be used:

| Input | Required | Description | Default |
| --- | --- | --- | --- |
| `test_type` | FALSE | Specify test type. Valid options are `plan`, `plan-apply`, `plan-apply-destroy`. | "plan" |
| `path` | FALSE | Specify path to Terraform module relevant to repo root. (Test module) | "." |
| `tf_version` | FALSE | Specifies the Terraform version to use. | "latest" |
| `tf_vars_file` | TRUE | Specifies Terraform TFVARS file name inside module path. (Test vars) | N/A |
| `tf_key` | TRUE | AZ backend - Specifies name that will be given to terraform state file and plan artifact | N/A |
| `az_resource_group` | TRUE | AZ backend - AZURE Resource Group name hosting terraform backend storage account | N/A |
| `az_storage_acc` | TRUE | AZ backend - AZURE terraform backend storage account name | N/A |
| `az_container_name` | TRUE | AZ backend - AZURE storage container hosting state files | N/A |
| `arm_client_id` | TRUE | The Azure Service Principal Client ID | N/A |
| `arm_client_secret` | TRUE | The Azure Service Principal Secret | N/A |
| `arm_subscription_id` | TRUE | The Azure Subscription ID | N/A |
| `arm_tenant_id` | TRUE | The Azure Service Principal Tenant ID | N/A |
| `github_token` | TRUE | Specify GITHUB TOKEN, only used in PRs to comment outputs such as `plan`, `fmt`, `init` and `validate`. `${{ secrets.GITHUB_TOKEN }}` already has permissions, but if using own token, ensure repo scope. | N/A |

This action has a special input called `test_type:` which can be used to run different types of tests:

- **test_type: "plan"**
  - This test type will only perform a terraform `plan` ONLY against a terraform configuration.
- **test_type: "plan-apply"**
  - This test type will perform a terraform `plan` AND a terraform `apply` in sequence against a terraform configuration.
- **test_type: "plan-apply-destroy"**
  - This test type will perform a terraform `plan`, a terraform `apply` AND a terraform `destroy` in sequence against a terraform configuration.

**WARNING:** Apply tests will create resources in your environment. Please be aware of cost and also please be aware of the environment used. When applying new resources ensure you are using a test subscription or test resource group inside of your test configuration file being targeted by the `path:` input or by using testing vars via a test `TFVARS` file.

As you can see I have written a terraform test in the path: `path: "tests/auto_test1"`

```hcl
terraform {
  backend "azurerm" {}
}

provider "azurerm" {
  features {}
}

##################################################
# MODULE TO TEST                                 #
##################################################
module "dynamic-subnets-test" {
  source                  = "../.."
  network_address_ip      = var.network_ip
  network_address_mask    = var.network_mask
  virtual_network_rg_name = var.resource_group_name
  virtual_network_name    = var.vnet_name
  subnet_config           = var.subnet_config
}
```

As you can see my terraform test is a simple terraform configuration using a source: `source = "../.."`, which will target the root module histed at the root of my project.  
The test actually involves creating a terraform plan, followed by an apply, followed by a destroy in sequence, as I selected input: `test_type: plan-apply-destroy`

Any issues or plans during the tests are then added to the PR as well as artifacts on the workflow.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Automated-Tests-Terraform/assets/planpr.png) ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Automated-Tests-Terraform/assets/destroy.png)

### merge_pr:

The next job in our workflow will only be called if the previous job that did the tests were successful using `needs: dependabot-plan-apply-destroy`:

```yml
##### If dependency tests are successful merge the pull request #####
merge_pr:
  needs: dependabot-plan-apply-destroy
  runs-on: ubuntu-latest
  permissions:
    pull-requests: write
    contents: write
  if: ${{ github.actor == 'dependabot[bot]' }}
  steps:
    - name: Dependabot metadata
      id: metadata
      uses: dependabot/fetch-metadata@v1.1.1
      with:
        github-token: '${{ secrets.GITHUB_TOKEN }}'

    - name: Auto-merge PR after tests
      run: gh pr merge --auto --merge "$PR_URL"
      env:
        PR_URL: ${{github.event.pull_request.html_url}}
        GITHUB_TOKEN: ${{secrets.GITHUB_TOKEN}}
```

This job will automatically merge the Pull Request opened by **dependabot** and the PR will be closed as all tests were successful. Again we need to give the `GITHUB_TOKEN` some additional permissions to be able to merge and close the PR.

### release_new_version:

The last job in our workflow will only be called if the previous job was successful in merging the PR `needs: merge_pr`:

```yml
##### Create and automate new release based on next patch version of releases #####
release_new_version:
  needs: merge_pr
  runs-on: ubuntu-latest
  permissions:
    contents: write
  if: ${{ github.actor == 'dependabot[bot]' }}
  steps:
    - name: Determine version
      id: version
      uses: zwaldowski/semver-release-action@v2
      with:
        bump: patch
        dry_run: true
        github_token: ${{secrets.GITHUB_TOKEN}}

    - name: Create new release and push to registry
      id: release
      uses: ncipollo/release-action@v1
      with:
        generateReleaseNotes: true
        name: 'v${{ steps.version.outputs.version }}'
        tag: ${{ steps.version.outputs.version }}
        token: ${{ secrets.GITHUB_TOKEN }}
```

This job will look at the project releases and determine what the next release version (semantic versioning) should be and then creates a new release automatically. We can decide what we want to increment the version by specifying: `bump: patch` (This can also be `bump: minor` or `bump: major`) depending on how you want to perform your releases, but because this use case is just a version change of the terraform provider dependency a `patch` increment should be fine.

As you can see a new release will automatically be created and reflected on the terraform registry:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Automated-Tests-Terraform/assets/workflow.png)

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Automated-Tests-Terraform/assets/release1.png)

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Automated-Tests-Terraform/assets/release2.png)

I hope you have enjoyed this post and have learned something new. You can find the code samples used in this blog post on my GitHub project [Terraform module repository - Dynamic Subnets](https://github.com/Pwd9000-ML/terraform-azurerm-dynamic-subnets). :heart:

If you are interested in checking out my public terraform modules on the registry here they are:

- [AZURE - Dynamic Subnets](https://registry.terraform.io/modules/Pwd9000-ML/dynamic-subnets/azurerm/latest)
- [AZURE - Secure Backend](https://registry.terraform.io/modules/Pwd9000-ML/secure-backend/azurerm/latest)

I will be adding a few more cool modules on the public registry in due course.

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
