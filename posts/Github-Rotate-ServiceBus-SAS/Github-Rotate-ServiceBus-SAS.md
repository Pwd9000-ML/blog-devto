---
title: Automate Azure Service Bus SAS tokens with Github
published: false
description: Github - Actions - Automate Service Bus SAS tokens
tags: 'actionshackathon21, security, azure, github'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Github-Rotate-ServiceBus-SAS/assets/main-sb.png'
canonical_url: null
id: 897066
---

## Overview

In todays tutorial I will demonstrate how to use PowerShell and Github Actions to automate Azure Service Bus SAS token generation for new tokens with a validity period of 30 minutes and securely store the newly generated SAS tokens inside of an Azure Key Vault ready for consumption.

We will create an [Azure Service Bus](https://docs.microsoft.com/en-gb/azure/service-bus-messaging/service-bus-messaging-overview) and [Key Vault](https://docs.microsoft.com/en-gb/azure/key-vault/general/overview) and a single github workflow to handle our SAS token generation as well as a service principal / Azure identity to fully automate everything. When our github workflow is triggered the workflow will generate a Service Bus SAS token that will only be valid for 30 minutes and store the SAS token inside of the key vault (The token validity period can be adjusted based on your needs or requirement).

This means that whenever we need a temporary SAS token to call our Azure service bus we can process this workflow to generate the 30 min token for us and then access the token securely from our key vault using a different process or even a different github workflow (which will be demonstrated by our second workflow for the purpose of this demo).

Lets take a look at a sample use case flow diagram of how this will look like:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Github-Rotate-ServiceBus-SAS/assets/flowdiag.png)

**Note:** Maintaining Service Bus SAS tokens using an Azure key vault is particularly useful for teams who maintain secrets management and need to ensure that only relevant users, principals and processes can access secrets from a secure managed location and also be rotated on a regular basis. Azure key vaults are also particularly useful for security or ops teams who maintain secrets management, instead of giving other teams access to our deployment repositories in Github, teams who look after deployments no longer have to worry about giving access to other teams in order to manage secrets as secrets management will be done from an Azure key vault which nicely separates roles of responsibility when spread across different teams.

### Protecting secrets in github

[Github Secrets](https://docs.github.com/en/actions/reference/encrypted-secrets) is a great way that will allow us to store sensitive information in our organization, repository, or repository environments. In fact we will set up github secrets later in this tutorial that will allow us to authenticate to Azure, and also store our Service Bus primary key used to generate SAS tokens from.

Even though this is a great feature to be able to have secrets management in Github, you may be looking after many repositories all with different secrets, this can become an administrative overhead when secrets or keys need to be rotated on a regular basis for best security practice, that's where [Azure key vault](https://docs.microsoft.com/en-gb/azure/key-vault/general/overview) can also be utilized as a central source for all your secret management in your GitHub workflows.

### What do we need to start generating Service Bus SAS tokens?

For the purpose of this demo and so you can follow along, I will set up the Azure environment with all the relevant resources described below.

1. **Resource Group:** This will be where we will create and group all of our Azure resources together.
2. **Service Bus Namespace:** We will create a service Bus Namespace and Queue.
3. **Azure key vault:** This will be where we centrally store, access and manage all our Service Bus SAS tokens.
4. **Azure AD App & Service Principal:** This is what we will use to authenticate to Azure from our github workflow.
5. **Github repository:** This is where we will keep all our source code and workflows.

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my [Github](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/Github-Rotate-ServiceBus-SAS/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}
