---
title: Securing Your Code with GitHub
published: false
description: Understanding and Leveraging GitHub's Security Tools
tags: 'github, devsecops, devops, security'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Code-Security/assets/main-gh-tips.png'
canonical_url: null
id: 1589878
series: GitHub Pro Tips
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

GitHub's [Dependabot](https://docs.github.com/en/code-security/dependabot/dependabot-alerts/about-dependabot-alerts) monitors your dependencies (viewable under the repository Security > vulnerability alerts > Dependabot) and sends alerts when it encounters any vulnerabilities.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Code-Security/assets/secalert.png)

For example, consider you're using an outdated or vulnerable version of a library. **Dependabot** would send you an alert mentioning the vulnerability, its severity level, and steps to resolve it. Depending on how serious the issue is, GitHub can generate an automated security update to alleviate the risk, bolstering your code's security.

---

## 2. Secret Scanning

In the rush of development work, it's not uncommon to accidentally commit sensitive details like **API keys** or **passwords**. GitHub's Secret Scanning feature comes in handy here.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Code-Security/assets/secscan.png)

Suppose you unknowingly committed an **Azure Storage Account Access Key** to your repository. The **Secret Scanning** feature, once activated, would identify this and notify you or the secret provider. You can then revoke the compromised secret and generate a new one, thereby preventing any unauthorised access.

Have a look at the [supported-secrets](https://docs.github.com/en/code-security/secret-scanning/secret-scanning-patterns#supported-secrets) for more information.

---

## 3. Code Scanning

GitHub's Code Scanning feature, empowered by the semantic analysis engine **CodeQL**, is a crucial security tool that scans your code for any potential vulnerabilities.  

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Code-Security/assets/codescan.png)

Consider a scenario where a developer unknowingly introduces a SQL injection vulnerability in their code. The **Code Scanning** feature would identify this vulnerability during its analysis, providing a description of the issue and advice for resolution. This proactive approach to threat detection allows for resolution before any damage occurs.

Have a look at [supported languages and frameworks](https://docs.github.com/en/code-security/code-scanning/introduction-to-code-scanning/about-code-scanning-with-codeql#about-codeql) for more information.  

If your repository hosts supported CodeQL languages, you can either let GitHub automatically analyse your code by using a **_default_** setting or allow you to customise an advanced configuration using a **YAML** config.  

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Code-Security/assets/codescan2.png)  

Here is what a default configuration config would looks like:  

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Code-Security/assets/codescan3.png)  

If your repository does not host supported CodeQL languages, or even if it does, but also contain other languages or frameworks, you can also add third-party code scanning tools in addition to your repository to further enhance your code's security, such as:  

- **_[SonarCloud:](https://github.com/Pwd9000-ML/terraform-azurerm-nsg-administration/actions/new?category=security&query=code+scanning)_** A cloud-based code analysis service that automatically detects bugs, vulnerabilities, and code smells in your code.  
- **_TFSEC:_** A static analysis security scanner for your Terraform code.  
- **_trivy:_** Scan Docker container images for vulnerabilities in OS packages and language dependencies.  

At the time of this writing there are over 70 third-party [code scanning tools/workflows](https://github.com/Pwd9000-ML/terraform-azurerm-nsg-administration/actions/new?category=security&query=code+scanning) available for use, and the list is growing.  

---

## Conclusion

I hope you have enjoyed this post and have learned something new. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
