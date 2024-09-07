resource_group_name = "Msdo-Inf-Dev-Rg"
location            = "UKSouth"
key_vault_name      = "Msdo-Inf-Dev-Kv"
use_rbac_mode       = true
tags = {
  terraformDeployment = "true",
  GithubRepo          = "https://github.com/Pwd9000-ML/MSDO-Lab"
  Environment         = "DEV"
}