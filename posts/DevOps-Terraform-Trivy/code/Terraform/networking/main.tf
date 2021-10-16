terraform {
  required_version = "~> 1.0.9"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 2.81.0"
    }
  }
  backend "azurerm" {

  }
}

provider "azurerm" {
  features {}
}

provider "azurerm" {
  features {}
  alias           = "core_network"
  subscription_id = "00000000-0000-0000-0000-000000000000"
  client_id       = "00000000-0000-0000-0000-000000000000"
  client_secret   = "S3cR3t20!"
  tenant_id       = "00000000-0000-0000-0000-000000000000"
}