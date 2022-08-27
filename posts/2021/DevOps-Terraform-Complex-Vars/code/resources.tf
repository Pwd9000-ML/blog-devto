provider "azurerm" {
  features {}
  skip_provider_registration = true
}

resource "azurerm_resource_group" "demo_rg" {
  count    = var.rg_config.create_rg ? 1 : 0
  name     = var.rg_config.name
  location = var.rg_config.location
  tags     = { Purpose = "Demo-RG", Automation = "true" }
}

resource "azurerm_storage_account" "sas" {
  count = length(var.storage_config)

  #Implicit dependency from previous resource
  resource_group_name = azurerm_resource_group.demo_rg[0].name
  location            = azurerm_resource_group.demo_rg[0].location

  #values from variable config object
  name                      = var.storage_config[count.index].name
  account_kind              = var.storage_config[count.index].account_kind
  account_tier              = var.storage_config[count.index].account_tier
  account_replication_type  = var.storage_config[count.index].account_replication_type
  access_tier               = var.storage_config[count.index].access_tier
  enable_https_traffic_only = var.storage_config[count.index].enable_https_traffic_only
  min_tls_version           = var.storage_config[count.index].min_tls_version
  is_hns_enabled            = var.storage_config[count.index].is_hns_enabled

  #Apply tags
  tags = { Purpose = "Demo-sa-${count.index + 1}", Automation = "true" }
}
