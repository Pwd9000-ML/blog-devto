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

Terraform supports many different [Module Sources](https://www.terraform.io/docs/language/modules/sources.html). In todays tutorial we look at how we can configure an Azure DevOps repo with SSH and use this repo as a module source in terraform.

## Step 1 - Prepare SSH Key

First we have to create a SSH key pair:  

1. Install Git for windows.
2. In a powershell console run: `ssh-keygen`. This will create a private key (id_rsa) and a public key (id_rsa.pub) under `%UserProfile%/.ssh`.
3. If a passphrase was also given, make a note of the passphrase as we will use that later on.
4. Next run: `ssh-keyscan -H -t rsa ssh.dev.azure.com > $env:userprofile/.ssh/known_hosts`. The Content of this file will be used later on in the setup of the [Install SSH Key](https://github.com/MicrosoftDocs/azure-devops-docs/blob/master/docs/pipelines/tasks/utility/install-ssh-key.md) devops task in a DevOps pipeline.

## Step 2 - Prepare Azure Devops

3. (Optional) If a passphrase was used in the generation of the ssh key pair in step one, you can create a variable in the azure devops pipeline `git_ssh_pass` and add the secret value. This can also be stored as a secret instead in Azure key vault and accessed via the **_azure key vault_** [devops task](https://docs.microsoft.com/en-us/azure/devops/pipelines/release/azure-key-vault?view=azure-devops).
4. Create the [Install SSH Key](https://github.com/MicrosoftDocs/azure-devops-docs/blob/master/docs/pipelines/tasks/utility/install-ssh-key.md) devops task and use the following parameters:

- Display Name: Install an SSH key
- Known Hosts Entry: $(git_ssh_known_hosts)
- SSH Public Key: $(git_ssh_pub)
- Passphrase: [none] (if no passphrase was generated in ssh key pair generation or [$(git_ssh_pass)] if a password was used)
- SSH Key: id_rsa (This was the private key we uploaded into secure files library)

Thats it, the [Install SSH Key](https://github.com/MicrosoftDocs/azure-devops-docs/blob/master/docs/pipelines/tasks/utility/install-ssh-key.md) Devops task will now install and set the SSH up on the ADO agent to connect securely to AzureDevOps git repo where our terraform module code is kept.

### Devops Yaml pipeline example

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
