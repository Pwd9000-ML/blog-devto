[CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'High')]
param(
    [Parameter(Mandatory)]
    [ValidatePattern('^[A-Za-z0-9_.-]+$')]
    [string]$Owner,

    [Parameter(Mandatory)]
    [ValidatePattern('^[A-Za-z0-9_.-]+$')]
    [string]$Repository,

    [Parameter(Mandatory)]
    [ValidateRange(1, [int]::MaxValue)]
    [int]$AlertNumber,

    [Parameter()]
    [string]$Token = $env:GITHUB_TOKEN
)

$apiVersion = '2026-03-10'
$assignee = 'copilot-swe-agent[bot]'
$ownerSegment = [Uri]::EscapeDataString($Owner)
$repositorySegment = [Uri]::EscapeDataString($Repository)
$uri = "https://api.github.com/repos/$ownerSegment/$repositorySegment/code-scanning/alerts/$AlertNumber"
$headers = @{
    Accept                 = 'application/vnd.github+json'
    Authorization          = "Bearer $Token"
    'X-GitHub-Api-Version' = $apiVersion
}
$body = @{ assignees = @($assignee) } | ConvertTo-Json -Compress
$target = "$Owner/$Repository code scanning alert #$AlertNumber"

if ($PSCmdlet.ShouldProcess($target, "Assign to $assignee")) {
    if ([string]::IsNullOrWhiteSpace($Token)) {
        throw 'Set GITHUB_TOKEN or pass -Token. The token must be authorised to update code scanning alerts.'
    }

    $response = Invoke-RestMethod -Method Patch -Uri $uri -Headers $headers -ContentType 'application/json' -Body $body -ErrorAction Stop

    [pscustomobject]@{
        AlertNumber = $response.number
        State       = $response.state
        Assignees   = @($response.assignees.login)
        Url         = $response.html_url
    }
}