#vars (APIM private IP after APIM created under $apimPrivateIP)
$port = '443'
$localaddress = (Get-NetIPConfiguration | Where-Object {$_.ipv4defaultgateway -ne $null}).IPv4Address.ipaddress
$apimPrivateIP = '10.0.2.5'

#Enable Port Forwarding on VM. 
#Enable IP forwarding on Azure for the VM's #network interface as well.
Set-ItemProperty -Path HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters -Name IpEnableRouter -Value 1
 
#Allow HTTPS(443) traffic inbound
New-NetFirewallRule -DisplayName "HTTPS-443-Inbound" -Direction Inbound -Action Allow -Protocol TCP -LocalPort $port

#Enable port 443 listener and forward
netsh interface portproxy add v4tov4 listenport=$port listenaddress=$localaddress connectport=$port connectaddress=$apimPrivateIP
