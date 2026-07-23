param(
    [switch]$OpenReport
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repoRoot

$env:PYTHONPATH = "src"

$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    $python = "python"
}

& $python -m mlbotnav.stas5_v5_folder_audit
if ($LASTEXITCODE -ne 0) {
    throw "stas5_v5_folder_audit failed with exit code $LASTEXITCODE"
}

$report = Join-Path $repoRoot "STAS5_ML_CORE\artifacts\v5\STAS5_V5_FOLDER_AUDIT_20260715_RU.md"
if ($OpenReport) {
    Invoke-Item -LiteralPath $report
}
