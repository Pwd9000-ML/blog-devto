#Log into Azure
az login

# Setup Variables.
$randomInt = Get-Random -Maximum 9999
$subscriptionId = $(az account show --query id -o tsv)
$resourceGroupName = "GitHub-Managed-Function-Demo"
$storageName = "demofuncsa$randomInt"
$functionAppName = "demofunc$randomInt"
$region = "uksouth"

# Create a resource resourceGroupName
az group create --name "$resourceGroupName" --location "$region"

# Create an azure storage account for function app
az storage account create `
    --name "$storageName" `
    --location "$region" `
    --resource-group "$resourceGroupName" `
    --sku "Standard_LRS" `
    --kind "StorageV2" `
    --https-only true `
    --min-tls-version "TLS1_2"

# Create a Function App
az functionapp create `
    --name "$functionAppName" `
    --storage-account "$storageName" `
    --consumption-plan-location "$region" `
    --resource-group "$resourceGroupName" `
    --os-type "Windows" `
    --runtime "dotnet" `
    --runtime-version "6" `
    --functions-version "4" `
    --assign-identity