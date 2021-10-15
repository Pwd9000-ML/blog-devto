---
title: Terraform IaC Scanning with Trivy
published: false
description: DevOps - Terraform - IaC Scanning with Trivy
tags: 'tutorial, security, productivity, devops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/DevOps-Terraform-Trivy/assets/main-trivy.png'
canonical_url: null
id: 864896
---

## Trivy Vulnerability Scanner

`Trivy` is a simple and comprehensive scanner for vulnerabilities in container images, file systems, and Git repositories, as well as for configuration issues in IaC. `Trivy` detects vulnerabilities of OS packages (Alpine, RHEL, CentOS, etc.) and language-specific packages (Bundler, Composer, npm, yarn, etc.). In addition, `Trivy` scans Infrastructure as Code (IaC) files such as Terraform, Dockerfile and Kubernetes, to detect potential configuration issues that expose your deployments to the risk of attack.

You can now scan your Terraform configuration artifacts easily giving you the confidence that all is well with your configuration before deploying your Terraform (IaC) configurations. It is a free/open source tool and provided by AquaSecurity. For more information go check out the [Trivy github page](https://github.com/aquasecurity/trivy)

Today we will look at how you can utilise `Trivy` as part of your DevOps CI/CD process for deploying Terraform (IaC) by scanning your terraform deployment source code for security risks, before actually deploying the configuration to ensure that there are no vulnerabilities or misconfigurations that could potentially open up security risks.

## How to

xx

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}
