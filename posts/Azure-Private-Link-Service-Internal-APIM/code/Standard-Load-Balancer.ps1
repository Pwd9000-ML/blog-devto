# Variables.
$resourceGroupName = "PrivateAPIM"
$vnetName = "MainNet"
$plsSubnet = ($vnet.Subnets | Where-Object {$_.name -eq "plsSubnet"}).id
$region = "uksouth"

#Vnet object
$vnet = Get-AzVirtualNetwork -Name $vnetName -ResourceGroupName $resourceGroupName

#load balancer frontend configuration
$feip = New-AzLoadBalancerFrontendIpConfig -Name 'plsFrontEnd' -PrivateIpAddress '10.0.1.5' -SubnetId $plsSubnet

#backend address pool configuration
$bepool = New-AzLoadBalancerBackendAddressPoolConfig -Name 'plsVMforwarderPool'

#health probe
$healthprobe = New-AzLoadBalancerProbeConfig -Name 'Check443' -Protocol 'Tcp' -Port '443' -IntervalInSeconds '360' -ProbeCount '5'

# load balancer rule
$rule = New-AzLoadBalancerRuleConfig -Name 'plsHTTPS' -Protocol 'Tcp' -FrontendPort '443' -BackendPort '443' -IdleTimeoutInMinutes '15' -FrontendIpConfiguration $feip -BackendAddressPool $bepool -EnableTcpReset

## Create the load balancer resource
$loadbalancer = @{
    ResourceGroupName = $resourceGroupName
    Name = 'PrivateLinkServiceLB'
    Location = $region
    Sku = 'Standard'
    FrontendIpConfiguration = $feip
    BackendAddressPool = $bePool
    LoadBalancingRule = $rule
    Probe = $healthprobe
}
New-AzLoadBalancer @loadbalancer