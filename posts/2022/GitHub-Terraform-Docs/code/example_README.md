<!-- BEGIN_TF_DOCS -->

## Requirements

| Name | Version |
| --- | --- |
| <a name="requirement_terraform"></a> [terraform](#requirement_terraform) | ~> 1.2.0 |
| <a name="requirement_azurerm"></a> [azurerm](#requirement_azurerm) | ~> 3.15.0 |

## Providers

| Name                                                         | Version   |
| ------------------------------------------------------------ | --------- |
| <a name="provider_azurerm"></a> [azurerm](#provider_azurerm) | ~> 3.15.0 |
| <a name="provider_random"></a> [random](#provider_random)    | n/a       |

## Modules

No modules.

## Resources

| Name | Type |
| --- | --- |
| [azurerm_container_group.sonarqube_aci](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/container_group) | resource |
| [azurerm_key_vault.sonarqube_kv](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault) | resource |
| [azurerm_key_vault_secret.password_secret](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault_secret) | resource |
| [azurerm_key_vault_secret.username_secret](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault_secret) | resource |
| [azurerm_mssql_database.sonarqube_mssql_db](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/mssql_database) | resource |
| [azurerm_mssql_firewall_rule.sonarqube_mssql_fw_rules](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/mssql_firewall_rule) | resource |
| [azurerm_mssql_server.sonarqube_mssql](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/mssql_server) | resource |
| [azurerm_resource_group.sonarqube_rg](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/resource_group) | resource |
| [azurerm_role_assignment.kv_role_assigment](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/role_assignment) | resource |
| [azurerm_storage_account.sonarqube_sa](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/storage_account) | resource |
| [azurerm_storage_share.sonarqube](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/storage_share) | resource |
| [azurerm_storage_share_file.sonar_properties](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/storage_share_file) | resource |
| [random_password.sql_admin_password](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/password) | resource |
| [azurerm_client_config.current](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/data-sources/client_config) | data source |
| [azurerm_resource_group.sonarqube_rg](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/data-sources/resource_group) | data source |

## Inputs

| Name | Description | Type | Default | Required |
| --- | --- | --- | --- | :-: |
| <a name="input_aci_dns_label"></a> [aci_dns_label](#input_aci_dns_label) | DNS label to assign onto the Azure Container Group. | `string` | `"sonarqube-aci"` | no |
| <a name="input_aci_group_config"></a> [aci_group_config](#input_aci_group_config) | Container group configuration object to create sonarqube aci with caddy reverse proxy. | <pre>object({<br> container_group_name = string<br> ip_address_type = string<br> os_type = string<br> restart_policy = string<br> })</pre> | <pre>{<br> "container_group_name": "sonarqubeaci9000",<br> "ip_address_type": "Public",<br> "os_type": "Linux",<br> "restart_policy": "OnFailure"<br>}</pre> | no |
| <a name="input_caddy_config"></a> [caddy_config](#input_caddy_config) | Caddy container configuration object to create caddy reverse proxy aci. | <pre>object({<br> container_name = string<br> container_image = string<br> container_cpu = number<br> container_memory = number<br> container_environment_variables = map(string)<br> container_commands = list(string)<br> })</pre> | <pre>{<br> "container_commands": [<br> "caddy",<br> "reverse-proxy",<br> "--from",<br> "custom.domain.com",<br> "--to",<br> "localhost:9000"<br> ],<br> "container_cpu": 1,<br> "container_environment_variables": null,<br> "container_image": "caddy:latest",<br> "container_memory": 1,<br> "container_name": "caddy-reverse-proxy"<br>}</pre> | no |
| <a name="input_create_rg"></a> [create_rg](#input_create_rg) | Create a new resource group for this deployment. (Set to false to use existing resource group) | `bool` | `true` | no |
| <a name="input_kv_config"></a> [kv_config](#input_kv_config) | Key Vault configuration object to create azure key vault to store sonarqube aci sql creds. | <pre>object({<br> name = string<br> sku = string<br> })</pre> | <pre>{<br> "name": "sonarqubekv9000",<br> "sku": "standard"<br>}</pre> | no |
| <a name="input_location"></a> [location](#input_location) | Location in azure where resources will be created. (Only in effect on newly created Resource Group when var.create_rg=true) | `string` | `"uksouth"` | no |
| <a name="input_mssql_config"></a> [mssql_config](#input_mssql_config) | MSSQL configuration object to create persistent SQL server instance for sonarqube aci. | <pre>object({<br> name = string<br> version = string<br> })</pre> | <pre>{<br> "name": "sonarqubemssql9000",<br> "version": "12.0"<br>}</pre> | no |
| <a name="input_mssql_db_config"></a> [mssql_db_config](#input_mssql_db_config) | MSSQL database configuration object to create persistent azure SQL db for sonarqube aci. | <pre>object({<br> db_name = string<br> collation = string<br> create_mode = string<br> license_type = string<br> max_size_gb = number<br> min_capacity = number<br> auto_pause_delay_in_minutes = number<br> read_scale = bool<br> sku_name = string<br> storage_account_type = string<br> zone_redundant = bool<br> point_in_time_restore_days = number<br> })</pre> | <pre>{<br> "auto_pause_delay_in_minutes": 60,<br> "collation": "SQL_Latin1_General_CP1_CS_AS",<br> "create_mode": "Default",<br> "db_name": "sonarqubemssqldb9000",<br> "license_type": null,<br> "max_size_gb": 128,<br> "min_capacity": 1,<br> "point_in_time_restore_days": 7,<br> "read_scale": false,<br> "sku_name": "GP_S_Gen5_2",<br> "storage_account_type": "Zone",<br> "zone_redundant": false<br>}</pre> | no |
| <a name="input_mssql_fw_rules"></a> [mssql_fw_rules](#input_mssql_fw_rules) | List of SQL firewall rules in format: [[rule1, startIP, endIP],[rule2, startIP, endIP]] etc. | `list(list(string))` | <pre>[<br> [<br> "Allow All Azure IPs",<br> "0.0.0.0",<br> "0.0.0.0"<br> ]<br>]</pre> | no |
| <a name="input_pass_length"></a> [pass_length](#input_pass_length) | Password length for sql admin creds. (Stored in sonarqube key vault) | `number` | `24` | no |
| <a name="input_sa_config"></a> [sa_config](#input_sa_config) | Storage configuration object to create persistent azure file shares for sonarqube aci. | <pre>object({<br> name = string<br> account_kind = string<br> account_tier = string<br> account_replication_type = string<br> access_tier = string<br> enable_https_traffic_only = bool<br> min_tls_version = string<br> is_hns_enabled = bool<br> })</pre> | <pre>{<br> "access_tier": "Hot",<br> "account_kind": "StorageV2",<br> "account_replication_type": "LRS",<br> "account_tier": "Standard",<br> "enable_https_traffic_only": true,<br> "is_hns_enabled": false,<br> "min_tls_version": "TLS1_2",<br> "name": "sonarqubesa9000"<br>}</pre> | no |
| <a name="input_shares_config"></a> [shares_config](#input_shares_config) | Sonarqube file shares | <pre>list(object({<br> share_name = string<br> quota_gb = number<br> }))</pre> | <pre>[<br> {<br> "quota_gb": 10,<br> "share_name": "data"<br> },<br> {<br> "quota_gb": 10,<br> "share_name": "extensions"<br> },<br> {<br> "quota_gb": 10,<br> "share_name": "logs"<br> },<br> {<br> "quota_gb": 1,<br> "share_name": "conf"<br> }<br>]</pre> | no |
| <a name="input_sonar_config"></a> [sonar_config](#input_sonar_config) | Sonarqube container configuration object to create sonarqube aci. | <pre>object({<br> container_name = string<br> container_image = string<br> container_cpu = number<br> container_memory = number<br> container_environment_variables = map(string)<br> container_commands = list(string)<br> })</pre> | <pre>{<br> "container_commands": [],<br> "container_cpu": 2,<br> "container_environment_variables": null,<br> "container_image": "sonarqube:lts-community",<br> "container_memory": 8,<br> "container_name": "sonarqube-server"<br>}</pre> | no |
| <a name="input_sonarqube_rg_name"></a> [sonarqube_rg_name](#input_sonarqube_rg_name) | Name of the existing resource group. (var.create_rg=false) / Name of the resource group to create. (var.create_rg=true). | `string` | `"Terraform-Sonarqube-aci"` | no |
| <a name="input_sql_admin_username"></a> [sql_admin_username](#input_sql_admin_username) | Username for sql admin creds. (Stored in sonarqube key vault) | `string` | `"Sonar-Admin"` | no |
| <a name="input_tags"></a> [tags](#input_tags) | A map of key value pairs that is used to tag resources created. | `map(string)` | <pre>{<br> "Author": "Marcel Lupo",<br> "Description": "Sonarqube aci with caddy",<br> "GitHub": "https://github.com/Pwd9000-ML/terraform-azurerm-sonarqube-aci",<br> "Terraform": "True"<br>}</pre> | no |

## Outputs

| Name | Description |
| --- | --- |
| <a name="output_sonarqube_aci_container_group_id"></a> [sonarqube_aci_container_group_id](#output_sonarqube_aci_container_group_id) | The container group ID. |
| <a name="output_sonarqube_aci_kv_id"></a> [sonarqube_aci_kv_id](#output_sonarqube_aci_kv_id) | The resource ID for the sonarqube key vault. |
| <a name="output_sonarqube_aci_mssql_db_id"></a> [sonarqube_aci_mssql_db_id](#output_sonarqube_aci_mssql_db_id) | The resource ID for the sonarqube MSSQL database. |
| <a name="output_sonarqube_aci_mssql_db_name"></a> [sonarqube_aci_mssql_db_name](#output_sonarqube_aci_mssql_db_name) | The name of the sonarqube MSSQL database. |
| <a name="output_sonarqube_aci_mssql_id"></a> [sonarqube_aci_mssql_id](#output_sonarqube_aci_mssql_id) | The resource ID for the sonarqube MSSQL Server instance. |
| <a name="output_sonarqube_aci_rg_id"></a> [sonarqube_aci_rg_id](#output_sonarqube_aci_rg_id) | Output Resource Group ID. (Only if new resource group was created as part of this deployment). |
| <a name="output_sonarqube_aci_sa_id"></a> [sonarqube_aci_sa_id](#output_sonarqube_aci_sa_id) | The resource ID for the sonarqube storage account hosting file shares. |
| <a name="output_sonarqube_aci_share_ids"></a> [sonarqube_aci_share_ids](#output_sonarqube_aci_share_ids) | List of resource IDs of each of the sonarqube file shares. |

<!-- END_TF_DOCS -->
