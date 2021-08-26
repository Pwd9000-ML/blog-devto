---
title: Dynamic terraform deployments using DevOps replace tokens
published: false
description: DevOps - Terraform - Replace Tokens
tags: 'tutorial, azure, productivity, devops'
cover_image: assets/main.jpg
canonical_url: null
id: 802801
---

## DevOps Pipeline

Under my repo path: `\terraform-azurerm-resourcegroup\pipelines\`, I have created the following three yaml pipelines (one for each environment):

1. **dev_deployment.yml** (Deploy dev RG)

    ```txt
    // code/terraform-azurerm-resourcegroup/pipelines/dev_deployment.yml
    ```

2. **uat_deployment.yml** (Deploy uat RG)

    ```txt
    // code/terraform-azurerm-resourcegroup/pipelines/uat_deployment.yml
    ```

3. **prod_deployment.yml** (Deploy prod RG)

    ```txt
    // code/terraform-azurerm-resourcegroup/pipelines/prod_deployment.yml
    ```

Now we can configure each pipeline, which will consume its own corresponding variable template file as well as a common variable template file, but use the same terraform configuration code to dynamically deploy the same resource group but each having its own state file, name and tags dynamically.

![pipelines](./assets/pipelines.jpg)

Also remember to set the environments in Azure DevOps as shown on each of our yaml pipelines e.g.:

```txt
// code/terraform-azurerm-resourcegroup/pipelines/dev_deployment.yml#L21-L21
```

![environments](./assets/environments.jpg)

After each pipeline has been run, you will notice that our terraform configuration was dynamically changed each time with the **replace tokens task**, replacing the values on our **TF** and **TFVARS** files.

![replace_tokens](./assets/replace_tokens.jpg)

You'll also see the each resource group have been dynamically created.

![rg_depl](./assets/rg_depl.jpg)

**NOTE:** Remember we changed prod to be in the UK West region on our variable template file for prod.

Also note that each of the deployments have their own unique state file based on the environment as depicted on each of the yaml pipelines and declared in the variable files e.g.:

```txt
// code/terraform-azurerm-resourcegroup/pipelines/dev_deployment.yml#L58-L58
```

![state](./assets/state.jpg)

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my [Github](https://github.com/Pwd9000-ML/blog-devto/tree/master/posts/DevOps-Replace-Tokens/code) page. :heart:

### _Author_

{% user pwd9000 %}
