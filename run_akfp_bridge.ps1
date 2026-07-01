param(
    [switch]$Execute,
    [string]$Policy = "configs/akfp_policy.yaml",
    [string]$StepLabel = "AKFP"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = (Get-Location).Path }
Set-Location $ProjectRoot
$env:PYTHONPATH = "src"

$python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "Python venv not found: $python. Run: py -m venv .venv; .\\.venv\\Scripts\\Activate.ps1; pip install -r requirements.txt"
}
$cmd = @(
    "-m", "mlbotnav.akfp_bridge",
    "--policy", $Policy,
    "--step-label", $StepLabel
)
if ($Execute) {
    $cmd += "--execute"
}

& $python @cmd
exit $LASTEXITCODE




