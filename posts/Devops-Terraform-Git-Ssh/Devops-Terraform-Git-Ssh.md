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



### Devops Yaml pipeline example

Here is a basic yaml pipeline example of the tasks/steps to read in secrets as variables from key vault and also including **install SSH keys** task.

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
    sshKeySecureFile: 'terraform_rsa' #This was originally renamed from id_rsa
```

### Terraform source module example

```hcl
module "mymodule" {

  source = "git::git@ssh.dev.azure.com:v3/Org/Project/repo"
  
}
```

### _Author_

Marcel.L - pwd9000@hotmail.co.uk
