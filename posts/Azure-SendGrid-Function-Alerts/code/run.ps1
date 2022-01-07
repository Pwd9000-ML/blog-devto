# Input bindings are passed in via param block.
param($Timer)

# Get the current universal time in the default string format.
$currentUTCtime = (Get-Date).ToUniversalTime()

# The 'IsPastDue' property is 'true' when the current function invocation is later than scheduled.
if ($Timer.IsPastDue) {
    Write-Host "PowerShell timer is running late!"
}

# SendGrid-Notification Function #
Function SendGrid-Notification {
    [CmdletBinding(SupportsShouldProcess)]
    Param(
        [Parameter(Mandatory, ValueFromPipeline)]
        [String]$ToAddress,
        [Parameter(Mandatory, ValueFromPipeline)]
        [String]$FromAddress,
        [Parameter(Mandatory, ValueFromPipeline)]
        [String]$Subject,
        [Parameter(Mandatory, ValueFromPipeline)]
        [String]$Body,
        [Parameter(Mandatory, ValueFromPipeline)]
        [String]$APIKey
    )

    # Body 
    $SendGridBody = @{
        "personalizations" = @(
            @{
                "to"      = @(
                    @{
                        "email" = $ToAddress
                    }
                )
                "subject" = $Subject
            }
        )

        "content"          = @(
            @{
                "type"  = "text/html"
                "value" = $Body
            }
        )

        "from"             = @{
            "email" = $FromAddress
        }
    }

    $BodyJson = $SendGridBody | ConvertTo-Json -Depth 4

    #Header for SendGrid API
    $Header = @{
        "authorization" = "Bearer $APIKey"
    }

    #Send the email through SendGrid API
    $Parameters = @{
        Method      = "POST"
        Uri         = "https://api.sendgrid.com/v3/mail/send"
        Headers     = $Header
        ContentType = "application/json"
        Body        = $BodyJson
    }
    Invoke-RestMethod @Parameters
}

# Set these environment variables up in Function App settings:
# These variables are from the Function App and is referenced from Key Vault
$apiKey = $env:sendGridApiKey #SendGrid API Key
$from = $env:fromAddress #SendGrid Sender Address

#Set additional Function variables
$to = "pwd9000@hotmail.co.uk"
$subscriptionName = (get-azcontext).Subscription.name
$subscriptionId = (get-azcontext).Subscription.Id

Write-Error "This is a forced error, something has failed, Please investigate xxxx"
$failureMessage = $error[0].Exception.message.ToString()

$body = "$failureMessage - Subscruption Details: [Name: $subscriptionName, Id: $subscriptionId ]"

$Parameters = @{
    ToAddress   = "$to"
    FromAddress = "$from"
    Subject     = "Error notification from Azure Function App via SendGrid API"
    Body        = "$body"
    APIKey      = "$apiKey"
}
SendGrid-Notification @Parameters