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

Terraform supports many different [Module Sources](https://www.terraform.io/docs/language/modules/sources.html). In todays tutorial we look at how we can configure our Azure DevOps repo with SSH and use this repo as a module source in terraform.

## Step 1 (Prepare SSH Key)

------

First we have to create the SSH key pair:  

1. Install Git for windows.
2. In a powershell console run:

    ```powershell
    ssh-keygen
    ```

    (This will create a private key (id_rsa) and a public key (id_rsa.pub)) under %UserProfile%/.ssh
3. Next run:

    ```powershell
    ssh-keyscan -H -t rsa ssh.dev.azure.com > $env:userprofile/.ssh/known_hosts
    ```

    Needed if The Content of this file can be used later on in the setup of the "Install SSH Key" devops task

## Step 2 (Prepare Azure Devops)

------

1. Copy the private key file (id_rsa) into azure pipelines -> Library -> Secure files
    (this file may be renamed to make it more friendly to use later on in the task)
2. Under the user settings in AzureDevops go to SSH public keys and select "Add"
3. Give a description and add the contents of the file created (id_rsa.pub)

## Step 3 (Using Install SSH Key devops task)

------

1. Create a variable in azure devops pipeline "git_ssh_pub" and add the content of file (id_rsa.pub)
(This can also be stored in keyvault and accessed via the **_azure key vault_** task)
Issue: https://github.com/microsoft/azure-pipelines-tasks/issues/11854
2. Create a variable in azure devops pipeline "git_ssh_known_hosts" and add the content of file (known_hosts) created above with ssh-keyscan.
(This can also be stored in keyvault and accessed via the **_azure key vault_** task)
Issue: https://github.com/microsoft/azure-pipelines-tasks/issues/11854
3. Create Devops Task Install SSH Key and use the following parameters:

- Display Name: Install an SSH key
- Known Hosts Entry: $(git_ssh_known_hosts)
- SSH Public Key: $(git_ssh_pub)
- Passphrase: [none] (if no passphrase was generated in ssh key pair generation)
- SSH Key: id_rsa (This was the private key we uploaded into secure files library)

Thats it, Azure Devops task will now install and set the SSH up on the ADO agent to connect securely to AzureDevOps git repos:

### Terraform source module example

```hcl
module "terraform_aws_eks" {

  source = "git::git@ssh.dev.azure.com:v3/Org/Project/repo"

}
```

NOTE: To use git source, the module must be on the repo root, so in cases where git is used to publish modules, each module would require its own repo.

### _Author_

Marcel.L - pwd9000@hotmail.co.uk
