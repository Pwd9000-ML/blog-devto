---
title: Connect Terraform to Azure DevOps Git Repos over SSH
published: true
description: DevOps - Terraform - Connecting Git over SSH
tags: 'terraform, azuredevops, iac, devops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/Devops-Terraform-Git-Ssh/assets/main-tf-tips.png'
canonical_url: null
id: 767794
series: Terraform Pro Tips
date: '2021-07-22T10:52:57Z'
---

## Terraform module sources?

Terraform supports many different [Module Sources](https://www.terraform.io/docs/language/modules/sources.html). In todays tutorial we look at how we can configure an Azure DevOps repo with SSH and use this repo as a module source in terraform. We will also take a look at how we can use the **install SSH key** DevOps task in a pipeline that runs terraform so that the DevOps agent running the terraform deployment can connect to the DevOps repo as a source over SSH.

## Step 1: Prepare SSH Key

First we have to create a SSH key pair:

- Install Git for windows.
- In a powershell console run: `ssh-keygen`. This will create a private key: `id_rsa` and a public key: `id_rsa.pub` under the following path: `%UserProfile%/.ssh`.
- If a passphrase was used in the creation of the key pair, make a note of the passphrase as we will need it later on.
- Next run: `ssh-keyscan -H -t rsa ssh.dev.azure.com > $env:userprofile/.ssh/known_hosts`. The content of the file will be used later on in the setup of the [Install SSH Key](https://github.com/MicrosoftDocs/azure-devops-docs/blob/main/docs/pipelines/tasks/utility/install-ssh-key.md) devops task in our DevOps pipeline.

![sshkey](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/Devops-Terraform-Git-Ssh/assets/sshkey.png)

## Step 2: Prepare Azure Devops

- Copy the private key file created in the previous step `id_rsa` into azure **pipelines -> Library -> Secure files**. The file can be renamed to make it more friendly to use later on in the [Install SSH Key](https://github.com/MicrosoftDocs/azure-devops-docs/blob/main/docs/pipelines/tasks/utility/install-ssh-key.md) devops task. In my case I have renamed my private key to `terraform_rsa`.

  ![securefile01](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/Devops-Terraform-Git-Ssh/assets/secfile.png)

- Under the **user settings** in Azure Devops go to SSH public keys and select **Add**. Give a name and add the contents of the file created `id_rsa.pub`. In my case I have renamed my public key to `terraform_rsa.pub`.

  ![sshpub](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/Devops-Terraform-Git-Ssh/assets/sshpub.gif)

## Step 3: How to use _Install SSH Key_ devops task

When using an Azure DevOps pipeline to execute terraform code from a DevOps agent referencing an Azure Devops git Repo as a module source, we can make use of the [Install SSH Key](https://github.com/MicrosoftDocs/azure-devops-docs/blob/main/docs/pipelines/tasks/utility/install-ssh-key.md) devops task to install the SSH key pair we just created onto the DevOps agent that will be executing the terraform code.

We will create a few variables next. These variables can either be created inside of a [variable group](https://docs.microsoft.com/en-us/azure/devops/pipelines/library/variable-groups?view=azure-devops&tabs=yaml#use-a-variable-group/?wt.mc_id=DT-MVP-5004771) or a [key vault](https://docs.microsoft.com/en-us/azure/key-vault/general/overview/?wt.mc_id=DT-MVP-5004771) and accessed using the [Azure key vault task](https://docs.microsoft.com/en-us/azure/devops/pipelines/release/azure-key-vault?view=azure-devops/?wt.mc_id=DT-MVP-5004771) in our devops pipeline.

- Create a **ssh public key** variable that will be used in our pipeline: `terraform-git-ssh-pub` and add the content of file `id_rsa.pub`. This can also be stored as a secret in Azure key vault instead and can be accessed as variables in our pipeline using the **azure key vault** [devops task](https://docs.microsoft.com/en-us/azure/devops/pipelines/release/azure-key-vault?view=azure-devops/?wt.mc_id=DT-MVP-5004771).
- Create a **known hosts** variable that will be used in our pipeline: `git_ssh_known_hosts` and add the content of file `known_hosts` created earlier with `ssh-keyscan`. This can also be stored as a secret in Azure key vault instead and can be accessed as variables in our pipeline using the **azure key vault** [devops task](https://docs.microsoft.com/en-us/azure/devops/pipelines/release/azure-key-vault?view=azure-devops/?wt.mc_id=DT-MVP-5004771).
- (Optional) If a passphrase was used in the generation of the ssh key pair in step one, you can create a variable that will be used in our pipeline: `git_ssh_pass` and add the secret value. This can also be stored as a secret in Azure key vault instead and can be accessed as variables in our pipeline using the **azure key vault** [devops task](https://docs.microsoft.com/en-us/azure/devops/pipelines/release/azure-key-vault?view=azure-devops/?wt.mc_id=DT-MVP-5004771).
- Create the [Install SSH Key](https://github.com/MicrosoftDocs/azure-devops-docs/blob/main/docs/pipelines/tasks/utility/install-ssh-key.md) devops task and use the following parameters:

1. Display Name: Install an SSH key
2. Known Hosts Entry: $(git_ssh_known_hosts)
3. SSH Public Key: $(terraform-git-ssh-pub)
4. Passphrase: $(git_ssh_pass) (Note: if no passphrase was used when the ssh key pair was generated, this can be left as [none])
5. SSH Key: terraform_rsa (This was the private key we uploaded into secure files library in step2, which we renamed from `id_rsa`)

Thats it, the [Install SSH Key](https://github.com/MicrosoftDocs/azure-devops-docs/blob/main/docs/pipelines/tasks/utility/install-ssh-key.md) Devops task will now install the SSH key on the Azure DevOps agent, allowing our terraform deployment to connect securely to our Azure DevOps git repo hosting our modules over ssh.

### Devops Yaml pipeline example

Here is a yaml pipeline example of the tasks/steps to read in secrets as variables from the **key vault** task and including the **install SSH keys** task.

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
  source = "git::ssh://git@ssh.dev.azure.com/v3/<OrgName>/<ProjectName>/<RepoName>//<SubPath>?ref=<VersionRef>"
}
```

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my [GitHub](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2021/Devops-Terraform-Git-Ssh/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
