---
title: Automate password rotation with Github and Azure (Part 2)
published: true
description: Automate VM password rotation using Github and Azure key vault
tags: 'githubactions, secdevops, github, azure'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Automate-VM-Password-Rotation-Part2/assets/main.png'
canonical_url: null
id: 957428
series: Automate password rotation
date: '2022-01-16T17:32:53Z'
---

### Overview

Welcome to part 2 of my series on **automating password rotation**. A few months ago I published a tutorial on how to automate password rotation using a **GitHub Action workflow** and an **Azure key vault**. Due to the popularity of that post I decided to create a public **GitHub Action** on the GitHub Actions marketplace for anyone to use in their own environments.

In this second part of the series I will discuss how to make use of the public marketplace action. For a full in depth understanding on the concepts I am using I would recommend going through Part 1 first.

- Link to GitHub Action on the public marketplace: [Rotate AZURE Virtual Machine Passwords](https://github.com/marketplace/actions/rotate-azure-virtual-machine-passwords)

- Link to my public GitHub repository hosting this action: [GitHub Repository](https://github.com/Pwd9000-ML/azure-vm-password-rotate)

### Concept

This Action will connect to a provided AZURE key vault as input and will loop through each secret key (server name). For each server, automatically generate a random unique password (default 24char), set that password against the VM and save the password value against the relevant secret key in the key vault. This will allow you to automate, maintain and manage all your server passwords from a centrally managed key vault in AZURE by only giving relevant access when required by anyone via key vault permissions.

- The Azure key vault must be pre-populated with `Secret Keys`, where each `key` represents a server name:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/azure-vm-password-rotate/master/assets/kvsecrets.png)

You can use the [AzurePreReqs](https://github.com/Pwd9000-ML/azure-vm-password-rotate/tree/master/azurePreReqs) script to create a key vault, generate a GitHub Secret to use as `AZURE_CREDENTIALS` and sets relevant RBAC access on the key vault, `Key Vault Officer`, as well as `Virtual Machine Contributor` over virtual machines in the Azure subscription.

See [Part 1](https://dev.to/pwd9000/automate-password-rotation-with-github-and-azure-412a) of this series on setting up the Azure key vault and GitHub Secret Credential (if needed).

## GitHub Action Inputs

| Inputs | Required | Description | Default |
| --- | --- | --- | --- |
| key-vault-name | True | Name of the Azure key vault pre-populated with secret name keys representing server names hosted in Azure. | N/A |
| password-length | False | The amount of characters in the password. | 24 |

## INSTALLATION

Copy and paste the following snippet into your .yml file.

```yml
- name: Rotate VMs administrator passwords
    uses: Pwd9000-ML/azure-vm-password-rotate@v1.0.2
    with:
      key-vault-name: ${{ env.KEY_VAULT_NAME }}
      password-length: 24 ##Optional configuration
```

## Example Usage

Here is a link to an example [workflow file](https://github.com/Pwd9000-ML/azure-vm-password-rotate/blob/master/exampleWorkflows/rotate-vm-passwords.yml)

## Example - Rotate VM Passwords every monday at 09:00 UTC

```yml
name: Update Azure VM passwords
on:
  workflow_dispatch:
  schedule:
    - cron: '0 9 * * 1' ##Runs at 9AM UTC every Monday##

jobs:
  publish:
    runs-on: windows-latest
    env:
      KEY_VAULT_NAME: 'your-key-vault-name'

    steps:
      - name: Check out repository
        uses: actions/checkout@v2

      - name: Log into Azure using github secret AZURE_CREDENTIALS
        uses: Azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
          enable-AzPSSession: true

      - name: Rotate VMs administrator passwords
        uses: Pwd9000-ML/azure-vm-password-rotate@v1.0.2
        with:
          key-vault-name: ${{ env.KEY_VAULT_NAME }}
```

## Notes

- As per the example above, you also need a GitHub Secret `AZURE_CREDENTIALS` to log into Azure using Action: `Azure/login@v1`

- You can use the [AzurePreReqs](https://github.com/Pwd9000-ML/azure-vm-password-rotate/tree/master/azurePreReqs) script to create a key vault, generate a GitHub Secret to use as `AZURE_CREDENTIALS` and sets relevant RBAC access on the key vault, `Key Vault Officer`, as well as `Virtual Machine Contributor` over virtual machines in the Azure subscription.

- Passwords will only be rotated for `secrets/names` of servers populated in the key vault as `secret` keys. Only virtual machines that are in a `running` state will have their passwords rotated:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/azure-vm-password-rotate/master/assets/runneroutput.png)

- Servers will be skipped if they are not running:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/azure-vm-password-rotate/master/assets/norun.png)

- If a server does not exist or the GitHub Secret `AZURE_CREDENTIALS` does not have access over the Virtual Machine a warning is issued of 'VM NOT found':

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/azure-vm-password-rotate/master/assets/nofind.png)

- DO NOT populate the key vault with servers that act as Domain Controllers.

## Versions of runner that can be used

At the moment only windows runners are supported. Support for all runner types will be released soon.

| Environment         | YAML Label                         |
| ------------------- | ---------------------------------- |
| Windows Server 2019 | `windows-latest` or `windows-2019` |
| Windows Server 2016 | `windows-2016`                     |

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my published [Github Action](https://github.com/Pwd9000-ML/azure-vm-password-rotate) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}
