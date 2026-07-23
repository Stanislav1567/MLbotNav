param(
    [string]$RunDir = "",
    [ValidateSet("overview", "closeups", "allcloseups", "folder", "all", "browse", "index", "day")]
    [string]$Open = "overview",
    [string]$Day = "",
    [switch]$NoOpen
)

$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$RunsDir = Join-Path $Root "STAS1_GOOD_LOW_REVIEW\runs"

if ([string]::IsNullOrWhiteSpace($RunDir)) {
    if (-not (Test-Path $RunsDir)) {
        throw "Runs folder not found: $RunsDir"
    }
    $latest = Get-ChildItem -Path $RunsDir -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($null -eq $latest) {
        throw "No STAS1 runs found in: $RunsDir"
    }
    $RunDir = $latest.FullName
}
else {
    $RunDir = (Resolve-Path $RunDir).Path
}

$overview = Get-ChildItem -Path $RunDir -Filter "GOOD_1PCT_REVIEW_POOL_DAY_OVERVIEW_*.png" -File |
    Sort-Object Name |
    Select-Object -First 1
$closeups = @(Get-ChildItem -Path $RunDir -Filter "GOOD_1PCT_REVIEW_POOL_GOOD_CLOSEUPS_PAGE_*.png" -File |
    Sort-Object Name)
$allCloseups = @(Get-ChildItem -Path $RunDir -Filter "GOOD_1PCT_REVIEW_POOL_ALL_CLOSEUPS_PAGE_*.png" -File |
    Sort-Object Name)
$browseDir = Join-Path $RunDir "BROWSE_BY_DAY"
$browseIndex = Join-Path $browseDir "00_RUN_INDEX.png"

Write-Host "RunDir: $RunDir"
if (Test-Path $browseDir) {
    Write-Host "BrowseByDay: $browseDir"
}
if (Test-Path $browseIndex) {
    Write-Host "BrowseIndex: $browseIndex"
}
if ($overview) {
    Write-Host "Overview: $($overview.FullName)"
}
if ($closeups) {
    Write-Host "GOOD Closeups:"
    $closeups | ForEach-Object { Write-Host "  $($_.FullName)" }
}
if ($allCloseups) {
    Write-Host "ALL Closeups (GOOD + BAD):"
    $allCloseups | ForEach-Object { Write-Host "  $($_.FullName)" }
}
if (Test-Path $browseDir) {
    Write-Host "Browse days:"
    Get-ChildItem -Path $browseDir -Directory | Sort-Object Name | ForEach-Object {
        Write-Host "  $($_.Name)"
    }
}

if ($NoOpen) {
    exit 0
}

switch ($Open) {
    "folder" {
        Invoke-Item $RunDir
    }
    "browse" {
        if (-not (Test-Path $browseDir)) {
            throw "Browse-by-day folder not found in: $RunDir"
        }
        Invoke-Item $browseDir
    }
    "index" {
        if (-not (Test-Path $browseIndex)) {
            throw "Browse index PNG not found in: $RunDir"
        }
        Invoke-Item $browseIndex
    }
    "day" {
        if ([string]::IsNullOrWhiteSpace($Day)) {
            throw "Use -Day YYYY-MM-DD with -Open day"
        }
        $dayDir = Join-Path $browseDir $Day
        if (-not (Test-Path $dayDir)) {
            throw "Day folder not found: $dayDir"
        }
        $dayOverview = Get-ChildItem -Path $dayDir -Filter "00_*_OVERVIEW.png" -File |
            Sort-Object Name |
            Select-Object -First 1
        if (-not $dayOverview) {
            throw "Day overview not found in: $dayDir"
        }
        Invoke-Item $dayOverview.FullName
    }
    "overview" {
        if (-not $overview) {
            throw "Overview PNG not found in: $RunDir"
        }
        Invoke-Item $overview.FullName
    }
    "closeups" {
        if (-not $closeups) {
            throw "Closeup PNG files not found in: $RunDir"
        }
        Invoke-Item $closeups[0].FullName
    }
    "allcloseups" {
        if (Test-Path $browseIndex) {
            Invoke-Item $browseIndex
        }
        elseif ($allCloseups) {
            Invoke-Item $allCloseups[0].FullName
        }
        else {
            throw "ALL closeup PNG files not found in: $RunDir"
        }
    }
    "all" {
        if (Test-Path $browseIndex) {
            Invoke-Item $browseIndex
        }
        elseif ($overview) {
            Invoke-Item $overview.FullName
        }
        else {
            Invoke-Item $RunDir
        }
    }
}
