##################################################
# LOCALS                                         #
##################################################
locals {
  common_tags = {
    billing_code   = var.billing_code[var.environment]
    cost_center    = var.cost_center[var.lob]
    Environment    = var.environment
    LineOfBusiness = var.lob
    Region         = var.region[var.location]
  }
  core_resourcegroupname = "${var.prefix}-Core-Networking-${lower(var.cost_center[var.lob])}"
  vnet_name              = "${var.prefix}-Core-VNET-${lower(var.cost_center[var.lob])}${random_integer.sa_num.result}"

  # Validation: 
  # This section validates input for location of available locations
  locations = {
    westeurope = "westeurope"
    centralus  = "centralus"
    eastasia   = "eastasia"
    uksouth    = "uksouth"
  }
  # Error is input variable "location" does not match locals location map
  validate_input_location = local.locations[var.location]
}

##################################################
# MODULES                                        #
##################################################
module "dynamic-subnets" {
  source                  = "github.com/Pwd9000-ML/terraform-azurerm-dynamic-subnets"
  common_tags             = local.common_tags
  dns_entries             = var.dns_servers
  environment             = var.environment
  location                = var.location
  network_address_ip      = var.network_ip
  network_address_mask    = var.network_mask
  virtual_network_rg_name = local.core_resourcegroupname
  virtual_network_name    = local.vnet_name
  subnet_config           = var.subnet_config
}

##################################################
# RESOURCES                                      #
##################################################
resource "random_integer" "sa_num" {
  min = 0001
  max = 9999
}