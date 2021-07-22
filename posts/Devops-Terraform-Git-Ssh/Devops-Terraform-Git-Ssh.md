---
title: Connect Terraform to Azure Devops Git Repos over SSH
published: true
description: DevOps - Terraform - Connecting Git over SSH
tags: 'tutorial, azure, productivity, devops'
cover_image: assets/main-tf-ado.png
canonical_url: null
id: 767794
---

## Terraform module sources?

Terraform supports many different [Module Sources](https://www.terraform.io/docs/language/modules/sources.html). In todays tutorial we look at how we can configure an Azure DevOps repo with SSH and use this repo as a module source in terraform. We will also take a look at how we can use the **install SSH key** DevOps task in a pipeline that runs terraform so that the DevOps agent running the terraform deployment can connect to the DevOps repo as a source over SSH.

## Step 1: Prepare SSH Key

```yaml
steps:
### Link to key vault.
- task: AzureKeyVault@1
  displayName: Keyvault
  inputs:
    azureSubscription: TerraformSP #ADO service connection (Service principal)
    KeyVaultName: 'mykeyvault'
    secretsFilter: '*'
    runAsPreJob: true 

### Install SSH key on ADO agent to access terraform modules git repo.
- task: InstallSSHKey@0
  displayName: 'Install an SSH key'
  inputs:
    knownHostsEntry: '$(git_ssh_known_hosts)' #Variable pulled in from key vault via key vault task above.
    sshPublicKey: '$(terraform-git-ssh-pub)' #Variable pulled in from key vault via key vault task above.
    sshPassphrase: '$(git_ssh_pass)' #Variable pulled in from key vault via key vault task above.
    sshKeySecureFile: 'terraform_rsa' #This was originally renamed from id_rsa and uploaded into secure files library on the project hosting our TF modules repo
```

### Terraform source module example

Here is an example of how we can reference our Azure DevOps repo containing our module code in our terraform deployment.

```hcl
module "mymodule" {

  source = "git::git@ssh.dev.azure.com:v3/Org/Project/repo"
  
}
```

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my [Github](https://github.com/Pwd9000-ML/blog-devto/tree/master/posts/Devops-Terraform-Git-Ssh/code). :heart:

### _Author_

Marcel.L - pwd9000@hotmail.co.uk
