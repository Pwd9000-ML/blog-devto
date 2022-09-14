---
title: GitHub commit verification using SSH keys
published: true
description: GitHub commit verification using SSH
tags: 'github, git, devops, devsecops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Verified-Commits-SSH/assets/main.png'
canonical_url: null
id: 1192184
date: '2022-09-13T16:16:10Z'
---

## Overview

Today we will discuss a very important security question that may not be as obvious at first glance.

We will take a look at **verifying** git commits by **signing** each commit with a **SSH key** and why it is important.

Implementing **commit verification** gives assurance about the **authenticity** of the author of commits made to your code.

GitHub always supported **commit signing** via GPG keys, but this was usually harder and a bit more tricky to implement.

Very recently GitHub started support for **commit signing and verification** using SSH keys, which really simplifies the process and gives you the same ability to **sign** commits and tags locally using a self-generated SSH public key, which will give others confidence about the origin of a change you have made. If a commit or tag has an SSH signature that is cryptographically verifiable, GitHub makes the commit or tag **"Verified"** or **"Partially Verified"**.

Signing commits adds a layer of protection for your codebase. We will also look at how we can actively enforce **signature verification** to prevent unsigned commits from being pushed to your repositories.

## Security liability - Example

Let's take a quick look at an example first. Recently a user called **"Pwd9000-ML"** has made a code change on my repository and committed those changes to my projects codebase. Have a look at the following git commit:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Verified-Commits-SSH/assets/fake01.png)

To the untrained eye, this doesn't look like anything out of the norm.

As you might have guessed, **my own** user account is called **"Pwd9000-ML"**, but this change didn't actually come from me. So how is this possible?  
Anyone can spoof a **git commit author** name with just a few git commands and pretend to be someone else, for example:

```powershell
git config user.name "Pwd9000-ML"
git config user.email "fake.email@spoofed.com"
git commit -m "Added awesome new feature"
```

This poses a big security question. How can you **verify** who is pushing code to your repository?

## Solution

Thankfully **GitHub** has made it so easy for us to secure our codebase even further by making the following easy to implement features available us.

### 1.) Enable vigilant mode

First let's turn on something called **[vigilant mode](https://docs.github.com/en/authentication/managing-commit-signature-verification/displaying-verification-statuses-for-all-of-your-commits)**, where we enable displaying verification statuses for all git commits.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Verified-Commits-SSH/assets/fake02.png)

Notice that the **spoofed** commit now shows as **"Unverified"**.

To enable vigilant mode:

1. Navigate to your GitHub account **'Settings'**. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Verified-Commits-SSH/assets/vig01.png)

2. Navigate to **'SSH and GPG keys'** and tick **'Flag unsigned commits as unverified'**. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Verified-Commits-SSH/assets/vig02.png)

### 2.) Create a SSH signing key

Next we will enable **SSH commit verification** so that any future commits will be signed and shown as **"Verified"**.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Verified-Commits-SSH/assets/veri01.png)

To enable SSH commit verification you can either use an [existing SSH key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/checking-for-existing-ssh-keys) or [generate a new SSH key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent):

Open a command terminal and run:

```txt
$ ssh-keygen -t ed25519 -C "your_email@example.com"
```

If you use the defaults for the above command in `Windows` it will save your SSH key in the path: `/c/Users/you/.ssh/id_algorithm`

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Verified-Commits-SSH/assets/veri02.png)

We are only interested in the `'.pub'` file as that contains the **Public Key**. Open the `'.pub'` file and copy the entire contents of the file to your clipboard.

1. Next navigate to your GitHub account **'Settings'**. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Verified-Commits-SSH/assets/vig01.png)

2. Navigate to **'SSH and GPG keys'** and select **'New SSH key'**. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Verified-Commits-SSH/assets/veri03.png)

3. Give the SSH key a **Title**, select the **Key type** as `'Signing Key'` and copy the entire contents of the `'.pub'` file into the **Key** field. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Verified-Commits-SSH/assets/veri04.png)

Next we will run a few git commands so that will configure **git** to sign all commits using the SSH key. Make sure that the minimum version of **git** is at least **v2.34** or above.

To configure **git commit signing** on an individual repository, open a command prompt and navigate to the **path** of your **cloned GitHub repository** and run the following commands:

```powershell
### Navigate to cloned repo root for individual repos ###
### Configure name ###
git config user.name "Your_User_Name"

### Configure email (same as what was specified in SSH key gen) ###
git config user.email "your_email@example.com"

### Specify the location of the SSH public key, default path is: /c/Users/you/.ssh/id_algorithm ###
git config user.signingkey "C:\Users\Monkey/.ssh/id_ed25519.pub"

### Enable/Enforce commit signing ###
git config commit.gpgsign true

### Configure commit signing format ###
git config gpg.format ssh
```

To configure **git commit signing** on all repositories, open a command prompt run the following **'global'** commands:

```powershell
### Global signing on all repos ###
### Configure name ###
git config --global user.name "Your_User_Name"

### Configure email (same as what was specified in SSH key gen) ###
git config --global user.email "your_email@example.com"

### Specify the location of the SSH public key, default path is: /c/Users/you/.ssh/id_algorithm ###
git config --global user.signingkey "C:\Users\Monkey/.ssh/id_ed25519.pub"

### Enable/Enforce commit signing ###
git config --global commit.gpgsign true

### Configure commit signing format ###
git config --global gpg.format ssh
```

That's it, now when you make any changes to your code and commit those changes they will be signed using the SSH public key and be displayed as **'Verfied'** on your **git commit history** on your GitHub repo.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Verified-Commits-SSH/assets/veri01.png)

### 3.) Enable a branch protection rule

The last thing I wanted to cover was how you can actively enforce **signature verification** to prevent unsigned commits from being pushed to your repositories.

We can easily achieve this by configuring a **[Branch protection rule](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/managing-a-branch-protection-rule)**

1. Navigate to the repository you want to protect and select **'Settings' -> 'Branches' -> 'Add branch protection rule'**. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Verified-Commits-SSH/assets/pol01.png)

2. Configure a **'Branch name pattern'** for the branch the policy should be applied to and select **'Require signed commits'**. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Verified-Commits-SSH/assets/pol02.png)

3. Select **'Create'**. You should now have a branch policy applied that will enforce signed commits. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Verified-Commits-SSH/assets/pol03.png)

## Conclusion

As you can see it is very easy to configure **commit signing and verification** features in **GitHub** using SSH keys which will ensure the authenticity of authors and collaborators on your repositories and codebase.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Verified-Commits-SSH/assets/final.png)

I hope you have enjoyed this post and have learned something new. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
