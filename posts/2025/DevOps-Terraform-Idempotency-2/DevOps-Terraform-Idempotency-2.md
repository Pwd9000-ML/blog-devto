---
title: Terraform_Data - Avoiding Duplicate Resource Violations in Azure with checks
published: true
description: 'Use terraform_data to check if an Azure resource exists before creating it, avoiding duplicate resource violations in Terraform deployments.'
tags: 'terraform, azure, tutorial, devops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2025/DevOps-Terraform-Idempotency-2/assets/main-tf-error.png'
canonical_url: null
id: 2291203
series: Terraform ERRORS!
date: '2025-02-25T18:33:49Z'
---

## Overview

Welcome to another post in the Terraform series, **[Terraform ERRORS!](https://dev.to/pwd9000/series/29961)** In this post, we'll explore how to avoid duplicate resource violations in Azure when working with Terraform by using the **terraform_data** resource to check if a resource already exists before creating it.

In the previous post of this series: **["Mastering Idempotency Violations - Handling Resource Conflicts and Failures in Azure"](https://dev.to/pwd9000/terraform-mastering-idempotency-violations-handling-resource-conflicts-and-failures-in-azure-3f3d)**, you may already be familiar with using `null_resource` and `local-exec` provisioners to run scripts or perform certain actions that will not be recorded to a Terraform configurations state file.

Luckily, the same functionality is now natively supported in Terraform using the `terraform_data` block instead, and `null_resource` is now deprecated.  
With Terraform v1.4 the same functionality is now natively built-in. Essentially an empty container resource that does everything `null_resource` did, but without the extra baggage of managing a separate provider.

This new resource also has feature parity with `null_resource`, so you can switch over without missing a beat.

Let's take a look at a scenario where you can use the `terraform_data` resource to avoid duplicate resource violations in Azure when working with Terraform.

## Scenario

A typical scenario is when you try to create a resource in Azure, but it already exists (perhaps it was created outside of Terraform or during a previous run). This can lead to errors like `Error: A resource with the ID already exists - to be managed via Terraform this resource needs to be imported into the State.`

If you want to manage the resource in Terraform, you can use the `import` block to import the existing resource into Terraform's state.

Have a look at my previous post: **["Mastering Idempotency Violations - Handling Resource Conflicts and Failures in Azure"](https://dev.to/pwd9000/terraform-mastering-idempotency-violations-handling-resource-conflicts-and-failures-in-azure-3f3d)** to see how you can **import existing resources** into Terraform's state using the new **"import"** block if the resource needs to be managed by Terraform.

However, in some cases you may not want to `import` the resource or manage the resource in Terraform. Perhaps it is out of scope of your responsibility for managing the resource, or it may be part of a different deployment.

In these situations you can use the `terraform_data` resource to check if a resource already exists. This way you can avoid the violation by creating the resources only when needed and also ensure your code will remain running if the configuration depends on existing resources that you do not want to manage in Terraform.

This method is useful when you want to only check and create resources conditionally and can be more flexible. The only drawback is that you won't be able to manage the resource in Terraform as mentioned, but you can always `import` the resource if needed later.

## Example

Say for example you want to create resources inside of a **resource group** called `Demo-Inf-Dev-Rg-720`, but the resource group already exists and is managed and provisioned by another team in your organisation. If you attempted to create the resource group you will get an error saying that the **resource group** already exists: `Error: A resource with the ID already exists - to be managed via Terraform this resource needs to be imported into the State.`

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2025/DevOps-Terraform-Idempotency-2/assets/error.png)

An Azure Resource Group is a very basic example, but the same concept can be applied to any resource in Azure that you may have a dependency on that is managed outside of Terraform that was created by another means.

It is also quite useful if you want to create resources, or modifications to existing resources, that are available, maybe as **_"Preview"_** features that are not yet added into the AzureRM Terraform provider, that can be imported at a later date when the provider is updated or become **_"Generally Available (GA)"_**.

In our example, you can use the `terraform_data` resource with `local-exec` instead, to check if the resource group exists and only create it if it does not exist. Let's take a look:

```hcl
resource "terraform_data" "rg_check" {
  input            = var.resource_group_name
  triggers_replace = timestamp()

  provisioner "local-exec" {
    # Use the Azure CLI with PowerShell Core to check if the resource group exists and create if not
    interpreter = ["pwsh", "-Command"]
    command     = <<EOT
      $ErrorActionPreference = "Stop"
      az login --service-principal --username $env:ARM_CLIENT_ID --password $env:ARM_CLIENT_SECRET --tenant $env:ARM_TENANT_ID --output none
      az account set --subscription $env:ARM_SUBSCRIPTION_ID --output none
      $rg_verify = az group show --name ${var.resource_group_name} --query id --output tsv
      if ($rg_verify) {
        $rg_exist = Write-Output "$rg_verify"
      } else {
        $rg_create = (az group create --name ${var.resource_group_name} --location ${var.location} --query id --output tsv)
      }
    EOT
  }
}

output "rg_id_output" {
  description = "The ID of the resource group that was created or already existed"
  value       = terraform_data.rg_check.output
}
```

Let's break down the code above and see how it works:

**Resource Definition:** `terraform_data.rg_check`

```hcl
resource "terraform_data" "rg_check" {
  input            = var.resource_group_name
  triggers_replace = timestamp()
```

This block defines a Terraform resource named `terraform_data.rg_check`. It has two attributes:

- **input:** This is set to the value of the variable `var.resource_group_name`, which is expected to be the name of the resource group to check.
- **triggers_replace:** This is set to the current `timestamp()`, ensuring that the resource is re-evaluated whenever the timestamp changes. This sort of trigger will cause the resource to be re-evaluated every time the configuration is applied, which is useful when you want to check if the resource exists every time the configuration is applied since it is not managed by Terraform and may change outside of Terraform.

**Provisioner:** `local-exec`

```terraform
  provisioner "local-exec" {
    # Use the Azure CLI with PowerShell Core to check if the resource group exists and create if not
    interpreter = ["pwsh", "-Command"]
    command     = <<EOT
      $ErrorActionPreference = "Stop"
      az login --service-principal --username $env:ARM_CLIENT_ID --password $env:ARM_CLIENT_SECRET --tenant $env:ARM_TENANT_ID --output none
      az account set --subscription $env:ARM_SUBSCRIPTION_ID --output none
      $rg_verify = az group show --name ${var.resource_group_name} --query id --output tsv
      if ($rg_verify) {
        $rg_exist = Write-Output "$rg_verify"
      } else {
        $rg_create = (az group create --name ${var.resource_group_name} --location ${var.location} --query id --output tsv)
      }
    EOT
  }
}
```

This nested block inside of the resource, defines a `local-exec` provisioner, which allows you to run a local command using **Powershell Core** for example. The provisioner has the following attributes:

- **interpreter:** Specifies the interpreter to use, in this case, **PowerShell Core (pwsh)**. You have to make sure that PowerShell Core is installed on the machine where the Terraform configuration is being applied.
- **command:** Contains the PowerShell script to execute. The script performs the following:
  - Sets the error action preference to "Stop" to halt execution on any error.
  - Logs into Azure using a service principal with credentials provided via environment variables. In this case the script uses **Azure service principal credentials** stored as **Github Secrets** and passed as environment variables into the **Github Actions workflow** CI/CD process.
  - Sets the Azure subscription context where the service principal has **IAM/RBAC** access to.
  - Checks if the resource group specified by `var.resource_group_name` exists using **Azure CLI**.
  - If the resource group exists, it outputs the `resource group ID`.
  - If the resource group does not exist, it creates the resource group using **Azure CLI** in the specified location and outputs the new `resource group ID`.

**Note:** The because the script uses a `local-exec` provisioner, using **PowerShell Core**, we are also using the **Azure CLI** to interact with Azure. So you will need to have **Azure CLI** also installed on the machine where the Terraform configuration is being applied.

**Output Definition:** `rg_id_output`

```hcl
output "rg_id_output" {
  description = "The ID of the resource group that was created or already existed"
  value       = terraform_data.rg_check.output
}
```

This block defines an output variable named `rg_id_output`. It has the following attributes:

- **description:** A brief description of the output, indicating that it represents the ID of the resource group that was either created or already existed.
- **value:** The value of the output, which is set to `terraform_data.rg_check.output`. This should be the output from the `local-exec` provisioner.

**Note:** The `--output` flag is set to `tsv` in the Azure CLI commands to output the result, and the result is then written back to Terraform as an output variable to be used in other parts of the configuration as needed, by using the `terraform_data.rg_check.<output>` variable. This is useful if you want to only capture specific outputs of the `local-exec` provisioner and use it in other parts of the Terraform configuration.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2025/DevOps-Terraform-Idempotency-2/assets/output.png)

## Conclusion

In this post, we explored how to avoid duplicate resource violations in Azure when working with Terraform by using the `terraform_data` resource.

Even though the `terraform_data` resource can be used for various other scenarios and use cases, it is very handy built-in functionality now that can be used and in our example case explained, to check if an Azure resource already exists before creating it conditionally.

Remember the resources you create or modify in Azure using this technique will not be managed by Terraform, so if you need to manage the resource in Terraform at a later time, you can always import the resource into Terraform's state when needed. Especially those resources that are managed outside of Terraform or are not yet supported by the Terraform provider you are using.

**Have you faced idempotency problems in Terraform? Share your solutions in the comments!**

If you enjoyed this post and want to learn more about **Terraform** and **Azure**, check out my other Terraform Series **[Terraform Pro Tips](https://dev.to/pwd9000/series/16567)**.

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [X](https://x.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-pwd9000/)

{% user pwd9000 %}
