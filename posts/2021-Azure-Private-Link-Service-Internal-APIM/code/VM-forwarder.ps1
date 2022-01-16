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