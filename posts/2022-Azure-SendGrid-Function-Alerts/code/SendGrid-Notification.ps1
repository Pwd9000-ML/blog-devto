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