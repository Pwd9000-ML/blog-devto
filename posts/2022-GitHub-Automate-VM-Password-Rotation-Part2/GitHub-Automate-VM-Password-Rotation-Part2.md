---
title: Automate password rotation with Github and Azure (Part 2)
published: false
description: Automate VM password rotation using Github and Azure key vault
tags: 'githubactions, secdevops, github, azure'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Automate-VM-Password-Rotation-Part2/assets/main.png'
canonical_url: null
id: 957428
series: Automate password rotation
---

### Overview

Welcome to part 2 of my series on **automating password rotation**. A few months ago I published a tutorial on how to automate password rotation using a **GitHub Action workflow** and an **Azure key vault**. Due to the popularity of that post I decided to create a public **GitHub Action** on the GitHub Actions marketplace for anyone to use in their own environments.  

In this second part of the series I will discuss how to make use of the public marketplace action. For a full in depth understanding on the concepts I am using I would recommend going through Part 1 first.

### Pre-Requirements

As in Part 1 our Pre-Requirements remains the same.

1. **Azure key vault:** This will be where we centrally store, access and manage all our virtual machine local admin passwords.
2. **Azure AD App & Service Principal:** This is what we will use to authenticate to Azure from our github workflow.
3. **Github repository:** This is where we will keep our source control and Github workflow / automation.

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my published [Github Action](https://github.com/Pwd9000-ML/azure-vm-password-rotate) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}
