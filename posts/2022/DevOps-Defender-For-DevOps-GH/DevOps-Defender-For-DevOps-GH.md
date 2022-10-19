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

**Microsoft Security DevOps** (MSDO) is a command line application which integrates **static analysis tools**, for **security** and **compliance** into the development cycle.

Today we will take a closer look at how we can use the [MSDO GitHub action](https://learn.microsoft.com/en-us/azure/defender-for-cloud/github-action?WT.mc_id=DT-MVP-5004771) and how it integrates with [Microsoft Defender for DevOps](https://learn.microsoft.com/en-us/azure/defender-for-cloud/defender-for-devops-introduction?WT.mc_id=DT-MVP-5004771).

MSDO installs, configures and runs the latest versions of **static analysis tools**. It is data-driven with portable configurations that enable deterministic execution across multiple environments.

The MSDO toolkit can output and convert results to [Static Analysis Results Interchange Format (SARIF)](https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/sarif-support-for-code-scanning) which can display the results in your **repository** on **GitHub**.

MSDO integrates with [Microsoft Defender for DevOps](https://learn.microsoft.com/en-us/azure/defender-for-cloud/defender-for-devops-introduction?WT.mc_id=DT-MVP-5004771) which enables a central console as part of [Microsoft Defender for Cloud](https://learn.microsoft.com/en-us/azure/defender-for-cloud/defender-for-cloud-introduction?WT.mc_id=DT-MVP-5004771) to provide security teams **DevOps insights** across multi-pipeline environments, such as **GitHub** and **Azure DevOps**.

These insights can then be correlated with other contextual cloud security intelligence to prioritize remediation in code and apply consistent security guardrails throughout the application lifecycle. The benefits of **Defender for DevOps**, available through **Defender for Cloud** are:

- Unified visibility into DevOps security posture.
- Visibility of rich security insights to help strengthen cloud resource configurations throughout the development lifecycle
- Prioritise remediation of critical issues in code.

### MSDO tools

At the time of this writing, **Microsoft Security DevOps** uses the following tools:

| Name | Language | License |
| --- | --- | --- |
| [Bandit](https://github.com/PyCQA/bandit) | Python | [Apache License 2.0](https://github.com/PyCQA/bandit/blob/master/LICENSE) |
| [Binskim](https://github.com/Microsoft/binskim) | Binary--Windows, ELF | [MIT License](https://github.com/microsoft/binskim/blob/main/LICENSE) |
| [ESlint](https://github.com/eslint/eslint) | JavaScript | [MIT License](https://github.com/eslint/eslint/blob/main/LICENSE) |
| [Credscan](https://learn.microsoft.com/en-us/azure/defender-for-cloud/detect-credential-leaks) | Secret scanning | Free during Defender for DevOps preview |
| [Template Analyzer](https://github.com/Azure/template-analyzer) | ARM templates, Bicep files | [MIT License](https://github.com/Azure/template-analyzer/blob/main/LICENSE.txt) |
| [Terrascan](https://github.com/accurics/terrascan) | Terraform (HCL2), Kubernetes (JSON/YAML), Helm v3, Kustomize, Dockerfiles, Cloud Formation | [Apache License 2.0](https://github.com/accurics/terrascan/blob/master/LICENSE) |
| [Trivy](https://github.com/aquasecurity/trivy) | Container images, File systems, Git repositories | [Apache License 2.0](https://github.com/aquasecurity/trivy/blob/main/LICENSE) |

### Getting started

Before we dive into the MSDO toolkit we first need to connect our GitHub Repository to [Microsoft Defender for Cloud](https://learn.microsoft.com/en-us/azure/defender-for-cloud/quickstart-onboard-github)

1. Log into the [Azure portal](https://portal.azure.com/).

2. Navigate to **Microsoft Defender for Cloud > Environment Settings**.

3. Select **Add environment**.

4. Select **GitHub**. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/DevOps-Defender-For-DevOps-GH/assets/dfc01.png)

5. Enter a **name**, select your **subscription**, **resource group**, and **region**. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/DevOps-Defender-For-DevOps-GH/assets/dfc02.png)

6. **Select Plans**. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/DevOps-Defender-For-DevOps-GH/assets/dfc03.png)

7. Select **Next: Authorize connection** and **Authorize** the **GitHub** connection after reviewing the permission request. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/DevOps-Defender-For-DevOps-GH/assets/dfc04.png)

8. After **Authorizing** click on **Install** under **Install Defender for DevOps app**. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/DevOps-Defender-For-DevOps-GH/assets/dfc05.png)

9. You can install the **Defender for DevOps** app on **All** or **Individual** repositories as necessary. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/DevOps-Defender-For-DevOps-GH/assets/dfc06.png)

10. Select **Next: Review and create**. Review the information and select **Create**.

**NOTES:** You will see the **GitHub** connector under **Microsoft Defender for Cloud > Environment Settings**. If you only added one repository and wanted to later change and add/onboard more repositories onto teh same **Defender for DevOps** plan, you can do so by navigating to your **GitHub Settings > Applications**.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/DevOps-Defender-For-DevOps-GH/assets/dfc07.png)

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/DevOps-Defender-For-DevOps-GH/assets/dfc08.png)

After installing **Defender for DevOps** on the selected repositories, they will be integrated with **Microsoft Defender for Cloud** and insights will be accessible from the **DevOps Security** dashboard.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/DevOps-Defender-For-DevOps-GH/assets/dfc09.png)

Next we will look at the MSDO toolkit GitHub action and see how we can use certain tools and populate the dashboard with rich security insights about our code.

### Configuring MSDO GitHub action

I hope you have enjoyed this post and have learned something new. You can find the code samples used in this blog post on my [GitHub](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2022/DevOps-Defender-For-DevOps-GH/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
