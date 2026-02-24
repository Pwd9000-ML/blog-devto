#!/usr/bin/env pwsh
# Audit all blog posts for front matter and footer consistency
Set-StrictMode -Version Latest

$root = Split-Path $PSScriptRoot -Parent
Set-Location $root

$posts = Get-ChildItem -Path "posts" -Recurse -Filter "*.md" | Where-Object {
    $_.FullName -notmatch '\\code\\' -and $_.Name -ne 'README.md' -and $_.Name -ne 'example_README.md'
} | Sort-Object FullName

$results = @()

foreach ($post in $posts) {
    $content = Get-Content $post.FullName -Raw -Encoding UTF8
    $lines = Get-Content $post.FullName -Encoding UTF8
    $relPath = $post.FullName.Replace("$root\", "").Replace("\", "/")
    $folder = Split-Path (Split-Path $post.FullName -Parent) -Leaf
    $fileName = [System.IO.Path]::GetFileNameWithoutExtension($post.Name)
    
    $issues = [System.Collections.ArrayList]::new()

    # --- FRONT MATTER ---
    if ($content -match '(?s)^---\r?\n(.*?)\r?\n---') {
        $fm = $matches[1]
        
        # Description length
        $descLen = 0
        if ($fm -match "description:\s*'([^']*)'") { $descLen = $matches[1].Length }
        elseif ($fm -match 'description:\s*"([^"]*)"') { $descLen = $matches[1].Length }
        elseif ($fm -match 'description:\s+([^\r\n]+)') { $descLen = $matches[1].Trim().Trim("'`"").Length }
        if ($descLen -gt 150) { [void]$issues.Add("FM: description too long ($descLen chars, max 150)") }

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

        # Description quoting
        if ($fm -match 'description:\s+[^''"]') {
            [void]$issues.Add("FM: description not single-quoted")
        }
    } else {
        [void]$issues.Add("FM: no front matter found")
    }

    # --- FILENAME vs FOLDER ---
    if ($fileName -cne $folder -and $fileName -ne "index") {
        [void]$issues.Add("NAMING: filename '$($post.Name)' does not match folder '$folder'")
    }

    # --- FOOTER ---
    $footerOk = $true
    
    # Check LinkedIn URL
    if ($content -match 'linkedin\.com/in/marcel-l-61b0a96b') {
        [void]$issues.Add("FOOTER: old LinkedIn URL /in/marcel-l-61b0a96b/ (should be /in/marcel-pwd9000/)")
        $footerOk = $false
    }
    if ($content -match 'linkedin\.com/in/marcel-pwd9000//') {
        [void]$issues.Add("FOOTER: double trailing slash in LinkedIn URL")
        $footerOk = $false
    }

    # Check footer presence
    if ($content -notmatch '\{%\s*user\s+pwd9000\s*%\}') {
        [void]$issues.Add("FOOTER: missing {% user pwd9000 %} tag")
    }

    # Check Date line
    if ($content -match 'Date:\s*(\d{2}-\d{2}-\d{4})') {
        # good format
    } elseif ($content -match 'Date:') {
        # Date line exists but wrong format
    } else {
        [void]$issues.Add("FOOTER: missing Date line")
    }

    # Check for X/Twitter link
    if ($content -notmatch ':penguin:\s*\[X\]' -and $content -notmatch ':penguin:\s*\[Twitter\]') {
        # Some very old posts may not have it
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
Write-Output "  Total issues: $(($results | Measure-Object -Property Count -Sum).Sum)"
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
