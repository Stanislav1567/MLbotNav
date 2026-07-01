param(
    [string]$Symbol = "SOLUSDT",
    [string]$Timeframe = "1m",
    [int]$Repeats = 1,
    [int]$Threads = 9,
    [int]$SearchWorkers = 9,
    [double]$GoalNetReturnPct = 100.0,
    [double]$Leverage = 10.0,
    [string]$StepPrefix = "P7.8",
    [switch]$AllowSubgoalCandidates
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = (Get-Location).Path }
Set-Location $ProjectRoot

if ($Threads -lt 9) {
    Write-Warning "Accelerated mode enforced: Threads raised from $Threads to 9."
    $Threads = 9
}
if ($SearchWorkers -lt 9) {
    Write-Warning "Accelerated mode enforced: SearchWorkers raised from $SearchWorkers to 9."
    $SearchWorkers = 9
}

function Assert-LatestQaPass([string]$Pattern, [string]$ExpectedStep, [string]$Label) {
    $file = Get-ChildItem $Pattern | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
    if (-not $file) {
        throw "[$Label] report not found by pattern: $Pattern"
    }
    $obj = Get-Content $file.FullName -Encoding UTF8 | ConvertFrom-Json
    if ($ExpectedStep -and ($obj.PSObject.Properties.Name -contains "step")) {
        if ($obj.step -ne $ExpectedStep) {
            throw "[$Label] step mismatch: expected=$ExpectedStep actual=$($obj.step) file=$($file.FullName)"
        }
    }
    if (-not ($obj.PSObject.Properties.Name -contains "status")) {
        throw "[$Label] status field missing in $($file.FullName)"
    }
    if ($obj.status -ne "PASS") {
        throw "[$Label] status is not PASS: $($obj.status) file=$($file.FullName)"
    }
    return $file.FullName
}

$windows = @(
    @{ Train = "2026-05-17"; Test = "2026-05-18"; Suffix = "A" },
    @{ Train = "2026-05-18"; Test = "2026-05-19"; Suffix = "B" },
    @{ Train = "2026-05-19"; Test = "2026-05-20"; Suffix = "C" }
)

$results = @()
foreach ($w in $windows) {
    $step = "$StepPrefix$($w.Suffix)"
    Write-Host "=== MATRIX WINDOW === train=$($w.Train) test=$($w.Test) step=$step"
    $args = @(
        "-ExecutionPolicy", "Bypass",
        "-File", ".\run_features_hypotheses_cycle.ps1",
        "-Symbol", $Symbol,
        "-Timeframe", $Timeframe,
        "-TrainDate", $w.Train,
        "-TestDate", $w.Test,
        "-Repeats", "$Repeats",
        "-Threads", "$Threads",
        "-SearchWorkers", "$SearchWorkers",
        "-GoalNetReturnPct", "$GoalNetReturnPct",
        "-Leverage", "$Leverage",
        "-StepLabel", $step
    )
    if ($AllowSubgoalCandidates) {
        $args += "-AllowSubgoalCandidates"
    }
    & powershell @args
    if ($LASTEXITCODE -ne 0) {
        throw "Window failed: step=$step exit_code=$LASTEXITCODE"
    }
    $tzGatePath = Assert-LatestQaPass -Pattern "reports/qa_gate/tz_gate_*.json" -ExpectedStep $step -Label "tz_gate"
    $convPath = Assert-LatestQaPass -Pattern "reports/qa_gate/table_convergence_5plus_*.json" -ExpectedStep "" -Label "table_convergence_5plus"
    $freezePath = Assert-LatestQaPass -Pattern "reports/qa_gate/p72_freeze_ready_*.json" -ExpectedStep "" -Label "p72_freeze_ready"
    $results += @{
        train_date = $w.Train
        test_date = $w.Test
        step = $step
        status = "completed"
        tz_gate_report = $tzGatePath
        convergence_report = $convPath
        freeze_report = $freezePath
    }
}

$runUtc = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$outDir = "reports\qa_gate"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$outPath = Join-Path $outDir "p78_matrix_run_${Symbol}_${Timeframe}_$runUtc.json"
$payload = @{
    generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    symbol = $Symbol
    timeframe = $Timeframe
    windows = $results
}
$payload | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 $outPath
Write-Host "Matrix report: $outPath"



