variable "rg_config" {
  type = object({
    create_rg = bool
    name      = string
    location  = string
  })
}

variable "storage_config" {
  type = list(object({
    name                      = string
    account_kind              = string
    account_tier              = string
    account_replication_type  = string
    access_tier               = string
    enable_https_traffic_only = bool
    min_tls_version           = string
    is_hns_enabled            = bool
  }))
}

#variable "storage_config" {}