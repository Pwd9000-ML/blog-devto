<#
.SYNOPSIS
    Runs a small, repeatable evaluation of Copilot CLI model configurations
    (for example HydraFusion versus fixed models) on verifiable coding tasks.

.DESCRIPTION
    For each task, model identifier, and repetition, the script:
      1. Creates a fresh git worktree from the repository's current HEAD.
      2. Runs Copilot CLI non-interactively with full permissions and a credit cap.
      3. Measures wall-clock time.
      4. Runs the task's deterministic check command in the worktree.
      5. Reads AI credits and the models used from --usage-output-file.
      6. For HydraFusion runs, reads the execution pattern from the JSONL stream.
      7. Appends a result row to a CSV and keeps the raw JSONL and usage files.

    Use only in a disposable repository. --yolo approves tool calls without
    prompting, so the agent can run commands and edit files freely.

    Credits are calculated as totalNanoAiu / 1e9 from the usage file, which
    matched GitHub's published per-token rates when tested with Copilot CLI
    1.0.89. The HydraFusion pattern comes from session.fusion_completed events
    in the JSONL output. Neither schema is documented, so the script tolerates
    missing fields and leaves those columns empty rather than guessing.

.PARAMETER RepositoryPath
    Path to a git repository to evaluate against (disposable copy recommended).

.PARAMETER TasksPath
    JSON file containing an array of objects with id, prompt, and check fields.

.PARAMETER ModelIds
    Model identifiers passed to `copilot --model`. GitHub documents
    `hydrafusion` as the identifier for HydraFusion in non-interactive use.

.PARAMETER ExperimentalModelIds
    Model identifiers that need `--experimental`. Default: hydrafusion. Fixed
    model baselines run without experimental features.

.PARAMETER Repetitions
    Number of runs per task and model. Default 1.

.PARAMETER MaxCreditsPerRun
    Value for `--max-ai-credits` on every run. Default 200 (about $2.00).
    Copilot CLI rejects values below 30.

.PARAMETER OutputCsv
    CSV file to append results to.

.PARAMETER OutputDirectory
    Directory for raw JSONL output, usage files, and worktrees.
    Default: ./hydrafusion-eval.

.PARAMETER TrustTaskFile
    Required when the task file contains check commands, because each check is
    executed as PowerShell in the disposable worktree.

.EXAMPLE
    ./Invoke-HydraFusionEval.ps1 -RepositoryPath C:\src\eval-lab -TasksPath ./tasks.sample.json -ModelIds @('hydrafusion','claude-opus-5') -Repetitions 2 -OutputCsv ./results.csv -TrustTaskFile
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string] $RepositoryPath,

    [Parameter(Mandatory)]
    [string] $TasksPath,

    [Parameter(Mandatory)]
    [string[]] $ModelIds,

    [string[]] $ExperimentalModelIds = @('hydrafusion'),

    [ValidateRange(1, 10)]
    [int] $Repetitions = 1,

    [ValidateRange(30, 10000)]
    [int] $MaxCreditsPerRun = 200,

    [Parameter(Mandatory)]
    [string] $OutputCsv,

    [string] $OutputDirectory = './hydrafusion-eval',

    [switch] $TrustTaskFile
)

$ErrorActionPreference = 'Stop'

foreach ($tool in @('git', 'copilot')) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
        throw "$tool is not installed or not on PATH."
    }
}

$RepositoryPath = (Resolve-Path $RepositoryPath).Path
$tasks = Get-Content -Raw -Path $TasksPath | ConvertFrom-Json
if (-not $tasks -or $tasks.Count -eq 0) { throw "No tasks found in $TasksPath." }
$tasksWithChecks = @($tasks | Where-Object { $_.check })
if ($tasksWithChecks.Count -gt 0) {
    if (-not $TrustTaskFile) {
        throw "Task checks from $TasksPath are executed as PowerShell in the disposable worktree. Re-run with -TrustTaskFile only for a trusted task file."
    }

    Write-Warning "Task checks from $TasksPath are executed as PowerShell in the disposable worktree. Use only a trusted task file."
}

New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
$OutputDirectory = (Resolve-Path $OutputDirectory).Path
$cliVersion = (& copilot version 2>&1 | Select-Object -First 1)
& git -C $RepositoryPath worktree prune

$results = [System.Collections.Generic.List[object]]::new()

function Get-Median {
    param([double[]] $Values)
    $sorted = @($Values | Sort-Object)
    if ($sorted.Count -eq 0) { return $null }
    $middle = [int][math]::Floor($sorted.Count / 2)
    if ($sorted.Count % 2) { return $sorted[$middle] }
    return [math]::Round(($sorted[$middle - 1] + $sorted[$middle]) / 2, 2)
}

foreach ($task in $tasks) {
    foreach ($modelId in $ModelIds) {
        for ($run = 1; $run -le $Repetitions; $run++) {
            $runId = '{0}__{1}__{2}' -f $task.id, ($modelId -replace '[^\w.-]', '_'), $run
            $worktree = Join-Path $OutputDirectory "wt-$runId"
            $jsonlPath = Join-Path $OutputDirectory "$runId.jsonl"
            $usagePath = Join-Path $OutputDirectory "$runId.usage.json"

            Write-Host "==> $runId" -ForegroundColor Cyan

            if (Test-Path $worktree) {
                & git -C $RepositoryPath worktree remove --force $worktree | Out-Null
            }
            if (Test-Path $usagePath) { Remove-Item $usagePath -Force }
            & git -C $RepositoryPath worktree add --detach $worktree HEAD | Out-Null
            if ($LASTEXITCODE -ne 0) { throw "Could not create worktree $worktree." }

            $copilotArgs = @(
                '-p', $task.prompt,
                '--model', $modelId,
                '--yolo',
                '--no-ask-user',
                '--max-ai-credits', $MaxCreditsPerRun,
                '--usage-output-file', $usagePath,
                '--output-format', 'json',
                '--log-level', 'none',
                '--no-color'
            )
            if ($ExperimentalModelIds -contains $modelId) {
                $copilotArgs = @('--experimental') + $copilotArgs
            }

            $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
            $exitCode = -1
            try {
                Push-Location $worktree
                & copilot @copilotArgs 2>&1 | Set-Content -Path $jsonlPath -Encoding utf8
                $exitCode = $LASTEXITCODE
            } catch {
                Write-Warning "Copilot run failed for ${runId}: $($_.Exception.Message)"
            } finally {
                Pop-Location
            }
            $stopwatch.Stop()

            $checkPassed = $false
            $checkOutput = ''
            if ($task.check) {
                try {
                    Push-Location $worktree
                    # Check commands must be native executables so the exit code is meaningful.
                    $global:LASTEXITCODE = 0
                    $checkOutput = (Invoke-Expression $task.check 2>&1 | Out-String)
                    $checkPassed = ($exitCode -eq 0 -and $LASTEXITCODE -eq 0)
                } catch {
                    $checkOutput = $_.Exception.Message
                } finally {
                    Pop-Location
                }
            }

            $changedFiles = @(& git -C $worktree status --porcelain).Count

            $credits = $null
            $modelsUsed = ''
            if (Test-Path $usagePath) {
                try {
                    $usage = Get-Content -Raw -Path $usagePath | ConvertFrom-Json
                    if ($null -ne $usage.totalNanoAiu) {
                        $credits = [math]::Round([double]$usage.totalNanoAiu / 1e9, 2)
                    }
                    if ($usage.modelMetrics) {
                        $modelsUsed = (@($usage.modelMetrics.PSObject.Properties.Name) | Sort-Object) -join ';'
                    }
                } catch {
                    Write-Warning "Could not read usage file for ${runId}: $($_.Exception.Message)"
                }
            }

            # session.fusion_completed is undocumented; record what is present and nothing else.
            $patterns = [System.Collections.Generic.List[string]]::new()
            $outcomes = [System.Collections.Generic.List[string]]::new()
            if (Test-Path $jsonlPath) {
                foreach ($line in Get-Content -Path $jsonlPath) {
                    if ($line -notmatch '"type"\s*:\s*"session\.fusion_completed"') { continue }
                    try {
                        $fusionEvent = $line | ConvertFrom-Json
                        if ($fusionEvent.data.pattern) { $patterns.Add([string]$fusionEvent.data.pattern) }
                        if ($fusionEvent.data.outcome) { $outcomes.Add([string]$fusionEvent.data.outcome) }
                    } catch {
                        continue
                    }
                }
            }

            $row = [PSCustomObject]@{
                Timestamp       = (Get-Date).ToString('o')
                CliVersion      = $cliVersion
                TaskId          = $task.id
                ModelId         = $modelId
                Run             = $run
                CopilotExitCode = $exitCode
                WallSeconds     = [math]::Round($stopwatch.Elapsed.TotalSeconds, 1)
                CheckPassed     = $checkPassed
                ChangedFiles    = $changedFiles
                Credits         = $credits
                ModelsUsed      = $modelsUsed
                FusionPatterns  = (@($patterns | Select-Object -Unique)) -join ';'
                FusionOutcomes  = (@($outcomes | Select-Object -Unique)) -join ';'
                JsonlPath       = $jsonlPath
                UsagePath       = $usagePath
            }
            $results.Add($row)
            $row | Export-Csv -Path $OutputCsv -Append -NoTypeInformation

            if (-not $checkPassed -and $checkOutput) {
                Set-Content -Path (Join-Path $OutputDirectory "$runId.check.txt") -Value $checkOutput
            }
        }
    }
}

Write-Host ''
$results |
    Group-Object ModelId |
    ForEach-Object {
        $passed = @($_.Group | Where-Object CheckPassed).Count
        $creditValues = @($_.Group | Where-Object { $null -ne $_.Credits } | ForEach-Object { [double]$_.Credits })
        $totalCredits = ($creditValues | Measure-Object -Sum).Sum
        [PSCustomObject]@{
            ModelId        = $_.Name
            Runs           = $_.Count
            PassRate       = if ($_.Count) { [math]::Round(100 * $passed / $_.Count, 1) } else { 0 }
            MedianSeconds  = Get-Median -Values @($_.Group.WallSeconds)
            MedianCredits  = Get-Median -Values $creditValues
            CreditsPerPass = if ($passed -and $creditValues.Count -eq $_.Count) { [math]::Round($totalCredits / $passed, 2) } else { $null }
            Patterns       = (@($_.Group.FusionPatterns | Where-Object { $_ } | ForEach-Object { $_ -split ';' } | Group-Object | ForEach-Object { '{0}={1}' -f $_.Name, $_.Count })) -join ' '
        }
    } | Format-Table -AutoSize

Write-Host "Results appended to $OutputCsv. Raw JSONL, usage files, and worktrees are under $OutputDirectory."
Write-Host 'Spot-check Credits against /usage or your billing report before you compare cost.'
