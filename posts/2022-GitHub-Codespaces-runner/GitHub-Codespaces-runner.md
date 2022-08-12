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

In todays post I will share with you an interesting concept, where you can use your **GitHub Codespace** not only as a "development environment" for working with your code, but also utilising the **Codespace** compute power, by running a **Self Hosted GitHub runner** at the same time.  

We will be using a custom **docker image** that will automatically provision a **self hosted runner agent** and register it at the same time as provisioning the **Codespace** as part of the development environment.  

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-GitHub-Codespaces-runner/assets/diag01.png)

We will also look at the **Codespace/Runner** lifecycle. By default any **Active** codespaces that becomes **idle** will go into a hibernation mode after **30 minutes** to save on compute costs, so we will look at how this timeout can be configured and also ensure that the **self hosted runner** will be removed cleanly and unregistered once the codespace is no longer 'active' or 'in-use'.  

We will actually be using the same **docker** configuration from a post on another blog series of mine called, **['Self Hosted GitHub Runner containers on Azure'](https://dev.to/pwd9000/series/18434)**. So do take a look at that series as well to get a better understanding on how to build and host your self hosted GitHub runners.  

## Conclusion

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my published [Github](https://github.com/Pwd9000-ML/GitHub-Codespaces-Lab) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
