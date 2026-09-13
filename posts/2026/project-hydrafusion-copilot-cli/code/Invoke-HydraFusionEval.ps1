<#
.SYNOPSIS
    Runs a small, repeatable evaluation of Copilot CLI model configurations
    (for example HydraFusion versus fixed models) on verifiable coding tasks.

.DESCRIPTION
    For each task, model identifier, and repetition, the script:
      1. Creates a fresh git worktree from the repository's current HEAD.
      2. Runs Copilot CLI non-interactively in autopilot style with a credit cap.
      3. Measures wall-clock time.
      4. Runs the task's deterministic check command in the worktree.
      5. Appends a result row to a CSV and keeps the raw JSONL output.

    Use only in a disposable repository. --yolo approves tool calls without
    prompting, so the agent can run commands and edit files freely.

    The script does not attempt to parse credit usage from the JSONL stream,
    because event field names are not documented and may change. Verify usage
    interactively with /usage or inspect the saved JSONL files.

.PARAMETER RepositoryPath
    Path to a git repository to evaluate against (disposable copy recommended).

.PARAMETER TasksPath
    JSON file containing an array of objects with id, prompt, and check fields.

.PARAMETER ModelIds
    Model identifiers passed to `copilot --model`. Supply the identifier shown by
    /model for HydraFusion; it is not documented for non-interactive use.

.PARAMETER Repetitions
    Number of runs per task and model. Default 1.

.PARAMETER MaxCreditsPerRun
    Value for `--max-ai-credits` on every run. Default 200 (about $2.00).

.PARAMETER OutputCsv
    CSV file to append results to.

.PARAMETER OutputDirectory
    Directory for raw JSONL output and worktrees. Default: ./hydrafusion-eval.

.EXAMPLE
    ./Invoke-HydraFusionEval.ps1 -RepositoryPath C:\src\eval-lab -TasksPath ./tasks.sample.json -ModelIds @('hydrafusion','claude-opus-5') -Repetitions 2 -OutputCsv ./results.csv
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string] $RepositoryPath,

    [Parameter(Mandatory)]
    [string] $TasksPath,

    [Parameter(Mandatory)]
    [string[]] $ModelIds,

    [ValidateRange(1, 10)]
    [int] $Repetitions = 1,

    [ValidateRange(1, 10000)]
    [int] $MaxCreditsPerRun = 200,

    [Parameter(Mandatory)]
    [string] $OutputCsv,

    [string] $OutputDirectory = './hydrafusion-eval'
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

New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
$OutputDirectory = (Resolve-Path $OutputDirectory).Path
$cliVersion = (& copilot version 2>&1 | Select-Object -First 1)

$results = [System.Collections.Generic.List[object]]::new()

foreach ($task in $tasks) {
    foreach ($modelId in $ModelIds) {
        for ($run = 1; $run -le $Repetitions; $run++) {
            $runId = '{0}__{1}__{2}' -f $task.id, ($modelId -replace '[^\w.-]', '_'), $run
            $worktree = Join-Path $OutputDirectory "wt-$runId"
            $jsonlPath = Join-Path $OutputDirectory "$runId.jsonl"

            Write-Host "==> $runId" -ForegroundColor Cyan

            if (Test-Path $worktree) {
                & git -C $RepositoryPath worktree remove --force $worktree | Out-Null
            }
            & git -C $RepositoryPath worktree add --detach $worktree HEAD | Out-Null

            $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
            $exitCode = -1
            try {
                Push-Location $worktree
                & copilot -p $task.prompt `
                    --model $modelId `
                    --yolo `
                    --max-ai-credits $MaxCreditsPerRun `
                    --output-format json `
                    --log-level none `
                    --no-color 2>&1 | Set-Content -Path $jsonlPath -Encoding utf8
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
                JsonlPath       = $jsonlPath
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
        [PSCustomObject]@{
            ModelId        = $_.Name
            Runs           = $_.Count
            PassRate       = if ($_.Count) { [math]::Round(100 * $passed / $_.Count, 1) } else { 0 }
            MedianSeconds  = if ($_.Count % 2) {
                $values = @($_.Group.WallSeconds | Sort-Object)
                $values[[int]($_.Count / 2)]
            } else {
                $values = @($_.Group.WallSeconds | Sort-Object)
                $middle = [int]($_.Count / 2)
                [math]::Round(($values[$middle - 1] + $values[$middle]) / 2, 1)
            }
        }
    } | Format-Table -AutoSize

Write-Host "Results appended to $OutputCsv. Raw JSONL and worktrees are under $OutputDirectory."
Write-Host 'Verify credit usage with /usage in an interactive session or from the JSONL files before comparing cost.'
