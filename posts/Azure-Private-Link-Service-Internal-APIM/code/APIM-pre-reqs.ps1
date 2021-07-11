#Login-AzAccount
# Variables.
$randomInt = Get-Random -Maximum 9999
$resourceGroupName = "PrivateAPIM"
$vnetName = "MainNet"
$apimSubnetName = "apimSubnet"
$plsSubnetName = "plsSubnet"
$apimName = "apim$randomInt"
$region = "uksouth"

# Create a resource resourceGroupName
New-AzResourceGroup -Name "$resourceGroupName" -Location "$region"

# Create NSG and pls (private link service) subnet.
$plsRule1 = New-AzNetworkSecurityRuleConfig `
    -Name "pls-in" `
    -Description "PLS inbound" `
    -Access "Allow" `
    -Protocol "Tcp" `
    -Direction "Inbound" `
    -Priority 100 `
    -SourceAddressPrefix "VirtualNetwork" `
    -SourcePortRange "*" `
    -DestinationAddressPrefix "VirtualNetwork" `
    -DestinationPortRange 443

$plsNsg = New-AzNetworkSecurityGroup `
    -ResourceGroupName "$resourceGroupName" `
    -Location "$region" `
    -Name "NSG-PLS" `
    -SecurityRules $plsRule1

$plsSubnet = New-AzVirtualNetworkSubnetConfig `
    -Name "$plsSubnetName" `
    -NetworkSecurityGroup $plsNsg `
    -AddressPrefix 10.0.1.0/24

# Create NSG and APIM subnet subnet.
$apimRule1 = New-AzNetworkSecurityRuleConfig `
    -Name "apim-in" `
    -Description "APIM inbound" `
    -Access "Allow" `
    -Protocol "Tcp" `
    -Direction "Inbound" `
    -Priority 100 `
    -SourceAddressPrefix "ApiManagement" `
    -SourcePortRange "*" `
    -DestinationAddressPrefix "VirtualNetwork" `
    -DestinationPortRange 3443

$apimNsg = New-AzNetworkSecurityGroup `
    -ResourceGroupName "$resourceGroupName" `
    -Location "$region" `
    -Name "NSG-APIM" `
    -SecurityRules $apimRule1

$apimSubnet = New-AzVirtualNetworkSubnetConfig `
    -Name "$apimSubnetName" `
    -NetworkSecurityGroup $apimNsg `
    -AddressPrefix 10.0.2.0/24

# Create VNET
Write-Output "Creating Virtual Network... Please Wait..."
$vnet = New-AzVirtualNetwork `
    -Name "$vnetName" `
    -ResourceGroupName "$resourceGroupName" `
    -Location "$region" `
    -AddressPrefix "10.0.0.0/16" `
    -Subnet $plsSubnet,$apimSubnet

#Get APIM subnet ID
$plsSubnetData = $vnet.Subnets[0]
$apimSubnetData = $vnet.Subnets[1]

# Create an API Management service instance. (Developer SKU for this demo... SKUs: Basic, Consumption, Developer, Premium, Standard)
Write-Output "Creating APIM service... Please Wait..."
$apimVirtualNetwork = New-AzApiManagementVirtualNetwork -SubnetResourceId $apimSubnetData.Id
$apimService = New-AzApiManagement `
    -ResourceGroupName "$resourceGroupName" `
    -Location "$region" `
    -Name "$apimName" `
    -Organization "pwd9000" `
    -AdminEmail "pwd9000@hotmail.co.uk" `
    -VirtualNetwork $apimVirtualNetwork `
    -VpnType "Internal" -Sku "Developer"