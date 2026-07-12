[CmdletBinding()]
param(
    [string]$PetId = 'roxy-inspired-mage'
)

$ErrorActionPreference = 'Stop'

$source = Join-Path $PSScriptRoot 'pet'
$petsRoot = Join-Path $HOME '.codex\pets'
$destination = Join-Path $petsRoot $PetId

if (-not (Test-Path -LiteralPath (Join-Path $source 'pet.json'))) {
    throw "Missing pet\pet.json. Extract the complete release before installing."
}

if (-not (Test-Path -LiteralPath (Join-Path $source 'spritesheet.png'))) {
    throw "Missing pet\spritesheet.png. Extract the complete release before installing."
}

New-Item -ItemType Directory -Force -Path $petsRoot | Out-Null

if (Test-Path -LiteralPath $destination) {
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $backup = "$destination.backup-$stamp"
    Copy-Item -LiteralPath $destination -Destination $backup -Recurse
    Write-Host "Existing pet backed up to: $backup" -ForegroundColor Yellow
}

New-Item -ItemType Directory -Force -Path $destination | Out-Null
Copy-Item -LiteralPath (Join-Path $source 'pet.json') -Destination $destination -Force
Copy-Item -LiteralPath (Join-Path $source 'spritesheet.png') -Destination $destination -Force

Write-Host ''
Write-Host 'Roxy Inspired Mage installed successfully.' -ForegroundColor Green
Write-Host "Installed at: $destination"
Write-Host 'Restart Codex, then select it from Settings > Pets.'

