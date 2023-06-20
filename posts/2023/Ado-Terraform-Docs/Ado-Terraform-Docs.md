---
title: Automating Terraform Documentation with Terraform-Docs and Azure DevOps
published: false
description: Automating Terraform Documentation with Terraform-Docs and Azure DevOps
tags: 'cicd, iac, terraform, azuredevops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/Ado-Terraform-Docs/assets/main-tf-tips.png'
canonical_url: null
id: 1510780
series: Terraform Pro Tips
---

## Overview

Based on a popular blog post I did last year, **["Automating Terraform Documentation with Terraform-Docs and GitHub Actions"](https://dev.to/pwd9000/auto-generate-documentation-from-terraform-modules-42bl)**. I decided to revisit the topic and see if I could automate the process using **Azure DevOps** instead of **GitHub Actions**.

Documenting infrastructure code is just as important as writing the code itself. It's crucial for the readability and maintainability of the code, especially when we are working as a part of the team. However, documentation is often neglected, and keeping it up-to-date can be a challenging task. Fortunately, there are tools like Terraform-Docs that help automate this process.

In this blog post, we will discuss how to automate the generation and update of your **Terraform** documentation with **Terraform-Docs** and **Azure DevOps Pipelines**. The process is straightforward and can be achieved with a few simple steps and I will show you a completely automated way of self-generating documentation for your **Terraform** modules on **Azure DevOps**.

## What is Terraform-Docs?  

**Terraform-Docs** is an open-source tool that generates documentation for your Terraform modules based on the metadata provided in the Terraform files. It supports multiple output formats like Markdown, JSON, YAML, and others. The tool scans your Terraform files and outputs comprehensive documentation, including inputs, outputs, providers, requirements, and more.

## The Automation Process

We are using **Azure DevOps pipelines** to automate this process.  

Say for example you have a **Terraform** module structure in **Git** that looks like this:  

```txt
├── @Terraform_Modules_Root_Dir/
│   ├── Module001/
│   │   ├── README.md
│   │   ├── variables.tf
│   │   ├── main.tf
│   │   ├── outputs.tf
│   ├── Module002/
│   │   ├── README.md
│   │   ├── variables.tf
│   │   ├── main.tf
│   │   ├── outputs.tf
```

To automate each sub module **README.md** file, we need to create a **Azure DevOps pipeline** that will run on a trigger when any changes are made and mergded in our **Git** repository **main** branch. The pipeline will then automatically generate the documentation for each Terraform module and commit the updated **README.md** files back to the repository.

Let's take a closer look at the following [Muti-Stage pipeline](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2023/Ado-Terraform-Docs/code/generate-terraform-docs-windows.yml) for windows OS build agents. (for linux based build agents see this [pipeline](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2023/Ado-Terraform-Docs/code/generate-terraform-docs-linux.yml) instead).

```yaml
trigger:
- main

variables:
  terraformDocsVersion: "0.16.0"
  serviceConnectionName: "Terraform-SPN-DevOps-MagiconionM"
  keyvaultName: "pwd9000-core-kv"

pool:
  vmImage: 'windows-latest'

stages:
- stage: GenerateTerraformDocumentation
  jobs:
  - job: Generate_Terraform_Documentation
    steps:
    - checkout: self
      persistCredentials: true  # this allows the later scripts to use the system-provided git token to push changes back to the repo

    ### Link to key vault.
    - task: AzureKeyVault@1
      inputs:
        azureSubscription: $(serviceConnectionName) #ADO service connection (Service principal)
        KeyVaultName: $(keyvaultName)
        SecretsFilter: "TerraformDocsPAToken"
        RunAsPreJob: true
      displayName: Get PAToken from Keyvault

    ### Install Terraform-Docs.
    - powershell: |
        Invoke-WebRequest -Uri "https://github.com/terraform-docs/terraform-docs/releases/download/v$(terraformDocsVersion)/terraform-docs-v$(terraformDocsVersion)-windows-amd64.zip" -OutFile "terraform-docs.zip"
        Expand-Archive -Path "terraform-docs.zip" -DestinationPath "$(System.DefaultWorkingDirectory)\terraform-docs" -Force
        $env:Path += ";$(System.DefaultWorkingDirectory)\terraform-docs"
      displayName: 'Install terraform-docs'

    ### Remove all old README.md files and generate new README.md files for each TF module.
    - powershell: |
        # Set Modules Root Directory
        Set-Location "$(Build.SourcesDirectory)\@TF_Modules"

        # Get all subdirectories (Terraform module directories)
        $terraformModuleDirs = Get-ChildItem -Path (Get-Location) -Directory

        # Loop through each directory to cleanup/remove old README files
        foreach ($dir in $terraformModuleDirs) {
            # Get all files in the directory
            $readMeFiles = Get-ChildItem -Path $dir.FullName -Filter 'README.md'

            # Loop through each file in each terraform module
            foreach ($file in $readMeFiles) {
                # Check if README file already exists and remove
                if ($file) {
                    # Remove the file
                    Remove-Item $file.FullName -Confirm:$false
                    Write-Output "Old file '$($file.Name)' removed from '$($dir.FullName)'"
                }
            }

            #After cleanup create a new README.md file with 'terraform-docs' based on latest TF module code in current folder(terraform module)
            $tfFiles = Get-ChildItem -Path $dir.FullName -Filter *.tf

            if ($tfFiles.Count -gt 0) {
                # Create new README.md file
                $(System.DefaultWorkingDirectory)\terraform-docs\terraform-docs.exe markdown table $dir.FullName --output-file "README.md"
            } else {
                Write-Output "No .tf files found."
            }
        }
      displayName: 'Cleanup and Generate new README for each TF module'

    ### Commit and push updated README.md files for TF modules.
    - powershell: |
        git config --local user.email "terraform-docs@myOrg.com"
        git config --local user.name "Terraform Docs"
        git add *.md
        git commit -m "Update README.md for each TF module"
        git push origin HEAD:$(Build.SourceBranchName)
      displayName: 'Commit and Push updated README.md files for TF modules'
      env:
        SYSTEM_ACCESSTOKEN: $(TerraformDocsPAToken)
```

The pipeline has a single stage, GenerateTerraformDocumentation, which contains a job Generate_Terraform_Documentation. This job performs the following steps:

Checkout Code: The first step checks out your code from the repository and persists the credentials. The persisted credentials allow the pipeline to push any changes back to the repository.

Link to Azure Key Vault: The pipeline then retrieves a personal access token (PAT) from an Azure Key Vault using the AzureKeyVault task. This PAT is used later to push updates back to the repository.

Install Terraform-Docs: Next, the pipeline downloads and installs a specific version of Terraform-Docs on the runner. The desired version is defined in the pipeline variables.

Generate Documentation: Once Terraform-Docs is installed, the pipeline cleans up any old README.md files and generates new ones for each Terraform module. It traverses the Terraform module directories, removes any existing README.md files, and generates new ones based on the current Terraform code.

Commit and Push: Finally, it commits the updated README.md files and pushes them back to the repository using the PAT retrieved from Azure Key Vault.

## Conclusion

Integrating this documentation generation process into your CI/CD pipeline can keep your Terraform module documentation updated in real-time. Every time you modify your Terraform code and push to your repository, the CI/CD pipeline can automatically generate and commit the updated documentation, ensuring your documentation is always up-to-date and synced with your latest Terraform code.

In conclusion, automating your Terraform documentation with Terraform-Docs and Azure DevOps is a great way to keep your Terraform modules documented and updated. It not only saves time but also ensures consistent and comprehensive documentation, leading to better code understanding and easier maintenance.

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my published [GitHub](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2023/Ado-Terraform-Docs/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
