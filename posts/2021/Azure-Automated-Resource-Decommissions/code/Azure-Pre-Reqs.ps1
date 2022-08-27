#Log into Azure
#az login

# Setup Variables.
$randomInt = Get-Random -Maximum 9999
$subscriptionId=$(az account show --query id -o tsv)
$resourceGroupName = "Automated-Resource-Decommissioning"
$storageName = "decomfuncsa$randomInt"
$tableName = "Tracker"
$tablePartition = "Decommissioned"
$functionAppName = "decomfunc$randomInt"
$region = "uksouth"
$scopes = "$subscriptionId" #Array of Subscriptions that will be covered by automate decommissioning e.g: "$subscriptionId1, $subscriptionId2"

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
    --runtime "powershell" `
    --runtime-version "7.0" `
    --functions-version "3" `
    --assign-identity

#Configure Function App environment variables:
$settings = @(
  "Function_Scopes=$scopes"  
  "Function_RGName=$resourceGroupName"
  "Function_SaActName=$storageName"
  "Function_TableName=$tableName"
  "Function_TablePartition=$tablePartition"
)

$settings | foreach-object {
    az functionapp config appsettings set --name "$functionAppName" --resource-group "$resourceGroupName" --settings """$_"""
}

# Authorize the operation to create the tracker table - Signed in User
az ad signed-in-user show --query id -o tsv | foreach-object {
    az role assignment create `
        --role "Reader and Data Access" `
        --assignee "$_" `
        --scope "/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.Storage/storageAccounts/$storageName"

    az role assignment create `
        --role "Storage Table Data Contributor" `
        --assignee "$_" `
        --scope "/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.Storage/storageAccounts/$storageName"
    }

#Create Tracker Table in Function storage acc
Start-Sleep -s 15
$storageKey = az storage account keys list -g $resourceGroupName -n $storageName --query [0].value -o tsv
az storage table create `
    --account-name "$storageName" `
    --account-key "$storageKey" `
    --name "$tableName"

#Create Table in Function storage to track failed decommissions
az storage table create `
    --account-name "$storageName" `
    --account-key "$storageKey" `
    --name "Failed"

#Assign Function System MI permissions to Storage account(Read) and table(Write) and contributor to subscription to be able to do decommissions
$functionMI = $(az resource list --name $functionAppName --query [*].identity.principalId --out tsv)| foreach-object {
    az role assignment create `
        --role "Reader and Data Access" `
        --assignee "$_" `
        --scope "/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.Storage/storageAccounts/$storageName"

    az role assignment create `
        --role "Storage Table Data Contributor" `
        --assignee "$_" `
        --scope "/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.Storage/storageAccounts/$storageName"

    az role assignment create `
        --role "Contributor" `
        --assignee "$_" `
        --subscription "$subscriptionId"
    }