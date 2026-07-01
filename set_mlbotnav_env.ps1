param(
    [int]$Threads = 9
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot
$venvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if ($Threads -lt 9) {
    Write-Warning "Accelerated mode enforced: Threads raised from $Threads to 9."
    $Threads = 9
}

if (-not (Test-Path $venvPython)) {
    throw "Python venv not found: $venvPython"
}

$envPath = Join-Path $ProjectRoot ".env"
if (Test-Path $envPath) {
    Get-Content $envPath | ForEach-Object {
        if ($_ -match "^\s*#") { return }
        if ($_ -match "^\s*$") { return }
        $parts = $_ -split "=", 2
        if ($parts.Count -ne 2) { return }
        $k = $parts[0].Trim()
        $v = $parts[1].Trim().Trim('"')
        if ($k) {
            [System.Environment]::SetEnvironmentVariable($k, $v, "Process")
        }
    }
}

if ([string]::IsNullOrWhiteSpace($env:OPTUNA_STORAGE_URL) -and -not [string]::IsNullOrWhiteSpace($env:POSTGRES_DSN)) {
    $env:OPTUNA_STORAGE_URL = $env:POSTGRES_DSN
}

$env:PYTHONPATH = "src"
$env:OMP_NUM_THREADS = "$Threads"
$env:MKL_NUM_THREADS = "$Threads"
$env:OPENBLAS_NUM_THREADS = "$Threads"
$env:NUMEXPR_NUM_THREADS = "$Threads"
$env:VIRTUAL_ENV = (Join-Path $ProjectRoot ".venv")
$env:MLBOTNAV_PYTHON = $venvPython
$env:PY_PYTHON = "3.13"

# Avoid accidental host-python overrides.
if ($env:PYTHONHOME) { Remove-Item Env:PYTHONHOME -ErrorAction SilentlyContinue }
if ($env:PYTHONEXECUTABLE) { Remove-Item Env:PYTHONEXECUTABLE -ErrorAction SilentlyContinue }

$guardScript = Join-Path $ProjectRoot "scripts\assert_python313_env.ps1"
if (-not (Test-Path $guardScript)) {
    throw "Python guard script not found: $guardScript"
}
& $guardScript -ProjectRoot $ProjectRoot | Out-Host

Write-Host "MLBotNav env configured:"
Write-Host "  PYTHONPATH=$($env:PYTHONPATH)"
Write-Host "  OPTUNA_STORAGE_URL=$($env:OPTUNA_STORAGE_URL)"
Write-Host "  THREADS=$Threads"
Write-Host "  MLBOTNAV_PYTHON=$($env:MLBOTNAV_PYTHON)"
