#Requires -RunAsAdministrator
param(
    [string]$ServiceName = "postgresql-x64-17",
    [string]$DbUser = "postgres",
    [string]$DbName = "postgres",
    [Parameter(Mandatory = $true)]
    [string]$NewPassword
)

$ErrorActionPreference = "Stop"

function Get-PostgresServiceData {
    param([string]$Name)
    $svc = Get-WmiObject Win32_Service -Filter "Name='$Name'"
    if (-not $svc) {
        throw "Service not found: $Name"
    }
    $pathName = [string]$svc.PathName
    $dataDir = $null
    if ($pathName -match '-D\s+"([^"]+)"') {
        $dataDir = $matches[1]
    }
    if (-not $dataDir) {
        throw "Cannot parse PostgreSQL data dir from service PathName: $pathName"
    }
    $pgCtl = $null
    if ($pathName -match '^"([^"]+pg_ctl\.exe)"') {
        $pgCtl = $matches[1]
    }
    if (-not $pgCtl) {
        throw "Cannot parse pg_ctl.exe from service PathName: $pathName"
    }
    $pgBinDir = Split-Path -Parent $pgCtl
    $psql = Join-Path $pgBinDir "psql.exe"
    if (-not (Test-Path $psql)) {
        throw "psql.exe not found: $psql"
    }
    return @{
        Service = $svc
        DataDir = $dataDir
        PgCtl = $pgCtl
        Psql = $psql
    }
}

function Add-TemporaryTrustRule {
    param(
        [string]$PgHbaPath
    )
    $markerA = "# MLBOTNAV_TEMP_TRUST_BEGIN"
    $markerB = "# MLBOTNAV_TEMP_TRUST_END"
    $content = Get-Content -Path $PgHbaPath -Raw -Encoding UTF8
    if ($content -match [regex]::Escape($markerA)) {
        return
    }
    $rules = @(
        $markerA,
        "host    all             postgres        127.0.0.1/32            trust",
        "host    all             postgres        ::1/128                 trust",
        $markerB,
        ""
    ) -join "`r`n"
    $content = $rules + $content
    Set-Content -Path $PgHbaPath -Value $content -Encoding UTF8
}

function Remove-TemporaryTrustRule {
    param([string]$PgHbaPath)
    $content = Get-Content -Path $PgHbaPath -Raw -Encoding UTF8
    $pattern = '(?ms)^# MLBOTNAV_TEMP_TRUST_BEGIN\r?\n.*?# MLBOTNAV_TEMP_TRUST_END\r?\n?'
    $content = [regex]::Replace($content, $pattern, "")
    Set-Content -Path $PgHbaPath -Value $content -Encoding UTF8
}

function Invoke-RestartPgService {
    param([string]$Name)
    Restart-Service -Name $Name -Force -ErrorAction Stop
    Start-Sleep -Seconds 2
}

function Invoke-ResetPassword {
    param(
        [string]$PsqlPath,
        [string]$User,
        [string]$Db,
        [string]$Password
    )
    $escaped = $Password.Replace("'", "''")
    $sql = "ALTER USER $User WITH PASSWORD '$escaped';"
    & $PsqlPath -h 127.0.0.1 -U $User -d $Db -v ON_ERROR_STOP=1 -c $sql
    if ($LASTEXITCODE -ne 0) {
        throw "psql ALTER USER failed with code $LASTEXITCODE"
    }
}

$meta = Get-PostgresServiceData -Name $ServiceName
$pgHba = Join-Path $meta.DataDir "pg_hba.conf"
if (-not (Test-Path $pgHba)) {
    throw "pg_hba.conf not found: $pgHba"
}

$backup = Join-Path $meta.DataDir ("pg_hba.conf.bak_mlbnav_" + (Get-Date -Format "yyyyMMddTHHmmss"))
Copy-Item -Path $pgHba -Destination $backup -Force

try {
    Add-TemporaryTrustRule -PgHbaPath $pgHba
    Invoke-RestartPgService -Name $ServiceName
    Invoke-ResetPassword -PsqlPath $meta.Psql -User $DbUser -Db $DbName -Password $NewPassword
}
finally {
    try {
        Copy-Item -Path $backup -Destination $pgHba -Force
        Invoke-RestartPgService -Name $ServiceName
    }
    catch {
        Write-Warning "Failed to restore/restart automatically. Restore manually from: $backup"
        throw
    }
}

Write-Host "Password reset completed successfully."
Write-Host "Service: $ServiceName"
Write-Host "DataDir: $($meta.DataDir)"
Write-Host "Backup:  $backup"
