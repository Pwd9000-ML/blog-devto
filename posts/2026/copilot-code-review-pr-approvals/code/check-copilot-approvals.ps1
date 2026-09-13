<#
.SYNOPSIS
    Reports Copilot code review approval state for one or more pull requests.

.DESCRIPTION
    Uses the authenticated GitHub CLI (gh auth login) to read reviews and merge
    readiness for each pull request, then prints whether a review from
    copilot-pull-request-reviewer[bot] exists, its state, and whether GitHub
    currently reports the pull request as APPROVED or REVIEW_REQUIRED.

    Read-only. No personal access token is required or accepted; the script
    relies on the gh CLI's existing credentials.

.PARAMETER Repository
    Repository in OWNER/NAME form.

.PARAMETER PullRequest
    One or more pull request numbers.

.EXAMPLE
    ./check-copilot-approvals.ps1 -Repository acme/docs-lab -PullRequest 42, 43
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidatePattern('^[\w.-]+/[\w.-]+$')]
    [string] $Repository,

    [Parameter(Mandatory)]
    [int[]] $PullRequest
)

$ErrorActionPreference = 'Stop'

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw 'GitHub CLI (gh) is not installed or not on PATH.'
}

$copilotReviewer = 'copilot-pull-request-reviewer[bot]'

foreach ($number in $PullRequest) {
    $json = gh pr view $number --repo $Repository --json number,title,reviews,reviewDecision,mergeStateStatus,files
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Could not read PR #$number in $Repository."
        continue
    }

    $pr = $json | ConvertFrom-Json
    $copilotReviews = @($pr.reviews | Where-Object { $_.author.login -eq $copilotReviewer })
    $latestCopilot = $copilotReviews | Sort-Object submittedAt | Select-Object -Last 1

    [PSCustomObject]@{
        PullRequest      = $pr.number
        Title            = $pr.title
        ChangedFiles     = @($pr.files).Count
        CopilotReviews   = $copilotReviews.Count
        LatestCopilot    = if ($latestCopilot) { $latestCopilot.state } else { 'NONE' }
        ReviewDecision   = $pr.reviewDecision
        MergeStateStatus = $pr.mergeStateStatus
    }
}
