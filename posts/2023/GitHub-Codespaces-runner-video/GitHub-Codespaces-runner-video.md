---
title: Run self-hosted GitHub runners on GitHub Codespaces (Video Tutorial)
published: true
description: A quick video tutorial to get you started on running your self-hosted GitHub Action runners inside of your GitHub Codespaces.
tags: 'github, codespaces, githubactions, development'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Codespaces-runner-video/assets/main01.png'
canonical_url: null
id: 1354453
series: GitHub Codespaces Pro Tips
date: '2023-02-05T14:35:57Z'
---

## Overview

Based on a [previous blog post](https://dev.to/pwd9000/hosting-your-self-hosted-runners-on-github-codespaces-2elc), this devcontainer is now publicly available as a template for anyone to use at [Dev Container Templates](https://containers.dev/templates) and integrated with publicly available Codespace images.

Check out the [repo and documentation](https://bit.ly/3iPYXoL).

## Video Tutorial

{% youtube 4CPoHrLgO1E %}

## How to add this Codespace config

Select `Add Dev Container Configuration Files...`:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Codespaces-runner-video/assets/add01.png)

Select `Create a new configuration...`:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Codespaces-runner-video/assets/add02.png)

Select `Show All Definitions...`:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Codespaces-runner-video/assets/add03.png)

Select `GitHub Actions Runner`:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Codespaces-runner-video/assets/add04.png)

Select Debian version `bullseye`:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Codespaces-runner-video/assets/add05.png)

Choose version of GitHub Runner to install inside of Codespace:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Codespaces-runner-video/assets/add06.png)

Select any additional features to install (example, Terraform):

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Codespaces-runner-video/assets/add07.png)

Notice `.devcontainer` now holds Codespace configuration:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Codespaces-runner-video/assets/add08.png)

**NOTE:** The config is the same template as found on this public Dev Container [.src/github-actions-runner-devcontainer/.devcontainer](https://github.com/Pwd9000-ML/devcontainer-templates/tree/main/src/github-actions-runner-devcontainer/.devcontainer)

Commit and sync Dev Container Configuration:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Codespaces-runner-video/assets/add09.png)

Launch new codespace with options:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Codespaces-runner-video/assets/add10.png)

Select options, compute size and Create new Codespace:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Codespaces-runner-video/assets/add11.png)

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
