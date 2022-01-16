---
title: Upload Files to Azure Storage using a PowerShell Function App
published: true
description: Azure - Function App file uploader
tags: 'azurefunctions, azure, serverless, powershell'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Azure-Upload-File-PoSH-Function-App/assets/main-cover.png'
canonical_url: null
id: 874213
date: '2021-10-24T13:31:36Z'
---

## Overview

With Hacktoberfest 2021 coming to an end soon, I thought I would share with you a little experiment I did using an Azure serverless Function App with Powershell as the code base. The idea was to create an easy to use, reusable `File Uploader API` that would allow someone to upload a file to an Azure Storage Account blob container by posting a HTTP request.

The HTTP request would be a JSON body and only requires the file name and the file Content/data in a serialized Base64 string. The PowerShell Function App would then deserialize the base64 string into a temporary file, rename and copy the file as a blob into a storage account container called `fileuploads`.

## Set environment up automatically

To stage and setup the entire environment for my API automatically I wrote a PowerShell script using AZ CLI, that would build and configure all the things I would need to start work on my function. There was one manual step however I will cover a bit later on. But for now you can find the script I used on my [github code](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2021-Azure-Upload-File-PoSH-Function-App/code) page called `setup_environment.ps1`.

First we will log into Azure by running:

```powershell
az login
```

After logging into Azure and selecting the subscription, we can run the script that will create all the resources and set the environment up:

```powershell
# Setup Variables.
$randomInt = Get-Random -Maximum 9999
$subscriptionId = (get-azcontext).Subscription.Id
$resourceGroupName = "Function-App-Storage"
$storageName = "storagefuncsa$randomInt"
$functionAppName = "storagefunc$randomInt"
$region = "uksouth"
$secureStore = "securesa$randomInt"
$secureContainer = "fileuploads"

# Create a resource resourceGroupName
az group create --name "$resourceGroupName" --location "$region"

# Create an azure storage account for secure store (uploads)
az storage account create `
    --name "$secureStore" `
    --location "$region" `
    --resource-group "$resourceGroupName" `
    --sku "Standard_LRS" `
    --kind "StorageV2" `
    --https-only true `
    --min-tls-version "TLS1_2"

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
  "SEC_STOR_RGName=$resourceGroupName"
  "SEC_STOR_StorageAcc=$secureStore"
  "SEC_STOR_StorageCon=$secureContainer"
)

az functionapp config appsettings set `
    --name "$functionAppName" `
    --resource-group "$resourceGroupName" `
    --settings @settings

# Authorize the operation to create the container - Signed in User (Storage Blob Data Contributor Role)
az ad signed-in-user show --query objectId -o tsv | foreach-object {
    az role assignment create `
        --role "Storage Blob Data Contributor" `
        --assignee "$_" `
        --scope "/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.Storage/storageAccounts/$secureStore"
    }

#Create Upload container in secure store
Start-Sleep -s 30
az storage container create `
    --account-name "$secureStore" `
    --name "$secureContainer" `
    --auth-mode login

#Assign Function System MI permissions to Storage account(Read) and container(Write)
$functionMI = $(az resource list --name $functionAppName --query [*].identity.principalId --out tsv)| foreach-object {
    az role assignment create `
        --role "Reader and Data Access" `
        --assignee "$_" `
        --scope "/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.Storage/storageAccounts/$secureStore" `

    az role assignment create `
        --role "Storage Blob Data Contributor" `
        --assignee "$_" `
        --scope "/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.Storage/storageAccounts/$secureStore/blobServices/default/containers/$secureContainer"
    }
```

Lets take a closer look, step-by-step what the above script does as part of setting up the environment.

1. Create a resource group called `Function-App-Storage`. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Azure-Upload-File-PoSH-Function-App/assets/rg.png)
2. Create an azure storage account, `secure store` where file uploads will be kept. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Azure-Upload-File-PoSH-Function-App/assets/secsa.png)
3. Create an azure storage account for the function app. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Azure-Upload-File-PoSH-Function-App/assets/funcsa.png)
4. Create a PowerShell Function App with `SystemAssigned` managed identity, `consumption` app service plan and `insights`. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Azure-Upload-File-PoSH-Function-App/assets/func.png) ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Azure-Upload-File-PoSH-Function-App/assets/funcmi1.png)
5. Configure Function App environment variables. (Will be consumed inside of function app later). ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Azure-Upload-File-PoSH-Function-App/assets/funcappsettings1.png)
6. Create `fileuploads` container in secure store storage account. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Azure-Upload-File-PoSH-Function-App/assets/sacontainer1.png)
7. Assign Function App `SystemAssigned` managed identity permissions to Storage account(Read) and container(Write). ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Azure-Upload-File-PoSH-Function-App/assets/sarbac1.png) ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Azure-Upload-File-PoSH-Function-App/assets/conrbac.png)
8. Remember I mentioned earlier there is one manual step. In the next step we will change the `requirements.psd1` file on our function to allow the `AZ` module inside of our function by uncommenting the following: ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Azure-Upload-File-PoSH-Function-App/assets/manual1.png)

**NOTE:** Remember to save the manual change we made on `requirements.psd1` above. That is it, our environment is set up and in the next section we will configure the file uploader function API powershell code.

## File Uploader Function

The following function app code can also be found under my [github code](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2021-Azure-Upload-File-PoSH-Function-App/code) page called `run.ps1`.

1. Navigate to the function app we created in the previous section and select `+ Create` under `Functions`. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Azure-Upload-File-PoSH-Function-App/assets/createfunc.png)
2. Select `Develop in portal` and for the template select `HTTP trigger`, name the function `uploadfile` and hit `Create`. ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Azure-Upload-File-PoSH-Function-App/assets/createfunc2.png)
3. Navigate to `Code + Test` and replace all the code under `run.ps1` with the following powershell code and hit `save`: ![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Azure-Upload-File-PoSH-Function-App/assets/createfunc3.png)

```powershell
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
```

Lets take a closer look at what this code actually does. In the first few lines we can see that the function app will take a `request` input parameter called `$request`. This parameter will be our main input and request body JSON object. We will use the JSON body to send details into our API about the file we want to upload. We also set a status and some variables.

Here is an example of a valid JSON request body for our function app:

```JSON
//JSON request Body Example
{
    "fileName":  "hello-world.txt",
    "fileContent":  "VXBsb2FkIHRoaXMgZmlsZSB0byBBenVyZSBjbG91ZCBzdG9yYWdlIHVzaW5nIEZ1bmN0aW9uIEFwcCBGaWxlIHVwbG9hZGVyIEFQSQ=="
}
```

Note that our `$Request` input parameter is linked to `$Request.body`, and we set two variables that will be taken from the JSON request body namely, `fileName` and `fileContent`. We will use these two values from the incoming POST request to store the serialized file content (Base64String) in a variable called `$fileContent` and the blob name in a variable called `$fileName`.

**NOTE:** Remember in the previous section `step 5` we set up some environment variables on our function app settings, we can reference these environment variables values in our function code with `$env:appSettingsKey` as show below):

```powershell
#// code/run.ps1#L1-L22
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

#Set Vars (From JSON request Body):
$fileName = $Request.Body["fileName"]
$fileContent = $Request.Body["fileContent"]
Write-Host "============================================"
Write-Host "Please wait, uploading new blob: [$fileName]"
Write-Host "============================================"
```

Next we have a `try/catch` block where we take the serialized `Base64 String` from the JSON request body `fileContent` stored in the PowerShell variable `$fileContent` and try to deserialize it into a temporary file:

```powershell
#// code/run.ps1#L25-L33
try {
    $bytes = [Convert]::FromBase64String($fileContent)
    $tempFile = New-TemporaryFile
    [io.file]::WriteAllBytes($tempFile, $bytes)
}
catch {
    $statusGood = $false
    $body = "FAIL: Failed to receive file data."
}
```

Then we have an `if statement` with a `try/catch` block where we take the deserialized temp file from the previous step and rename and save the file into our `fileuploads` container using the `$fileName` variable which takes the `fileName` value from our JSON request body. Because our function apps managed identity has been given permission against the container using RBAC earlier when we set up the environment, we should have no problems here:

```powershell
#// code/run.ps1#L36-L48
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
```

Finally in the last few lines, given our status is still good, we return a message body to the user to say that the file has been uploaded successfully.

```powershell
#// code/run.ps1#L50-L62
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
```

## Testing the function app

Lets test our function app and see if it does what it says on the tin.

Before we test the function lets create a new temporary function key to test with. Navigate to the function app function and select `Function Keys`. Create a `+ New function key` and call the key `temp_token` (Make a note of the token as we will use it in the test script):

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Azure-Upload-File-PoSH-Function-App/assets/token.png)

Also make a note of the Function App URL. If you followed this tutorial it would be: `https://<FunctionAppName>.azurewebsites.net/api/uploadfile`. Or you can also get this under `Code + Test` and selecting `Get function URL` and drop down using the key: `temp_token`:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Azure-Upload-File-PoSH-Function-App/assets/funcurl.png)

I have created the following powershell script to test the file uploader API. The following test script can be found under my [github code](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2021-Azure-Upload-File-PoSH-Function-App/code) page called `test_upload.ps1`.

```powershell
#File and path to upload
$fileToUpload = "C:\temp\hello-world.txt"

#Set variables for Function App (URI + Token)
$functionUri = "https://<functionAppname>.azurewebsites.net/api/uploadfile"
$temp_token = "<TokenSecretValue>"

#Set fileName and serialize file content for JSON body
$fileName = Split-Path $fileToUpload -Leaf
$fileContent = [Convert]::ToBase64String((Get-Content -Path $fileToUpload -Encoding Byte))

#Create JSON body
$body = @{
    "fileName" = $fileName
    "fileContent" = $fileContent
} | ConvertTo-Json -Compress

#Create Header
$header = @{
    "x-functions-key" = $temp_token
    "Content-Type" = "application/json"
}

#Trigger Function App API
Invoke-RestMethod -Uri $functionUri -Method 'POST' -Body $body -Headers $header
```

Lets try it out with a txt file:

![image.gif](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Azure-Upload-File-PoSH-Function-App/assets/txtupload01.gif)

Lets do another test but with an image file this time:

![image.gif](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Azure-Upload-File-PoSH-Function-App/assets/pngupload04.gif)

**NOTE:** Ensure to keep your function app tokens safe. (You can delete your `temp_token` after testing).

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my [Github](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2021-Azure-Upload-File-PoSH-Function-App/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}
