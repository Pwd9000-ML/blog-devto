---
title: Terraform IaC Scanning with Trivy
published: false
description: DevOps - Terraform - IaC Scanning with Trivy
tags: 'tutorial, security, productivity, devops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/DevOps-Terraform-Trivy/assets/main-trivy.png'
canonical_url: null
id: 864896
---

## Azure DevOps pipeline/YAML resources

Azure DevOps pipelines provides very useful [resources](https://docs.microsoft.com/en-us/azure/devops/pipelines/process/resources?view=azure-devops&tabs=schema) we can define in our pipeline in one place and be consumed anywhere in our pipeline.

A resource is anything used by a pipeline that lives outside the pipeline. Pipeline resources include:

- CI/CD pipelines that produce artifacts (Azure Pipelines, Jenkins, etc.)
- code repositories (Azure Repos Git repos, GitHub, GitHub Enterprise, Bitbucket Cloud)
- container image registries (Azure Container Registry, Docker Hub, etc.)
- package feeds (GitHub packages)

Today we will take a look at the [Pipelines Resource](https://docs.microsoft.com/en-us/azure/devops/pipelines/process/resources?view=azure-devops&tabs=schema#resources-pipelines), in particular we will look at how we can use this resource in a pipeline to consume an artifact that was produced in another pipeline in a completely different project. Our pipeline will also even be triggered automatically by the source pipeline after the artifact has been created and published.

## Consume remote pipeline artifacts

### _Author_

{% user pwd9000 %}

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) \ :penguin: [Twitter](https://twitter.com/pwd9000) \ :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)
