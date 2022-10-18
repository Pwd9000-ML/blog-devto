---
title: Defender for DevOps on GitHub
published: false
description: Microsoft Security DevOps (MSDO) GitHub action
tags: 'github, DevSecOps, AzureDefender, Security'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/DevOps-Defender-For-DevOps-GH/assets/main.png'
canonical_url: null
id: 1223249
series: Defender for DevOps
---

### Microsoft Security DevOps (MSDO) GitHub action

**Microsoft Security DevOps** (MSDO) is a command line application which integrates static analysis tools into the development cycle.

Today we will take a closer look at how we can use the [MSDO GitHub action](https://learn.microsoft.com/en-us/azure/defender-for-cloud/github-action?WT.mc_id=DT-MVP-5004771) and how it integrates with [Azure Defender for DevOps](https://learn.microsoft.com/en-us/azure/defender-for-cloud/defender-for-devops-introduction?WT.mc_id=DT-MVP-5004771).

MSDO installs, configures and runs the latest versions of **static analysis tools** (including, but not limited to, SDL/security and compliance tools). It is data-driven with portable configurations that enable deterministic execution across multiple environments.

For tools that output results, MSDO can convert the results to [Static Analysis Results Interchange Format (SARIF)](https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/sarif-support-for-code-scanning?WT.mc_id=DT-MVP-5004771) which can display the results in your **repository** on **GitHub**.

MSDO integrates with [Azure Defender for DevOps](https://learn.microsoft.com/en-us/azure/defender-for-cloud/defender-for-devops-introduction?WT.mc_id=DT-MVP-5004771) which enables a central console as part of [Microsoft Defender for Cloud](https://learn.microsoft.com/en-us/azure/defender-for-cloud/defender-for-cloud-introduction?WT.mc_id=DT-MVP-5004771) to provide security teams **DevOps insights** across multi-pipeline environments, such as **GitHub** and **Azure DevOps**.

These insights can then be correlated with other contextual cloud security intelligence to prioritize remediation in code and apply consistent security guardrails throughout the application lifecycle. Key capabilities starting in **Defender for DevOps**, available through **Defender for Cloud** includes:

- Unified visibility into DevOps security posture.
- Strengthen cloud resource configurations throughout the development lifecycle.
- Prioritize remediation of critical issues in code.

### MSDO tools

As of the time of this writing, **Microsoft Security DevOps** uses the following Open Source tools:

| Name | Language | License |
| --- | --- | --- |
| [Bandit](https://github.com/PyCQA/bandit) | --- | --- |
| [Binskim](https://github.com/Microsoft/binskim) | --- | --- |
| [ESlint](https://github.com/eslint/eslint) | --- | --- |
| [Credscan](https://learn.microsoft.com/en-us/azure/defender-for-cloud/detect-credential-leaks) | --- | --- |
| [Template Analyzer](https://github.com/Azure/template-analyzer) | --- | --- |
| [Terrascan](https://github.com/accurics/terrascan) | --- | --- |
| [Trivy](https://github.com/aquasecurity/trivy) | --- | --- |

### Getting started

I hope you have enjoyed this post and have learned something new. You can find the code samples used in this blog post on my [GitHub](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2022/DevOps-Defender-For-DevOps-GH/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
