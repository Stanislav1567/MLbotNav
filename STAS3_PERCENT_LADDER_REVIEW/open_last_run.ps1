param(
    [ValidateSet("folder", "browse", "xlsx", "report", "tp", "day")]
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

$run = Get-ChildItem $runsDir -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($null -eq $run) {
    throw "No STAS3 runs found in $runsDir"
}

$target = $run.FullName
if ($Open -eq "browse") {
    $target = Join-Path $run.FullName "BROWSE_BY_DAY"
} elseif ($Open -eq "xlsx") {
    $target = Join-Path $run.FullName "STAS3_PERCENT_LADDER_TABLES.xlsx"
} elseif ($Open -eq "report") {
    $target = Join-Path $run.FullName "STAS3_REPORT_RU.md"
} elseif ($Open -eq "tp") {
    $target = Join-Path $run.FullName "STAS3_TP_LADDER_V0_RU.md"
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
