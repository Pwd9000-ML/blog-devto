---
title: Hosting your self hosted runners on GitHub Codespaces
published: true
description: How to use your GitHub Codespace as a self hosted runner
tags: 'github, codespaces, githubactions, development'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Codespaces-runner/assets/main01.png'
canonical_url: null
id: 1165803
series: GitHub Codespaces Pro Tips
date: '2022-08-13T14:10:07Z'
---

## Overview

Welcome to another part of my series **['GitHub Codespaces Pro Tips'](https://dev.to/pwd9000/series/19195)**. In the last part we spoke about integrating **GitHub** with **Azure DevOps** and how you can use some of the great features of GitHub, like **Codespaces** along with Azure DevOps.

In todays post I will share with you how you can use your **GitHub Codespace** not only as a "development environment" for working with your code, but also utilising the **Codespace** compute power, by running a **Self Hosted GitHub runner** inside of the Codespace at the same time.

We will be using a custom **docker image** that will automatically provision a **self hosted runner agent** and register it at the same time as provisioning the **Codespace** as part of the development environment.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Codespaces-runner/assets/diag01.png)

We will also look at the **Codespace/Runner** lifecycle. By default any **Active** codespaces that becomes **idle** will go into a hibernation mode after **30 minutes** to save on compute costs, so we will look at how this timeout can be configured and extended (if needed).

We will actually be using a very similar approach for the docker image configuration based on one of my previous blog posts, ['Create a Docker based Self Hosted GitHub runner Linux container'](https://dev.to/pwd9000/create-a-docker-based-self-hosted-github-runner-linux-container-48dh). So do check out that post also if you wanted more info on how **self hosted GitHub runner** containers work.

## Getting started

All of the code samples and examples are also available on my [GitHub Codespaces Demo Repository](https://github.com/Pwd9000-ML/GitHub-Codespaces-Lab/tree/master/.devcontainer/codespaceRunner).

Since **Codespaces/Dev containers** are based on **docker images**, we will create a **custom linux docker image** that will start and bootstrap a runner agent as the codespace starts up.

We will create the following folder structure tree in the [root](https://github.com/Pwd9000-ML/GitHub-Codespaces-Lab/tree/master/.devcontainer/codespaceRunner) of our **GitHub repository:**

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Codespaces-runner/assets/root01.png)

In your **GitHub repository** create a sub folder under `'.devcontainer'`, in my case I have called my codespace configuration folder `'codespaceRunner'`.

Next, create the following [Dockerfile](https://github.com/Pwd9000-ML/GitHub-Codespaces-Lab/blob/master/.devcontainer/codespaceRunner/Dockerfile):

```dockerfile
# You can pick any Debian/Ubuntu-based image. 😊
FROM mcr.microsoft.com/vscode/devcontainers/base:0-bullseye

# [Optional] Install zsh
ARG INSTALL_ZSH="true"
# [Optional] Upgrade OS packages to their latest versions
ARG UPGRADE_PACKAGES="false"

# Install needed packages and setup non-root user. Use a separate RUN statement to add your own dependencies.
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID
COPY library-scripts/*.sh /tmp/library-scripts/
RUN bash /tmp/library-scripts/common-debian.sh "${INSTALL_ZSH}" "${USERNAME}" "${USER_UID}" "${USER_GID}" "${UPGRADE_PACKAGES}" "true" "true"

# cd into the user directory, download and unzip the github actions runner
RUN cd /home/vscode && mkdir actions-runner && cd actions-runner

#input GitHub runner version argument
ARG RUNNER_VERSION="2.292.0"

RUN cd /home/vscode/actions-runner \
    && curl -O -L https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz \
    && tar xzf /home/vscode/actions-runner/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz \
    && /home/vscode/actions-runner/bin/installdependencies.sh

# copy over the start.sh script
COPY library-scripts/start.sh /home/vscode/actions-runner/start.sh

# Apply ownership of home folder
RUN chown -R vscode ~vscode

# make the script executable
RUN chmod +x /home/vscode/actions-runner/start.sh

# Clean up
RUN rm -rf /var/lib/apt/lists/* /tmp/library-scripts
```

Then create a `'devcontainer.json'` file. (See my [previous blog post](https://dev.to/pwd9000/introduction-to-github-codespaces-building-your-first-dev-container-69l) on how this file can be amended with additional features and extensions):

```JSON
{
	"name": "CodespaceRunner",
	"dockerFile": "Dockerfile",

	// Configure tool-specific properties.
	"customizations": {
		// Configure properties specific to VS Code.
		"vscode": {
			// Add the IDs of extensions you want installed when the container is created.
			"extensions": [
				"ms-vscode.azurecli",
				"ms-vscode.powershell",
				"hashicorp.terraform",
				"esbenp.prettier-vscode",
				"tfsec.tfsec"
			]
		}
	},

	// Use 'forwardPorts' to make a list of ports inside the container available locally.
	// "forwardPorts": [],

	// Use 'postStartCommand' to run commands each time the container is successfully started..
    "postStartCommand": "/home/vscode/actions-runner/start.sh",

	// Comment out to connect as root instead. More info: https://aka.ms/vscode-remote/containers/non-root.
	"remoteUser": "vscode",
    // Amend GitHub runner version with 'RUNNER_VERSION'. https://github.com/actions/runner/releases.
	"build": {
		"args": {
			"UPGRADE_PACKAGES": "true",
			"RUNNER_VERSION": "2.295.0"
		}
	},
	"features": {
		"terraform": "latest",
		"azure-cli": "latest",
		"git-lfs": "latest",
		"github-cli": "latest",
		"powershell": "latest"
	}
}
```

**NOTE:** You can amend the [GitHub runner version](https://github.com/actions/runner/releases) by amending the **build args** attribute **RUNNER_VERSION**.

```JSON
// Amend GitHub runner version with 'RUNNER_VERSION'. https://github.com/actions/runner/releases.
"build": {
    "args": {
        "UPGRADE_PACKAGES": "true",
        "RUNNER_VERSION": "2.295.0"
    }
```

Next we will create a folder with a few scripts that will be used by our **docker image**.

Create a folder called `'library-scripts'` and place the following two script inside: ['start.sh'](https://github.com/Pwd9000-ML/GitHub-Codespaces-Lab/blob/master/.devcontainer/codespaceRunner/library-scripts/start.sh) and ['common-debian.sh'](https://github.com/Pwd9000-ML/GitHub-Codespaces-Lab/blob/master/.devcontainer/codespaceRunner/library-scripts/common-debian.sh)

Let's take a closer look at each of the scripts.

1. **[common-debian.sh](https://github.com/Pwd9000-ML/GitHub-Codespaces-Lab/blob/master/.devcontainer/codespaceRunner/library-scripts/common-debian.sh)**: This script will install additional **debian** based tooling onto the **dev container**.

2. **[start.sh](https://github.com/Pwd9000-ML/GitHub-Codespaces-Lab/blob/master/.devcontainer/codespaceRunner/library-scripts/start.sh)**:

```bash
#start.sh
#!/bin/bash

GH_OWNER=$GH_OWNER
GH_REPOSITORY=$GH_REPOSITORY
GH_TOKEN=$GH_TOKEN

HOSTNAME=$(hostname)
RUNNER_SUFFIX="runner"
RUNNER_NAME="${HOSTNAME}-${RUNNER_SUFFIX}"
USER_NAME_LABEL=$( (git config --get user.name) | sed -e 's/ //g')
REPO_NAME_LABEL="$GH_REPOSITORY"

REG_TOKEN=$(curl -sX POST -H "Accept: application/vnd.github.v3+json" -H "Authorization: token ${GH_TOKEN}" https://api.github.com/repos/${GH_OWNER}/${GH_REPOSITORY}/actions/runners/registration-token | jq .token --raw-output)

/home/vscode/actions-runner/config.sh --unattended --url https://github.com/${GH_OWNER}/${GH_REPOSITORY} --token ${REG_TOKEN} --name ${RUNNER_NAME}  --labels ${USER_NAME_LABEL},${REPO_NAME_LABEL}
/home/vscode/actions-runner/run.sh
```

The second script will start up with the **Codespace/Dev container** and bootstraps the **GitHub runner** when the Codespace starts. Notice that we need to provide the script with some parameters:

```bash
GH_OWNER=$GH_OWNER
GH_REPOSITORY=$GH_REPOSITORY
GH_TOKEN=$GH_TOKEN
```

These parameters (environment variables) are used to configure and **register** the self hosted github runner against the correct repository.

We need to provide the GitHub account/org name via the `'GH_OWNER'` environment variable, repository name via `GH_REPOSITORY` and a PAT token with `GH_TOKEN`.

You can store sensitive information, such as tokens, that you want to access in your codespaces via environment variables. Let's configure these parameters as encrypted [secrets for codespaces](https://docs.github.com/en/codespaces/managing-your-codespaces/managing-encrypted-secrets-for-your-codespaces).

1. Navigate to the repository `'Settings'` page and select `'Secrets -> Codespaces'`, click on `'New repository secret'`. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Codespaces-runner/assets/sec01.png)

2. Create each **Codespace secret** with the values for your environment. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Codespaces-runner/assets/sec02.png)

**NOTE:** When the **self hosted runner** is started up and registered, it will also be labeled with the **'user name'** and **'repository name'**, from the following lines. (These labels can be amended if necessary):

```bash
USER_NAME_LABEL=$(git config --get user.name)
REPO_NAME_LABEL="$GH_REPOSITORY"
```

## Note on Personal Access Token (PAT)

See [creating a personal access token](https://docs.github.com/en/enterprise-server@3.4/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) on how to create a GitHub PAT token. PAT tokens are only displayed once and are sensitive, so ensure they are kept safe.

The minimum permission scopes required on the PAT token to register a self hosted runner are: `"repo"`, `"read:org"`:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Codespaces-runner/assets/PAT.png)

**Tip:** I recommend only using short lived PAT tokens and generating new tokens whenever new agent runner registrations are required.

## Deploying the Codespace GitHub runner

As you can see in the screenshot below, my repository does not have any runners configured.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Codespaces-runner/assets/run01.png)

1. Navigate to your repository, click on the `'<> Code'` dropdown and select the `'Codespaces'` tab, select the `'Advanced'` option to **Configure and create codespace**. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Codespaces-runner/assets/run02.png)

2. Select the relevant `'Branch'`, `'Region'`, `'Machine type'` and for the `'Dev container configuration'`, select the `'codespaceRunner'` config we created and click on `'Createcodespace'`. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Codespaces-runner/assets/run03.png)

It takes a few minutes to build and start the container, but you can view the logs whilst the codespace is provisioning in real time.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Codespaces-runner/assets/run04.png)

To speed up codespace creation, repository administrators can enable **Codespaces prebuilds** for a repository. For more information, see "[About GitHub Codespaces prebuilds](https://docs.github.com/en/codespaces/prebuilding-your-codespaces/about-github-codespaces-prebuilds)."

Once the **codespace** is provisioned, you can see the **hostname** of the underlying compute by typing in the terminal: `'hostname'`

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Codespaces-runner/assets/run05.png)

Navigate to your repository **settings** page, notice that there is now a **self hosted GitHub runner** registered and **labeled** with your **user name** and **repo name**. The **runner name** matches the **Codepsace hostname**.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Codespaces-runner/assets/run06.png)

## Managing Codespace/Runner lifecycle

When you **stop** your **codepsace** the self hosted runner will not be removed but will only go into an `'Offline'` state, and when you start the codespace up again the **runner** will be available again.

Also, as mentioned, by default any **Active** codespaces that are not **stopped** manually, will be **idle** and go into a hibernation mode after **30 minutes** to save on compute costs. Let's take a look at how we can amend [codespaces lifecycle](https://docs.github.com/en/codespaces/developing-in-codespaces/codespaces-lifecycle).

1. In the upper-right corner of any page, click your profile photo, then click **Settings** and in the "Code, planning, and automation" section of the sidebar, click **Codespaces**. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Codespaces-runner/assets/time01.png)

2. Under "Default idle timeout", enter the time that you want, then click Save. The time must be between 5 minutes and 240 minutes (4 hours). ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Codespaces-runner/assets/time02.png)

## Conclusion

As you can see, it is pretty easy to run **self hosted action runners** inside of your **Codespace** and utilize the compute power of the **dev container** itself.

By doing this we can solve a few problems with one solution.

1. Cost - Not wasting cost and compute power by adding compute separately for **self hosted runners** alongside **Codespaces**.
2. Administration - Having both services running on the same compute and sharing the same configuration and tooling saves time on administration and maintenance.
3. Availability - Having **self hosted runners** available as part of the running **codespace**.

**IMPORTANT:** Do note that making use of **runner labels** is very important when **triggring/running actions** against runners or runner groups provisioned on a **Codespace**. Hence each runner is labeled with the **user name** and **repo name**.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022/GitHub-Codespaces-runner/assets/label01.png)

## Example

A self-hosted runner automatically receives certain labels when it is added to GitHub Actions. These are used to indicate its operating system and hardware platform:

- `self-hosted`: Default label applied to all self-hosted runners.
- `linux`, `windows`, or `macOS`: Applied depending on operating system.
- `x64`, `ARM`, or `ARM64`: Applied depending on hardware architecture.

You can use your workflow's YAML to send jobs to a combination of these labels. In this example, a self-hosted runner that matches all three labels will be eligible to run the job:

```yml
runs-on: [self-hosted, linux, ARM64]
```

- `self-hosted` - Run this job on a self-hosted runner.
- `linux` - Only use a Linux-based runner.
- `ARM64` - Only use a runner based on ARM64 hardware.

The default labels are fixed and cannot be changed or removed. Consider using custom labels if you need more control over job routing.

As you can see from this [example workflow](https://github.com/Pwd9000-ML/GitHub-Codespaces-Lab/blob/master/.github/workflows/testCodespaceRunner.yml) in my repository, I am routing my **GitHub Action** jobs, specifically to my own **self hosted runner** on my **Codespace** using my **user name** and **repo name** labels with `'runs-on'`:

```yml
name: Runner on Codespace test

on:
  workflow_dispatch:

jobs:
  testRunner:
    runs-on: [self-hosted, Pwd9000, GitHub-Codespaces-Lab]
    steps:
      - uses: actions/checkout@v3.6.0
      - name: Display Terraform Version
        run: terraform --version
      - name: Display Azure-CLI Version
        run: az --version
```

## 24/01/2023 - Now available as a public Codespace

This devcontainer is now publicly available as a template for anyone to use at [Dev Container Templates](https://containers.dev/templates) and integrated with publicly available Codespace images.

Check out the [repo and documentation](https://bit.ly/3iPYXoL). Or the video tutorial on this [new blog post](https://dev.to/pwd9000/run-self-hosted-github-runners-on-github-codespaces-video-tutorial-1ggh) with detailed information on building the Codepace from the publicly available template directly in VSCode.

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my published [GitHub](https://github.com/Pwd9000-ML/GitHub-Codespaces-Lab) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [X/Twitter](https://x.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
