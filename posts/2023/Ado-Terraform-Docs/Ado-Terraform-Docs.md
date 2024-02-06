---
title: Automating Terraform Documentation with Terraform-Docs and Azure DevOps
published: true
description: Automating Terraform Documentation with Terraform-Docs and Azure DevOps
tags: 'cicd, iac, terraform, azuredevops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/Ado-Terraform-Docs/assets/main-tf-tips.png'
canonical_url: null
id: 1510780
series: Terraform Pro Tips
date: '2023-06-20T16:05:49Z'
---

## Overview

Based on a popular blog post I did last year, **["Automating Terraform Documentation with Terraform-Docs and GitHub Actions"](https://dev.to/pwd9000/auto-generate-documentation-from-terraform-modules-42bl)**. I decided to revisit the topic and see if I could automate the process using **Azure DevOps** instead of **GitHub Actions**.

Documenting infrastructure code is just as important as writing the code itself. It's crucial for the readability and maintainability of the code, especially when we are working as a part of the team. However, documentation is often neglected, and keeping it up-to-date can be a challenging task. Fortunately, there are tools like Terraform-Docs that help automate this process.

In this blog post, we will discuss how to automate the generation and update of your **Terraform** documentation with **Terraform-Docs** and **Azure DevOps Pipelines**. The process is straightforward and can be achieved with a few simple steps and I will show you a completely automated way of self-generating documentation for your **Terraform** modules on **Azure DevOps**.

## What is Terraform-Docs?

**Terraform-Docs** is an open-source tool that generates documentation for your Terraform modules based on the metadata provided in the Terraform files. It supports multiple output formats like Markdown, JSON, YAML, and others. The tool scans your Terraform files and outputs comprehensive documentation, including inputs, outputs, providers, requirements, and more.

## The Automation Process

We are going to use **Azure DevOps pipelines** to automate this process. Say for example you have a **Terraform** module structure in **Git** that looks like this:

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

To automate each sub module **'README.md'** file, we need to create an **Azure DevOps pipeline** that will run on a trigger when any changes are made to our terraform code base and merged in our **Git** repository's **'main'** branch. The pipeline will then automatically generate the documentation for each Terraform module and commit the updated **'README.md'** files back to the repository.

Let's take a closer look at the following [Multi-Stage pipeline for windows](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2023/Ado-Terraform-Docs/code/generate-terraform-docs-windows.yml). (for linux based build agents see this [Multi-Stage pipeline for linux](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2023/Ado-Terraform-Docs/code/generate-terraform-docs-linux.yml) instead).

```yaml
### Muti-Stage pipeline for windows
trigger:
  - main

variables:
  terraformDocsVersion: '0.16.0'
  serviceConnectionName: 'Terraform-SPN-DevOps-MagiconionM'
  keyvaultName: 'pwd9000-core-kv'

pool:
  vmImage: 'windows-latest'

stages:
  - stage: GenerateTerraformDocumentation
    jobs:
      - job: Generate_Terraform_Documentation
        steps:
          - checkout: self
            persistCredentials: true # this allows the later scripts to use the system-provided git token to push changes back to the repo

          ### Link to key vault.
          - task: AzureKeyVault@1
            inputs:
              azureSubscription: $(serviceConnectionName) #ADO service connection (Service principal)
              KeyVaultName: $(keyvaultName)
              SecretsFilter: 'TerraformDocsPAToken'
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
              Set-Location "$(Build.SourcesDirectory)\@Terraform_Modules_Root_Dir"

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

For **Linux** based build agents:

```yaml
### Muti-Stage pipeline for linux
trigger:
  - main

variables:
  terraformDocsVersion: '0.16.0'
  serviceConnectionName: 'Terraform-SPN-DevOps-MagiconionM'
  keyvaultName: 'pwd9000-core-kv'

pool:
  vmImage: 'ubuntu-latest'

stages:
  - stage: GenerateTerraformDocumentation
    jobs:
      - job: Generate_Terraform_Documentation
        steps:
          - checkout: self
            persistCredentials: true # this allows the later scripts to use the system-provided git token to push changes back to the repo

          ### Link to key vault.
          - task: AzureKeyVault@1
            inputs:
              azureSubscription: $(serviceConnectionName) #ADO service connection (Service principal)
              KeyVaultName: $(keyvaultName)
              SecretsFilter: 'TerraformDocsPAToken'
              RunAsPreJob: true
            displayName: Get PAToken from Keyvault

          ### Install Terraform-Docs.
          - script: |
              wget https://github.com/terraform-docs/terraform-docs/releases/download/v$(terraformDocsVersion)/terraform-docs-v$(terraformDocsVersion)-linux-amd64.tar.gz
              tar -xvf terraform-docs-v$(terraformDocsVersion)-linux-amd64.tar.gz
              sudo mv terraform-docs /usr/local/bin/
            displayName: 'Install terraform-docs'

          ### Remove all old README.md files and generate new README.md files for each TF module.
          - script: |
              # Set Modules Root Directory
              root_dir="$(Build.SourcesDirectory)/@Terraform_Modules_Root_Dir"

              # Get all subdirectories (Terraform module directories)
              terraformModuleDirs=$(find $root_dir -maxdepth 1 -type d)

              # Loop through each directory to cleanup/remove old README files
              for dir in $terraformModuleDirs; do
                  # Get all files in the directory
                  readMeFiles=$(find "$dir" -name "README.md")

                  # Loop through each file in each Terraform module
                  for file in $readMeFiles; do
                      # Check if README file already exists and remove
                      if [ -f "$file" ]; then
                          # Remove the file
                          rm -f "$file"
                          echo "Old file $(basename "$file") removed from $(realpath "$dir")"
                      fi
                  done

                  #After cleanup create a new README.md file with 'terraform-docs' based on latest TF module code in current folder(terraform module)
                  tfFiles=$(find "$dir" -name "*.tf")

                  if [ "$(echo "$tfFiles" | wc -l)" -gt 0 ]; then
                      # Create new README.md file
                      terraform-docs markdown table $(realpath "$dir") --output-file "$dir/README.md"
                  else
                      echo "No .tf files found."
                  fi
              done
            displayName: 'Cleanup and Generate new README for each TF module'

          ### Commit and push updated README.md files for TF modules.
          - script: |
              git config --local user.email "terraform-docs@myOrg.com"
              git config --local user.name "Terraform Docs"
              git add "*.md"
              git commit -m "Update README.md for each TF module"
              git push origin HEAD:$(Build.SourceBranchName)
            displayName: 'Commit and Push updated README.md files for TF modules'
            env:
              SYSTEM_ACCESSTOKEN: $(TerraformDocsPAToken)
```

The pipeline has a single stage, **'GenerateTerraformDocumentation'**, which contains a job **'Generate_Terraform_Documentation'**. This job performs the following steps:

1. **Checkout Code:** The first step checks out your code from the repository and persists the credentials. The persisted credentials allow the pipeline to push any changes back to the repository.

2. **Link to Azure Key Vault:** The pipeline then retrieves a personal access token (PAT) from an Azure Key Vault using the AzureKeyVault task. This PAT is used later to push updates back to the repository.

3. **Install Terraform-Docs:** Next, the pipeline downloads and installs a specific version of Terraform-Docs on the DevOps hosted agent. The desired version is defined in the pipeline variables.

4. **Generate Documentation:** Once Terraform-Docs is installed, the pipeline cleans up any old `README.md` files and generates new ones for each Terraform module. It traverses the Terraform module directories under the path `$(Build.SourcesDirectory)/@Terraform_Modules_Root_Dir`, removes any existing `README.md` files, and generates new ones based on the current Terraform code. (You can update this path to match your Terraform module directory structure.)

5. **Commit and Push:** Finally, it commits the updated `README.md` files and pushes them back to the repository using the PAT retrieved from Azure Key Vault.

## Pre-requisites

There are a few pre-requisites for this solution that we need to set up before we can run the pipeline. These include the following based on the above steps/tasks performed by the pipeline:

### 1. Create a Personal Access Token (PAT) in Azure DevOps

Notice the **keyvault** step above:

```yaml
### Link to key vault.
- task: AzureKeyVault@1
  inputs:
    azureSubscription: $(serviceConnectionName) #ADO service connection (Service principal)
    KeyVaultName: $(keyvaultName)
    SecretsFilter: 'TerraformDocsPAToken'
    RunAsPreJob: true
  displayName: Get PAToken from Keyvault
```

This step will retrieve a keyvault secret called **'TerraformDocsPAToken'** using the AzureKeyVault task from the keyvault specified in the pipeline **Variables**. This secret is used later to push updates back to the repository using this task:

```yaml
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

Notice the `SYSTEM_ACCESSTOKEN: $(TerraformDocsPAToken)` environment variable above. This is the PAT retrieved from the keyvault and used to push updates back to the repository.

The PAT token scope of permissions required for this solution is **'Code (Read & write)'**.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/Ado-Terraform-Docs/assets/PAT.png)

For more information on how to create a PAT token, see [here](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops&tabs=preview-page?wt.mc_id=DT-MVP-5004771).

After creating the PAT token, add it to the keyvault as a secret called **'TerraformDocsPAToken'** and update the pipeline variables to point to the correct keyvault name.

### 2. Add generic-contribute permissions to the service principal used by the ADO service connection

The ADO service connection used by the pipeline to connect to the repository must have **'Generic Contribute'** permissions to the repository. This is required to allow the pipeline to push updates back to the repository. To do this you will need to navigate to the repository in ADO and add the service principal used by the ADO service connection to the repository with **'Generic Contribute'** permissions.

In Azure DevOps, navigate to the repository settings. You can find this under **Project settings -> Repos -> Repositories** and select the repository where you want to allow access.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/Ado-Terraform-Docs/assets/repo1.png)

Navigate to the **'Security'** tab. Find the user or group that matches your pipeline identity. If your pipeline is running at the project scope, this will be **'Project Build Service ({ProjectName})'**. If it's running at the organization scope, this will be **'Project Collection Build Service ({OrganizationName})'**. Once you've found the correct identity, check the **'Contribute'** permission.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/Ado-Terraform-Docs/assets/repo2.png)

Next, on the same page, **'Add'** the pipeline to the **'Pipeline permissions'**.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/Ado-Terraform-Docs/assets/repo3.png)

Lastly, **'Add'** the ADO service connection used by the pipeline to the **'Git refs permissions'** on the **'main'** branch with **'Bypass policies when pushing'** set to **'Allow'**.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/Ado-Terraform-Docs/assets/repo4.png)

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/Ado-Terraform-Docs/assets/repo5.png)

That is it, now once a Pull Request is merged into the **'main'** branch, the pipeline will automatically run and update the Terraform module documentation in each module directory and push each updated **'README.md'** file back to the repository:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/Ado-Terraform-Docs/assets/result.png)

## Conclusion

Integrating this documentation generation process into your CI/CD pipeline can keep your Terraform module documentation updated in real-time. Every time you modify your Terraform code and push to your repository, the CI/CD pipeline can automatically generate and commit the updated documentation, ensuring your documentation is always up-to-date and synced with your latest Terraform code.

In conclusion, automating your Terraform documentation with Terraform-Docs and Azure DevOps is a great way to keep your Terraform modules documented and updated. It not only saves time but also ensures consistent and comprehensive documentation, leading to better code understanding and easier maintenance.

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my published [GitHub](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2023/Ado-Terraform-Docs/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
