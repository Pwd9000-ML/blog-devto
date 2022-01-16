##################################################
# Terraform Config                               #
##################################################
terraform {
  required_version = ">= ~{terraformVersion}~"

  backend "azurerm" {
    resource_group_name  = "~{terraformBackendRG}~"
    storage_account_name = "~{terraformBackendSA}~"
    container_name       = "tfstate"
    key                  = "infra_~{environment}~_rg.tfstate"
  }

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 2.73"
    }
  }
}

provider "azurerm" {
  features {}
  skip_provider_registration = true
}

##################################################
# RESOURCES                                      #
##################################################
resource "azurerm_resource_group" "resource_group" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}