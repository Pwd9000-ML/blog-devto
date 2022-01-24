az login

#Set variables
$randomInt = Get-Random -Maximum 9999
$subscriptionId = $(az account show --query "id" --output tsv)
$resourceGroupName = "Actions-Service-Bus-Demo"
$location = "UKSouth"
$keyVaultName = "secrets-vault$randomInt"
$nameSpaceName = "githubactions"
$queueName = "queue01"
$policyName = "myauthrule"
$currentUser = $(az ad signed-in-user show --query "objectId" --output tsv)

#Create ResourceGroup and Key Vault
az group create --name $resourceGroupName -l $location
az keyvault create --name $keyVaultName --resource-group $resourceGroupName --location $location --enable-rbac-authorization

#Grant Key Vault Creator/Current User [Key Vault Secrets Officer]
az role assignment create --assignee-object-id "$currentUser" `
    --role "Key Vault Secrets Officer" `
    --scope "/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.KeyVault/vaults/$keyVaultName" `
    --assignee-principal-type "User"

#Create Service Bus and Queue (and policy with Send and Listen rights)
az servicebus namespace create --resource-group $resourceGroupName --name $nameSpaceName --location $location --sku "Basic"
az servicebus queue create --resource-group $resourceGroupName --namespace-name $nameSpaceName --name $queueName
az servicebus namespace authorization-rule create --resource-group $resourceGroupName --namespace-name $nameSpaceName --name $policyName --rights "Send" "Listen"

#Retrieve and save primary key of new policy to key vault (will be used later as a GH Secret in GH workflow)
$policyPrimaryKey = az servicebus namespace authorization-rule keys list --resource-group $resourceGroupName --namespace-name $nameSpaceName --name $policyName --query "primaryKey" --output tsv
az keyvault secret set --vault-name $keyVaultName --name "$($policyName)PrimaryKey" --value $policyPrimaryKey

# a name for our azure ad app
$appName="gitHubActionsVaultUser"

#Create azure ad app & Service Principal to be used as GH Secret credential to authenticate to Azure (Make note of JSON output on this step)
az ad sp create-for-rbac --name $appName `
    --role "Key Vault Secrets Officer" `
    --scopes "/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.KeyVault/vaults/$keyVaultName" `
    --sdk-auth