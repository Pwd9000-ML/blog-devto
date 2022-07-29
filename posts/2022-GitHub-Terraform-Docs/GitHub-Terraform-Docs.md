---
title: Auto generate documentation from Terraform modules
published: false
description: Automatically generate documentation from Terraform modules - GitHub Action
tags: 'githubactions, github, terraform, devops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Terraform-Docs/assets/main05.png'
canonical_url: null
id: 1154693
series: Using Terraform on GitHub
---

## Overview

As we all know, the importance of documentation in software development becomes visibly apparent when knowledge or information needs to be shared about the project or code.

Even if you write and develop IaC (Infrastructure as Code) using terraform, working in a team or sharing your terraform modules with others, you're most likely going to want to create some sort of documentation about your terraform code/modules so that others may understand the code better, or to give more information on how to use your modules.

Today we are going to look at a cool tool that can be used to automatically generate your Terraform module documentation called [terraform-docs](https://terraform-docs.io/).

If you want a quick autonomous way to document your terraform modules you're going to love this tool. We will look at how the tool can be used manually first followed by how it can be automated in CI/CD using GitHub Actions.

## Manual Usage

If you want to use this tool locally there are a few ways that you can install it on your development machine which is documented here: [terraform-docs Installation](https://terraform-docs.io/user-guide/installation/). In my case I am using a **Windows** machine and will use **Chocolatey** to install the tool:

- First install **'Chocolatey'** [(Online instructions)](https://chocolatey.org/install):

Open an **Administrative shell** and run:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

**NOTE:** After chocolatey is installed you'll need to restart your shell session.

- Next install **'terraform-docs'**:

```powershell
choco install terraform-docs
```

### Example

Now with the tool installed locally I can simply run the following command to generate a [markdown table](https://terraform-docs.io/reference/markdown-table/):

```powershell
terraform-docs markdown table [/path/to/module] [flags]
```

You can also add additional [flags](https://terraform-docs.io/reference/markdown-table/) to the command if needed.

Here I have a terraform module I have written on my local development machine under the folder path `'C:\temp\sonarcube-aci'`:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Terraform-Docs/assets/local.png)

After running the following command:

```powershell
terraform-docs markdown table "C:\temp\sonarcube-aci" --output-file "README.md"
```

We can now see a **README.md** file has been created:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Terraform-Docs/assets/local02.png)

Take a look here to see what the **README.md** document looks like: [example_README.md](https://github.com/Pwd9000-ML/blog-devto/blob/main/posts/2022-GitHub-Terraform-Docs/code/example_README.md)

You can also create a **[configuration yaml](https://terraform-docs.io/user-guide/configuration/)** file with additional options and have consistent execution through the `'.terraform-docs.yml'` file.

Once you've set up a **configuration** file, every time you or your teammates want to regenerate documentation (manually, through a pre-commit hook, or as part of a CI pipeline) all you need to do is run `'terraform-docs /module/path'`.

## Automated Usage using GitHub Actions

The examples this section can also be found on my GitHub repository: [Azure-Terraform-Deployments](https://github.com/Pwd9000-ML/Azure-Terraform-Deployments).

So far we have looked at how to use the tool locally. In this section we will look at how our documentation can be automated through CI/CD using the tool as a **GitHub Action** inside of a workflow.

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my published [Github](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2022-GitHub-Terraform-Docs/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
