param(
    [string]$ProjectRoot = "",
    [switch]$SoftFail
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
}

$venvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$reportDir = Join-Path $ProjectRoot "reports\qa_gate"
$ts = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$reportPath = Join-Path $reportDir ("python313_env_guard_{0}.json" -f $ts)

New-Item -ItemType Directory -Force -Path $reportDir | Out-Null

$result = [ordered]@{
    status = "FAIL"
    report_path = $reportPath
    timestamp_utc = (Get-Date).ToUniversalTime().ToString("o")
    project_root = $ProjectRoot
    checks = @{}
    error = $null
}

try {
    if (-not (Test-Path $venvPython)) {
        throw "Missing venv interpreter: $venvPython"
    }

    $pyInfoRaw = & $venvPython -c "import json,sys,sysconfig,platform; print(json.dumps({'executable': sys.executable, 'version': platform.python_version(), 'major': sys.version_info[0], 'minor': sys.version_info[1], 'soabi': sysconfig.get_config_var('SOABI')}, ensure_ascii=False))" 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Cannot execute venv python: $pyInfoRaw"
    }

    $pyInfo = ($pyInfoRaw | Select-Object -Last 1 | ConvertFrom-Json)
    $result.checks.python_executable = $pyInfo.executable
    $result.checks.python_version = $pyInfo.version
    $result.checks.soabi = $pyInfo.soabi

    if ([int]$pyInfo.major -ne 3 -or [int]$pyInfo.minor -ne 13) {
        throw "Python version mismatch. Expected 3.13, got $($pyInfo.version)"
    }

    $importsRaw = & $venvPython -c "import json,importlib.util as u; mods=['numpy','pandas','yaml','joblib','optuna']; print(json.dumps({m: bool(u.find_spec(m)) for m in mods}, ensure_ascii=False))" 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Cannot check module specs: $importsRaw"
    }
    $imports = ($importsRaw | Select-Object -Last 1 | ConvertFrom-Json)
    $result.checks.required_modules = $imports

    $missing = @()
    foreach ($m in @("numpy","pandas","yaml","joblib","optuna")) {
        if (-not $imports.$m) { $missing += $m }
    }
    if ($missing.Count -gt 0) {
        throw ("Missing required modules in .venv: {0}" -f ($missing -join ", "))
    }

    $abiRaw = & $venvPython -c "import json,numpy,pandas; print(json.dumps({'numpy': numpy.__version__, 'pandas': pandas.__version__}, ensure_ascii=False))" 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Binary import check failed (possible ABI conflict): $abiRaw"
    }
    $abi = ($abiRaw | Select-Object -Last 1 | ConvertFrom-Json)
    $result.checks.numpy_version = $abi.numpy
    $result.checks.pandas_version = $abi.pandas

    $result.status = "PASS"
}
catch {
    $result.error = $_.Exception.Message
    if (-not $SoftFail) {
        $result | ConvertTo-Json -Depth 6 | Set-Content -Path $reportPath -Encoding UTF8
        Write-Output ($result | ConvertTo-Json -Depth 6)
        throw
    }
}

$result | ConvertTo-Json -Depth 6 | Set-Content -Path $reportPath -Encoding UTF8
Write-Output ($result | ConvertTo-Json -Depth 6)
