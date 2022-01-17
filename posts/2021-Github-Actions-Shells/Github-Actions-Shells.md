---
title: GitHub Actions - All the Shells
published: true
description: GitHub Actions Shells
tags: 'devops, githubactions, github, automation'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Github-Actions-Shells/assets/main-sh.png'
canonical_url: null
id: 904114
date: '2021-11-22T17:35:44Z'
---

## :bulb: What are GitHub Actions?

[GitHub Actions](https://docs.github.com/en/actions/learn-github-actions/understanding-github-actions) helps automate tasks within your software development life cycle. They are event-driven, meaning that you can run a series of commands after a specified event has occurred. For example, every time someone creates a pull request for a repository, you can automatically run a command that executes a software testing script. In fact you can create any sort of creative automation using GitHub Actions.

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

## :turtle: What are Actions Shells?

Now that you have some idea of all the different components that makes up GitHub Actions lets take a look at what **Shells** are.

As you know within a workflow **job** you can have certain **steps**, and a step can be either an **action** or a **shell** command. So let's take a look at a typical shell command that can be initiated using **runs**. Each **run** keyword represents a new process and **shell** in the **runner** environment.

When you provide multi-line commands, each line runs in the same shell. Here is an example of a basic run command in a workflow step:

```yaml
jobs:
  name-of-job:
    runs-on: windows-latest
    steps:
      - name: Hello world
        run: |
          write-output "Hello World"
```

You will notice that I have used a powershell command: `write-output "Hello World"`, you might be wondering why would I use powershell commands here? The reason is because the **runner** environment I have specified is using a VM image: `windows-latest` and each runner environment will have a different **default shell** language to run commands, for **windows** this happens to be `pwsh (PowerShell core)`. Here is a table showing the default shells for different **runner** environments/platforms:

| Platforms | Default Shell | Description |
| --- | --- | --- |
| Windows | `pwsh` | This is the default shell used on Windows. The PowerShell Core. GitHub appends the extension .ps1 to your script name. If your self-hosted Windows runner does not have PowerShell Core installed, then PowerShell Desktop is used instead. |
| non-Windows platforms | `bash` | The default shell on non-Windows platforms with a fallback to sh. When specifying a bash shell on Windows, the bash shell included with Git for Windows is used. |

Additional shells that are supported but must be specified explicitly (non-default) are as follow:

| Platforms | Shell | Description |
| --- | --- | --- |
| All (windows + Linux) | `python` | Executes the python command |
| All (windows + Linux) | `pwsh` | Default shell used on Windows, must be specified on other **runner** environment types |
| All (windows + Linux) | `bash` | Default shell used on non-Windows platforms, must be specified on other **runner** environment types |
| Linux / macOS | `sh` | The fallback behavior for non-Windows platforms if no shell is provided and bash is not found in the path. |
| Windows | `cmd` | GitHub appends the extension .cmd to your script |
| Windows | `PowerShell` | The PowerShell Desktop. GitHub appends the extension .ps1 to your script name. |

Let's take a look and see how we can explicitly set our shell to be a scripting shell language we prefer to override the default of the **runner** environment:

```yaml
jobs:
  name-of-job:
    runs-on: ubuntu-latest
    steps:
      - name: Hello world
        shell: pwsh
        run: |
          write-output "Hello World"
```

You will notice that I have again used a PowerShell command: `write-output "Hello World"`, but my **runner** environment this time is a non-windows `ubuntu-latest` VM image. The default **Shell** on Ubuntu would be `bash` but I have explicitly set an override of `pwsh` / PowerShell Core by specifying `shell: pwsh` before my **run**.

Here are a few more examples on how `shell:` can be used to override a **runners** default command line program:

- Running a script using bash

```yaml
steps:
  - name: Display the path
    run: echo $PATH
    shell: bash
```

- Running a script using Windows cmd

```yaml
steps:
  - name: Display the path
    run: echo %PATH%
    shell: cmd
```

- Running a script using PowerShell Core

```yaml
steps:
  - name: Display the path
    run: write-output ${env:PATH}
    shell: pwsh
```

- Using PowerShell Desktop to run a script

```yaml
steps:
  - name: Display the path
    run: write-output ${env:PATH}
    shell: powershell
```

- Running a python script

```yaml
steps:
  - name: Display the path
    run: |
      import os
      print(os.environ['PATH'])
    shell: python
```

- Custom shell

You can set the shell value to a template string using: `command […options] {0} [..more_options]`. GitHub interprets the first whitespace-delimited word of the string as the command, and inserts the file name for the temporary script at `{0}`.

For example:

```yaml
steps:
  - name: Display the environment variables and their values
    run: |
      print %ENV
    shell: perl {0}
```

The command used, `perl` in this example, must be installed on the runner.

## Set default shell

You can use `defaults.run` to provide default `shell` option for all run steps in a workflow. You can also set default settings for run that are only available to a job. When more than one default setting is defined with the same name, GitHub uses the most specific default setting. For example, a default setting defined in a job will override a default setting that has the same name defined in a workflow.

**Example:** Set the default shell and working directory

```yaml
name: my workflow
on: push

jobs:
  name-of-job:
    runs-on: windows-latest
    defaults:
      run:
        shell: pwsh
    steps:
      - name: Hello world
        run: |
          write-output "Hello World"
```

I hope you have enjoyed this post and have learned something new. :heart: You can find more information on action shells on the [Github actions syntax page](https://docs.github.com/en/actions/learn-github-actions/workflow-syntax-for-github-actions#jobsjob_idstepsshell)

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}
