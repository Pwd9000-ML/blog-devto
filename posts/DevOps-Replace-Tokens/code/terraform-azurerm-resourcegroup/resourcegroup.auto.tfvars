resource_group_name = "Infra-~{environment}~-Rg"
location            = "~{location}~"
tags = {
  terraformDeployment = "true"
  Environment         = "~{environment}~"
}