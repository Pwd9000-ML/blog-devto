# Login to Azure
az login

# Variables
$resourceGroup="<RGName>"
$keyVaultName="<KVName>"
$appName="<SPNAppName>"
$location="UKSouth"

#Create Resource Group and Key Vault
az group create --name $resourceGroup -l $location
az keyvault create --name $keyVaultName --resource-group $resourceGroup --location $location --enable-rbac-authorization

# Create Azure AD app
az ad app create --display-name $appName --homepage "http://localhost/$appName" 

# Get Azure AD app ID
$appId=$(az ad app list --display-name $appName --query [].appId -o tsv)

# Get Subscription ID where Key Vault Resides
$subscriptionId=$(az account show --query id -o tsv) # You can change this value to the subscription ID where the key vault resides

# Create Service Principal and assign to RBAC Role on Key Vault 
az ad sp create-for-rbac --name $appId `
    --role "Key Vault Secrets Officer" `
    --scopes /subscriptions/$subscriptionId/resourceGroups/$resourceGroup/providers/Microsoft.KeyVault/vaults/$keyVaultName `
    --sdk-auth

# Assign aditional RBAC role to Service Principal Subscription to manage Virtual machines 
az role assignment create --assignee "<ClientID from previous step>" `
    --role "Virtual Machine Contributor" `
    --subscription $subscriptionId