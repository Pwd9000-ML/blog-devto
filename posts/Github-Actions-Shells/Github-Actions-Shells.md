---
title: GitHub Actions - All the Shells
published: false
description: GitHub Actions Shells
tags: 'devops, actions, tutorial, github'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/Github-Actions-Shells/assets/main-sh.png'
canonical_url: null
id: 904114
---

## :bulb: What are GitHub Actions? :bulb:

Let's first start by looking at what are [GitHub Actions](https://docs.github.com/en/actions/learn-github-actions/understanding-github-actions)? GitHub Actions helps automate tasks within your software development life cycle. They are event-driven, meaning that you can run a series of commands after a specified event has occurred. For example, every time someone creates a pull request for a repository, you can automatically run a command that executes a software testing script. In fact you can create any sort of creative automation using GitHub Actions.

[GitHub Actions](https://docs.github.com/en/actions/learn-github-actions/understanding-github-actions) consists of a few different components, let's take a look at some of these components in a bit more detail.

- **Workflows**

A workflow is a YAML based file that acts as an automated procedure that you add to your repository in a special directory path `.github/workflows` at the root of your GitHub repository. It is synonymous to an Azure DevOps multistage YAML pipeline and also shares a very similar [YAML syntax schema](https://docs.github.com/en/actions/learn-github-actions/workflow-syntax-for-github-actions). Workflows are made up of one or more jobs and can be scheduled or triggered by an event. Workflows can be used to build, test, package, release, or deploy a project on GitHub. You can even reference a workflow within another workflow by [Reusing workflows](https://docs.github.com/en/actions/learn-github-actions/reusing-workflows)

- **Events**

An event is a specific activity that triggers a workflow. For example, activity can originate from GitHub when someone pushes a commit to a repository or when an issue or pull request is created. You can also use the [repository dispatch webhook](https://docs.github.com/en/rest/reference/repos#create-a-repository-dispatch-event) to trigger a workflow when an external event occurs. You can have workflows run on a specified schedule using CRON or even have the option to trigger a workflow run manually. There is a whole [LIST](https://docs.github.com/en/actions/learn-github-actions/events-that-trigger-workflows) of events that can be used to trigger workflows.

- **Jobs**

A job is a set of steps that execute on the same runner. By default, a workflow with multiple jobs will run those jobs in parallel. You can also configure a workflow to run jobs sequentially. For example, a workflow can have two sequential jobs that build and test code, where the test job is dependent on the status of the build job. If the build job fails, the test job will not run.

- **Steps**

A step is an individual task that can run commands in a job. A step can be either an **action** or a **shell** command. Each step in a job executes on the same runner, allowing the actions in that job to share data with each other.

- **Actions**

Actions are standalone commands that are combined into steps to create a job. Actions are the smallest portable building block of a workflow. You can create your own actions, or use actions created by the GitHub community. To use an action in a workflow, you must include it as a step.

- **Runners**

A runner is a server that has the **GitHub Actions runner application** installed. It is synonymous to Azure DevOps-hosted agents. You can use a runner hosted by GitHub, or you can host your own. A runner listens for available jobs, runs one job at a time, and reports the progress, logs, and results back to GitHub. GitHub-hosted runners are based on Ubuntu Linux, Microsoft Windows, and macOS, and each job in a workflow runs in a fresh virtual environment, you can also see what software are installed on each of the [GitHub-hosted runners VM images](https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners). If you need a different operating system or require a specific hardware configuration, you can host your own runners using [self-hosted runners](https://docs.github.com/en/actions/hosting-your-own-runners).

## :turtle: What are Actions Shells? :turtle:

Now that you have some idea of all the different components that makes up GitHub Actions lets take a look at what **Shells** are.

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my [Github](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/DevOps-Terraform-Complex-Vars/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}
