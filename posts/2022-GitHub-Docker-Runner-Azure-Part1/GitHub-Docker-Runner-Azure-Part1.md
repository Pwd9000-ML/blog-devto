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

To start of, before building and running our docker images we need to set up a few things. For my environment I will be using a **Windows11** virtual machine. You can also use Windows Server 2019/2022 or any Windows based OS that your prefer to run your docker environment on. Things that we will need on our VM are:  

- 
- 
- 
- 


I hope you have enjoyed this post and have learned something new. You can find the code samples used in this blog post on my [Github](https://github.com/Pwd9000-ML/docker-github-runner-windows) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
