---
title: Create a Docker based Windows Self Hosted GitHub runner container
published: false
description: Create a Windows based Github Self Hosted runner container image and run using docker and docker-compose
tags: 'github, azure, docker, containers'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part1/assets/main.png'
canonical_url: null
id: 1107070
series: Self Hosted Docker GitHub Runners on Azure
---

### Overview

All the code used in this tutorial can be found on my GitHub project: [docker-github-runner-windows](https://github.com/Pwd9000-ML/docker-github-runner-windows).

Welcome to Part 1 of my series: **Self Hosted Docker GitHub Runners on Azure**.

In part one of this series, we will focus and look at how we can create a **windows container** image using docker that will essentially be a packaged up image we can use to deploy and run self hosted **GitHub runners** as containers. We will focus more on the docker image itself and how we can build our image and run our image on a local server or VM running **docker for windows** and also scaling out multiple instances of our image using **docker-compose**.

Part two will focus on building a **Linux based Ubuntu image** and in parts three and four, we will look at how we can utilize Azure to store and run our containers in the cloud using technologies such as **Azure Container Registry (ACR)** to store images, and **Azure Container Instances (ACI)** and **Azure Container Apps (ACA)** to run and scale our self hosted GitHub runners, instead of using a VM based approach with docker running inside of a VM.

### Setup environment

Before building and running docker images we need to set a few things up first. For my environment I will be using a **Windows 11** virtual machine running **WSL2**. Here is more information on running docker on [Windows Server](https://docs.microsoft.com/en-us/virtualization/windowscontainers/quick-start/set-up-environment?tabs=Windows-Server#install-docker). Things that we will need on our VM are:

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

- Once **Docker Desktop For Windows** is installed you need to switch to Windows containers. Use the Docker item in the Windows system tray:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part1/assets/winc.png)

### Prepare PowerShell Scripts used in image creation

Now that we have **Docker-Desktop** as well as **Docker-Compose** installed and set to use **Windows Containers** we can start to build out our self hosted GitHub runner docker image.

Open VSCode, you can clone the repo found on my GitHub project [docker-github-runner-windows](https://github.com/Pwd9000-ML/docker-github-runner-windows) which contains all the files or simply follow along with the following steps. We will prepare a few PowerShell scripts that will be needed as part of our docker image creation.

Create a `root` folder called `docker-github-runner-windows` and then another sub folder called `scripts`. Inside of the [scripts](https://github.com/Pwd9000-ML/docker-github-runner-windows/tree/master/scripts) folder you can create the following three PowerShell scripts:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part1/assets/scripts.png)

### [Cleanup-Runners.ps1](https://github.com/Pwd9000-ML/docker-github-runner-windows/blob/master/scripts/Cleanup-Runners.ps1)

Because we will run and scale self hosted runners using docker/docker-compose dynamically using our image, this script will be used to remove and unregister any old/offline GitHub runner registrations against our GitHub repository when we scale containers up and down based on our needs.

```powershell
#This script invokes GitHub-CLI (Pre-installed on container image)
Param (
    [Parameter(Mandatory = $false)]
    [string]$owner = $env:GH_OWNER,
    [Parameter(Mandatory = $false)]
    [string]$repo = $env:GH_REPOSITORY,
    [Parameter(Mandatory = $false)]
    [string]$pat = $env:GH_TOKEN
)

#Use --with-token to pass in a PAT token on standard input. The minimum required scopes for the token are: "repo", "read:org".
#Alternatively, gh will use the authentication token found in environment variables. See gh help environment for more info.
#To use gh in GitHub Actions, add GH_TOKEN: $ to "env". on Docker run: Docker run -e GH_TOKEN='myPatToken'
gh auth login --with-token $pat

#Cleanup#
#Look for any old/stale dockerNode- registrations to clean up
#Windows containers cannot gracefully remove registration via powershell due to issue: https://github.com/moby/moby/issues/25982#
#For this reason we can use this scrip to cleanup old offline instances/registrations
$runnerBaseName = "dockerNode-"
$runnerListJson = gh api -H "Accept: application/vnd.github.v3+json" "/repos/$owner/$repo/actions/runners"
$runnerList = (ConvertFrom-Json -InputObject $runnerListJson).runners

Foreach ($runner in $runnerList) {
    try {
        If (($runner.name -like "$runnerBaseName*") -and ($runner.status -eq "offline")) {
            write-host "Unregsitering old stale runner: $($runner.name)"
            gh api --method DELETE -H "Accept: application/vnd.github.v3+json" "/repos/$owner/$repo/actions/runners/$($runner.id)"
        }
    }
    catch {
        Write-Error $_.Exception.Message
    }
}

#Remove PAT token after cleanup
$pat=$null
$env:GH_TOKEN=$null
```

### [Install-Choco.ps1](https://github.com/Pwd9000-ML/docker-github-runner-windows/blob/master/scripts/Install-Choco.ps1)

This script will be used to install Chocolatey (Windows package manager) into our docker image when we build the image.

```powershell
$securityProtocolSettingsOriginal = [System.Net.ServicePointManager]::SecurityProtocol
try {
    # Set TLS 1.2 (3072), then TLS 1.1 (768), then TLS 1.0 (192), finally SSL 3.0 (48)
    # Use integers because the enumeration values for TLS 1.2 and TLS 1.1 won’t
    # exist in .NET 4.0, even though they are addressable if .NET 4.5+ is
    # installed (.NET 4.5 is an in-place upgrade).
    [System.Net.ServicePointManager]::SecurityProtocol = 3072 -bor 768 -bor 192 -bor 48
}
catch {
    Write-Warning "Unable to set PowerShell to use TLS 1.2 and TLS 1.1 check .NET Framework installed. If you see underlying connection closed or trust errors, try the following: (1) upgrade to .NET Framework 4.5 (2) specify internal Chocolatey package location (set $env:chocolateyDownloadUrl prior to install or host the package internally), (3) use the Download + PowerShell method of install. See https://chocolatey.org/install for all install options."
}
Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
[System.Net.ServicePointManager]::SecurityProtocol = $securityProtocolSettingsOriginal
```

### [start.ps1](https://github.com/Pwd9000-ML/docker-github-runner-windows/blob/master/scripts/start.ps1)

This script will be used as our `ENTRYPOINT` script and will be used to bootstrap our docker container when we start/run a container from the image we will be creating. The main purpose of this script is to register a new self hosted GitHub runner instance on the repo we pass into the docker environment each time a new container is spun up from the image.

```powershell
#This script invokes GitHub-CLI (Already installed on container image)
#To use this entrypoint script run: Docker run -e GH_TOKEN='myPatToken' -e GH_OWNER='orgName' -e GH_REPOSITORY='repoName' -d imageName
Param (
    [Parameter(Mandatory = $false)]
    [string]$owner = $env:GH_OWNER,
    [Parameter(Mandatory = $false)]
    [string]$repo = $env:GH_REPOSITORY,
    [Parameter(Mandatory = $false)]
    [string]$pat = $env:GH_TOKEN
)

#Use --with-token to pass in a PAT token on standard input. The minimum required scopes for the token are: "repo", "read:org".
#Alternatively, gh will use the authentication token found in environment variables. See gh help environment for more info.
#To use gh in GitHub Actions, add GH_TOKEN: $ to "env". on Docker run: Docker run -e GH_TOKEN='myPatToken'
gh auth login

#Get Runner registration Token
$jsonObj = gh api --method POST -H "Accept: application/vnd.github.v3+json" "/repos/$owner/$repo/actions/runners/registration-token"
$regToken = (ConvertFrom-Json -InputObject $jsonObj).token
$runnerBaseName = "dockerNode-"
$runnerName = $runnerBaseName + (((New-Guid).Guid).replace("-", "")).substring(0, 5)

try {
    #Register new runner instance
    write-host "Registering GitHub Self Hosted Runner on: $owner/$repo"
    ./config.cmd --unattended --url "https://github.com/$owner/$repo" --token $regToken --name $runnerName

    #Remove PAT token after registering new instance
    $pat=$null
    $env:GH_TOKEN=$null

    #Start runner listener for jobs
    ./run.cmd
}
catch {
    Write-Error $_.Exception.Message
}
finally {
    # Trap signal with finally - cleanup (When docker container is stopped remove runner registration from GitHub)
    # Does not currently work due to issue: https://github.com/moby/moby/issues/25982#
    # Perform manual cleanup of stale runners using Cleanup-Runners.ps1
    ./config.cmd remove --unattended --token $regToken
}
```

### Building the Docker Image (Windows)

Now with our scripts ready, we can get to the fun part... Building the **windows docker image**. Navigate back to the root folder and create a file called: `dockerfile`:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part1/assets/folder.png)

### [dockerfile](https://github.com/Pwd9000-ML/docker-github-runner-windows/blob/master/dockerfile)

This dockerfile contains the instructions to build our container image.

```dockerfile
##### BASE IMAGE INFO ######
#Using servercore insider edition for compacted size.
#For compatibility on "your" host running docker you may need to use a specific tag.
#E.g. the host OS version must match the container OS version.
#If you want to run a container based on a newer Windows build, make sure you have an equivalent host build.
#Otherwise, you can use Hyper-V isolation to run older containers on new host builds.
#The default entrypoint is for this image is Cmd.exe. To run the image:
#docker run mcr.microsoft.com/windows/servercore/insider:10.0.{build}.{revision}
#tag reference: https://mcr.microsoft.com/en-us/product/windows/servercore/insider/tags

#Win10
#FROM mcr.microsoft.com/windows/servercore/insider:10.0.19035.1

#Win11
FROM mcr.microsoft.com/windows/servercore/insider:10.0.20348.1

#input GitHub runner version argument
ARG RUNNER_VERSION

LABEL Author="Marcel L"
LABEL Email="pwd9000@hotmail.co.uk"
LABEL GitHub="https://github.com/Pwd9000-ML"
LABEL BaseImage="servercore/insider:10.0.19035.1"
LABEL RunnerVersion=${RUNNER_VERSION}

SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop';"]

#Set working directory
WORKDIR /actions-runner

#Install chocolatey
ADD scripts/Install-Choco.ps1 .
RUN .\Install-Choco.ps1 -Wait; \
    Remove-Item .\Install-Choco.ps1 -Force

#Install Git, GitHub-CLI, Azure-CLI and PowerShell Core with Chocolatey (add more tooling if needed at build)
RUN choco install -y \
    git \
    gh \
    powershell-core \
    azure-cli

#Download GitHub Runner based on RUNNER_VERSION argument (Can use: Docker build --build-arg RUNNER_VERSION=x.y.z)
RUN Invoke-WebRequest -Uri "https://github.com/actions/runner/releases/download/v$env:RUNNER_VERSION/actions-runner-win-x64-$env:RUNNER_VERSION.zip" -OutFile "actions-runner.zip"; \
    Expand-Archive -Path ".\\actions-runner.zip" -DestinationPath '.'; \
    Remove-Item ".\\actions-runner.zip" -Force

#Add GitHub runner configuration startup script
ADD scripts/start.ps1 .
ADD scripts/Cleanup-Runners.ps1 .
ENTRYPOINT ["pwsh.exe", ".\\start.ps1"]
```

Let's break down and see what this docker build file will actually do step by step:

```dockerfile
#Win11
FROM mcr.microsoft.com/windows/servercore/insider:10.0.20348.1
```

The `FROM` instruction will tell our docker build to fetch and use a windows OS base image. Because windows base images can be fairly large we are using servercore **insider** edition, because the size is very compact and optimized.

**NOTE:** For compatibility on "your" host/VM running docker you may need to use a specific tag. The host OS version must match the container OS version. If you want to run a container based on a newer Windows build, make sure you have an equivalent host build. Otherwise, you can use Hyper-V isolation to run older containers on new host builds. `mcr.microsoft.com/windows/servercore/insider:10.0.{build}.{revision}`  
Servercore tag reference: https://mcr.microsoft.com/en-us/product/windows/servercore/insider/tags

```dockerfile
#input GitHub runner version argument
ARG RUNNER_VERSION

LABEL Author="Marcel L"
LABEL Email="pwd9000@hotmail.co.uk"
LABEL GitHub="https://github.com/Pwd9000-ML"
LABEL BaseImage="servercore/insider:10.0.19035.1"
LABEL RunnerVersion=${RUNNER_VERSION}
```

The next section we define an input argument using `ARG`. This is so that we can instruct the docker build command to use a very specific version of the **GitHub runner** agent when building the image. Because we are using a **windows container**, `ARG` will create a system variable **$env:RUNNER_VERSION** which will be accessible to PowerShell.

In addition we can also label our image with some **metadata** using `LABEL` to add more information about the image. You can change these values as necessary.

```dockerfile
SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop';"]

#Set working directory
WORKDIR /actions-runner
```

We then configure **PowerShell** as our default shell for running scripts or commands and also set a working directory named **actions-runner**

```dockerfile
#Install chocolatey
ADD scripts/Install-Choco.ps1 .
RUN .\Install-Choco.ps1 -Wait; \
    Remove-Item .\Install-Choco.ps1 -Force

#Install Git, GitHub-CLI, Azure-CLI and PowerShell Core with Chocolatey (add more tooling if needed at build)
RUN choco install -y \
    git \
    gh \
    powershell-core \
    azure-cli
```

The `ADD` instruction will copy our **Install-Choco.ps1** script into the working directory called **actions-runner**, then `RUN` the script which will install **Chocolatey** into the image, and then cleanup/remove the script.

The second `RUN` will then use **Chocolatey** to install **Git**, **GitHub-CLI**, **Azure-CLI** and **PowerShell Core** into the image. You can add any additional tooling you which to add to the image at build time here.

**NOTE:** Try not to install too many packages at build time to keep the image as lean, compact and re-usable as possible. You can always use a **GitHub Action** in a workflow when running the container and use **Chocolatey** which is baked into the image/container to install more software. I will be showing how we can add more software e.g. **Terraform** later on when we run our container, using a GitHub Action.

```dockerfile
#Download GitHub Runner based on RUNNER_VERSION argument (Can use: Docker build --build-arg RUNNER_VERSION=x.y.z)
RUN Invoke-WebRequest -Uri "https://github.com/actions/runner/releases/download/v$env:RUNNER_VERSION/actions-runner-win-x64-$env:RUNNER_VERSION.zip" -OutFile "actions-runner.zip"; \
    Expand-Archive -Path ".\\actions-runner.zip" -DestinationPath '.'; \
    Remove-Item ".\\actions-runner.zip" -Force
```

The next `RUN` instruction will run a series of PowerShell commands to download and extract a specific version of the GitHub runner binaries based on the `ARG` value passed into the container build process, that sets the environment variable: **$env:RUNNER_VERSION** as described earlier.

```dockerfile
#Add GitHub runner configuration startup script
ADD scripts/start.ps1 .
ADD scripts/Cleanup-Runners.ps1 .
ENTRYPOINT ["pwsh.exe", ".\\start.ps1"]
```

The last section will copy our **Cleanup-Runners.ps1** as well as an `ENTRYPOINT` script named **start.ps1** into the working directory **actions-runner**. This entrypoint script is set to run each time a new container is run/created. It acts as a bootstrapper that will look for specific environment variables we can pass into the **Docker Run** command later on such as, **$env:GH_OWNER**, **env:GH_REPOSITORY** and **$env:GH_TOKEN** in order to register our self hosted runner against a specific **repository** in our **GitHub organisation**.

!?!

I hope you have enjoyed this post and have learned something new. You can find the code samples used in this blog post on my [Github](https://github.com/Pwd9000-ML/docker-github-runner-windows) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
