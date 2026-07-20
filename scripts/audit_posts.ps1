#!/usr/bin/env pwsh
# Audit new or explicitly selected blog posts for publishing consistency.
[CmdletBinding()]
param(
    [string[]]$Path,
    [switch]$ChangedOnly,
    [string]$BaseRef = 'HEAD',
    [switch]$FailOnIssues
)

Set-StrictMode -Version Latest

$root = Split-Path $PSScriptRoot -Parent
Set-Location $root

function Get-PostFiles {
    param([string[]]$RequestedPath)

    if ($RequestedPath) {
        return @($RequestedPath | ForEach-Object {
            Get-Item -Path $_ -ErrorAction Stop
        } | Where-Object { $_.Extension -eq '.md' })
    }

    return @(Get-ChildItem -Path "posts" -Recurse -Filter "*.md" | Where-Object {
        $_.FullName -notmatch '\\code\\' -and $_.Name -ne 'README.md' -and $_.Name -ne 'example_README.md'
    })
}

$posts = @(Get-PostFiles -RequestedPath $Path | Sort-Object FullName)

if ($ChangedOnly) {
    $changed = if ($BaseRef -eq 'HEAD') {
        git diff --name-only --diff-filter=ACMR HEAD -- 'posts/**/*.md'
    } else {
        git diff --name-only --diff-filter=ACMR "$BaseRef...HEAD" -- 'posts/**/*.md'
    }
    $posts = @($posts | Where-Object {
        $relativePath = $_.FullName.Replace("$root\", '').Replace('\', '/')
        $changed -contains $relativePath
    })
}

$results = @()

foreach ($post in $posts) {
    $content = Get-Content $post.FullName -Raw -Encoding UTF8
    $relPath = $post.FullName.Replace("$root\", "").Replace("\", "/")
    $folder = Split-Path (Split-Path $post.FullName -Parent) -Leaf
    $fileName = [System.IO.Path]::GetFileNameWithoutExtension($post.Name)
    
    $issues = [System.Collections.ArrayList]::new()
    $fm = ''

    # --- FRONT MATTER ---
    if ($content -match '(?s)^---\r?\n(.*?)\r?\n---') {
        $fm = $matches[1]
        
        # Required front matter and description length.
        foreach ($field in @('title', 'published', 'description', 'tags', 'cover_image', 'canonical_url', 'id', 'series', 'date')) {
            if ($fm -notmatch "(?m)^${field}:\s*") {
                [void]$issues.Add("FM: missing $field field")
            }
        }

        $descLen = 0
        if ($fm -match "description:\s*'([^']*)'") { $descLen = $matches[1].Length }
        elseif ($fm -match 'description:\s*"([^"]*)"') { $descLen = $matches[1].Length }
        elseif ($fm -match 'description:\s+([^\r\n]+)') { $descLen = $matches[1].Trim().Trim("'`"").Length }
        if ($descLen -gt 150) { [void]$issues.Add("FM: description too long ($descLen chars, max 150)") }
        if ($fm -notmatch "(?m)^description:\s*'[^']*'$" ) { [void]$issues.Add("FM: description not single-quoted") }

        if ($fm -notmatch "(?m)^published:\s*(true|false)$") { [void]$issues.Add("FM: published must be true or false") }
        if ($fm -match "(?m)^date:\s*'([^']+)'" -and $matches[1] -notmatch '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$') {
            [void]$issues.Add("FM: date is not ISO 8601 UTC")
        }

        # Cover image URL variant
        if ($fm -match 'cover_image:.*refs/heads/main') {
            [void]$issues.Add("FM: cover_image uses refs/heads/main variant (should use /main/posts/...)")
        }
        if ($fm -notmatch 'cover_image:') {
            [void]$issues.Add("FM: cover_image field missing")
        }

        # Cover filename
        if ($fm -match 'cover_image:.*?/assets/([^''"\s]+)') {
            $coverFile = $matches[1].TrimEnd("'", '"')
            if ($coverFile -ne "main.png") {
                [void]$issues.Add("FM: cover filename is '$coverFile' (convention: main.png)")
            }
        }

        # Tags count
        if ($fm -match "tags:\s*'([^']*)'") {
            $tagCount = ($matches[1] -split ',').Count
            if ($tagCount -gt 4) { [void]$issues.Add("FM: too many tags ($tagCount, max 4)") }
        }

        if ($fm -match "(?m)^tags:\s*'([^']*)'") {
            $tags = @($matches[1] -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ })
            if ($tags.Count -eq 0) { [void]$issues.Add("FM: tags must contain at least one tag") }
        }
    } else {
        [void]$issues.Add("FM: no front matter found")
    }

    # --- ASSETS AND LINKS ---
    if ($fm -match "cover_image:\s*'([^']+)'") {
        $coverUrl = $matches[1]
        if ($coverUrl -match '/assets/([^/]+)$') {
            $coverPath = Join-Path $post.DirectoryName "assets\$($matches[1])"
            if (-not (Test-Path $coverPath)) {
                [void]$issues.Add("ASSET: cover file does not exist: $($matches[1])")
            } elseif ($matches[1] -eq 'main.png') {
                try {
                    $bytes = [System.IO.File]::ReadAllBytes($coverPath)
                    if ($bytes.Length -lt 24 -or $bytes[0] -ne 137 -or $bytes[1] -ne 80 -or $bytes[2] -ne 78 -or $bytes[3] -ne 71) {
                        throw 'Not a PNG file'
                    }
                    $width = [System.BitConverter]::ToUInt32(@($bytes[19], $bytes[18], $bytes[17], $bytes[16]), 0)
                    $height = [System.BitConverter]::ToUInt32(@($bytes[23], $bytes[22], $bytes[21], $bytes[20]), 0)
                    if ($width -ne 1000 -or $height -ne 420) {
                        [void]$issues.Add("ASSET: main.png is ${width}x${height}, expected 1000x420")
                    }
                } catch {
                    [void]$issues.Add("ASSET: could not inspect PNG cover dimensions")
                }
            }
        }
    }

    foreach ($placeholder in @('TODO:', 'YYYY', 'DD-MM-YYYY')) {
        if ($content -match [regex]::Escape($placeholder)) {
            [void]$issues.Add("CONTENT: placeholder remains: $placeholder")
        }
    }

    foreach ($match in [regex]::Matches($content, '!\[[^]]*\]\(([^)]+)\)')) {
        $imageReference = $match.Groups[1].Value
        if ($imageReference -notmatch '^https?://') {
            $imagePath = Join-Path $post.DirectoryName $imageReference
            if (-not (Test-Path $imagePath)) { [void]$issues.Add("LINK: image does not exist: $imageReference") }
        }
    }

    # --- FILENAME vs FOLDER ---
    if ($fileName -cne $folder -and $fileName -ne "index") {
        [void]$issues.Add("NAMING: filename '$($post.Name)' does not match folder '$folder'")
    }

    # --- FOOTER ---
    # Check LinkedIn URL
    if ($content -match 'linkedin\.com/in/marcel-l-61b0a96b') {
        [void]$issues.Add("FOOTER: old LinkedIn URL /in/marcel-l-61b0a96b/ (should be /in/marcel-pwd9000/)")
    }
    if ($content -match 'linkedin\.com/in/marcel-pwd9000//') {
        [void]$issues.Add("FOOTER: double trailing slash in LinkedIn URL")
    }

    # Check footer presence
    if ($content -notmatch '\{%\s*user\s+pwd9000\s*%\}') {
        [void]$issues.Add("FOOTER: missing {% user pwd9000 %} tag")
    }

    if ($content -notmatch ':octopus:\s*\[GitHub\].*:penguin:\s*\[X\].*:space_invader:\s*\[LinkedIn\]') {
        [void]$issues.Add("FOOTER: social links block is missing or incomplete")
    }

    # Check Date line
    if ($content -match 'Date:\s*(\d{2}-\d{2}-\d{4})') {
        # good format
    } elseif ($content -match 'Date:') {
        [void]$issues.Add("FOOTER: Date line must use DD-MM-YYYY")
    } else {
        [void]$issues.Add("FOOTER: missing Date line")
    }

    # --- EMDASHES ---
    # Check content body (after front matter) for emdashes
    $body = $content
    if ($content -match '(?s)^---\r?\n.*?\r?\n---\r?\n(.*)$') {
        $body = $matches[1]
    }
    if ($body -match ([char]0x2014)) {
        [void]$issues.Add("STYLE: contains emdash character (use full stop or comma instead)")
    }

    if ($body -notmatch 'https?://') {
        [void]$issues.Add("SOURCES: no external reference URL found")
    }

    if ($issues.Count -gt 0) {
        $results += [PSCustomObject]@{
            Path = $relPath
            Issues = $issues -join "; "
            Count = $issues.Count
        }
    }
}

Write-Output "`n========================================="
Write-Output "  BLOG POST AUDIT REPORT"
Write-Output "  Total posts scanned: $($posts.Count)"
Write-Output "  Posts with issues: $($results.Count)"
$totalIssues = 0
if ($results.Count -gt 0) {
    $sumValue = ($results | Measure-Object -Property Count -Sum | Select-Object -ExpandProperty Sum)
    if ($null -ne $sumValue) {
        $totalIssues = [int]$sumValue
    }
}
Write-Output "  Total issues: $totalIssues"
Write-Output "=========================================`n"

foreach ($r in $results) {
    Write-Output "--- $($r.Path) ($($r.Count) issue(s)) ---"
    foreach ($issue in ($r.Issues -split '; ')) {
        Write-Output "  - $issue"
    }
    Write-Output ""
}

# Summary by category
$allIssues = $results | ForEach-Object { ($_.Issues -split '; ') } 
$fmIssues = @($allIssues | Where-Object { $_ -match '^FM:' }).Count
$footerIssues = @($allIssues | Where-Object { $_ -match '^FOOTER:' }).Count
$namingIssues = @($allIssues | Where-Object { $_ -match '^NAMING:' }).Count
$styleIssues = @($allIssues | Where-Object { $_ -match '^STYLE:' }).Count

Write-Output "========================================="
Write-Output "  SUMMARY BY CATEGORY"
Write-Output "  Front Matter:  $fmIssues"
Write-Output "  Footer:        $footerIssues"
Write-Output "  Naming:        $namingIssues"
Write-Output "  Style:         $styleIssues"
Write-Output "========================================="

if ($FailOnIssues -and $results.Count -gt 0) {
    exit 1
}
