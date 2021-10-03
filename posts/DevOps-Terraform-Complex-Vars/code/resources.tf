provider "azurerm" {
  features {}
  skip_provider_registration = true
}

resource "azurerm_resource_group" "demo_rg" {
  count    = lookup(var.rg_config, "create_rg", false) ? 1 : 0
  name     = lookup(var.rg_config, "name", "Default-RG-Name")
  location = lookup(var.rg_config, "location", "uksouth")
  tags     = { Purpose = "Demo-RG", Automation = "true" }
}

resource "azurerm_storage_account" "sas" {
  count = length(var.storage_config)

  #Implicit dependency from previous resource
  resource_group_name = azurerm_resource_group.demo_rg[0].name
  location            = azurerm_resource_group.demo_rg[0].location

  #lookup values e.g. lookup(map, key, default)
  name                      = lookup(var.storage_config[count.index], "name", "defaultsaname")
  account_kind              = lookup(var.storage_config[count.index], "account_kind", "StorageV2")
  account_tier              = lookup(var.storage_config[count.index], "account_tier", "Standard")
  account_replication_type  = lookup(var.storage_config[count.index], "account_replication_type", "LRS")
  access_tier               = lookup(var.storage_config[count.index], "access_tier", "Hot")
  enable_https_traffic_only = lookup(var.storage_config[count.index], "enable_https_traffic_only", true)
  min_tls_version           = lookup(var.storage_config[count.index], "min_tls_version", "TLS1_2")
  is_hns_enabled            = lookup(var.storage_config[count.index], "is_hns_enabled", false)

  #Apply tags
  tags = { Purpose = "Demo-sa-${count.index + 1}", Automation = "true" }
}
