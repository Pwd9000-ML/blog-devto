---
title: IaC Scanning with TFSEC for VsCode (Extension)
published: false
description: DevOps - Terraform - IaC Scanning with TFSEC for VsCode
tags: 'terraform, azuredevops, iac, DevSecOps'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-DevOps-Terraform-Tfsec-Vscode/assets/main-tfsec.png'
canonical_url: null
id: 970626
series: Terraform Pro Tips
---

## TFSEC Vulnerability Scanner

`tfsec` is a static analysis security scanner for your Terraform code.

Designed to run locally and in your CI pipelines, developer-friendly output and fully documented checks mean detection and remediation can take place as quickly and efficiently as possible.

`tfsec` takes a developer-first approach to scanning your Terraform templates; using static analysis and deep integration with the official HCL parser it ensures that security issues can be detected before your infrastructure changes take effect.

## IaC using the TFSEC VsCode extension

In this tutorial we will go through how to install **tfsec** and the **tfsec extension for VsCode** on your development machine where you are developing and writing your Terraform code, and show how you can scan and detect for any vulnerabilities or misconfigurations to detect potential issues that expose your deployments to the risk of attack.

You can scan your Terraform configuration artifacts easily giving you the confidence that all is well with your configuration before committing your code to source control / deploying your Terraform (IaC) configurations. It is a free/open source tool by AquaSecurity. For more information go check out the [Tfsec github page](https://github.com/aquasecurity/tfsec)

## Installing TFSEC

First we need to make sure we have the latest version of `tfsec` installed on our development machine. There are a couple of ways to do this:

Install with [brew/linuxbrew](https://brew.sh)

```bash
brew install tfsec
```

Install with [Chocolatey](https://chocolatey.org/)

```cmd
choco install tfsec
```

Install with [Scoop](https://scoop.sh/)

```cmd
scoop install tfsec
```

You can also grab the binary for your system from the [releases page](https://github.com/aquasecurity/tfsec/releases).

Alternatively, install with Go:

```bash
go install github.com/aquasecurity/tfsec/cmd/tfsec@latest
```

Please note that using `go install` will install directly from the `master` branch and version numbers will not be reported via `tfsec --version`.

## Installing TFSEC extension for VSCODE

The next step is to just open up VsCode and under extensions you can search for the extension called **TFSEC** and hit the `install` button.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-DevOps-Terraform-Tfsec-Vscode/assets/install.png)

You should now see the **TFSEC** logo on your **VsCode** side bar to the left.

## Run TFSEC VsCode extension

Next we will create a simple **Terraform** configuration and use the extension to inspect for any issues before committing the code to source control.

I created a very basic terraform configuration that will build a resource group and key vault. You can take a look at the configuration [here](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-DevOps-Terraform-Tfsec-Vscode/code/TF_Module).

After writing you terraform configuration navigate to the **TFSEC** extension on teh left of the screen:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-DevOps-Terraform-Tfsec-Vscode/assets/nav.png)

Click on the button that says **Run tfsec now**:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-DevOps-Terraform-Tfsec-Vscode/assets/run.png)

As you can see all of my Terraform have been scanned and notified me of what issues are in my configuration, the severity rating of the issue, as well as guidance on remediating the issue.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-DevOps-Terraform-Tfsec-Vscode/assets/result.png)

I hope you have enjoyed this post and have learned something new. You can find the code samples used in this blog post on my [Github](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2022-DevOps-Terraform-Tfsec-Vscode/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}