#### Ensure VNET and AzureBastionSubnet with /26 CIDR is available before creation of Bastion Host ####
#Login to Azure
az login
az account set --subscription "Your-Subscription-Id"

#Set Variables
$location = "uksouth"
$bastionName = "Pwd9000-EB-Bastion"
$bastionPip = "Pwd9000-EB-Bastion-Pip"
$bastionRG = "Pwd9000-EB-Network"
$bastionVNET = "UKS-EB-VNET"

#Deploy Public IP for Bastion
az network public-ip create --resource-group $bastionRG `
    --name $bastionPip `
    --location $location `
    --sku "Standard"
    
#Deploy Bastion
az network bastion create --name $bastionName `
    --public-ip-address $bastionPip `
    --resource-group $bastionRG `
    --vnet-name $bastionVNET `
    --location $location `
    --sku "Standard"