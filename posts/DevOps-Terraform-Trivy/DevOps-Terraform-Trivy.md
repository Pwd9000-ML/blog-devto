---
title: Terraform IaC Scanning with Trivy
published: false
description: DevOps - Terraform - IaC Scanning with Trivy
tags: 'tutorial, security, productivity, devops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/DevOps-Terraform-Trivy/assets/main-trivy.png'
canonical_url: null
id: 864896
---

## Trivy Vulnerability Scanner

`Trivy` is a simple and comprehensive scanner for vulnerabilities in container images, file systems, and Git repositories, as well as for configuration issues in IaC. `Trivy` detects vulnerabilities of OS packages (Alpine, RHEL, CentOS, etc.) and language-specific packages (Bundler, Composer, npm, yarn, etc.). In addition, `Trivy` scans Infrastructure as Code (IaC) files such as Terraform, Dockerfile and Kubernetes, to detect potential configuration issues that expose your deployments to the risk of attack.

You can scan your Terraform configuration artifacts easily giving you the confidence that all is well with your configuration before deploying your Terraform (IaC) configurations. It is a free/open source tool by AquaSecurity. For more information go check out the [Trivy github page](https://github.com/aquasecurity/trivy)

Today we will look at how you can utilise `Trivy` as part of your DevOps CI/CD process by scanning your Terraform (IaC) code for security risks, before actually deploying the configuration to ensure that there are no vulnerabilities or misconfigurations that could potentially open up security risks.

## How to Scan IaC

This tutorial is based on the following [Azure DevOps Repository](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/DevOps-Terraform-Trivy/code) blueprint, which will use a CI/CD YAML pipeline to deploy an Azure Virtual Network using terraform IaC configuration files.

There are terraform configuration files under the path [/Terraform/networking](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/DevOps-Terraform-Trivy/code/Terraform/networking). There is also a YAML pipeline `network.yml` under [/pipelines/](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/DevOps-Terraform-Trivy/code/pipelines) which is used to deploy the terraform code. The pipeline will trigger a `build.yml` template which essentially creates our Terraform artifact and if successful the pipeline will trigger the `deploy.yml` template which will apply our terraform configuration artifact. The pipeline templates are kept under the path [/task_groups/](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/DevOps-Terraform-Trivy/code/task_groups).

We will utilise `Trivy` during our build phase, so lets take a look at the `build.yml` file:

```yml
#// code/task_groups/build.yml#L16-L89

jobs:
  - job: build
    pool:
      vmImage: ${{ parameters.pool }}
    workspace:
      clean: all
    steps:
      - checkout: self
        path: src

      - task: TerraformInstaller@0
        inputs:
          terraformVersion: ${{ parameters.terraformVersion }}

      - task: CmdLine@2
        displayName: 'Download and Install Trivy vulnerability scanner'
        inputs:
          script: |
            sudo apt-get install rpm
            wget https://github.com/aquasecurity/trivy/releases/download/v${{ parameters.trivyVersion }}/trivy_${{ parameters.trivyVersion }}_Linux-64bit.deb
            sudo dpkg -i trivy_${{ parameters.trivyVersion }}_Linux-64bit.deb
            trivy -v

      - task: TerraformTaskV2@2
        displayName: Terraform Init
        inputs:
          provider: 'azurerm'
          command: 'init'
          workingDirectory: '$(Agent.BuildDirectory)/src/${{ parameters.root_directory }}'
          backendServiceArm: ${{ parameters.backend_service_connection_name }}
          backendAzureRmResourceGroupName: ${{ parameters.backend_resource_group }}
          backendAzureRmStorageAccountName: ${{ parameters.backend_storage_accountname }}
          backendAzureRmContainerName: ${{ parameters.container_name }}
          backendAzureRmKey: ${{ parameters.container_key }}

      - task: CmdLine@2
        displayName: 'LOW/MED - Trivy vulnerability scanner in IaC mode'
        inputs:
          script: |
            trivy config --severity LOW,MEDIUM --exit-code 0 $(Agent.BuildDirectory)/src/${{ parameters.root_directory }}

      - task: CmdLine@2
        displayName: 'HIGH/CRIT - Trivy vulnerability scanner in IaC mode'
        inputs:
          script: |
            trivy config --severity HIGH,CRITICAL --exit-code 1 $(Agent.BuildDirectory)/src/${{ parameters.root_directory }}

      - task: TerraformTaskV2@2
        displayName: Terraform Plan
        inputs:
          provider: 'azurerm'
          command: 'plan'
          workingDirectory: '$(Agent.BuildDirectory)/src/${{ parameters.root_directory }}'
          commandOptions: '--var-file=$(Agent.BuildDirectory)/src/${{ parameters.root_directory }}${{ parameters.tfvarFile }} --out=$(Agent.BuildDirectory)/src/${{ parameters.root_directory }}plan.tfplan'
          environmentServiceNameAzureRM: ${{ parameters.deployment_service_connection_name }}

      - task: CopyFiles@2
        displayName: 'Copy Files to Staging'
        inputs:
          SourceFolder: '$(Agent.BuildDirectory)/src'
          Contents: 'Terraform/**'
          TargetFolder: '$(Build.ArtifactStagingDirectory)'

      - task: ArchiveFiles@2
        inputs:
          rootFolderOrFile: '$(Build.ArtifactStagingDirectory)'
          archiveFile: '$(Build.ArtifactStagingDirectory)/$(Build.BuildId).zip'
          replaceExistingArchive: true
          includeRootFolder: false
        displayName: Archive Terraform Artifact

      - publish: '$(Build.ArtifactStagingDirectory)/$(Build.BuildId).zip'
        artifact: '$(Build.BuildId)-trivy'
        displayName: Publish Pipeline Artifact
```

As you can see from the `build` process above we are performing the following steps:

- Download and Install Terraform.
- Download and Install Trivy vulnerability scanner.
- Perform a Terraform Init on our terraform network configuration.
- Run Trivy vulnerability scanner in IaC mode for (LOW / MEDIUM) risks.
- Run Trivy vulnerability scanner in IaC mode for (HIGH / CRITICAL) risks.
- Run a Terraform plan.
- Copy our Terraform deployment files to a staging area.
- Create a Terraform deployment Artifact (zip) from the staging area.
- Publish the Terraform deployment artifact created to the pipeline for later use.

**NOTE:** Trivy will not cause the `build` process of the pipeline to fail on (LOW/MEDIUM) risks, but will cause a failure if any (HIGH/CRITICAL) issues are detected. This is defined by the `--exist-code (1)(0)` argument:

```yml
#// code/task_groups/build.yml#L51-L61

- task: CmdLine@2
displayName: "LOW/MED - Trivy vulnerability scanner in IaC mode"
inputs:
    script: |
        trivy config --severity LOW,MEDIUM --exit-code 0 $(Agent.BuildDirectory)/src/${{ parameters.root_directory }}

- task: CmdLine@2
displayName: "HIGH/CRIT - Trivy vulnerability scanner in IaC mode"
inputs:
    script: |
        trivy config --severity HIGH,CRITICAL --exit-code 1 $(Agent.BuildDirectory)/src/${{ parameters.root_directory }}
```

That is it as far as configuring and integrating Trivy into your CI/CD process to check your Terraform deployments for any security or misconfiguration issues before completing a build. Let's take a look at an example.

## Example

**NOTE:** Please note that this example does not protect secrets being committed into source control and is meant as a guide. If you find any secrets in source code or terraform configurations after they have been committed please remove and rotate them as soon as possible.

As you can see in my Terraform configuration [main.tf](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/DevOps-Terraform-Trivy/code/Terraform/networking/main.tf). I have configured a second provider using an alias, but I configured my provider with a `client_secret` value in plain text:

```hcl
# Terraform/networking/main.tf#L18-L25

provider "azurerm" {
  features {}
  alias           = "core_network"
  subscription_id = "00000000-0000-0000-0000-000000000000"
  client_id       = "00000000-0000-0000-0000-000000000000"
  client_secret   = "S3cR3t20!"
  tenant_id       = "00000000-0000-0000-0000-000000000000"
}
```

When trivy runs a scan against my Terraform configuration you will see that my `build` pipeline fails due to a **CRITICAL** security risk that it identified.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/DevOps-Terraform-Trivy/assets/detect.png)

## What is checked?

Trivy checks Terraform IaC using [TFSEC](https://github.com/aquasecurity/tfsec). You can take a look at all the check that are performed [HERE](https://github.com/aquasecurity/tfsec#included-checks). As the example above in the screenshot Trivy detected a risk called: [Potentially sensitive data stored in block attribute](https://tfsec.dev/docs/general/secrets/sensitive-in-attribute/)

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my [Github](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/DevOps-Terraform-Trivy/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}
