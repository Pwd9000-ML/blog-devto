---
title: Securing Your Code with GitHub
published: true
description: Understanding and Leveraging GitHub's Security Tools
tags: 'github, devsecops, devops, security'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Code-Security/assets/main-gh-tips.png'
canonical_url: null
id: 1589878
series: GitHub Pro Tips
date: '2023-09-06T15:10:04Z'
---

## Understanding and Leveraging GitHub's Security Tools

GitHub is the preferred platform for millions of developers worldwide, and for good reason. Alongside its version control functionalities, GitHub provides a wealth of security features specially designed to keep your projects safe.

In this guide, we will walk you through the varied features, from **security alerts** for **vulnerable dependencies** to **secret scanning**, to help you fortify your code.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Code-Security/assets/orgsec.png)

## Automating Code Security

Before we dive deeper, let's understand why we need to focus on securing our code. With cyber threats on the rise, we simply can't ignore the importance of robust security measures. Hackers often exploit weak spots in your code and dependencies, which might be left vulnerable accidentally.

GitHub has automated security features that help mitigate these risks, making your projects resilient to such threats.

You can enable and configure these security features on **_all_** repositories, by navigating to the **Security & Analysis** tab in your organisation's **settings**.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Code-Security/assets/orgsec2.png)

Or you can also enable/disable security features on individual repositories, by navigating to the **Security** tab in your repository's **settings**.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Code-Security/assets/repo-sec.png)

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Code-Security/assets/repo-sec2.png)

**Recommendation:** I recommended to enable these features on **_all_** repositories (existing and new) in your organisation, and if absolutely necessary, disable the ones you do not need on a per repository basis.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Code-Security/assets/orgsec.png)

Let's take a look at some of these security features in a bit more detail.

---

## 1. Security Alerts for Vulnerable Dependencies

GitHub's **[Dependabot Alerts](https://docs.github.com/en/code-security/dependabot/dependabot-alerts/about-dependabot-alerts?wt.mc_id=DT-MVP-5004771)** monitors your dependencies (viewable under the repository Security > vulnerability alerts > Dependabot) and sends alerts when it encounters any vulnerabilities.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Code-Security/assets/secalert.png)

For example, consider you're using an outdated or vulnerable version of a library. **Dependabot** would send you an alert mentioning the vulnerability, its severity level, and steps to resolve it. Depending on how serious the issue is, GitHub can generate an automated security update to alleviate the risk, bolstering your code's security.

---

## 2. Secret Scanning

In the rush of development work, it's not uncommon to accidentally commit sensitive details like **API keys** or **passwords**. GitHub's Secret Scanning feature comes in handy here.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Code-Security/assets/secscan.png)

Suppose you unknowingly committed an **Azure Storage Account Access Key** to your repository. The **Secret Scanning** feature, once activated, would identify this and notify you or the secret provider. You can then revoke the compromised secret and generate a new one, thereby preventing any unauthorised access.

Have a look at the [supported-secrets](https://docs.github.com/en/code-security/secret-scanning/secret-scanning-patterns#supported-secrets?wt.mc_id=DT-MVP-5004771) for more information.

---

## 3. Code Scanning

GitHub's Code Scanning feature, empowered by the semantic analysis engine **CodeQL**, is a crucial security tool that scans your code for any potential vulnerabilities.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Code-Security/assets/codescan.png)

Consider a scenario where a developer unknowingly introduces a SQL injection vulnerability in their code. The **Code Scanning** feature would identify this vulnerability during its analysis, providing a description of the issue and advice for resolution. This proactive approach to threat detection allows for resolution before any damage occurs.

Have a look at [supported languages and frameworks](https://docs.github.com/en/code-security/code-scanning/introduction-to-code-scanning/about-code-scanning-with-codeql#about-codeql?wt.mc_id=DT-MVP-5004771) for more information.

If your repository hosts supported CodeQL languages, you can either let GitHub automatically analyse your code by using a **_default_** setting or allow you to customise an advanced configuration using a **YAML** config.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Code-Security/assets/codescan2.png)

Here is what a default configuration config would looks like:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Code-Security/assets/codescan3.png)

If your repository does not host supported CodeQL languages, or even if it does, but also contain other languages or frameworks, you can also add third-party code scanning tools in addition to your repository to further enhance your code's security, such as:

- **_[SonarCloud:](https://github.com/Pwd9000-ML/terraform-azurerm-nsg-administration/actions/new?category=security&query=SonarCloud)_** A cloud-based code analysis service that automatically detects bugs, vulnerabilities, and code smells in your code.
- **_[TfSec:](https://github.com/Pwd9000-ML/terraform-azurerm-nsg-administration/actions/new?category=security&query=TfSec)_** A static analysis security scanner for your Terraform code.
- **_[trivy:](https://github.com/Pwd9000-ML/terraform-azurerm-nsg-administration/actions/new?category=security&query=Trivy)_** Scan Docker container images for vulnerabilities in OS packages and language dependencies.

At the time of this writing, there are over 76 third-party [code scanning tools/workflows](https://github.com/Pwd9000-ML/terraform-azurerm-nsg-administration/actions/new?category=security&query=code+scanning) available for use, and the list is growing.

---

## 4. Dependabot Security/Dependency Updates

**[Dependabot Security Updates](https://docs.github.com/en/code-security/dependabot/dependabot-security-updates/about-dependabot-security-updates?wt.mc_id=DT-MVP-5004771)** is a security tool that handles your project **dependencies** by generating **alerts** for **vulnerabilities** as mentioned earlier, but can also create pull requests to update them.

Dependabot Security Updates is a feature of **Dependabot**, which is a bot that automates dependency updates not just for security, but also for non-security updates, or out of date dependencies, keeping your project up to date.

For instance, if a new version of a dependency you're using is released that fixes a major security flaw, Dependabot would send an alert. It would also raise a pull request to update the dependency version in your project, keeping your project secure without requiring manual intervention.

Here is an example of a Dependabot pull request where it has updated the **[Terraform AzureRM Provider](https://github.com/hashicorp/terraform-provider-azurerm/releases)** from version **3.69.0** to **3.71.0**:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Code-Security/assets/dependabot.png)

Have a look at all the [supported package ecosystems](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file#package-ecosystem?wt.mc_id=DT-MVP-5004771) Dependabot supports for more information.

You can also look at what dependencies are being monitored by **Dependabot** in your repository by navigating to the **Insights** tab in your repository.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Code-Security/assets/insights.png)

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Code-Security/assets/insights2.png)

---

## 5. Security Policies and Advisories

GitHub allows developers to forge their security policies and advisories by allowing anyone to report security vulnerabilities directly and privately to the maintainers.

- A **security policy** document assists contributors in understanding how to report a security vulnerability in your project. It's like creating a help page for a user who identifies a potential breach, thereby promoting responsible reporting.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Code-Security/assets/pol.png)

- A **security advisory**, on the other hand, allows you to interact with users regarding identified vulnerabilities. For example, you could use an advisory to discuss a recently discovered flaw in your project, suggest a workaround, and preview a fix before public disclosure.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Code-Security/assets/report.png)

When private vulnerability reporting is enabled for a repository, security researchers will see a new button in the Advisories page of the repository. The security researcher can click this button to privately discuss, fix, and publish information about security vulnerabilities in your repository's code.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Code-Security/assets/report2.png)

Have a look at **_[Privately reporting a security vulnerability](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability?wt.mc_id=DT-MVP-5004771)_** for more information.

---

## Conclusion

GitHub's security features can drastically help lower the risks of your code getting exploited. By using these tools in concert, you benefit from both proactive detection and resolution of potential vulnerabilities.

Moreover, the value of automating your code security cannot be overstated. With these automated features, you can manage vulnerabilities, dependencies, and other threats all in one place. The ability to find and fix issues before they become problematic means you can continue to write code confidently.

By harnessing the potential of GitHub's security features, you are taking a significant step towards a more secure coding environment. Protecting your code is as crucial as writing it. Lean on GitHub's comprehensive suite of security tools and keep your projects safe and resilient.

I hope you have enjoyed this post and have learned something new. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [X/Twitter](https://x.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
