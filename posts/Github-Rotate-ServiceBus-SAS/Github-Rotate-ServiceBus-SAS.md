---
title: Automate Azure Service Bus SAS tokens with Github
published: false
description: Github - Actions - Automate Service Bus SAS tokens
tags: 'actionshackathon21, security, azure, github'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Github-Rotate-ServiceBus-SAS/assets/Main.png'
canonical_url: null
id: 897066
---

## Overview

In todays tutorial I will demonstrate how to use PowerShell and Github Actions to automate Azure Service Bus SAS token generation for new tokens with a validity period of 30 minutes and securely store the newly generated SAS token inside of an Azure Key Vault.  

We will create an [Azure Service Bus](https://docs.microsoft.com/en-gb/azure/service-bus-messaging/service-bus-messaging-overview) and [Key Vault](https://docs.microsoft.com/en-gb/azure/key-vault/general/overview) in Azure and a single github workflow as well as a service principal / Azure identity to fully automate everything. When our github workflow is triggered the workflow will generate a Service Bus SAS token that will only be valid for 30 minutes and store the SAS token inside of the key vault (The token validity period can be adjusted based on your needs or requirement).  

This means that whenever we need a temporary SAS token to call our Azure service bus we can process this workflow to generate the 30 min token for us and then access the token securely from our key vault using a different process or even a different github workflow.

**Note:** Maintaining Service Bus SAS tokens using an Azure key vault is particularly useful for teams who maintain secrets management and need to ensure that only relevant users, principals and processes can access secrets from a secure managed location and also be rotated on a regular basis. Azure key vaults are also particularly useful for security or ops teams who maintain secrets management, instead of giving other teams access to our deployment repositories in Github, teams who look after deployments no longer have to worry about giving access to other teams in order to manage secrets as secrets management will be done from an Azure key vault which nicely separates roles of responsibility when spread across different teams.

### Protecting secrets in github

When using Github workflows we need the ability to authenticate to Azure, we may also need to sometimes use passwords, secrets, API keys or connection strings in our source code in order to pass through some configuration of a deployment which needs to be set during the deployment. So how do we protect these sensitive pieces of information that our deployment needs and ensure that they are not in our source control when we start our deployment?

make use of [Github Secrets](https://docs.github.com/en/actions/reference/encrypted-secrets). This is a great way that will allow us to store sensitive information in our organization, repository, or repository environments. In fact we will set up a github secrets later in this tutorial that will allow us to authenticate to Azure, and also store our Service Bus primary key we will use to generate SAS tokens from.  

Even though this is a great feature to be able to have secrets management in Github, you may be looking after many repositories all with different secrets, this can become an administrative overhead when secrets or keys need to be rotated on a regular basis for best security practice. This is where [Azure key vault](https://docs.microsoft.com/en-gb/azure/key-vault/general/overview) can be utilized as a central source for all our secret management in our GitHub workflows.

### Let's get started. What do we need to start generating Service Bus SAS tokens?

1. **Azure key vault:** This will be where we centrally store, access and manage all our virtual machine local admin passwords.
2. **Azure AD App & Service Principal:** This is what we will use to authenticate to Azure from our github workflow.
3. **Github repository:** This is where we will keep our source control and Github workflow / automation.

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my [Github](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/DevOps-Terraform-Trivy/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}
