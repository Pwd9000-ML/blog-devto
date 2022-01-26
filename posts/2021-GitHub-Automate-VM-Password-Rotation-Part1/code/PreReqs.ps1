# Login to Azure
az login

# Variables
$subscriptionId=$(az account show --query id -o tsv)
$resourceGroup="<RGName>"
$keyVaultName="<KVName>"
$appName="<SPNAppName>"
$location="UKSouth"

#Create Resource Group and Key Vault
az group create --name $resourceGroup -l $location
az keyvault create --name $keyVaultName --resource-group $resourceGroup --location $location --enable-rbac-authorization

# Create AAD App and Service Principal and assign to RBAC Role on Key Vault 
az ad sp create-for-rbac --name $appName `
    --role "Key Vault Secrets Officer" `
    --scopes /subscriptions/$subscriptionId/resourceGroups/$resourceGroup/providers/Microsoft.KeyVault/vaults/$keyVaultName `
    --sdk-auth

# Assign additional RBAC role to Service Principal Subscription to manage Virtual machines 
az ad sp list --display-name $appName --query [].appId -o tsv | ForEach-Object {
    az role assignment create --assignee "$_" `
        --role "Virtual Machine Contributor" `
        --subscription $subscriptionId
    }

# Authorize the operation to create a few secrets - Signed in User (Key Vault Secrets Officer)
az ad signed-in-user show --query objectId -o tsv | foreach-object {
    az role assignment create `
        --role "Key Vault Secrets Officer" `
        --assignee "$_" `
        --scope "/subscriptions/$subscriptionId/resourceGroups/$resourceGroup/providers/Microsoft.KeyVault/vaults/$keyVaultName"
    }