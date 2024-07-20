---
title: Best Practices for Using GitHub Secrets - Part 1
published: true
description: Best Practices for Managing Sensitive Information in a GitHub Workflow
tags: 'github, git, devops, devsecops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/GitHub-Secrets-Best-Practise/assets/main-gh-tips.png'
canonical_url: null
id: 1924247
series: GitHub Pro Tips
date: '2024-07-18T09:35:58Z'
---

## Managing Sensitive Information in a GitHub Workflow

This article is **Part 1** of a 2-Part series where we'll explore the best practices for managing sensitive information in your **[GitHub workflows](https://docs.github.com/en/actions/using-workflows/about-workflows?wt.mc_id=DT-MVP-5004771)** by using **[GitHub Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#about-secrets?wt.mc_id=DT-MVP-5004771)** using the GitHub Website UI and giving a general overview and feel for **GitHub Secrets** and why you would want to use them.

In today's fast-paced development environment, automation is key. However, this often requires the handling of **sensitive information** such as **API keys**, **credentials**, and other **secrets**. Managing these securely is crucial to avoid unauthorised access and data breaches.

This is where **[GitHub Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#about-secrets?wt.mc_id=DT-MVP-5004771)** come in. **[GitHub Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#about-secrets?wt.mc_id=DT-MVP-5004771)** allow you to securely store sensitive information and access it in your workflows without exposing sensitive information in your codebase.

In this part we will focus more on what is available natively in **GitHub** in terms of **Secrets** management, what types of **Secrets** you can use and how to use them in your **GitHub Workflows**.

In **Part 2** of this series we will go further and look at how we can store **Secrets** securely in **[Azure Key Vault](https://learn.microsoft.com/en-us/azure/key-vault/general/basic-concepts?wt.mc_id=DT-MVP-5004771)** and how to integrate your GitHub Workflows with **Azure** for retrieving **Secrets** from a **Key Vault** to use in workflows, giving you another flexible way of using secrets in your code and offers a more centralised management of your **Secrets**.

### Why Secure Handling of Sensitive Information is Crucial

What is the purpose of **GitHub Secrets** you may wonder, and why do you even want to use them?

The reason is simple, exposing sensitive information in **git** code repositories can lead to severe consequences such as **unauthorised access**, **data breaches**, and possible leak of **sensitive** or **private information** which can lead to **reputational damage**. Properly managing this information ensures the security and integrity of your applications and data.

### Common Pitfalls to Avoid

When managing sensitive information in your workflows and repositories, there are some common pitfalls to avoid:

1. **Hardcoding Secrets:** Never hardcode secrets in your codebase. Always use **[GitHub Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#about-secrets?wt.mc_id=DT-MVP-5004771)** or secret management tools such as **[Azure Key Vault](https://learn.microsoft.com/en-us/azure/key-vault/general/basic-concepts?wt.mc_id=DT-MVP-5004771)**.
2. **Improper Access Control:** Ensure that only necessary workflows and users have access to secrets.
3. **Exposing Secrets in Logs:** Be cautious not to print secrets in logs, as logs can be accessed by unauthorised users.

## Using GitHub Secrets

Let's take a closer look at how you can start with using **[GitHub Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#about-secrets?wt.mc_id=DT-MVP-5004771)** and how you can access them in your workflows using the GitHub Website UI. Remember that secrets are encrypted and only exposed to selected workflows.

1. **Navigate to Your Repository:**  
   1.1. Go to your GitHub repository.  
   1.2. Click on `Settings`.  
   ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/GitHub-Secrets-Best-Practise/assets/1-settings.png)

2. **Access Secrets:**  
   2.1. In the left sidebar, click on `Secrets and variables` under the `Security` section.  
   2.2. Notice that you have options for `Actions`, `Codespaces` and `Dependabot`.  
   ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/GitHub-Secrets-Best-Practise/assets/1-secrets.png)  
   2.3. Because we are working with GitHub Workflows, we will focus on `Actions`. But also know that you can use secrets in other areas of your repository as well, such as inside of your **Codespaces** or for **Dependabot** specific workflows.  
   For more information on using **Secrets** in **Codespaces** check out: **[Codespaces Secrets](https://docs.github.com/en/codespaces/managing-your-codespaces/managing-your-account-specific-secrets-for-github-codespaces?wt.mc_id=DT-MVP-5004771)**, and for using **Secrets** in **Dependabot** check out: **[Dependabot Secrets](https://docs.github.com/en/code-security/dependabot/working-with-dependabot/automating-dependabot-with-github-actions#accessing-secrets?wt.mc_id=DT-MVP-5004771)**.

3. **Adding Secrets:**  
    3.1. We will be setting up a **repository secret**, but note that you can configure secrets at different levels. Click on `New repository secret` on the bottom right corner. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/GitHub-Secrets-Best-Practise/assets/1-add-secret.png) **[Environment Secrets:](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-an-environment?wt.mc_id=DT-MVP-5004771)** If you have [github environments](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment?wt.mc_id=DT-MVP-5004771) configured, you can also create secrets that are stored at the environment level, this allows you to enable required reviewers to control access to the secrets. Another benefit of this is that workflow jobs cannot access environment secrets until approval is granted by required approvers.  
   **[Organization Secrets:](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-an-organization?wt.mc_id=DT-MVP-5004771)** Organization-level secrets lets you share secrets between multiple repositories, which can reduce the need for creating duplicate secrets per repository. Another benefit is that you can use access policies to control which repositories can use organization-level secrets. Unfortunately this feature is not available for free accounts on private repositories.  
   **[Repository Secrets:](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository?wt.mc_id=DT-MVP-5004771)** Repository-level secrets are stored in a single repository and can be used by workflows in the same repository. These secrets are not available to forks of the repository. Also see **[variables](https://docs.github.com/en/actions/learn-github-actions/variables?wt.mc_id=DT-MVP-5004771)** for more information on configuring non-secret variables in your workflows.  
    3.2. Provide a `Name` and `Value` for your secret.  
    3.3. Click `Add secret`.  
    ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/GitHub-Secrets-Best-Practise/assets/2-add-secret.png) Once the `Secret` is added, it is encrypted and cannot be viewed again. You can only update or delete the secret after it is created, no secret history is maintained either.  
    ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/GitHub-Secrets-Best-Practise/assets/3-add-secret.png)

### Using GitHub Secrets in an Actions Workflow

Secrets can be accessed in your workflows using the `${{ secrets.SECRET_NAME }}` syntax. Here's an example of how to use **GitHub Secrets** in a **GitHub Actions workflow**:

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

In the above example, in the last step named `Deploy`, the `API_KEY` secret is accessed using `${{ secrets.API_KEY }}`. This ensures that the secret is securely accessed in the workflow without exposing it in the codebase:

```yml
- name: Deploy
  env:
    API_KEY: ${{ secrets.API_KEY }}
  run: |
    echo "Deploying with API Key: $API_KEY"  
    # Insert your deployment script here
```

## Access Control for Secrets

To be able to create secrets on the repository you need to have **Admin access** to the repository, otherwise the UI will not be visible, since it is under the repository settings.

That also means that team members that do not have Admin access, cannot see the repository secrets in the UI and for organization level secrets you need Admin access at the organization level.

For more information on how to manage, access and maintain secrets as a non-admin user, you can check out this article by **[Rob Bos](https://www.linkedin.com/in/bosrob/)** explaining how you can use the **[GitHub API](https://docs.github.com/en/rest/actions/secrets?wt.mc_id=DT-MVP-5004771)** and **[GitHub CLI](https://cli.github.com/manual/gh_secret_list?wt.mc_id=DT-MVP-5004771)** to manage secrets as a non-admin user: **[GitHub Secrets Without Admin Rights](https://devopsjournal.io/blog/2022/11/02/GitHub-secrets-without-admin-rights)**.

## Conclusion

Managing sensitive information securely is vital for any DevOps workflow. By utilising **GitHub Secrets**, you can ensure that your secrets are stored and accessed securely. Always follow best practices and avoid common pitfalls to maintain the security and integrity of your applications and code base.

In this post we only covered a basic overview of **GitHub Secrets** and how to use them in your **GitHub Workflows**. But we can go even further by storing **Secrets** securely in **Azure Key Vault** and integrating **Github** with **Azure**, allowing your **GitHub Action Workflows** to retrieve secrets from **Azure Key Vault**, which offers a few more benefits and flexibility in managing **Secrets**.

One of the biggest benefits of using **Azure Key Vault** is that it allows you to store your secrets in a centralised location, separate from your codebase, apart from **[Organization Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-an-organization?wt.mc_id=DT-MVP-5004771)**, it addresses the limitation with **[Repository Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository?wt.mc_id=DT-MVP-5004771)** where secrets have to be set in each unique repository which can make secrets management or rotation cumbersome.

Just to name a few more benefits of using **Secrets** in **GitHub** with **[Azure Key Vault](https://learn.microsoft.com/en-us/azure/key-vault/general/basic-concepts?wt.mc_id=DT-MVP-5004771)** is that they can be accessed by multiple repositories and workflows, secret rotation can be managed centrally, access to secrets can be controlled using **[Azure RBAC](https://learn.microsoft.com/en-us/azure/role-based-access-control/overview?wt.mc_id=DT-MVP-5004771)** instead of assigning Admin access over repos, secrets history can also be maintained for auditing purposes and previous versions of secrets can be restored if needed.

Take a look at how you can integrate **Azure Key Vault** with your **GitHub Workflows** by using passwordless/federated integration between **GitHub** and **Azure** using OIDC (Open ID Connect), in the next part of this series: **COMING SOON! [Integrating Azure Key Vault for Secrets with GitHub Action Workflows - Part 2]() COMING SOON!**.

I hope you have enjoyed this post and have learned something new. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
