param(
    [string]$RunDir = "",
    [ValidateSet("folder", "browse", "index", "day", "overview", "entries", "xlsx", "report")]
    [string]$Open = "browse",
    [string]$Day = "",
    [switch]$NoOpen
)

$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$RunsDir = Join-Path $Root "STAS2_MARKET_PHASE_REVIEW\runs"

if ([string]::IsNullOrWhiteSpace($RunDir)) {
    if (-not (Test-Path $RunsDir)) {
        throw "Runs folder not found: $RunsDir"
    }
    $latest = Get-ChildItem -Path $RunsDir -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($null -eq $latest) {
        throw "No STAS2 runs found in: $RunsDir"
    }
    $RunDir = $latest.FullName
}
else {
    $RunDir = (Resolve-Path $RunDir).Path
}

$browseDir = Join-Path $RunDir "BROWSE_BY_DAY"
$browseIndex = Join-Path $browseDir "00_RUN_INDEX.png"
$xlsx = Join-Path $RunDir "STAS2_MARKET_PHASE_TABLES.xlsx"
$report = Join-Path $RunDir "STAS2_REPORT_RU.md"
$overview = Get-ChildItem -Path $RunDir -Filter "STAS2_DAY_OVERVIEW_*.png" -File | Sort-Object Name | Select-Object -First 1
$entryPages = @(Get-ChildItem -Path $RunDir -Filter "STAS2_ENTRY_CONTEXT_PAGE_*.png" -File | Sort-Object Name)

Write-Host "RunDir: $RunDir"
if (Test-Path $browseDir) { Write-Host "BrowseByDay: $browseDir" }
if (Test-Path $browseIndex) { Write-Host "BrowseIndex: $browseIndex" }
if (Test-Path $xlsx) { Write-Host "Excel: $xlsx" }
if (Test-Path $report) { Write-Host "Report: $report" }
if ($overview) { Write-Host "Overview: $($overview.FullName)" }
if ($entryPages) {
    Write-Host "Entry context pages:"
    $entryPages | ForEach-Object { Write-Host "  $($_.FullName)" }
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
        if (-not (Test-Path $browseDir)) { throw "Browse-by-day folder not found in: $RunDir" }
        Invoke-Item $browseDir
    }
    "index" {
        if (-not (Test-Path $browseIndex)) { throw "Browse index PNG not found in: $RunDir" }
        Invoke-Item $browseIndex
    }
    "day" {
        if ([string]::IsNullOrWhiteSpace($Day)) { throw "Use -Day YYYY-MM-DD with -Open day" }
        $dayDir = Join-Path $browseDir $Day
        if (-not (Test-Path $dayDir)) { throw "Day folder not found: $dayDir" }
        $dayOverview = Get-ChildItem -Path $dayDir -Filter "00_*_OVERVIEW.png" -File | Sort-Object Name | Select-Object -First 1
        if (-not $dayOverview) { throw "Day overview not found in: $dayDir" }
        Invoke-Item $dayOverview.FullName
    }
    "overview" {
        if (-not $overview) { throw "Overview PNG not found in: $RunDir" }
        Invoke-Item $overview.FullName
    }
    "entries" {
        if (-not $entryPages) { throw "Entry context PNG files not found in: $RunDir" }
        Invoke-Item $entryPages[0].FullName
    }
    "xlsx" {
        if (-not (Test-Path $xlsx)) { throw "Excel file not found in: $RunDir" }
        Invoke-Item $xlsx
    }
    "report" {
        if (-not (Test-Path $report)) { throw "Report not found in: $RunDir" }
        Invoke-Item $report
    }
}
