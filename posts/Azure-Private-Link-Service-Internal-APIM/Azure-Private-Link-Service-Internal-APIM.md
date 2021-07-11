---
title: Access internal APIM securely with Private Link Service
published: false
description: Azure - internal APIM + Private Link Service
tags: 'tutorial, azure, productivity, security'
cover_image: assets/PLSMain.png
canonical_url: null
id: 755878
---

## What is Azure Private Link Service?

[Azure Private Link service](https://docs.microsoft.com/en-us/azure/private-link/private-link-service-overview) is the reference to your own service that is powered by Azure Private Link. Your service that is running behind Azure Standard Load Balancer can be enabled for Private Link access so that consumers to your service can access it privately from their own VNets. Your customers can create a private endpoint inside their VNet and map it to this service.

### Access internal API Management Service securely with Private Link Service from an external non-peered VNET

In todays tutorial we will look into an interesting use case for this service, in how we can connect an external source to consume an API management service (internal VNET mode) from an external non-peered VNET. As depicted in the following diagram:

![networkDiag](./assets/networkDiag.png)

**Note:** The source or entry point where we will place out private endpoint can be in a network that is in a completely different region, tenant or subscription.

Before we get started, let's just think about why we would want to do this?  

**APIM (Internal VNET mode):** When API management deploys in internal VNET mode, you can only view the service endpoints within a VNET whose access you control. In order to reduce the attack surface area, configuring APIM with all it's endpoints (e.g. gateway, APIM portals and management endpoints) will be protected within an internal VNET, and cannot be directly accessed from any potential threats from the public internet. The service can only be accessed from peered VNETs tha have connectivity to our VNET hosting our APIM service.  

This is all good security and practice, but what if we have a requirement where we have a consumer that needs to use our API that is located in another VNET that perhaps overlaps IP address space and cannot be peered or connected to our VNET hosting our APIM service? Or what is we have a close business partner or company that has a VNET in a completely separate region, tenant and subscription? How can we make our API management service available to such consumers and keep everything internal and secure at the same time?  

Luckily there is a solution to this problem statement, and the answer is Azure private link service. With Azure Private Link Service we can create a **Standard Load Balancer** that will be connected to a **Virtual Machine** or **Virtual Machine Scale Set** which will act as a relay using **IP/Port forwarding** to our internal APIM, we will front the load balancer with **Private Link Service** and create a **Private endpoint** on our source network that will allow entry point connectivity.  

## What do we need?

1. **Azure Virtual Network:** We will need either a new or an existing VNET with two subnets for our Private Link Service and APIM.
2. **APIM (Internal VNET mode):** For this tutorial we will create an [internal APIM](https://docs.microsoft.com/en-us/azure/api-management/api-management-using-with-internal-vnet).
3. **VM or VMMS:** For this tutorial we will create a single windows VM and configure it to be a forwarder to our internal APIM. (You can also use a VMSS instead)
4. **Standard Load Balancer:** We will use a standard load balancer to front our connect VM/VMSS which will be used by the private link service.
5. **Private Link Service:** We will create a Private link service and connect it up with our load balancer.
6. **Private Endpoint:** We will then create a private endpoint in the external VNET and test our connectivity to our internal APIM from the external network.

To get everything ready I will be using AZ powershell. First we will log into Azure by running:

```powershell
Login-AzAccount
```

Next we will create a `resource group`, `virtual network` and `APIM (internal VNET mode)` by running:

```powershell
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
```

**Note:** Because we are creating a new APIM service for this tutorial, the above powershell code can take anything between 10-20 minutes to complete.

After our APIM is created make a note of the APIM **Private IP** as we will se this in a later step to configure our forwarder.

![apimPrivateIP]()

Next we will create our `Virtual machine` that will be used as a forwarder by running:

```powershell
# Variables.
$vmLocalAdmin = "pwd9000admin"
$vmLocalAdminPassword = Read-Host -assecurestring "Please enter your password"
$region = "uksouth"
$resourceGroupName = "PrivateAPIM"
$computerName = "VmPls01"
$vmName = "VmPls01"
$vmSize = "Standard_DS2_V2"
$networkName = "MainNet"
$nicName = "VmPls01-nic"
$vNet = Get-AzVirtualNetwork -Name $NetworkName
$plsSubnetId = ($vnet.Subnets | Where-Object {$_.name -eq "plsSubnet"}).id

$NIC = New-AzNetworkInterface -Name $nicName -ResourceGroupName $resourceGroupName -Location $region -SubnetId $plsSubnetId -EnableIPForwarding
$Credential = New-Object System.Management.Automation.PSCredential ($vmLocalAdmin, $vmLocalAdminPassword);
$VirtualMachine = New-AzVMConfig -VMName $vmName -VMSize $vmSize
$VirtualMachine = Set-AzVMOperatingSystem -VM $VirtualMachine -Windows -ComputerName $computerName -Credential $Credential -ProvisionVMAgent -EnableAutoUpdate
$VirtualMachine = Add-AzVMNetworkInterface -VM $VirtualMachine -Id $NIC.Id
$VirtualMachine = Set-AzVMSourceImage -VM $VirtualMachine -PublisherName 'MicrosoftWindowsServer' -Offer 'WindowsServer' -Skus '2019-Datacenter' -Version latest
$VirtualMachine = Set-AzVMOSDisk -VM $VirtualMachine -StorageAccountType "Standard_LRS" -CreateOption FromImage -Windows | Set-AzVMBootDiagnostic -Disable

New-AzVM -ResourceGroupName $resourceGroupName -Location $region -VM $VirtualMachine -Verbose
```

**Note:** IP Forwarding has been enabled on the network interface of the VM we will use as a forwarder.

```txt
// code/VM-forwarder.ps1#L13-L13
```

Now that our VM is created we need to run a few commands on the VM to allow certain traffic to be forwarded. First we will enable IP Forwarding on the registry, and also create a firewall rule to allow https(443) traffic incoming and lastly we will enable forwarding to our APIMs private IP address using `netsh`.

`netsh interface portproxy add v4tov4 listenport=443 listenaddress=10.2.1.4 connectport=443 connectaddress=10.2.2.5`

### _Author_

Marcel.L - pwd9000@hotmail.co.uk
