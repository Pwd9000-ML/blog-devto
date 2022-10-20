---
title: Defender for DevOps on AzureDevOps (Credscan edition)
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

Today we will look at how to integrate **Defender for DevOps** with **Azure DevOps** and also how to use the same MSDO toolkit, but instead of a GitHub action, as a **Microsoft Security DevOps** [(MSDO) Marketplace Extension](https://marketplace.visualstudio.com/items?itemName=ms-securitydevops.microsoft-security-devops-azdevops) to be able to use the same analysis tools on **Azure DevOps**. We will also look at how to configure **Credscan** to analyze and identify credential leaks in source code and configuration files.

Some of the common types of credentials are **default passwords**, **SQL connection strings** and **Certificates with private keys**.

We will also look at another DevOps Extension called **[SARIF SAST Scans Tab](https://marketplace.visualstudio.com/items?itemName=sariftools.scans&targetId=8e02e9e3-062e-46a7-8558-c30016c43306&utm_source=vstsproduct&utm_medium=ExtHubManageList)** to better view the results of MSDO analyzer scans, outside of the console output and results file. It will look for `*.sarif` files in the `CodeAnalysisLogs` build artifact directory and display them as source annotations.

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

**NOTE:** You will see the **Azure DevOps** connector under **Microsoft Defender for Cloud > Environment Settings**. If you only added one repository and wanted to later change and add/onboard more repositories onto the same **Defender for DevOps** plan, you can do so by navigating to your **GitHub Settings > Applications**.

After installing **Defender for DevOps** on the selected repositories you want to onboard, they will be integrated with **Microsoft Defender for Cloud** and insights will be accessible from the **DevOps Security** dashboard under **Defender for Cloud** in the **Azure portal**.

Next we will look at the **MSDO GitHub action** and see how we can use certain tools and populate the dashboard with rich security insights about our code.

**NOTE:** **GitHub Advanced Security** features are available on **public** GitHub repositories. If you are using **private** repositories, follow [this guidance](https://docs.github.com/en/organizations/keeping-your-organization-secure/managing-security-settings-for-your-organization/managing-security-and-analysis-settings-for-your-organization) to set up **GitHub Advanced Security** in your organisation/account.

### Configuring the MSDO GitHub action (with Terrascan)

The following examples can also be found on my [MSDO-Lab GitHub page](https://github.com/Pwd9000-ML/MSDO-Lab).

As mentioned MSDO features a few different tools (I will cover some of the other tools in a future blog post), but I want to concentrate on a specific tool today called [Terrascan](https://github.com/accurics/terrascan) which is part of the MSDO toolkit.

**Terrascan** is a static code analyzer for Infrastructure as Code (IaC). Let's take a look at an example on how we can use **MSDO** integration with **Defender for DevOps** to get security insights and detect compliance and security violations in a **Terraform** configuration to mitigate risk before provisioning cloud infrastructure.

On my [GitHub repository](https://github.com/Pwd9000-ML/MSDO-Lab) under the path [01_Foundation](https://github.com/Pwd9000-ML/MSDO-Lab/tree/master/01_Foundation) I have the following terraform configuration that simply builds a **Resource Group** and a **Key Vault**.

```hcl
### Data Sources ###
data "azurerm_client_config" "current" {}

#Create a Resource Group
resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

#Create a Key Vault for the Resource Group
resource "azurerm_key_vault" "kv" {
  name                        = "${lower(var.key_vault_name)}${random_integer.kv_num.result}"
  location                    = azurerm_resource_group.rg.location
  resource_group_name         = azurerm_resource_group.rg.name
  enable_rbac_authorization   = var.use_rbac_mode
  enabled_for_disk_encryption = true
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  soft_delete_retention_days  = 7
  purge_protection_enabled    = false
  sku_name                    = "standard"
  tags                        = var.tags
}

resource "random_integer" "kv_num" {
  min = 0001
  max = 9999
}
```

Let's take a look at how we can configure the **Terrascan** analyzer using the **[MSDO GitHub action](https://github.com/marketplace/actions/security-devops-action)** to scan our terraform code and how the results will be displayed on the **Defender for DevOps** dashboard in the Azure portal.

1. Sign in to [GitHub](https://www.github.com/) and select a repository you added earlier to **Defender for DevOps** on which you want to configure the **MSDO GitHub action**.

2. Select **Actions > set up a workflow yourself**
3. Give the workflow file a name. For example, `msdevopssec.yml`.

4. Copy and paste the following [sample action workflow](https://github.com/Pwd9000-ML/MSDO-Lab/blob/master/.github/workflows/msdevopssec.yml) into the **Edit new file** tab.

```yml
# My Microsoft Security DevOps (MSDO) Terrascan workflow
name: MSDO windows-latest
on:
  workflow_dispatch:

jobs:
  MSDO:
    # MSDO runs on windows-latest and ubuntu-latest.
    # macos-latest supporting coming soon
    runs-on: windows-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v2

      # Run MSDO analyzers
      - name: Run Microsoft Security DevOps Analysis
        uses: microsoft/security-devops-action@preview
        id: msdo
        env:
          terrascan_scan: 'scan'
          terrascan_outputtype: 'sarif'
          terrascan_iacdir: '01_Foundation'

      # Upload alerts to the Security tab
      - name: Upload alerts to Security tab
        uses: github/codeql-action/upload-sarif@v1
        with:
          sarif_file: ${{ steps.msdo.outputs.sarifFile }}
```

After creating the workflow you can run it manually under the **Actions** tab as the trigger is set to `workflow_dispatch:`:

After running the workflow you can review the steps. Note that the MSDO toolkit is installed and then runs **Terrascan** against the repo path **01_Foundation** we specified which contains the terraform IaC configuration files.

Let's take a closer look at the MSDO GitHub action being used:

```yml
# Run MSDO analyzers
- name: Run Microsoft Security DevOps Analysis
uses: microsoft/security-devops-action@preview
id: msdo
env:
    terrascan_scan: 'scan'
    terrascan_outputtype: 'sarif'
    terrascan_iacdir: '01_Foundation'
```

### How to configure different MSDO analyzers

There are a few ways to configure the various tools and their inputs:

- By creating a `*.gdnconfig` file to save configurations:

  - Great for reuse between team members and local/remote runs.
  - Can save multiple tool configurations in a single file to run all configurations.

- By using environment variables:
  - Great for quick configurations in build pipelines.
  - They follow the format `[GDN_]<ToolName>_<ArgumentId>`, where `GDN_` is optional and `ToolName` and `ArgumentId` are defined by the tool integration file to (\*.gdntool).

As you can see in the workflow step we specified the tool, **(Terrascan)** and some of it's supported inputs are defined as environment variables on the action itself using `env:` e.g:

```yml
steps:
  - uses: microsoft/security-devops-action
    env:
      <ToolName>_<ArgumentId>: '<supported value1>'
      <ToolName>_<ArgumentId>: '<supported value2>'
      <ToolName>_<ArgumentId>: '<supported value3>'
```

You can see all the different tools and their supported inputs (environment variables) included in the MSDO toolkit on the following [Wiki Documentation page](https://github.com/microsoft/security-devops-action/wiki#table-of-contents)

### Terrascan options

MSDO GitHub action inputs specifically related to **Terrascan** can be found here: https://github.com/microsoft/security-devops-action/wiki#terrascan-options

### Defender for DevOps Dashboard

As mentioned MSDO closely integrates with **Microsoft Defender for Cloud** and has its own **'DevOps Security'** dashboard, to review and observe security insights across DevOps and your codebase.

In the Azure portal navigate to **Microsoft Defender for Cloud**, select the **DevOps Security** pane and then click on the GitHub connector:

Notice there are some **Unhealthy** recommendations to resolve detected by MSDO infrastructure as code scanning **(Terrascan)**:

Let's navigate back to the **GitHub repository**, select the **security tab** and **Code Scanning**:

Because we selected the output format to be **SARIF** and used another action in our workflow; `github/codeql-action/upload-sarif@v1` to upload the **SARIF** file we can now see the MSDO Terrascan results and issues that needs to be resolved directly from the repository Security tab:

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
