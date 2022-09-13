---
title: GitHub commit verification using SSH
published: false
description: GitHub commit verification using SSH
tags: 'github, git, devops, devsecops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Verified-Commits-SSH/assets/main.png'
canonical_url: null
id: 1192184
---

## Overview

Today we will discuss a very important security question that may not be as obvious at first glance.  

**Verifying** commits by **signing** each commit with an **SSH key**. Implementing **commit verification** gives assurance about the **authenticity** of the author of commits made to your code.

GitHub now supports **SSH commit verification**, so you can **sign** commits and tags locally using a self-generated SSH public key, which will give others confidence about the origin of a change you have made. If a commit or tag has an SSH signature that is cryptographically verifiable, GitHub makes the commit or tag **"Verified"** or **"Partially Verified"**.

Signing commits adds a layer of protection for your codebase. We will also look at how we can actively enforce **signature verification** to prevent unsigned commits from being pushed to your repositories.

## Example - Security liability

Let's take a quick look at an example first. Recently a user called **"Pwd9000-ML"** has made a code change on my repository and committed those changes to my projects codebase. Have a look at the following git commit:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Verified-Commits-SSH/assets/fake01.png)

Doesn't look like anything out of the norm.

As you might have guessed, **my own** user account is called **"Pwd9000-ML"**, this change didn't actually come from me.  
In fact, anyone can spoof a **Git commit** or **author** name with just a few terminal commands and pretend to be someone else, for example:

```txt
$ git config user.name "Pwd9000-ML"
$ git config user.email "fake.email@spoofed.com"
$ git commit -m "Added awesome new feature"
```

This poses a big security question. If you can't **verify** who is pushing code to your repository, how will you know if your codebase is being hijacked by someone pretending to be someone else?

## Solution

Thankfully **GitHub** has made this so easy.

### Enable vigilant mode

First let's turn on something called **[vigilant mode](https://docs.github.com/en/authentication/managing-commit-signature-verification/displaying-verification-statuses-for-all-of-your-commits)**, where we enable displaying verification statuses for all git commits.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Verified-Commits-SSH/assets/fake02.png)

Notice that the **spoofed** commit now shows as **"Unverified"**.

To enable vigilant mode:

1. Navigate to your GitHub account **'Settings'**. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Verified-Commits-SSH/assets/vig01.png)

2. Navigate to **'SSH and GPG keys'** and tick **'Flag unsigned commits as unverified'**. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Verified-Commits-SSH/assets/vig02.png)

### Create a SSH signing key

Secondly we will enable **SSH commit verification** so that any future commits will be signed and shown as **"Verified"**.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Verified-Commits-SSH/assets/veri01.png)

To enable SSH commit verification:

1.

## Conclusion

I hope you have enjoyed this post and have learned something new. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
