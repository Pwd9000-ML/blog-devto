---
title: Securing Your GitHub Workflows - Best Practices for Using GitHub Secrets
published: false
description: Best Practices for Managing Sensitive Information in a GitHub Workflow
tags: 'github, git, devops, devsecops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/GitHub-Secrets-Best-Practise/assets/main-gh-tips.png'
canonical_url: null
id: 1924247
series: GitHub Pro Tips
---

## Overview - Managing Sensitive Information in a GitHub Workflow

In today's fast-paced development environment, automation is key. However, this often requires the handling of **sensitive information** such as **API keys**, **credentials**, and other **secrets**. Managing these securely is crucial to avoid unauthorised access and data breaches.

In this blog post, we'll explore best practices for managing sensitive information in your **[GitHub workflows](https://docs.github.com/en/actions/using-workflows/about-workflows?wt.mc_id=DT-MVP-5004771)** by using **[GitHub Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#about-secrets?wt.mc_id=DT-MVP-5004771)**, and also how we can go further by storing **Secrets** securely in **[Azure Key Vault](https://learn.microsoft.com/en-us/azure/key-vault/general/basic-concepts?wt.mc_id=DT-MVP-5004771)**, integrating your GitHub Workflows with **Azure Key Vault** for enhanced security.

### Why Secure Handling of Sensitive Information is Crucial

What is the purpose of **GitHub Secrets** you may wonder, and why do you even want to use them?

The reason is simple, exposing sensitive information in **git** code repositories can lead to severe consequences such as **unauthorised access**, **data breaches**, and possible leak of sensitive or **private information** which can lead to **reputational damage**. Properly managing this information ensures the security and integrity of your applications and data.

### Using GitHub Secrets

**[GitHub Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#about-secrets?wt.mc_id=DT-MVP-5004771)** allow you to securely store sensitive information and access it in your workflows. These secrets are encrypted and only exposed to selected workflows. Let's take a look at how you can get started with **GitHub Secrets** and how to set them up in your workflows.

1. **Navigate to Your Repository:**
    - Go to your GitHub repository.
    - Click on `Settings`. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/GitHub-Secrets-Best-Practise/assets/1-settings.png)

2. **Access Secrets:**
    - In the left sidebar, click on `Secrets and variables` under the `Security` section.
    - Notice that you have options for `Actions`, `Codespaces` and `Dependabot`.
    - Because we are working with GitHub Workflows, we will focus on `Actions`. But also know that you can use these secrets in other areas of your repository as well, such as inside of your **Codespaces** or for **Dependabot** specific workflows.
     For more information on using **Secrets** in **Codespaces** check out: **[Codespaces Secrets](https://docs.github.com/en/codespaces/managing-your-codespaces/managing-your-account-specific-secrets-for-github-codespaces?wt.mc_id=DT-MVP-5004771)**
    - For more information on using **Secrets** in **Dependabot** check out: **[Dependabot Secrets](https://docs.github.com/en/code-security/dependabot/working-with-dependabot/automating-dependabot-with-github-actions#accessing-secrets?wt.mc_id=DT-MVP-5004771)** ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/GitHub-Secrets-Best-Practise/assets/1-secrets.png)

3. **Add a New Secret:**  
    - Click on `New repository secret`.  
    - Provide a `Name` and `Value` for your secret.  
    - Click `Add secret`.  
    - Note that you can set up **[Environment Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-an-environment?wt.mc_id=DT-MVP-5004771)**, **[Organization Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-an-organization?wt.mc_id=DT-MVP-5004771)** and **[Repository Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository?wt.mc_id=DT-MVP-5004771)**. As well as **[variables](https://docs.github.com/en/actions/learn-github-actions/variables?wt.mc_id=DT-MVP-5004771)** for use in your workflows. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/GitHub-Secrets-Best-Practise/assets/1-add-secret.png) ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/GitHub-Secrets-Best-Practise/assets/2-add-secret.png) ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/GitHub-Secrets-Best-Practise/assets/3-add-secret.png)  

### Example: Using GitHub Secrets in a Workflow  

Secrets can be accessed in your workflows using the `${{ secrets.SECRET_NAME }}` syntax. Here's an example of how to use GitHub Secrets in a GitHub Actions workflow:  

```yaml
Here's an example of how to use GitHub Secrets in a GitHub Actions workflow:  

```yaml  
name: CI/CD Pipeline  
   
on: [push]  
   
jobs:  
  build:  
    runs-on: ubuntu-latest  
  
    steps:  
    - uses: actions/checkout@v2  
  
    - name: Use Node.js  
      uses: actions/setup-node@v2  
      with:  
        node-version: '14'  
  
    - name: Install Dependencies  
      run: npm install  
  
    - name: Run Tests  
      run: npm test  
  
    - name: Deploy  
      env:  
        API_KEY: ${{ secrets.API_KEY }}  
      run: |  
        echo "Deploying with API Key: $API_KEY"  
        # Insert your deployment script here  
```  

In this example, `API_KEY` is a secret stored in GitHub Secrets. It is accessed using `${{ secrets.API_KEY }}` within the workflow.  

## Conclusion

I hope you have enjoyed this post and have learned something new. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
