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

**NOTE:** Linux container is the default setting, so if you skipped part one of this series **Docker Desktop For Windows** will already be set to **Linux Containers**

### Prepare Bash Scripts used in image creation

Now that we have **Docker-Desktop** as well as **Docker-Compose** installed and set to use **Linux Containers** we can start to build out our self hosted GitHub runner docker image.

Open VSCode, you can clone the repo found on my GitHub project [docker-github-runner-linux](https://github.com/Pwd9000-ML/docker-github-runner-linux) which contains all the files or simply follow along with the following steps. We will prepare a few Bash scripts that will be needed as part of our docker image creation.

Create a `root` folder called `docker-github-runner-linux` and then another sub folder called `scripts`. Inside of the [scripts](https://github.com/Pwd9000-ML/docker-github-runner-linux/tree/master/scripts) folder you can create the following Bash script:
