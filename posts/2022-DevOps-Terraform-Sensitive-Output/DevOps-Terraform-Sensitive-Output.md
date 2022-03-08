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

## Sensitive Variable Type

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

## Sensitive Output Type

Similarly to variables, outputs can also be marked as sensitive. For example say we want to create a sensitive output we can mark the `output` as `sensitive = true` as shown the the below example:

```hcl
## appservices.tf ##
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

Another way to mark output as sensitive is by using the terraform `sensitive()` function. in the demo [configuration](https://github.com/Pwd9000-ML/Azure-Terraform-Deployments/tree/master/04_App_Acr) let's change the way we send `app_settings` to the app service configuration by creating a dynamic `locals` config instead of a variable:  

```hcl
## local.tf ##
locals {
  #Appsvc Settings
  app_settings = {
    default_settings = {
      APPINSIGHTS_INSTRUMENTATIONKEY = "${azurerm_application_insights.INSIGHTS.instrumentation_key}"
      DOKCER_REGISTRY_SERVER_URL     = "${var.acr_name}.azurecr.io"
    },
    linux_app_settings = {
      APPINSIGHTS_INSTRUMENTATIONKEY = "${azurerm_application_insights.INSIGHTS.instrumentation_key}"
      DOKCER_REGISTRY_SERVER_URL     = "${var.acr_name}.azurecr.io"
      WEBSITE_PULL_IMAGE_OVER_VNET   = "true"
      LINUX_SENSITIVE_VALUE          = "!!sensitive_value!!"
    }
  }
  linux_fx_version = "DOCKER|${var.acr_name}/${var.appsvc_name}:latest"
}
```

As you can see the locals configuration has two configurations, one called `default_settings` and another called `linux_app_settings`, we can send the relevant config by using the terraform `lookup()` function as shown below `app_settings = lookup(local.app_settings, "linux_app_settings", null)`:

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

  app_settings = lookup(local.app_settings, "linux_app_settings", null)
}
```

Since our app insights instrumentation key output is already marked as a sensitive output, it is all good and well for that value to be hidden from the output:  

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-DevOps-Terraform-Sensitive-Output/assets/lookup01.png)

But what about if we want the entire `app_settings` config block to be hidden?  
This is where the `sensitive()` function comes in, as you can see by just wrapping the relevant locals variables in the `sensitive()` function will instruct terraform to hide the entire block from output:

```hcl
## local.tf ##
locals {
  #Appsvc Settings
  app_settings = {
    default_settings = sensitive({
      APPINSIGHTS_INSTRUMENTATIONKEY = "${azurerm_application_insights.INSIGHTS.instrumentation_key}"
      DOKCER_REGISTRY_SERVER_URL     = "${var.acr_name}.azurecr.io"
    }),
    linux_app_settings = sensitive({
      APPINSIGHTS_INSTRUMENTATIONKEY = "${azurerm_application_insights.INSIGHTS.instrumentation_key}"
      DOKCER_REGISTRY_SERVER_URL     = "${var.acr_name}.azurecr.io"
      WEBSITE_PULL_IMAGE_OVER_VNET   = "true"
      LINUX_SENSITIVE_VALUE          = "!!sensitive_value!!"
    })
  }
  linux_fx_version = "DOCKER|${var.acr_name}/${var.appsvc_name}:latest"
}
```

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-DevOps-Terraform-Sensitive-Output/assets/lookup02.png)  

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-DevOps-Terraform-Sensitive-Output/assets/appsvc.png)

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my [Github](https://github.com/Pwd9000-ML/Azure-Terraform-Deployments/tree/master/04_App_Acr) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>