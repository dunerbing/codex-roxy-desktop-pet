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
Copy-Item -LiteralPath (Join-Path $source 'encouragement.wav') -Destination $destination -Force
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'Voice-Companion.ps1') -Destination $destination -Force

$startupDirectory = [Environment]::GetFolderPath('Startup')
$shortcutPath = Join-Path $startupDirectory 'Roxy Codex Pet Voice.lnk'
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = 'powershell.exe'
$shortcut.Arguments = "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$(Join-Path $destination 'Voice-Companion.ps1')`""
$shortcut.WorkingDirectory = $destination
$shortcut.WindowStyle = 7
$shortcut.Description = 'Roxy Codex desktop pet voice companion'
$shortcut.Save()

Start-Process powershell.exe -WindowStyle Hidden -ArgumentList @(
    '-NoProfile', '-ExecutionPolicy', 'Bypass',
    '-File', ('"{0}"' -f (Join-Path $destination 'Voice-Companion.ps1'))
)

Write-Host ''
Write-Host 'Roxy Inspired Mage installed successfully.' -ForegroundColor Green
Write-Host "Installed at: $destination"
Write-Host 'Restart Codex, then select it from Settings > Pets.'
Write-Host 'Voice companion enabled: hover over the pet to hear encouragement.'
