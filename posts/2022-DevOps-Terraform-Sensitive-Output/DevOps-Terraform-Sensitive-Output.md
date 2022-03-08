---
title: Terraform - Sensitive Output
published: false
description: DevOps - Terraform - Sensitive Output
tags: 'terraform, azure, iac, azuredevops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-DevOps-Terraform-Sensitive-Output/assets/main-tf.png'
canonical_url: null
id: 1016375
series: Terraform Pro Tips
---

## Overview

This tutorial uses examples from the following GitHub project: [Azure Terraform Deployments](https://github.com/Pwd9000-ML/Azure-Terraform-Deployments).  

When creating terraform configurations, especially when using CI/CD tooling such as Azure DevOps or GitHub it is very easy to overlook what exactly is being output as part of a Terraform configuration plan, especially if the configuration contains sensitive data. This could lead to sensitive data and settings to be leaked.  

In todays tutorial we will look at examples on how we can protect and hide sensitive data in terraform output using masking.  

## Sensitive Variable Types

In the following demo [configuration](https://github.com/Pwd9000-ML/Azure-Terraform-Deployments/tree/master/04_App_Acr) we will use Terraform to create the following resources in Azure:

- Resource Group
- App Service Plan
- App Insights
- App Service

Let's take a closer look at the App service configuration:  

```hcl
## appservices.tf ##
resource "azurerm_app_service" "APPSVC" {
  name                = var.appsvc_name
  location            = azurerm_resource_group.RG.location
  resource_group_name = azurerm_resource_group.RG.name
  app_service_plan_id = azurerm_app_service_plan.ASP.id
  https_only          = true

  identity {
    type = "SystemAssigned"
  }

  site_config {
    acr_use_managed_identity_credentials = true
    ftps_state                           = "FtpsOnly"
    linux_fx_version                     = var.asp_kind == "linux" ? local.linux_fx_version : null
  }

  app_settings = var.appsvc_settings
}
```

Notice the setting called `app_settings = var.appsvc_settings`. The variable for this setting is defined as a map:

```hcl
## variables.tf ##
variable "appsvc_settings" {
  type        = map(any)
  description = "Specifies the app service settings to be created."
  default     = null
}
```

If we pass the following variable into the terraform config: 

```hcl
appsvc_settings = {
  APPINSIGHTS_INSTRUMENTATIONKEY = "!!sensitive_Key!!"
  sensitive_key1                 = "P@ssw0rd01"
  sensitive_key2                 = "P@ssw0rd02"
}
```

Notice that when the terraform plan is being run, terraform will actually output the variable into the terraform plan and log to the CI/CD tooling as output:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-DevOps-Terraform-Sensitive-Output/assets/var01.png)

This can be an issue because the data will be leaked to anyone who has access to the CI/CD logs/output. Especially dangerous if the repository or project is public.  

So what we can do to mask the setting from output is to mark the variable as `sensitive`. We can do that by adding `sensitive = true` to the variable:  

```hcl
## variables.tf ##
variable "appsvc_settings" {
  type        = map(any)
  description = "Specifies the app service settings to be created."
  default     = null
  sensitive   = true
}
```

Notice now that when the terraform plan is being run, terraform will mask the output of the the variable:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-DevOps-Terraform-Sensitive-Output/assets/var02.png)

## Sensitive Output Types

Similarly to variables, outputs can also be marked as sensitive. For example say we want to create a sensitive output we can mark the output as `sensitive`:

```hcl
resource "azurerm_application_insights" "INSIGHTS" {
  name                = var.app_insights_name
  location            = azurerm_resource_group.RG.location
  resource_group_name = azurerm_resource_group.RG.name
  application_type    = "web"
  workspace_id        = var.workspace_id != null ? var.workspace_id : null
}

output "insights_key" {
    value = azurerm_application_insights.INSIGHTS.instrumentation_key
    sensitive = true
}
```

## Sensitive Function


