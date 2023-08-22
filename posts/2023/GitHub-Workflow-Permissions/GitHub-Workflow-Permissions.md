---
title: GitHub - Understanding Workflow Permissions
published: false
description: GitHub - Understanding GitHub Workflow Permissions
tags: 'github, githubactions, cicd, automation'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Workflow-Permissions/assets/main-gh-tips.png'
canonical_url: null
id: 1576283
series: GitHub Pro Tips
date: '2023-08-22T09:46:21Z'
---

## Overview - Managing Permissions in GitHub Actions Workflows

In this **GitHub Pro Tips** post we will look at how to manage permissions in GitHub Actions workflows.

GitHub Actions is a powerful tool for automating your CI/CD pipelines/workflows. It allows you to create workflows that can be triggered by events such as a **push** to a repository, a **pull request**, or a **new release**. Workflows are defined in **YAML** files that live in the `.github/workflows` directory of your repository.

In terms of Continuous Integration/Continuous Deployment (CI/CD), GitHub Actions provides a robust feature set for automating, customizing, and executing your software development workflows right in your repository. Today we will look at the the `permissions` parameter as a groundbreaking feature for constraining the `permissions` provided to the GitHub token.

We will also look at a few practical examples of how and when you would use this feature.

## A Dive Into GitHub Workflow's 'Permissions'

Let's discuss the **'permissions'** key in detail, which was officially released by GitHub in April 2021. This new feature enables more fine-grained control over the permissions given to the **[GITHUB_TOKEN](https://docs.github.com/en/actions/security-guides/automatic-token-authentication#about-the-github_token-secret)** in workflows.

This is particularly useful to maintain **'principle of least privilege'** - an important security concept stating that a user should have just enough rights necessary to perform their job and nothing more. By minimising the access to resources, you can reduce the damage that could result from accidents or exploits.

The `permissions` key allows you to set read, write, or none to different `scopes`. You define permissions at the **top level** or per **job level**, giving you flexibility and granularity in terms of access control.

Here is an example of defining permissions at the root level of a workflow:

```yaml
name: 'My workflow'

on: [push]

permissions:
  actions: read|write|none
  checks: read|write|none
  contents: read|write|none
  deployments: read|write|none
  id-token: read|write|none
  issues: read|write|none
  discussions: read|write|none
  packages: read|write|none
  pages: read|write|none
  pull-requests: read|write|none
  repository-projects: read|write|none
  security-events: read|write|none
  statuses: read|write|none

jobs: ...
```

You can also define permissions at the job level:

```yaml
jobs:
  stale:
    runs-on: ubuntu-latest

    permissions:
      actions: read|write|none
      checks: read|write|none
      contents: read|write|none
      deployments: read|write|none
      id-token: read|write|none
      issues: read|write|none
      discussions: read|write|none
      packages: read|write|none
      pages: read|write|none
      pull-requests: read|write|none
      repository-projects: read|write|none
      security-events: read|write|none
      statuses: read|write|none

    steps:
      - uses: actions/stale@v5
```

If you specify the access for any of these scopes, all of those that are not specified are set to `none`.

You can use the following syntax to define read or write access for all of the available scopes:

```yaml
permissions: read-all|write-all
```

You can use the following syntax to disable permissions for all of the available scopes:

```yaml
permissions: {}
```

## Practical Use Cases

Now that we understand how the permissions key is structured, let's move on to a few practical use cases.

1. **Workflows That Need Custom Permissions**

In workflows where you need to increase or restrict permissions for a particular job, you can set permissions on the job level:

```yaml
jobs:
  job1:
    permissions:
      contents: write
    runs-on: ubuntu-latest
    steps:
      - name: Push commit
        run: |
          echo "Hello, GitHub!" > hello.txt
          git add hello.txt
          git commit -m "Add hello.txt"
          git push
```

In this example, `job1` has **write** access to the repository contents which allows it to create a commit.

2. **Cases Where You Want to Limit Potential Damage**

fgdfg

## Conclusion

I hope you have enjoyed this post and have learned something new. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
