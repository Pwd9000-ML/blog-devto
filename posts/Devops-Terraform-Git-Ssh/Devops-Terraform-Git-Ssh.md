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



### _Author_

Marcel.L - pwd9000@hotmail.co.uk
