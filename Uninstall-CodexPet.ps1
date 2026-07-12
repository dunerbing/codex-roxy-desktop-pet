[CmdletBinding()]
param(
    [string]$PetId = 'roxy-inspired-mage'
)

$ErrorActionPreference = 'Stop'

$petsRoot = [System.IO.Path]::GetFullPath((Join-Path $HOME '.codex\pets'))
$destination = [System.IO.Path]::GetFullPath((Join-Path $petsRoot $PetId))
$expectedPrefix = $petsRoot.TrimEnd([System.IO.Path]::DirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar

if (-not $destination.StartsWith($expectedPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw 'Refusing to remove a path outside the Codex pets directory.'
}

if (-not (Test-Path -LiteralPath $destination)) {
    Write-Host 'Roxy Inspired Mage is not installed.' -ForegroundColor Yellow
    exit 0
}

Remove-Item -LiteralPath $destination -Recurse -Force
Write-Host 'Roxy Inspired Mage uninstalled. Restart Codex to refresh the pet list.' -ForegroundColor Green

