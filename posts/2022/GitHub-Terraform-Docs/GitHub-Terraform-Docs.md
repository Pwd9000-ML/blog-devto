---
title: Auto generate documentation from Terraform modules
published: true
description: Automatically generate documentation from Terraform modules - GitHub Action
tags: 'githubactions, github, terraform, devops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Terraform-Docs/assets/main-tf-tips.png'
canonical_url: null
id: 1154693
series: Terraform Pro Tips
---

## Overview

As we all know, the importance of documentation in software development becomes visibly apparent when knowledge or information needs to be shared about the project or code.

Even if you write and develop IaC (Infrastructure as Code) using terraform, working in a team or sharing your terraform modules with others, you're most likely going to want to create some sort of documentation about your terraform code/modules so that others may understand the code better, or to give more information on how to use your modules.

Today we are going to look at a cool tool that can be used to "automagically" generate your Terraform module documentation called [terraform-docs](https://terraform-docs.io/).

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

**NOTE:** You can also add additional [flags](https://terraform-docs.io/reference/markdown-table/) to the command if needed. There are also other [output formats](https://terraform-docs.io/reference/terraform-docs/) available other than **markdown**, such as **JSON**, **XML** etc.

Here I have a terraform module I have written on my local development machine under the folder path `'C:\temp\sonarcube-aci'`:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Terraform-Docs/assets/local.png)

After running the following command:

```powershell
terraform-docs markdown table "C:\temp\sonarcube-aci" --output-file "README.md"
```

We can now see a **README.md** file has been created:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Terraform-Docs/assets/local02.png)

Take a look here to see what the **README.md** document looks like: [example_README.md](https://github.com/Pwd9000-ML/blog-devto/blob/main/posts/2022/GitHub-Terraform-Docs/code/example_README.md)

You can also create a **[configuration yaml](https://terraform-docs.io/user-guide/configuration/)** file with additional options and have consistent execution through the `'.terraform-docs.yml'` file.

Once you've set up a **configuration** file, every time you or your teammates want to regenerate documentation (manually, through a pre-commit hook, or as part of a CI pipeline) all you need to do is run `'terraform-docs /module/path'`.

## Automated Usage using GitHub Actions

The examples in this section can also be found on my GitHub repository: [Azure-Terraform-Deployments](https://github.com/Pwd9000-ML/Azure-Terraform-Deployments).

So far we have looked at how to use the tool locally. In this section we will look at how our documentation can be automated through CI/CD using the tool as a **GitHub Action** inside of a workflow.

In my GitHub repository called: [Azure-Terraform-Deployments](https://github.com/Pwd9000-ML/Azure-Terraform-Deployments), notice that I have structured my terraform module code with folders using a numbering system e.g: `'01_Foundation'`, `'02_Storage'`, etc.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Terraform-Docs/assets/repo01.png)

In each terraform module folder there is no documentation or 'README.md' file:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Terraform-Docs/assets/repo02.png)

### Create GitHub Actions workflow

Under the `'.github/workflows'` folder I created the following GitHub workflow: [Auto_Generate_Module_Documentation.yml](https://github.com/Pwd9000-ML/Azure-Terraform-Deployments/blob/master/.github/workflows/Auto_Generate_Module_Documentation.yml):

```yaml
name: Generate terraform docs
on:
  workflow_dispatch:
  pull_request:
    branches:
      - master

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          ref: ${{ github.event.pull_request.head.ref }}

      - name: Render terraform docs inside the README.md and push changes back to PR branch
        uses: terraform-docs/gh-actions@v1.0.0
        with:
          find-dir: .
          output-file: README.md
          output-method: inject
          git-push: 'true'
```

Notice in the above workflow the GitHub Action under `'steps:'` for terraform-docs:

```yml
- name: Render terraform docs inside the README.md and push changes back to PR branch
    uses: terraform-docs/gh-actions@v1.0.0
    with:
        find-dir: .
        output-file: README.md
        output-method: inject
        git-push: "true"
```

The parameters passed into the **GitHub Action** is done using `'with:'`. You can look at all the available **input parameters** on the official [terraform-docs GitHub Actions page](https://github.com/terraform-docs/gh-actions#configuration).

I am using a parameter called `'find-dir'` and pointing it to the root of my repository using dot: `'.'`. The `'find-dir'` parameter is a setting that will extract a list of directories by running `'find ./find\_dir -name \*.tf'` to automatically find the directories containing my module `'.tf'` files, so I do not have to specify each directory.

You can also specify a comma separated list of directories to generate docs for each directory manually by using the `'working-dir'` parameter instead.

You should now see the **GitHub Action** under the repository **Actions pane** and be able to run the workflow manually as we specified the `'workflow_dispatch:'` trigger:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Terraform-Docs/assets/run.png)

After running the **workflow** you will now notice that each of my module folders have a `'README.md'` file:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Terraform-Docs/assets/workflow01.png)

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Terraform-Docs/assets/repo03.png)

You can take a look at the **README.md** file that was created here: [README.md](https://github.com/Pwd9000-ML/Azure-Terraform-Deployments/blob/master/01_Foundation/README.md).

## Conclusion

As you can see, this tool can be a valuable asset to easily maintain and have terraform documentation for your modules without much effort.

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my published [GitHub](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2022/GitHub-Terraform-Docs/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
