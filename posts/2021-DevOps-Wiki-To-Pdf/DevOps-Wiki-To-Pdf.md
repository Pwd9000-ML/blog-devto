---
title: Create a PDF document from an Azure DevOps Wiki
published: true
description: DevOps - Convert Devops Wiki to PDF
tags: 'automation, azure, devops, azuredevops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-DevOps-Wiki-To-Pdf/assets/main.png'
canonical_url: null
id: 824638
date: '2021-09-15T09:20:57Z'
---

## Azure DevOps Wiki

When working on Azure DevOps or Github, we have special needs when it comes to wiki's and documentation. Specifically, we often have our documentation sit next to our source code in our repos, allowing us to version our documentation along with our source code. This developer-specific workflow is totally supported by Azure DevOps Wiki. What is great about using the Azure DevOps wiki is that similarly how teams can share and collaborate on a projects source code the same team, using the same workflow can also share and collaborate on a projects documentation through its Wiki. Documentation such as release notes, manuals and any sort of documentation that needs to accompany a project can be created in a Wiki. The documentation is then also kept in source control and in a central place that a team can access and collaborate on.

But this might not be suitable or possible at all times in all use cases, for example to see the DevOps wiki a person must have access to the DevOps Project and Wiki. Say for example someone who is in a different project or in a management role that does not have access to the DevOps project or wiki would like to see a products release notes or maybe some sort of documentation on the project in a document, this makes things a bit more tricky. So today I will share with you how you can convert your DevOps or Github wiki into a PDF document. We will also look at how we can create a pipeline that will automatically generate a new "Wiki PDF" document when required.

## DevOps Wiki PDF Export Task

WIKI PDF Export Tasks is a DevOps extension that can be installed into your DevOps Organisation from the Azure DevOps [marketplace](https://marketplace.visualstudio.com/items?itemName=richardfennellBM.BM-VSTS-WikiPDFExport-Tasks), simply put it is an Azure Pipelines extension that can give teams another way to present their Wiki as a PDF document, whether it be an export of a whole WIKI or just a single page.

The extension is based on a tool called [**AzureDevOps.WikiPDFExport**](https://github.com/MaxMelcher/AzureDevOps.WikiPDFExport) by Max Melcher that allows you to export a whole WIKI (or a single file) as a PDF. The tool performs the following tasks:

- Clone a WIKI Repo
- Run the command line tool passing in a path to the root of the cloned wiki repo
- The .order file is read
- A PDF is generated

## Wiki to PDF Pipeline

After installing [WIKI PDF Export Tasks](https://marketplace.visualstudio.com/items?itemName=richardfennellBM.BM-VSTS-WikiPDFExport-Tasks) in your Devops Organisation. Navigate to your Wiki repository.  
In this tutorial I am using a repo on my project called: **Devops.Wiki** published as my project wiki.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-DevOps-Wiki-To-Pdf/assets/wiki.png)

Under my repo I then created a new folder/path called: `.pipelines`

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-DevOps-Wiki-To-Pdf/assets/paths.png)

In this path we will create our YAML pipeline called `wiki-to-pdf.yml` with the following code:

```yaml
# code/wiki-to-pdf.yml

name: Wiki-To-PDF-$(Rev:rr)
trigger: none

stages:
- stage: wiki_export
  displayName: Wiki Export

  jobs:
  - job: wiki_to_pdf
    displayName: Wiki To PDF
    pool:
      vmImage: windows-latest
    
    steps:
    - task: UseDotNet@2
      displayName: 'Use .NET Core sdk'
      inputs:
        packageType: 'sdk'
        version: '6.0.x'
        includePreviewVersions: true

    - task: richardfennellBM.BM-VSTS-WikiPDFExport-Tasks.WikiPDFExportTask.WikiPdfExportTask@2
      displayName: 'Export a private Azure DevOps WIKI'
      inputs:
        cloneRepo: true
        repo: 'https://dev.azure.com/magiconionM/Devto_Blog_Demos/_git/DevOps.Wiki'
        useAgentToken: true
        localpath: '$(System.DefaultWorkingDirectory)/DevOpsWiki' 
        outputFile: '$(Build.ArtifactStagingDirectory)/PDF/DevOpsWiki.pdf'
    
    - task: PublishPipelineArtifact@1
      displayName: 'Publish wiki export to Azure Pipeline'
      inputs:
        targetPath: '$(Build.ArtifactStagingDirectory)/PDF'
        artifactName: DevOpsWiki


```

We can then set up this pipeline and trigger it manually, once the pipeline has completed it will generate an artifact that contains the PDF document.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-DevOps-Wiki-To-Pdf/assets/run.png)

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-DevOps-Wiki-To-Pdf/assets/artifact.png)

[Here](https://github.com/Pwd9000-ML/blog-devto/blob/main/posts/2021-DevOps-Wiki-To-Pdf/code/DevOpsWiki.pdf) is an example PDF export.

## Other Examples

Note on our pipeline the task used is specifically to export a private Azure DevOps WIKI:

```yml
- task: richardfennellBM.BM-VSTS-WikiPDFExport-Tasks.WikiPDFExportTask.WikiPdfExportTask@2
  displayName: 'Export a private Azure DevOps WIKI'
  inputs:
    cloneRepo: true
    repo: 'https://dev.azure.com/magiconionM/Devto_Blog_Demos/_git/DevOps.Wiki'
    useAgentToken: true
    localpath: '$(System.DefaultWorkingDirectory)/DevOpsWiki'
    outputFile: '$(Build.ArtifactStagingDirectory)/PDF/DevOpsWiki.pdf'
```

Here are two more examples. Export a Single File:

```yml
- task: richardfennellBM.BM-VSTS-WikiPDFExport-Tasks.WikiPDFExportTask.WikiPdfExportTask@2
  displayName: 'Export Single File'
  inputs:
    cloneRepo: false
    usePreRelease: false
    localpath: '$(System.DefaultWorkingDirectory)'
    singleFile: 'release_notes.md'
    outputFile: '$(Build.ArtifactStagingDirectory)/PDF/ReleaseNotes.pdf'
```

Export a public GitHub WIKI:

```yml
- task: richardfennellBM.BM-VSTS-WikiPDFExport-Tasks.WikiPDFExportTask.WikiPdfExportTask@2
  displayName: 'Export a public GitHub WIKI'
  inputs:
    cloneRepo: true
    repo: 'https://github.com/rfennell/AzurePipelines.wiki.git'
    useAgentToken: false
    localpath: '$(System.DefaultWorkingDirectory)\GitHubRepo'
    outputFile: '$(Build.ArtifactStagingDirectory)\PDF\GitHubWiki.pdf'
```

**NOTE:** This blog post has been updated to reflect the changes in V2 of the task/extension. The `AzureDevOps.WikiPDFExport` tool since 4.0.0 is [.NET6](https://dotnet.microsoft.com/download/dotnet/6.0) based. Hence [.NET6](https://dotnet.microsoft.com/download/dotnet/6.0) must be installed on the agent.

This can easily be done by using the following build pipeline task as shown on the yaml config, before the extension is called.

```yaml
# code/wiki-to-pdf.yml#L15-L20

- task: UseDotNet@2
  displayName: 'Use .NET Core sdk'
  inputs:
    packageType: 'sdk'
    version: '6.0.x'
    includePreviewVersions: true
```

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my [Github](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2021-DevOps-Wiki-To-Pdf/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
