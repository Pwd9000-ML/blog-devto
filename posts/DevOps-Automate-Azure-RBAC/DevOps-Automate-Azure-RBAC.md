---
title: Automate Azure Role Based Access Control (RBAC) with DevOps
published: false
description: DevOps - Automate Azure RBAC
tags: 'tutorial, azure, devops, productivity'
cover_image: assets/Azure-RBAC.png
canonical_url: null
id: 688322
---

## What are Azure Roles and Custom Definitions?

When you start working more and more with Azure permission you will undoubtedly have used Azure RBAC (also known as IAM) and have most likely used some of the great [built-in roles](https://docs.microsoft.com/en-us/azure/role-based-access-control/built-in-roles) that have been created and provided by Microsoft, but sometimes you may come across a requirement or need to have a very specific role tailored with a set of permissions that are more granular than what comes out of the box in a standard Azure (RBAC) built-in role.  

Luckily Azure offers a great deal of flexibility when it comes to defining your own custom roles vs built-in roles. This is where [Custom Role Definitions](https://docs.microsoft.com/en-us/azure/role-based-access-control/role-definitions) comes into play.  

Today we will look at how we can utilize Azure DevOps in creating and also updating our Azure (RBAC) custom role definitions through source control and automatically reflecting those changes in Azure through pipelines without much effort.  

If you are still a bit unclear on what Azure RBAC is, or wanted more information have a look at [Microsoft Docs](https://docs.microsoft.com/en-us/azure/role-based-access-control/overview).

## How to automate Custom Role Definitions in Azure using DevOps

Firstly we will need to have an Azure DevOps repository where we can store our custom role definition JSON files.  
If you need more information on how to set up a new repository, have a look [here](https://docs.microsoft.com/en-us/azure/devops/repos/git/create-new-repo?view=azure-devops).  

In my repository I have created 3 main folder paths:
![rbac-repo-structure](assets/RBAC-Repo-Structure).

1. pipelines (Here we will define and create our Azure pipeline)
2. roleDefinitions (Here we will keep all our custom role definitions / or create new ones)
3. scripts (Here we will keep scripts that are used in the pipeline)

Clone the newly set up repository and let's create our first role definition JSON file now. We will create a simple role definition JSON that will only allow resource health read permissions, because we want to give someone the ability to look at resource health within a subscription in our tenant.  
We will use this JSON template structure to build our definition:

```JSON
{
    "Name": "",
    "IsCustom": true,
    "Description": "",
    "Actions": [],
    "NotActions": [],
    "AssignableScopes": []
}
```

Our complete definition will look something like this:

```JSON
{
    "Name": "CUSTOM-RESOURCEHEALTH-Reader",
    "IsCustom": true,
    "Description": "Users with rights to only view Azure resource/service/subscription health.",
    "Actions": [
        "Microsoft.ResourceHealth/*/read"
    ],
    "NotActions": [],
    "AssignableScopes": [
        "/subscriptions/<subscriptioId1>"
    ]
}
```

**Note:** We can add more subscriptions to our assignable scopes or even use management groups if required. But for the purpose of this tutorial we only want to make the role available to a single Azure subscription.  

Other valuable links for reference when creating custom role definitions:  

* [Operations:](https://docs.microsoft.com/en-us/azure/role-based-access-control/resource-provider-operations)
* [Operations format:](https://docs.microsoft.com/en-us/azure/role-based-access-control/role-definitions#operations-format)
* [Assignable Scopes:](https://docs.microsoft.com/en-us/azure/role-based-access-control/role-definitions#assignablescopes)

## _Author_

Marcel.L - pwd9000@hotmail.co.uk
