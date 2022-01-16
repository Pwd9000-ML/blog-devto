using namespace System.Net

# Input bindings are passed in via param block.
param($Request, $TriggerMetadata)

# Write to the Azure Functions log stream.
Write-Host "POST request - File Upload triggered."

#Set Status
$statusGood = $true

#Set Vars (Func App Env Settings):
$resourceGroupName = $env:SEC_STOR_RGName
$storageAccountName =  $env:SEC_STOR_StorageAcc
$blobContainer = $env:SEC_STOR_StorageCon

#Set Vars (From request Body):
$fileName = $Request.Body["fileName"]
$fileContent = $Request.Body["fileContent"]
Write-Host "============================================"
Write-Host "Please wait, uploading new blob: [$fileName]"
Write-Host "============================================"

#Construct temp file from fileContent (Base64String)
try {
    $bytes = [Convert]::FromBase64String($fileContent)
    $tempFile = New-TemporaryFile
    [io.file]::WriteAllBytes($tempFile, $bytes)
}
catch {
    $statusGood = $false
    $body = "FAIL: Failed to receive file data."
}

#Get secureStore details and upload blob.
If ($tempFile) {
    try {
        $storageAccount = Get-AzStorageAccount -ResourceGroupName $resourceGroupName -Name $storageAccountName
        $storageContext = $storageAccount.Context
        $container = (Get-AzStorageContainer -Name $blobContainer -Context $storageContext).CloudBlobContainer

        Set-AzStorageBlobContent -File $tempFile -Blob $fileName -Container $container.Name -Context $storageContext
    }
    catch {
        $statusGood = $false
        $body = "FAIL: Failure connecting to Azure blob container: [$($container.Name)], $_"
    }
}

if(!$statusGood) {
    $status = [HttpStatusCode]::BadRequest
}
else {
    $status = [HttpStatusCode]::OK
    $body = "SUCCESS: File [$fileName] Uploaded OK to Secure Store container [$($container.Name)]"
}

# Associate values to output bindings by calling 'Push-OutputBinding'.
Push-OutputBinding -Name Response -Value ([HttpResponseContext]@{
    StatusCode = $status
    Body = $body
})