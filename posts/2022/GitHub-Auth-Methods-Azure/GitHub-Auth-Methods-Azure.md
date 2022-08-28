---
title: GitHub authentication methods for Azure
published: false
description: GitHub authentication methods for Azure
tags: 'github, azure, authentication, devsecops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Auth-Methods-Azure/assets/main0.png'
canonical_url: null
id: 1177675
date: '2022-08-27T15:37:53Z'
---

## Overview

When you're working with **GitHub Actions** and start to write and develop automation **workflows** you will sometimes need to connect your **workflow** to different platforms, such as a **cloud provider** for example, to allow your **workflows** access and permissions to perform actions on the cloud provider. Thus you will need to **connect** and **authenticate** your **workflows** with the cloud provider.

Today we will look at two ways you can link and authenticate your **GitHub Action workflows** with **Azure**, a popular Microsoft cloud provider.

In both methods we will create what is known as an [app registration/service principal](https://docs.microsoft.com/en-us/azure/active-directory/develop/app-objects-and-service-principals), assigning permissions to the principal and link the principal with GitHub to allow our **workflows** to authenticate and perform relevant tasks.

**NOTE:** If you are familiar with using **Azure DevOps** and **Azure pipelines**, this is very similar to [service connections](https://docs.microsoft.com/en-us/azure/devops/pipelines/library/service-endpoints?view=azure-devops&tabs=yaml).

## Method 1 - Client and Secret

## Method 2 - Open ID Connect (OIDC)

## Conclusion

xxxxxxxx

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my published [GitHub](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2022/GitHub-Auth-Methods-Azure/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
