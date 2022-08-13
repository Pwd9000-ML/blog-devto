---
title: Hosting your self hosted runners on GitHub Codespaces
published: false
description: How to use your GitHub Codespace as a self hosted runner
tags: 'github, codespaces, azuredevops, development'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Codespaces-runner/assets/main01.png'
canonical_url: null
id: 1165803
series: GitHub Codespaces Pro Tips
---

## Overview

Welcome to another part of my series **['GitHub Codespaces Pro Tips'](https://dev.to/pwd9000/series/19195)**. In the last part we spoke about integrating **GitHub** with **Azure DevOps** and how you can use some of the great features of GitHub, like **Codespaces** along with Azure DevOps.

In todays post I will share with you how you can use your **GitHub Codespace** not only as a "development environment" for working with your code, but also utilising the **Codespace** compute power, by running a **Self Hosted GitHub runner** inside of the Codespace at the same time.

We will be using a custom **docker image** that will automatically provision a **self hosted runner agent** and register it at the same time as provisioning the **Codespace** as part of the development environment.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Codespaces-runner/assets/diag01.png)

We will also look at the **Codespace/Runner** lifecycle. By default any **Active** codespaces that becomes **idle** will go into a hibernation mode after **30 minutes** to save on compute costs, so we will look at how this timeout can be configured and also ensure that the **self hosted runner** will be removed cleanly and unregistered once the codespace is no longer 'active' or 'in-use', so that the self hosted runner is only available when the Codespace is.

We will actually be using a very similar approach and docker image configuration from my previous blog post, ['Create a Docker based Self Hosted GitHub runner Linux container'](https://dev.to/pwd9000/create-a-docker-based-self-hosted-github-runner-linux-container-48dh). So do check out that post for detailed info on how the container works.  

## Getting started

All of the code samples and examples are also available on my [GitHub Codespaces Demo Repository](https://github.com/Pwd9000-ML/GitHub-Codespaces-Lab/tree/master/.devcontainer/codespaceRunner).

Since **Codespaces/Dev containers** are based on **docker images**, we will create a **custom linux docker image** that will start and bootstrap a runner agent as the codespace starts up.

In your **GitHub repository** create a sub folder under `'.devcontainer'`, in my case I have called my codespace configuration folder `'codepsaceRunner'`.

Next create the following [Dockerfile](https://github.com/Pwd9000-ML/GitHub-Codespaces-Lab/blob/master/.devcontainer/codespaceRunner/dockerfile). (Amend the file if needed for your own `tooling` and `LABELS`):

```dockerfile
ARG RUNNER_VERSION
ARG VARIANT

# base image
FROM mcr.microsoft.com/vscode/devcontainers/base:0-${VARIANT}

#input GitHub runner version argument
ENV DEBIAN_FRONTEND=noninteractive

LABEL Author="Marcel L"
LABEL Email="pwd9000@hotmail.co.uk"
LABEL GitHub="https://github.com/Pwd9000-ML"
LABEL BaseImage=${VARIANT}
LABEL RunnerVersion=${RUNNER_VERSION}

# update the base packages + add a non-sudo user
RUN apt-get update -y && apt-get upgrade -y && useradd -m docker

# [Optional] Uncomment this section to install additional OS packages.
RUN apt-get install -y --no-install-recommends \
    curl nodejs wget unzip vim git jq build-essential libssl-dev libffi-dev python3 python3-venv python3-dev python3-pip

# cd into the user directory, download and unzip the github actions runner
RUN cd /home/docker && mkdir actions-runner && cd actions-runner \
    && curl -O -L https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz \
    && tar xzf ./actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz

# install some additional dependencies
RUN chown -R docker ~docker && /home/docker/actions-runner/bin/installdependencies.sh

# add over the start.sh script
ADD scripts/start.sh start.sh

# make the script executable
RUN chmod +x start.sh

# set the user to "docker" so all subsequent commands are run as the docker user
USER docker

# set the entrypoint to the start.sh script
ENTRYPOINT ["./start.sh"]
```

Next, create a `'devcontainer.json'` file. 

```JSON
// For format details, see https://aka.ms/devcontainer.json. For config options, see the README at:
// https://github.com/microsoft/vscode-dev-containers/tree/v0.238.1/containers/ubuntu
{
	"name": "Ubuntu",
	"build": {
		"dockerfile": "Dockerfile",
		// Update 'VARIANT' to pick an Ubuntu version: jammy / ubuntu-22.04, focal / ubuntu-20.04, bionic /ubuntu-18.04
		// Use ubuntu-22.04 or ubuntu-18.04 on local arm64/Apple Silicon.
		"args": { 
			"VARIANT": "ubuntu-22.04",
			"RUNNER_VERSION": "2.295.0"
		 }
	},

	// Configure tool-specific properties.
	"customizations": {
		// Configure properties specific to VS Code.
		"vscode": {
			//"settings": {},
			//"devPort": {},
			// Specify which VS Code extensions to install (List of IDs)
			"extensions": [
				"ms-vscode.powershell",
				"ms-dotnettools.csharp",
				"hashicorp.terraform",
				"esbenp.prettier-vscode",
				"tfsec.tfsec"
				]
			}
		},

	// Use 'forwardPorts' to make a list of ports inside the container available locally.
	// "forwardPorts": [],

	// Use 'postCreateCommand' to run commands after the container is created.
	// "postCreateCommand": "uname -a",

	// Comment out to connect as root instead. More info: https://aka.ms/vscode-remote/containers/non-root.
	"remoteUser": "vscode",
	"features": {
		"kubectl-helm-minikube": "latest",
		"terraform": "latest",
		"git-lfs": "latest",
		"github-cli": "latest",
		"azure-cli": "latest",
		"powershell": "7.1"
	}
}
```

Create another folder called `'scripts'` and place the following script inside: ['start.sh'](https://github.com/Pwd9000-ML/GitHub-Codespaces-Lab/blob/master/.devcontainer/codespaceRunner/scripts/start.sh)

```bash
#!/bin/bash

GH_OWNER=$GH_OWNER
GH_REPOSITORY=$GH_REPOSITORY
GH_TOKEN=$GH_TOKEN

RUNNER_SUFFIX=$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 5 | head -n 1)
RUNNER_NAME="dockerNode-${RUNNER_SUFFIX}"

REG_TOKEN=$(curl -sX POST -H "Accept: application/vnd.github.v3+json" -H "Authorization: token ${GH_TOKEN}" https://api.github.com/repos/${GH_OWNER}/${GH_REPOSITORY}/actions/runners/registration-token | jq .token --raw-output)

cd /home/docker/actions-runner

./config.sh --unattended --url https://github.com/${GH_OWNER}/${GH_REPOSITORY} --token ${REG_TOKEN} --name ${RUNNER_NAME}

cleanup() {
    echo "Removing runner..."
    ./config.sh remove --unattended --token ${REG_TOKEN}
}

trap 'cleanup; exit 130' INT
trap 'cleanup; exit 143' TERM

./run.sh & wait $!
```

This script will start up with the **Codespace/Dev container** and bootstrap the **GitHub runner** when the Codespace starts. But you will notice that we need to provide the script some parameters:

```bash
GH_OWNER=$GH_OWNER
GH_REPOSITORY=$GH_REPOSITORY
GH_TOKEN=$GH_TOKEN
```

These parameters (environment variables) are used to configure and **register** the self hosted github runner against the correct repository.  

We need to provide the GitHub account/org name via the `'GH_OWNER'` environment variable, repository name via `GH_REPOSITORY` and a PAT token with `GH_TOKEN`.  

You can store sensitive information, like tokens, that you want to access in your codespaces via environment variables. Let's configure these parameters as encrypted [secrets for codespaces](https://docs.github.com/en/codespaces/managing-your-codespaces/managing-encrypted-secrets-for-your-codespaces):  

1. Navigate to the repository `'Settings'` page and select `'Secrets -> Codespaces'`, click on `'New repository secret'`.  ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Codespaces-runner/assets/sec01.png)  

2. Create each **Codespace secret** with the values for your environment.  ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Codespaces-runner/assets/sec02.png)  

## Note on Personal Access Token (PAT)

See [creating a personal access token](https://docs.github.com/en/enterprise-server@3.4/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) on how to create a GitHub PAT token. PAT tokens are only displayed once and are sensitive, so ensure they are kept safe.

The minimum permission scopes required on the PAT token to register a self hosted runner are: `"repo"`, `"read:org"`:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Codespaces-runner/assets/PAT.png)

**Tip:** I recommend only using short lived PAT tokens and generating new tokens whenever new agent runner registrations are required.

## Deploying the Codespace GitHub runner

As you can see in my example screenshot below, my repository does not have any runners configured.  

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Codespaces-runner/assets/run01.png)  

1. Navigate to your repository, click on the `'<> Code'` dropdown and select the `'Codespaces'` tab, select the `'Advanced'` option to **Configure and create codespace**.  ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Codespaces-runner/assets/run02.png)  



## Conclusion

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my published [Github](https://github.com/Pwd9000-ML/GitHub-Codespaces-Lab) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
