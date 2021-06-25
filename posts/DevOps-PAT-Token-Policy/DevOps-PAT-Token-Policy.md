---
title: Restrict Azure DevOps PAT tokens with Azure AD policy
published: false
description: DevOps - Personal Access Token (PAT) policy
tags: 'tutorial, azure, devops, security'
cover_image: assets/azure-pat.png
canonical_url: null
id: 739025
---

## What is an Azure DevOps Personal Access Token (PAT)?

So you might be wondering what exactly is an Azure DevOps PAT token and why is this important?
A personal access token (PAT) is used as an alternative to using a password to authenticate into Azure DevOps.

When you're working with third-party tools, APIs or the command line that don't support Microsoft or Azure AD accounts or you don't want to provide your primary credentials to the tool, you can make use of PATs.

PATs are easy to create when you need them and easy to revoke when you don’t.

![newPat](./assets/new-pat.png)

When creating a new PAT you can select the organization where you want to use the token, and then choose a lifespan for your token. Say for example making it only active for a period of 30days. A PATs lifetime can also be extended when needed, but cannot be for any period longer than the maximum of 2 years. You can also specify granular permissions / [scopes](https://docs.microsoft.com/en-us/azure/devops/integrate/get-started/authentication/oauth?view=azure-devops#scopes) to specify what access the token will authorise.

### _Author_

Marcel.L - pwd9000@hotmail.co.uk
