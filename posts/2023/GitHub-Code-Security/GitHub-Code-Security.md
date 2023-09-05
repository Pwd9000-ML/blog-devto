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

### Feature 1: Security Alerts for Vulnerable Dependencies

GitHub's [Dependabot](https://docs.github.com/en/code-security/dependabot/dependabot-alerts/about-dependabot-alerts) monitors your dependencies (viewable under the repository Security > vulnerability alerts > Dependabot) and sends alerts when it encounters any vulnerabilities.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Code-Security/assets/secalert.png)

For example, consider you're using an outdated or vulnerable version of a library. **Dependabot** would send you an alert mentioning the vulnerability, its severity level, and steps to resolve it. Depending on how serious the issue is, GitHub can generate an automated security update to alleviate the risk, bolstering your code's security.

---

### Feature 2: Secret Scanning

In the rush of development work, it's not uncommon to accidentally commit sensitive details like **API keys** or **passwords**. GitHub's Secret Scanning feature comes in handy here.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Code-Security/assets/secscan.png)

Suppose you unknowingly committed an **Azure Storage Account Access Key** to your repository. The **Secret Scanning** feature, once activated, would identify this and notify you or the secret provider. You can then revoke the compromised secret and generate a new one, thereby preventing any unauthorised access.

Have a look at the [supported-secrets](https://docs.github.com/en/code-security/secret-scanning/secret-scanning-patterns#supported-secrets) for more information.

---

## Conclusion

I hope you have enjoyed this post and have learned something new. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
