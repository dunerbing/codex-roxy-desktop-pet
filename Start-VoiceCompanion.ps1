$ErrorActionPreference = 'Stop'
$script = Join-Path $PSScriptRoot 'Voice-Companion.ps1'
Start-Process powershell.exe -WindowStyle Hidden -ArgumentList @(
    '-NoProfile',
    '-ExecutionPolicy', 'Bypass',
    '-File', ('"{0}"' -f $script)
)
Write-Host 'Roxy voice companion started.' -ForegroundColor Green

