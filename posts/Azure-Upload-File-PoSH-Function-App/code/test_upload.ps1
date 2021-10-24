$fileToUpload = "C:\temp\hello-world.txt"

$functionUri = "https://storagefunc6190.azurewebsites.net/api/uploadfile"
$temp_token = "U7ztqa1nun0OtUssx0mpS/EnZ8j/fyiDdeOaVq8bzxZvh5gnI3eO1g=="

$fileName = Split-Path $fileToUpload -Leaf
$fileContent = [Convert]::ToBase64String((Get-Content -Path $fileToUpload -Encoding Byte))

$body = @{
    "fileName" = $fileName
    "fileContent" = $fileContent
} | ConvertTo-Json -Compress

$header = @{
    "x-functions-key" = $temp_token
    "Content-Type" = "application/json"
}

Invoke-RestMethod -Uri $functionUri -Method 'POST' -Body $body -Headers $header