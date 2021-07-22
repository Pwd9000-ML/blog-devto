---
title: Connect Terraform to Azure Devops Git Repos over SSH
published: false
description: DevOps - Terraform - Connecting Git over SSH
tags: 'tutorial, azure, productivity, devops'
cover_image: assets/main-tf-ado.png
canonical_url: null
id: 767794
---

## Terraform module sources?

Terraform supports many different [Module Sources](https://www.terraform.io/docs/language/modules/sources.html). In todays tutorial we look at how we can configure an Azure DevOps repo with SSH and use this repo as a module source in terraform. We will also create a DevOps pipeline that will trigger a basic terraform deployment using a Azure DevOps repo as source and connect to it over SSH.

## Step 1 - Prepare SSH Key



### Devops Yaml pipeline example

Here is a yaml pipeline example of the tasks/steps to read in secrets/variables from key vault and also the for the **install SSH keys** task.

```yaml
todo
```

### Terraform source module example

```hcl
module "terraform_aws_eks" {

  source = "git::git@ssh.dev.azure.com:v3/Org/Project/repo"
  
}
```

### _Author_

Marcel.L - pwd9000@hotmail.co.uk
