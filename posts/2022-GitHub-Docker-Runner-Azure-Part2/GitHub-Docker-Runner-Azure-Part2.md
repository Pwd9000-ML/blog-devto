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
ENV DEBIAN_FRONTEND=noninteractive

LABEL Author="Marcel L"
LABEL Email="pwd9000@hotmail.co.uk"
LABEL GitHub="https://github.com/Pwd9000-ML"
LABEL BaseImage="ubuntu:20.04"
LABEL RunnerVersion=${RUNNER_VERSION}

# update the base packages + add a non-sudo user
RUN apt-get update -y && apt-get upgrade -y && useradd -m docker

# install the packages and dependencies along with jq so we can parse JSON (add additional packages as necessary)
RUN apt-get install -y --no-install-recommends \
    curl nodejs wget unzip vim git azure-cli jq build-essential libssl-dev libffi-dev python3 python3-venv python3-dev python3-pip

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

Let's take a closer look and see what this docker build file will actually do, step by step:

```dockerfile
# base image
FROM ubuntu:20.04
```

The `'FROM'` instruction will tell our docker build to fetch and use an Ubuntu 20.04 OS **base image**. We will add additional configuration to this base image next.

```dockerfile
#input GitHub runner version argument
ARG RUNNER_VERSION
ENV DEBIAN_FRONTEND=noninteractive

LABEL Author="Marcel L"
LABEL Email="pwd9000@hotmail.co.uk"
LABEL GitHub="https://github.com/Pwd9000-ML"
LABEL BaseImage="ubuntu:20.04"
LABEL RunnerVersion=${RUNNER_VERSION}
```

We define an input argument using `'ARG'`. This is so that we can instruct the docker build command to load a specific version of the **GitHub runner** agent into the image when building the image. Because we are using a **linux container**, `'ARG'` will create a system variable **$RUNNER_VERSION** which will be accessible to Bash inside the container.

We also set an **Enviornment Variable** called **DEBIAN_FRONTEND** to **noninteractive** with `'ENV'`, this is so that we can run commands later on in unattended mode.

In addition we can also label our image with some **metadata** using `'LABEL'` to add more information about the image. You can change these values as necessary.

**NOTE:** `'LABEL RunnerVersion=${RUNNER_VERSION}'`, this label is dynamically updated from the build argument we will be passing into the docker build command later.

```dockerfile
# update the base packages + add a non-sudo user
RUN apt-get update -y && apt-get upgrade -y && useradd -m docker

# install the packages and dependencies along with jq so we can parse JSON (add additional packages as necessary)
RUN apt-get install -y --no-install-recommends \
    curl nodejs wget unzip vim git azure-cli jq build-essential libssl-dev libffi-dev python3 python3-venv python3-dev python3-pip
```

The first `'RUN'` instruction will update the base packages on the Ubuntu 20.04 image and add a non-sudo user called **docker**.

The second `'RUN'` will install **git**, **Azure-CLI**, **python** and the packages and dependencies along with **jq** so we can parse JSON.

**NOTE:** Try not to install too many packages at build time to keep the image as lean, compact and re-usable as possible. You can always use a **GitHub Action** later in a workflow when running the container and use actions to install more tooling.

I will also be showing how we can add more software and tooling e.g. **Terraform** later on when we run our container, using a GitHub Action.

```dockerfile
# cd into the user directory, download and unzip the github actions runner
RUN cd /home/docker && mkdir actions-runner && cd actions-runner \
    && curl -O -L https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz \
    && tar xzf ./actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz

# install some additional dependencies
RUN chown -R docker ~docker && /home/docker/actions-runner/bin/installdependencies.sh
```

The next `'RUN'` instruction will create a new folder called **actions-runner** and then download and extract a specific version of the GitHub runner binaries based on the build argument `'ARG'` value passed into the container build process that sets the environment variable: **$RUNNER_VERSION** as described earlier. A few more additional dependencies are also installed from the extracted GitHub runner.

```dockerfile
# add over the start.sh script
ADD scripts/start.sh start.sh

# make the script executable
RUN chmod +x start.sh

# set the user to "docker" so all subsequent commands are run as the docker user
USER docker

# set the entrypoint to the start.sh script
ENTRYPOINT ["./start.sh"]
```

The last section will `'ADD'` the `'ENTRYPOINT'` script named **start.sh** into the directory **actions-runner**. The entrypoint script will run each time a new container is created. It acts as a bootstrapper that will, based on specific environment variables we pass into the **Docker Run** command, such as, **$GH_OWNER**, **$GH_REPOSITORY** and **$GH_TOKEN** to register the containers self hosted runner agent against a specific **repository** in the **GitHub organisation** we specify.

Now that we have our scripts as well as our dockerfile ready we can build our image.

**NOTE:** We can build and run the linux container images using **docker-desktop** or **docker-compose**, I will show both methods next.

### Building the Docker Image - Docker Desktop (Linux)

In VSCode terminal or a PowerShell session, navigate to the root folder containing the docker file and run the following command. Remember we need to pass in a build argument to tell docker what version of the GitHub runner agent to use in the image creation. [GitHub Runner Releases](https://github.com/actions/runner/releases)

```powershell
#Build container: docker build [OPTIONS] PATH
docker build --build-arg RUNNER_VERSION=2.292.0 --tag docker-github-runner-lin .
```

The build process can take a little while to complete:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part2/assets/docker-build.png)

Once the process is complete, you will see the new image in **Docker Desktop for Windows** under **images**:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part2/assets/docker-image.png)

### Run the Docker Image - Docker Desktop (Linux)

To run and provision a new self hosted GitHub runner linux container from the image we just created, run the following command. We have to pass in some **environment variables** using the `'-e'` option to specify the **PAT (Personal Access Token)**, **GitHub Organisation** and **Repository** to register the runner against.

```powershell
#Run container from image:
docker run -e GH_TOKEN='myPatToken' -e GH_OWNER='orgName' -e GH_REPOSITORY='repoName' -d image-name
```

See [creating a personal access token](https://docs.github.com/en/enterprise-server@3.4/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) on how to create a GitHub PAT token. PAT tokens are only displayed once and are sensitive, so ensure they are kept safe.

The minimum permission scopes required on the PAT token to register a self hosted runner are: `"repo"`, `"read:org"`:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part2/assets/PAT.png)

**Tip:** I recommend only using short lived PAT tokens and generating new tokens whenever new agent runner registrations are required.

After running this command, under the GitHub repository settings, you will see a new self hosted GitHub runner. (This is our docker container):

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part2/assets/nodes.png)

You will also be able to see the running container under **Docker Desktop for Windows** under **Containers**:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part2/assets/container-run.png)

Lets test our new docker container self hosted GitHub runner by creating a **GitHub workflow** to run a few **GitHub Actions** by installing **Terraform** on the running container.

You can also use this [test workflow](https://github.com/Pwd9000-ML/docker-github-runner-windows/blob/master/.github/workflows/testRunner.yml) from my GitHub project: [docker-github-runner-linux](https://github.com/Pwd9000-ML/docker-github-runner-linux).

Create a new workflow under the GitHub repository where you deployed the self hosted runner where it is running:

```yml
name: Local runner test

on:
  workflow_dispatch:

jobs:
  testRunner:
    runs-on: [self-hosted]
    steps:
      - uses: actions/checkout@v2
      - name: Install Terraform
        uses: hashicorp/setup-terraform@v2
      - name: Display Terraform Version
        run: terraform --version
      - name: Display Azure-CLI Version
        run: az --version
```

Notice that the workflow `'runs-on: [self-hosted]'`. We can now use the following step to install **Terraform**:

```yml
steps:
- name: Install Terraform
    uses: hashicorp/setup-terraform@v2
- name: Display Terraform Version
    run: terraform --version
```

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part2/assets/terra.png)

To spin up additional docker runners (containers), we just simply re-run the docker command we ran earlier (Each run will create an additional runner instance/container):

```powershell
#Run container from image:
docker run -e GH_TOKEN='myPatToken' -e GH_OWNER='orgName' -e GH_REPOSITORY='repoName' -d image-name
```

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part2/assets/runners.png)

Next we will look at stopping/destroying our running docker instances and cleaning up the registrations for all the self hosted runners registered against our GitHub repository.

To stop and remove all running containers simply run:

```powershell
docker stop $(docker ps -aq) && docker rm $(docker ps -aq)
```

You will notice that all the running containers under **Docker Desktop for Windows** are no longer there, as well as the docker node registrations against our GitHub repository has also been cleaned up and removed:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part2/assets/runners-decom.png)

The reason our GitHub runner registrations are also removed is because of the cleanup code inside of our `'ENTRYPOINT'` script **start.sh**, that will automatically trigger a cleanup of the runner registration when the docker container is stopped and destroyed:

```bash
cleanup() {
    echo "Removing runner..."
    ./config.sh remove --unattended --token ${REG_TOKEN}
}

trap 'cleanup; exit 130' INT
trap 'cleanup; exit 143' TERM
```

Next we will look how we can build the image and also run our image at scale using **docker-compose**.

### Building the Docker Image - Docker Compose (Linux)

As we saw earlier, it is pretty easy to build our image using docker commands, but we can also use **docker-compose** with a configuration file to make things a bit easier. So following on, navigate to the root folder again that contains the **dockerfile** we created earlier, and create a new `'YAML'` file called **docker-compose.yml**:

```yml
---
version: '3.8'

services:
  runner:
    image: pwd9000-github-runner-lin:latest
    build:
      context: .
      args:
        RUNNER_VERSION: '2.292.0'
    environment:
      GH_TOKEN: ${GH_TOKEN}
      GH_OWNER: ${GH_OWNER}
      GH_REPOSITORY: ${GH_REPOSITORY}
```

In the docker compose configuration file we can set out the parameters for our docker image by specifying things like the image name, GitHub runner version, as well as our environment variables.

Note that we have to set these environment variables on our **host**, windows 11 machine in order for **docker compose** to be able to interpret the values specified on the `'YAML'` file inside of the `'${}'` symbols. This can easily be done by running the following PowerShell commands on the windows 11 host:

```powershell
#set system environment with $env: (or use .env file to pass GH_TOKEN, GH_OWNER, GH_REPOSITORY)
$env:GH_OWNER='Org/Owner'
$env:GH_REPOSITORY='Repository'
$env:GH_TOKEN='myPatToken'
```

**NOTE:** You can also use an environment file instead to pass environment variables onto the docker compose build process using a [docker-compose.yml](https://github.com/Pwd9000-ML/docker-github-runner-linux/blob/master/Docker-Compose-Examples/docker-compose-ExampleEnvFile.yml) file like this instead:

```yml
---
version: '3.8'

services:
  runner:
    image: pwd9000-github-runner-lin:latest
    build:
      context: .
      args:
        RUNNER_VERSION: '2.292.0'
    env_file:
      - ./variables.env
```

This method however requires us to create another file in the root of our working folder called **./variables.env** and populating this file with our environment variables like so:

```txt
GH_OWNER=orgName
GH_REPOSITORY=repoName
GH_TOKEN=myPatToken
```

**IMPORTANT:** Don't use this method, and don't commit this file to source control if you are using **sensitive values** and storing your code in a remote source control repository. Add this environment file to your `'.gitignore'` file if needed, so that it is not pushed into source control.

Which ever method you decide to use, you can kick off the build process after creating this **docker-compose.yml** file by running the following PowerShell command:

```powershell
docker-compose build
```

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part2/assets/compose-build.png)

Once the process is complete, you will see the new image in **Docker Desktop for Windows** under **images**:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part2/assets/compose-image.png)

### Run and scale the Docker Image - Docker Compose (Windows)

What's really nice about using **docker-compose** is that we can easily scale the amount of runners we want to use simply by running the following command:

```powershell
docker-compose up --scale runner=3 -d
```

Because all of our configuration and details are kept in **environment variables** and the **docker-compose** `'YAML'` file, we don't really have to run long docker commands as we did earlier, and we simply scale the amount of runners we want by specifying the `'--scale'` parameter.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part2/assets/gh-runners.png)

**NOTE:** The `'--scale runner=3 -d'` parameter is based on the docker compose file, `'services:'` setting, which in our case is called `'runner'`:

```yml
services:
  runner:
```

To scale down to one runner, we can simply rerun the command as follow:

```powershell
docker-compose up --scale runner=1 -d
```

To stop and remove all running containers simply run:

```powershell
docker-compose stop
docker rm $(docker ps -aq)
```

As described earlier, you will notice that all the running containers under **Docker Desktop for Windows** are no longer there, as well as the registrations against our GitHub repository have been cleaned up:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Docker-Runner-Azure-Part2/assets/runners-decom.png)

In this part of the blog series we have covered how you can build and run self hosted **Github runners** as **linux containers** using **docker-desktop** and **docker-compose**. In part three of this blog series we will take a look at hosting and running our **GitHub runner** containers in **Azure**.

I hope you have enjoyed this post and have learned something new. You can find the code samples used in this blog post on my [Github](https://github.com/Pwd9000-ML/docker-github-runner-linux) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
