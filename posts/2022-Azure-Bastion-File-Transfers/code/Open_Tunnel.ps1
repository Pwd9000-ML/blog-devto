#Login to Azure
az login
az account set --subscription "Your-Subscription-Id"

#Set Variables
$bastionName = "Pwd9000-EB-Bastion"
$bastionRG = "Pwd9000-EB-Network"
$targetVmResourceId = "/subscriptions/829efd7e-aa80-4c0d-9c1c-7aa2557f8e07/resourceGroups/Linux-Vms/providers/Microsoft.Compute/virtualMachines/mylinuxvm9000"

az network bastion tunnel --name $bastionName `
    --resource-group $bastionRG `
    --target-resource-id $targetVmResourceId `
    --resource-port "22" `
    --port "50022"