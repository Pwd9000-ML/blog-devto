#Custom DNS for VNet (When new VNET is created)
dns_servers = ["10.2.0.10", "10.2.0.138"]

#e.g. Development, UAT, QA, POC, Testing, Production
environment = "Testing"

#e.g. IT, Development, Research
lob = "Development"

#e.g. uksouth, westeurope, centralus, eastasia (input validated)
location = "uksouth"

#Vnet base IP address (When new VNET is created)
network_ip = "10.2.0.0"

#Vnet mask (When new VNET is created)
network_mask = 22

#Global prefix
prefix = "Terraform"

#Subnet Configuration maps.
subnet_config = {
  Dmz1 = {
    name      = "Dmz1"
    mask      = 25
    cidr_base = "10.2.0.0"
  }
  Dmz2 = {
    name      = "Dmz2"
    mask      = 25
    cidr_base = "10.2.0.128"
  }
  Prod = {
    name      = "Prod"
    mask      = 24
    cidr_base = "10.2.1.0"
  }
  Dev = {
    name      = "Dev"
    mask      = 24
    cidr_base = "10.2.2.0"
  }
}