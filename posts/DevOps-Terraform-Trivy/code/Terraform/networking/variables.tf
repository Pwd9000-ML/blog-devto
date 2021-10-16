##################################################
# VARIABLES                                      #
##################################################
variable "billing_code" {
  type = map(string)
  default = {
    Development = "100"
    UAT         = "101"
    QA          = "102"
    POC         = "103"
    Testing     = "104"
    Production  = "105"
  }
  description = "Optional Input - Billing code map based on environment. (used for common tags defined in locals)"
}

variable "cost_center" {
  type = map(string)
  default = {
    IT          = "IT"
    Development = "DEV"
    Research    = "RND"
  }
  description = "Optional Input - Cost center map based on line of business. (used for naming conventions defined in locals)"
}

variable "dns_servers" {
  type        = list(string)
  default     = []
  description = "Optional Input - Set custom dns config. If no values specified, this defaults to Azure DNS (Only in effect on newly created Vnet when variable:create_vnet=true)"
}

variable "environment" {
  type        = string
  description = "Required Input - Value to describe the environment. Primarily used for tagging and naming resources. (used for naming conventions defined in locals)"
}

variable "lob" {
  type        = string
  description = "Required Input - Describes line of business. (used for naming conventions defined in locals; accepted values: IT, Development, Research)"
}

variable "location" {
  type        = string
  description = "Required Input - Location in azure where resources will be created. (ONLY accepted values [validation]: westeurope, centralus, eastasia, uksouth)"
}

variable "network_ip" {
  type        = string
  description = "Required Input - Network IP to construct network address space. (Only in effect on newly created Vnet when variable:create_vnet=true)"
}

variable "network_mask" {
  type        = number
  description = "Required Input - Network address mask to construct network address space. (Only in effect on newly created Vnet when variable:create_vnet=true)"
}
variable "prefix" {
  type        = string
  default     = "Demo"
  description = "Required Input - Used for naming conventions defined in locals"
}

variable "region" {
  type        = map(string)
  description = "Optional Input - Regional map based on location. (used for naming conventions defined in locals)"
  default = {
    westeurope = "EMEA"
    centralus  = "NA"
    eastasia   = "APAC"
    uksouth    = "UK"
  }
}

variable "subnet_config" {
  type        = map(any)
  description = "Required Input - Subnet Configuration"
}