---
title: Create a Docker based Self Hosted GitHub runner Linux container
published: false
description: Create a Linux based Github Self Hosted runner container image and run using docker and docker-compose
tags: 'github, azure, docker, containers'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part2/assets/main.png'
canonical_url: null
id: 1107071
series: Self Hosted Docker GitHub Runners on Azure
---

### Overview

All the code used in this tutorial can be found on my GitHub project: [docker-github-runner-linux](https://github.com/Pwd9000-ML/docker-github-runner-linux).

Welcome to Part 2 of my series: **Self Hosted Docker GitHub Runners on Azure**.

In part one of this series, we looked at how we can create a **windows container** image using docker and then running our self hosted **GitHub runners** as containers. In this part we will focus on building a **Linux based Ubuntu image** instead.

In parts three and four, we will look at how we can utilize Azure to store and run our containers in the cloud using **Azure Container Registry (ACR)** to store images, and **Azure Container Instances (ACI)** and **Azure Container Apps (ACA)** to run and scale our self hosted GitHub runners, instead of using a VM based approach with docker running inside of a VM.

### Setup environment

Similarly as described in part one, before building and running docker images we need to set a few things up first. For my environment I will be using a **Windows 11** virtual machine running **WSL2**. Here is more information on running docker on [Windows Server](https://docs.microsoft.com/en-us/virtualization/windowscontainers/quick-start/set-up-environment?tabs=Windows-Server#install-docker). Things that we will need on our VM are:

- Install a code editor such as [VSCode](https://code.visualstudio.com/download)

- Install and enable WSL2 (For more information see: [how to enable WSL2](https://docs.microsoft.com/en-us/windows/wsl/install)):

_Open PowerShell as administrator and run:_

```powershell
wsl --install
```

_After WSL is installed, run:_

```powershell
Enable-WindowsOptionalFeature -Online -FeatureName $("Microsoft-Hyper-V", "Containers") -All
```

**NOTE:** You will need to reboot the system after adding the relevant features above.

- Download and Install [Docker Desktop For Windows](https://docs.docker.com/desktop/windows/install/) (This will automatically also install **Docker-Compose**)

- Once **Docker Desktop For Windows** is installed you need to switch to Linux containers. Use the Docker item in the Windows system tray:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part2/assets/linc.png)

**NOTE:** Linux containers is the default setting, so if you skipped part one of this series **Docker Desktop For Windows** will already be set to use **Linux Containers** by default.

### Prepare Bash Scripts used in image creation

Now that we have **Docker-Desktop** as well as **Docker-Compose** installed and set to use **Linux Containers** we can start to build out our self hosted GitHub runner docker image.

Open VSCode, you can clone the repo found on my GitHub project [docker-github-runner-linux](https://github.com/Pwd9000-ML/docker-github-runner-linux) which contains all the files or simply follow along with the following steps. We will prepare a few scripts that will be needed as part of our docker image creation.

Create a `root` folder called `docker-github-runner-linux` and then another sub folder called `scripts`. Inside of the [scripts](https://github.com/Pwd9000-ML/docker-github-runner-linux/tree/master/scripts) folder you can create the following script:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part2/assets/scripts.png)

### [start.sh](https://github.com/Pwd9000-ML/docker-github-runner-linux/blob/master/scripts/start.sh)

This script will be used as our `ENTRYPOINT` script and will be used to bootstrap our docker container when we start/run a container from the image we will be creating. The main purpose of this script is to register a new self hosted GitHub runner instance on the repo we pass into the docker environment each time a new container is spun up or scaled up from the image.

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

### Prepare dockerfile to build image (Linux)

Now with our scripts ready, we can get to the fun part... Building the **linux docker image**. Navigate back to the root folder and create a file called: `dockerfile`:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part2/assets/folder.png)

### [dockerfile](https://github.com/Pwd9000-ML/docker-github-runner-linux/blob/master/dockerfile)

This dockerfile contains the instructions to build our container image.

```dockerfile
# base image
FROM ubuntu:20.04

#input GitHub runner version argument
ARG RUNNER_VERSION

LABEL Author="Marcel L"
LABEL Email="pwd9000@hotmail.co.uk"
LABEL GitHub="https://github.com/Pwd9000-ML"
LABEL BaseImage="ubuntu:20.04"
LABEL RunnerVersion=${RUNNER_VERSION}

# update the base packages and add a non-sudo user
RUN apt-get update -y && apt-get upgrade -y && useradd -m docker

# install python and the packages the code depends on along with jq so we can parse JSON
# add additional packages as necessary
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    curl jq build-essential libssl-dev libffi-dev python3 python3-venv python3-dev python3-pip

# cd into the user directory, download and unzip the github actions runner
RUN cd /home/docker && mkdir actions-runner && cd actions-runner \
    && curl -O -L https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz \
    && tar xzf ./actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz

# install some additional dependencies
RUN chown -R docker ~docker && /home/docker/actions-runner/bin/installdependencies.sh

# copy over the start.sh script
COPY scripts/start.sh start.sh

# make the script executable
RUN chmod +x start.sh

# set the user to "docker" so all subsequent commands are run as the docker user
USER docker

# set the entrypoint to the start.sh script
ENTRYPOINT ["./start.sh"]
```

Let's take a closer look and see what this docker build file will actually do, step by step:

```dockerfile
# base image
FROM ubuntu:20.04
```

The `'FROM'` instruction will tell our docker build to fetch and use an Ubuntu 20.04 OS **base image**. We will add additional configuration to this base image next.

```dockerfile
# base image
#input GitHub runner version argument
ARG RUNNER_VERSION

LABEL Author="Marcel L"
LABEL Email="pwd9000@hotmail.co.uk"
LABEL GitHub="https://github.com/Pwd9000-ML"
LABEL BaseImage="ubuntu:20.04"
LABEL RunnerVersion=${RUNNER_VERSION}
```

We define an input argument using `'ARG'`. This is so that we can instruct the docker build command to load a specific version of the **GitHub runner** agent into the image when building the image. Because we are using a **linux container**, `'ARG'` will create a system variable **$RUNNER_VERSION** which will be accessible to Bash inside the container.

In addition we can also label our image with some **metadata** using `'LABEL'` to add more information about the image. You can change these values as necessary.

**NOTE:** `'LABEL RunnerVersion=${RUNNER_VERSION}'`, this label is dynamically updated from the build argument we will be passing into the docker build command later.

```dockerfile
# update the base packages and add a non-sudo user
RUN apt-get update -y && apt-get upgrade -y && useradd -m docker

# install python and the packages the code depends on along with jq so we can parse JSON
# add additional packages as necessary
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    curl git azure-cli jq build-essential libssl-dev libffi-dev python3 python3-venv python3-dev python3-pip
```

The first `'RUN'` instruction will update the base packages on the Ubuntu 20.04 image and add a non-sudo user called **docker**.

The second `'RUN'` will install **git**, **Azure-CLI**, **python** and the packages the code depends on along with **jq** so we can parse JSON.

**NOTE:** Try not to install too many packages at build time to keep the image as lean, compact and re-usable as possible. You can always use a **GitHub Action** later in a workflow when running the container and use **a shell script** action to install more tooling.

I will also be showing how we can add more software and tooling e.g. **Terraform** later on when we run our container, using a GitHub Action.
