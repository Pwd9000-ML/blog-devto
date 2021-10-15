---
title: Consume artifacts from a remote DevOps project pipeline
published: true
description: DevOps - Pipelines - Consume remote artifact
tags: 'tutorial, azure, productivity, devops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/DevOps-Pipeline-from-Pipeline/assets/main-ado.png'
canonical_url: null
id: 783932
date: '2021-08-07T14:06:14Z'
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

In my DevOps organisation I have created two projects namely **ProjectA** and **ProjectB**. I also created two YAML pipelines for each corresponding project named **PipelineA** and **PipelineB**. **PipelineA** will be my triggering/source pipeline which will create an artifact called **ArtifactA**. **PipelineB** will be my pipeline which will contain the pipeline resource for **PipelineA** and will consume **ArtifactA**.

![main](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/DevOps-Pipeline-from-Pipeline/assets/main-ado.png)

In **ProjectA** I also created a repository called **RepoA** which contains a file called **MyConfig.txt**.

![projects](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/DevOps-Pipeline-from-Pipeline/assets/projects.png)

![myConfig](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/DevOps-Pipeline-from-Pipeline/assets/myconfig.png)

I also created the following code in **PipelineA.yml**.

```yaml
## code/PipelineA.yml

trigger: none

stages:
  - stage: Build_Artifact
    displayName: Build Artifact A

    jobs:
      - job: Build
        displayName: Build
        pool:
          name: Azure Pipelines
          vmImage: windows-2019

        steps:
          - task: CopyFiles@2
            displayName: 'Copy myConfig to Staging'
            inputs:
              SourceFolder: '$(Build.SourcesDirectory)'
              Contents: 'MyConfig.txt'
              TargetFolder: '$(Build.ArtifactStagingDirectory)/drop'

          - task: PublishPipelineArtifact@1
            displayName: 'Publish Artifact to Pipeline'
            inputs:
              targetPath: '$(Build.ArtifactStagingDirectory)/drop'
              artifactName: ArtifactA
```

**NOTE:** It is important to note that when we create the above pipeline in our source project we must rename the pipeline to the same name as what we will refer to it in our pipeline resource on **PipelineB**. In my case I will refer to this as **PipelineA**.

![rename](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/DevOps-Pipeline-from-Pipeline/assets/rename.png)

The above YAML pipeline will take the file **MyConfig.txt** and create a pipeline artifact containing the file called **ArtifactA**.

![pipelineA](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/DevOps-Pipeline-from-Pipeline/assets/pipelineA.png)

![artifactA](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/DevOps-Pipeline-from-Pipeline/assets/artifactA.png)

In **ProjectB** I have **PipelineB.yml** that contains the pipeline resource for **PipelineA** and will be triggered once **PipelineA** completes and we will use the download task to also consume the artifact that was produced by **PipelineA**.

```yaml
## code/PipelineB.yml

trigger: none
pr: none

# ------ This is our Pipeline Resource ------
resources:
  pipelines:
    - pipeline: PipelineA # identifier for the resource used in pipeline resource variables.
      project: ProjectA # project for the source; optional for current project.
      source: PipelineA # name of the pipeline that produces an artifact.
      trigger: # triggers are not enabled by default unless you add trigger section to the resource.
        branches: # branch conditions to filter the events, optional; Defaults to all branches.
          include: # branches to consider the trigger events, optional; Defaults to all branches.
            - main
# ------------------------------------------

stages:
  - stage: Consume_Artifact
    displayName: Consume Artifact A

    jobs:
      - job: Consume
        displayName: Consume
        pool:
          name: Azure Pipelines
          vmImage: windows-2019

        steps:
          - task: PowerShell@2
            displayName: 'Information'
            inputs:
              targetType: inline
              script: |
                Write-output "This pipeline has been triggered by: $(resources.pipeline.PipelineA.pipelineName)"

          - download: PipelineA
            artifact: 'ArtifactA'

          - task: PowerShell@2
            displayName: 'Get-Content MyConfig.txt'
            inputs:
              targetType: inline
              script: |
                Get-Content -path $(Pipeline.Workspace)/PipelineA/ArtifactA/MyConfig.txt
```

**NOTE:** It is important to note that we have to configure **ProjectB** pipeline settings to allow it to connect to **ProjectA** in order to download the artifact that was produced.

![pipesettings](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/DevOps-Pipeline-from-Pipeline/assets/pipesettings.png)

Metadata for a pipeline resource, are available as predefined variables that we can reference, as you can see from our **PipelineB.yml** in the following code snippet:

```yml
## code/PipelineB.yml#L29-L30
script: |
  Write-output "This pipeline has been triggered by: $(resources.pipeline.PipelineA.pipelineName)"
```

**Predefined pipeline resource variables:**

```txt
resources.pipeline.<Alias>.projectID
resources.pipeline.<Alias>.pipelineName
resources.pipeline.<Alias>.pipelineID
resources.pipeline.<Alias>.runName
resources.pipeline.<Alias>.runID
resources.pipeline.<Alias>.runURI
resources.pipeline.<Alias>.sourceBranch
resources.pipeline.<Alias>.sourceCommit
resources.pipeline.<Alias>.sourceProvider
resources.pipeline.<Alias>.requestedFor
resources.pipeline.<Alias>.requestedForID
```

Now when we trigger and run **PipelineA** in **ProjectA**, it will automatically create our **ArtifactA** and also after completion **PipelineB** in **ProjectB** will be automatically triggered and also download and consume **ArtifactA** that was created in **ProjectA**.

![results](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/DevOps-Pipeline-from-Pipeline/assets/results.png)

Also note that triggers for resources are created based on the default branch configuration of our YAML, which is master. However, if we want to configure resource triggers from a different branch, we will need to change the default branch for the pipeline. For more information have a look at [Default branch for triggers](https://docs.microsoft.com/en-us/azure/devops/pipelines/process/resources?view=azure-devops&tabs=example#default-branch-for-triggers).

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my [Github](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/DevOps-Pipeline-from-Pipeline/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}
