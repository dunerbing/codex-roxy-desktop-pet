[CmdletBinding()]
param(
    [string]$PetId = 'roxy-inspired-mage',
    [ValidateRange(112, 224)]
    [int]$Width = 224,
    [switch]$WaitForAppExit
)

$ErrorActionPreference = 'Stop'

$mutex = [Threading.Mutex]::new($false, 'Local\CodexRoxyMaxSizeUpdate')
if (-not $mutex.WaitOne(0, $false)) {
    exit 0
}

try {
    if ($WaitForAppExit) {
        while (Get-Process ChatGPT, codex -ErrorAction SilentlyContinue) {
            Start-Sleep -Seconds 1
        }
        Start-Sleep -Milliseconds 500
    }

    foreach ($name in '.codex-global-state.json', '.codex-global-state.json.bak') {
        $path = Join-Path (Join-Path $HOME '.codex') $name
        if (-not (Test-Path -LiteralPath $path)) {
            continue
        }

        $state = Get-Content -LiteralPath $path -Raw -Encoding UTF8 | ConvertFrom-Json
        $atoms = $state.'electron-persisted-atom-state'
        if ($null -eq $atoms) {
            $atoms = [pscustomobject]@{}
            $state | Add-Member -NotePropertyName 'electron-persisted-atom-state' -NotePropertyValue $atoms
        }
        $atoms | Add-Member -Force -NotePropertyName 'selected-avatar-id' -NotePropertyValue "custom:$PetId"
        $atoms | Add-Member -Force -NotePropertyName 'avatar-overlay-mascot-width-px' -NotePropertyValue $Width

        $temporaryPath = "$path.roxy-size.tmp"
        $state | ConvertTo-Json -Depth 100 -Compress | Set-Content -LiteralPath $temporaryPath -Encoding UTF8
        Move-Item -LiteralPath $temporaryPath -Destination $path -Force
    }
} finally {
    $mutex.ReleaseMutex()
    $mutex.Dispose()
}

