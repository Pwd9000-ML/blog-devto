rg_config = {
  create_rg = true
  name      = "Demo-Terraform-RG"
  location  = "uksouth"
}

storage_config = [
  #V2 Storage
  {
    name                      = "pwd9000v2sa001"
    account_kind              = "StorageV2"
    account_tier              = "Standard"
    account_replication_type  = "LRS"
    min_tls_version           = "TLS1_2"
    enable_https_traffic_only = true
    access_tier               = "Cool"
    is_hns_enabled            = true
  },
  #ADLS2 Storage
  {
    name                      = "pwd9000adls2sa001"
    account_kind              = "BlockBlobStorage"
    account_tier              = "Premium"
    account_replication_type  = "ZRS"
    min_tls_version           = "TLS1_2"
    enable_https_traffic_only = false
    access_tier               = "Hot"
    is_hns_enabled            = true
  }
]
