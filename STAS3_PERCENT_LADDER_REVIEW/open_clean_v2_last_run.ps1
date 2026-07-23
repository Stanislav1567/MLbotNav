param(
    [ValidateSet("folder", "browse", "xlsx", "report", "day", "entries", "medium")]
    [string]$Open = "folder",
    [string]$Day = "",
    [switch]$NoOpen
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$runsDir = Join-Path $root "STAS3_PERCENT_LADDER_REVIEW\runs"
if (-not (Test-Path $runsDir)) {
    throw "Runs folder not found: $runsDir"
}

$run = Get-ChildItem $runsDir -Directory |
    Where-Object { $_.Name -like "stas3_v2_clean_*" } |
    Where-Object { Test-Path (Join-Path $_.FullName "STAS3_V2_CLEAN_PAYLOAD.json") } |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if ($null -eq $run) {
    throw "No STAS3 V2 clean runs found in $runsDir"
}

$target = $run.FullName
if ($Open -eq "browse") {
    $target = Join-Path $run.FullName "BROWSE_BY_DAY"
} elseif ($Open -eq "xlsx") {
    $target = Join-Path $run.FullName "STAS3_V2_CLEAN_TABLES.xlsx"
} elseif ($Open -eq "report") {
    $target = Join-Path $run.FullName "STAS3_V2_CLEAN_REPORT_RU.md"
} elseif ($Open -eq "entries") {
    $target = Join-Path $run.FullName "ENTRY_PAGES"
} elseif ($Open -eq "medium") {
    $target = Join-Path $run.FullName "MEDIUM_1PCT_PLUS_PAGES"
} elseif ($Open -eq "day") {
    if ([string]::IsNullOrWhiteSpace($Day)) {
        throw "-Day is required for -Open day"
    }
    $target = Join-Path $run.FullName ("BROWSE_BY_DAY\" + $Day)
}

Write-Output $target
if (-not $NoOpen) {
    Invoke-Item $target
}
