---
title: Restrict Azure DevOps PAT tokens with Azure AD policy
published: true
description: DevOps - Personal Access Token (PAT) policy
tags: 'azure, devops, devopssecurity, azuredevops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-DevOps-PAT-Token-Policy/assets/azure-pat2.png'
canonical_url: null
id: 739025
date: '2021-06-25T13:31:42Z'
---

## What is an Azure DevOps Personal Access Token (PAT)?

A personal access token (PAT) is used as an alternative to using a password to authenticate into Azure DevOps. When you're working with third-party tools, APIs or the command line that don't support Microsoft or Azure AD accounts or you don't want to provide your primary credentials to the tool, you can make use of PATs.

PATs are easy to create when you need them and easy to revoke when you don’t.

![newPat](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-DevOps-PAT-Token-Policy/assets/new-pat2.png)

When creating a new PAT you can select the organization where you want to use the token, and then choose a lifespan for your token. Say for example making it only active and usable for a period of 30 days. A PATs lifetime can be extended if needed, but cannot be longer than the maximum period of 1 year. You can also specify granular [permissions scopes](https://docs.microsoft.com/en-us/azure/devops/integrate/get-started/authentication/oauth?view=azure-devops#scopes) to specify what access is authorised.

## Restricting personal access token (PAT) scope and lifespan via Azure AD tenant policy

So PATs are really handy and make it easy to authenticate against Azure DevOps to integrate with your tools and services. However it also poses a big security risk as leaked tokens could compromise your Azure DevOps account and data, putting your applications and services at risk. Microsoft has recently added some controls to limit the threat surface area posed by leaked PATs. A new set of policies which can be used to restrict the scope and lifespan of your organization’s Azure DevOps personal access tokens (PATs).

## What do we need?

- You would need to connect your Azure DevOps Organisation to Azure AD. [Here are the steps](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/connect-organization-to-azure-ad?view=azure-devops#connect-your-organization-to-azure-ad).

- You would need to be assigned to the **Azure DevOps Administrator** RBAC role in Azure Active Directory.

After your Org has been connected to Azure AD you can navigate to the **Azure Active Directory** tab in the **organization settings**.

![Azuread](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-DevOps-PAT-Token-Policy/assets/azure-ad2.png)

Here you can:

1. Restrict the creation of global personal access tokens (tokens that work for all Azure DevOps organizations accessible by the user).
2. Restrict the creation of full-scoped personal access tokens.
3. Define a maximum lifespan for new personal access tokens.

These policies will apply to all new PATs created by users for Azure DevOps organizations linked to the Azure AD tenant. Each of the policies have an allow list for users and groups who should be exempt from the policy. The list of users and groups in the Allow list will not have access to manage policy configuration.

These policies only apply to new PATs, and will not affect existing PATs that have already been created and are in use. After the policies have been enabled however, any existing, now non-compliant PATs must be updated to be within the restrictions before they can be renewed.

![patpolicy](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-DevOps-PAT-Token-Policy/assets/pat-policy2.png)

For more detailed information have a look at: [Managing Personal Access Tokens with policies](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/manage-pats-with-policies-for-administrators?view=azure-devops).

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}
