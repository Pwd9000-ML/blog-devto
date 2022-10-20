---
title: Defender for DevOps on AzureDevOps (Terrascan edition)
published: false
description: Microsoft Security DevOps (MSDO) Azure DevOps extension
tags: 'azuredevops, DevSecOps, AzureDefender, Security'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/DevOps-Defender-For-DevOps-ADO/assets/main.png'
canonical_url: null
id: 1223252
series: Defender for DevOps
---

### Overview

Welcome to the second part of this blog series on [Microsoft Defender for DevOps](https://learn.microsoft.com/en-us/azure/defender-for-cloud/defender-for-devops-introduction?WT.mc_id=DT-MVP-5004771).

In my [previous post](https://dev.to/pwd9000/defender-for-devops-on-github-terrascan-edition-45bd) we looked at how you can integrate **Defender for DevOps** with **GitHub** and also how to use the **Microsoft Security DevOps** [(MSDO) GitHub action](https://github.com/marketplace/actions/security-devops-action) to configure **Terrascan** to analyze a **Terraform IaC Configuration** and how the scan results are published on the Azure portal under the **DevOps Security** dashboard inside **Microsoft Defender for Cloud**.

Today we will look at how to integrate **Defender for DevOps** with **Azure DevOps** instead and using the same MSDO toolkit, instead of a GitHub action, **Azure DevOps** has a **Microsoft Security DevOps** [(MSDO) Marketplace Extension](https://marketplace.visualstudio.com/items?itemName=ms-securitydevops.microsoft-security-devops-azdevops).

So we will be able to use the same analysis tools on **Azure DevOps**. We will also look at how to configure **Credscan** to analyze and identify credential leaks in source code and configuration files.

We will also look at another Azure DevOps Extension called **[SARIF SAST Scans Tab](https://marketplace.visualstudio.com/items?itemName=sariftools.scans&targetId=8e02e9e3-062e-46a7-8558-c30016c43306&utm_source=vstsproduct&utm_medium=ExtHubManageList)** to better view the results of MSDO analyzer scans, outside of the console output and results file. It will look for `*.sarif` files in the `CodeAnalysisLogs` build artifact directory and display them as source annotations.

We will also look at how the scan results are published on the Azure portal under the **DevOps Security** dashboard inside **Microsoft Defender for Cloud**.

### Microsoft Security DevOps (MSDO) Overview

Just to recap on what MSDO is, **Microsoft Security DevOps** (MSDO) is a command line application which integrates **static analysis tools**, for **security** and **compliance** into the development cycle.

MSDO installs, configures and runs the latest versions of **static analysis tools**. It is data-driven with portable configurations that enable deterministic execution across multiple environments.

The MSDO toolkit can output and convert results to [Static Analysis Results Interchange Format (SARIF)](https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/sarif-support-for-code-scanning) which can display the results in your **repository** using the **SARIF SAST Scans Tab** on Azure DevOps.

MSDO also integrates with [Microsoft Defender for DevOps](https://learn.microsoft.com/en-us/azure/defender-for-cloud/defender-for-devops-introduction?WT.mc_id=DT-MVP-5004771) which enables a central console as part of [Microsoft Defender for Cloud](https://learn.microsoft.com/en-us/azure/defender-for-cloud/defender-for-cloud-introduction?WT.mc_id=DT-MVP-5004771) to provide security teams **DevOps insights** across multi-pipeline environments, such as **GitHub** and **Azure DevOps**.

These insights can then be correlated with other contextual cloud security intelligence to prioritise remediation in code and apply consistent security guardrails throughout the application lifecycle. The benefits of **Defender for DevOps**, available through **Defender for Cloud** are:

- Unified visibility into DevOps security posture.
- Visibility of rich security insights to help strengthen cloud resource configurations throughout the development lifecycle.
- Prioritise remediation of critical issues in code.

### MSDO tools

At the time of this writing, **Microsoft Security DevOps** uses the following tools:

| Name | Language | License |
| --- | --- | --- |
| [Bandit](https://github.com/PyCQA/bandit) | Python | [Apache License 2.0](https://github.com/PyCQA/bandit/blob/master/LICENSE) |
| [Binskim](https://github.com/Microsoft/binskim) | Binary--Windows, ELF | [MIT License](https://github.com/microsoft/binskim/blob/main/LICENSE) |
| [ESlint](https://github.com/eslint/eslint) | JavaScript | [MIT License](https://github.com/eslint/eslint/blob/main/LICENSE) |
| [Credscan](https://learn.microsoft.com/en-us/azure/defender-for-cloud/detect-credential-leaks) | code, artifacts | Free during Defender for DevOps preview |
| [Template Analyzer](https://github.com/Azure/template-analyzer) | ARM templates, Bicep files | [MIT License](https://github.com/Azure/template-analyzer/blob/main/LICENSE.txt) |
| [Terrascan](https://github.com/accurics/terrascan) | Terraform (HCL2), Kubernetes (JSON/YAML), Helm v3, Kustomize, Dockerfiles, Cloud Formation | [Apache License 2.0](https://github.com/accurics/terrascan/blob/master/LICENSE) |
| [Trivy](https://github.com/aquasecurity/trivy) | Container images, File systems, Git repositories | [Apache License 2.0](https://github.com/aquasecurity/trivy/blob/main/LICENSE) |

### Getting started

Before we dive into the MSDO toolkit we first need to connect our Azure DevOps repository to [Microsoft Defender for Cloud](https://learn.microsoft.com/en-us/azure/defender-for-cloud/quickstart-onboard-github?WT.mc_id=DT-MVP-5004771).

1. Log into the [Azure portal](https://portal.azure.com/).

2. Navigate to **Microsoft Defender for Cloud > Environment Settings**.

3. Select **Add environment** and then Select **Azure DevOps**. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/DevOps-Defender-For-DevOps-ADO/assets/dfc01.png)

4. Enter a **name**, select your **subscription**, **resource group**, and **region**. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/DevOps-Defender-For-DevOps-ADO/assets/dfc02.png)

5. **Select Plans**. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/DevOps-Defender-For-DevOps-ADO/assets/dfc03.png)

6. Select **Next: Authorize connection** and **Authorize** the **Azure DevOps** connection after reviewing the permission request. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/DevOps-Defender-For-DevOps-ADO/assets/dfc04.png) **IMPORTANT:** If your authorizing account is part of multiple **Azure DevOps Organisations**, ensure that you are logged into the correct org using (https://aex.dev.azure.com/) ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/DevOps-Defender-For-DevOps-ADO/assets/dfc006.png) You will also be able to verify your permissions to link **Defender for DevOps** to the correct **Azure DevOps Org** by looking at the top of the permission request screen before accepting. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/DevOps-Defender-For-DevOps-ADO/assets/dfc07.png)

7. After **Authorizing**, Select your relevant **organization(s)**, **project(s)** and **repository(s)** from the drop-down menus. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/DevOps-Defender-For-DevOps-ADO/assets/dfc05.png)

8. Select **Next: Review and create**. Review the information and select **Create**.

After creation you will see the **Azure DevOps** connector under **Microsoft Defender for Cloud > Environment Settings**.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/DevOps-Defender-For-DevOps-ADO/assets/dfc08.png)

You will also see newly created **service hooks** in the selected **Azure DevOps Project(s)** where **Defender for Devops** have been onboarded.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/DevOps-Defender-For-DevOps-ADO/assets/dfc09.png)

With **Defender for DevOps** now connected on the selected **Azure DevOps** projects you want to onboard, they will be integrated with **Microsoft Defender for Cloud** and insights will be accessible from the **DevOps Security** dashboard under **Microsoft Defender for Cloud** in the **Azure portal**.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/DevOps-Defender-For-DevOps-ADO/assets/dfc10.png)

Next we will install the MSDO Azure DevOps **[Marketplace Extensions](https://marketplace.visualstudio.com/)**.

### Install required Devops extensions

Navigate to your Azure DevOps Org and install the following two **Marketplace Extensions**:

- **[Microsoft Security DevOps (MSDO)](https://marketplace.visualstudio.com/items?itemName=ms-securitydevops.microsoft-security-devops-azdevops)**
- **[SARIF SAST Scans Tab](https://marketplace.visualstudio.com/items?itemName=sariftools.scans&targetId=8e02e9e3-062e-46a7-8558-c30016c43306&utm_source=vstsproduct&utm_medium=ExtHubManageList)**

You can verify the installed extensions by navigating to the **Shopping Bag Logo > Manage extensions** in your DevOps Org.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/DevOps-Defender-For-DevOps-ADO/assets/ext01.png)

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/DevOps-Defender-For-DevOps-ADO/assets/ext02.png)

Next we will look at how we can use the MSDO toolkit to populate the **Defender for DevOps** dashboard with rich security insights about our code.

### Using the MSDO marketplace extension

As mentioned MSDO features a few different tools (I will cover some of the other tools in a future blog post), but I want to concentrate on a specific tool today called [Terrascan](https://github.com/accurics/terrascan).

**Terrascan** is a static code analyzer for Infrastructure as Code (IaC). Let's take a look at an example on how we can use **MSDO** integration with **Defender for DevOps** to get security insights and detect compliance and security violations in a **Terraform** configuration to mitigate risk before provisioning cloud infrastructure.

Let's look at an example. On my **Azure DevOps repository** I have a the following **[Terraform IaC configuration](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2022/DevOps-Defender-For-DevOps-ADO/code/01_Foundation)**.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/DevOps-Defender-For-DevOps-ADO/assets/ado0001.png)

Next we'll configure a YAML pipeline to run the MSDO extension and using the **Terrascan** analyzer see if it can detect any issues on the **Terraform configuration** and how that will be displayed on the **SARIF SAST Scan Tab** as well as the **Microsoft Defender for Cloud** DevOps security dashboard on the Azure portal.

1. Navigate to your Azure DevOps project and under pipelines, select **New pipeline** ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/DevOps-Defender-For-DevOps-ADO/assets/pipe01.png)

2. Select **Azure Repos Git**. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/DevOps-Defender-For-DevOps-ADO/assets/pipe02.png)

3. Select the relevant repository. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/DevOps-Defender-For-DevOps-ADO/assets/pipe03.png)

4. Select **Starter pipeline**. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/DevOps-Defender-For-DevOps-ADO/assets/pipe04.png)

5. Paste and commit the following YAML into the pipeline, select **Save and run**:

```yml
# Starter pipeline
# Start with a minimal pipeline that you can customize to build and deploy your code.
# Add steps that build, run tests, deploy, and more:
# https://aka.ms/yaml
trigger: none
pool:
  vmImage: 'windows-latest'
steps:
  - checkout: self
  - task: UseDotNet@2
    displayName: 'Use dotnet'
    inputs:
      version: 3.1.x
  - task: UseDotNet@2
    displayName: 'Use dotnet'
    inputs:
      version: 5.0.x
  - task: UseDotNet@2
    displayName: 'Use dotnet'
    inputs:
      version: 6.0.x
  - task: MicrosoftSecurityDevOps@1
    displayName: 'Microsoft Security DevOps'
    inputs:
      categories: 'IaC,secrets'
      tools: 'terrascan'
```

Take a closer look at the MSDO task and notice that we supply certain `inputs:`

```yml
  - task: MicrosoftSecurityDevOps@1
    displayName: 'Microsoft Security DevOps'
    inputs:
      categories: 'IaC,secrets'
      tools: 'terrascan'
```

After running the pipeline, notice that there is a new **Scans** tab next to the pipeline run **Summary** (SARIF SAST Scan Tab). This tab is from the extension we installed earlier as the MSDO toolkit exports results into a `*.sarif` file and will be picked up in this tab.  

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/DevOps-Defender-For-DevOps-ADO/assets/pipe05.png)  

Notice that the **Terrascan** results will be displayed in the **Scans** tab, based on teh `*.sarif` file artifact.  

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/DevOps-Defender-For-DevOps-ADO/assets/pipe06.png)  

### Defender for DevOps Dashboard

As mentioned MSDO closely integrates with **Microsoft Defender for Cloud** and has its own **'DevOps Security'** dashboard, to review and observe security insights across DevOps and your codebase.

In the Azure portal navigate to **Microsoft Defender for Cloud**, select the **DevOps Security** pane and then click on the GitHub connector:  

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/DevOps-Defender-For-DevOps-ADO/assets/results01.png)  

Notice there are some **Unhealthy** recommendations to resolve detected by MSDO infrastructure as code scanning **(Terrascan)**:  


### Code scanning severities

You can also define code scanning severities which will **fail** a **pull request check** to prevent security issues from being committed and introduced into your code.

This can be configured under the **GitHub repository Settings > Code security and analysis**:

Once the **IaC** security findings are resolved you will notice that the status of the recommendation on the **Defender for DevOps** dashboard has changed from **Unhealthy** to **Healthy**:

Stay tuned for my next blog post where we will use MSDO on **Azure DevOps** instead of GitHub and also demonstrate how to use the **Azure DevOps MSDO Marketplace extension** instead of the MSDO GitHub action, integrating **Defender for DevOps** on **Azure DevOps**.

I hope you have enjoyed this post and have learned something new. You can find the code samples used in this blog post on my [GitHub](https://github.com/Pwd9000-ML/MSDO-Lab) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
