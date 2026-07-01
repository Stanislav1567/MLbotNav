$ErrorActionPreference = "Stop"
$root = "C:\Users\007\Desktop\MLbotNav"
$aptuna = Join-Path $root "APTuna"
if ($PWD.Path -ne $root -and $PWD.Path -ne $aptuna) {
  throw "Run shell only from: $root OR $aptuna"
}
chcp 65001 > $null
[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
if (Test-Path "$root\.venv\Scripts\Activate.ps1") {
  . "$root\.venv\Scripts\Activate.ps1"
}
Write-Host "Workspace OK: $($PWD.Path)" -ForegroundColor Green
Write-Host "Encoding OK: UTF-8, codepage 65001" -ForegroundColor Green
