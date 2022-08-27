resource_group_name = "Demo-Infra-Dev-Rg"
location            = "UKSouth"
key_vault_name      = "Pwd9000-Infra-Dev-Kv"
use_rbac_mode       = true
tags = {
  terraformDeployment = "true",
  GitHubRepo          = "https://github.com/Pwd9000-ML/Azure-Terraform-Deployments"
  Environment         = "DEV"
}