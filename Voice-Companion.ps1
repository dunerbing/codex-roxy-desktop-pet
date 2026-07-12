[CmdletBinding()]
param(
    [string]$AudioPath = '',
    [int]$PollMilliseconds = 100,
    [int]$CooldownMilliseconds = 1800
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($AudioPath)) {
    $projectMp3 = Join-Path $PSScriptRoot 'pet\encouragement.mp3'
    $installedMp3 = Join-Path $PSScriptRoot 'encouragement.mp3'
    $projectAudio = Join-Path $PSScriptRoot 'pet\encouragement.wav'
    $installedAudio = Join-Path $PSScriptRoot 'encouragement.wav'
    $AudioPath = if (Test-Path -LiteralPath $projectMp3) {
        $projectMp3
    } elseif (Test-Path -LiteralPath $installedMp3) {
        $installedMp3
    } elseif (Test-Path -LiteralPath $projectAudio) {
        $projectAudio
    } else {
        $installedAudio
    }
}

if (-not (Test-Path -LiteralPath $AudioPath)) {
    throw "Voice file not found: $AudioPath"
}

$mutex = [Threading.Mutex]::new($false, 'Local\CodexRoxyVoiceCompanion')
if (-not $mutex.WaitOne(0, $false)) {
    exit 0
}

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type -ReferencedAssemblies @('System.dll', 'System.Drawing.dll') -TypeDefinition @'
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.InteropServices;

public static class RoxyPetWindow {
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
    [DllImport("user32.dll")] private static extern bool EnumWindows(EnumWindowsProc callback, IntPtr extraData);
    [DllImport("user32.dll")] private static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")] private static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);
    [DllImport("user32.dll")] private static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);

    private struct RECT { public int Left, Top, Right, Bottom; }

    public static System.Drawing.Rectangle FindOverlay() {
        var candidates = new List<System.Drawing.Rectangle>();
        EnumWindows((window, state) => {
            if (!IsWindowVisible(window)) return true;
            uint processId;
            GetWindowThreadProcessId(window, out processId);
            try {
                var process = Process.GetProcessById((int)processId);
                if (!process.ProcessName.Equals("ChatGPT", StringComparison.OrdinalIgnoreCase)) return true;
            } catch { return true; }
            RECT rect;
            if (!GetWindowRect(window, out rect)) return true;
            int width = rect.Right - rect.Left;
            int height = rect.Bottom - rect.Top;
            if (width >= 160 && height >= 160 && width <= 520 && height <= 520) {
                candidates.Add(new System.Drawing.Rectangle(rect.Left, rect.Top, width, height));
            }
            return true;
        }, IntPtr.Zero);
        if (candidates.Count == 0) return System.Drawing.Rectangle.Empty;
        candidates.Sort((a, b) => (a.Width * a.Height).CompareTo(b.Width * b.Height));
        return candidates[0];
    }
}
'@

$isWave = [IO.Path]::GetExtension($AudioPath).Equals('.wav', [StringComparison]::OrdinalIgnoreCase)
if ($isWave) {
    $player = [System.Media.SoundPlayer]::new($AudioPath)
    $player.Load()
} else {
    Add-Type -AssemblyName PresentationCore
    $player = [Windows.Media.MediaPlayer]::new()
    $player.Open([Uri]::new($AudioPath))
    $player.Volume = 1
}
$wasInside = $false
$lastPlayed = [DateTime]::MinValue

try {
    while ($true) {
        $overlay = [RoxyPetWindow]::FindOverlay()
        $cursor = [System.Windows.Forms.Cursor]::Position
        $inside = -not $overlay.IsEmpty -and $overlay.Contains($cursor)
        $cooldownElapsed = ([DateTime]::UtcNow - $lastPlayed).TotalMilliseconds -ge $CooldownMilliseconds
        if ($inside -and -not $wasInside -and $cooldownElapsed) {
            if (-not $isWave) {
                $player.Position = [TimeSpan]::Zero
            }
            $player.Play()
            $lastPlayed = [DateTime]::UtcNow
        }
        $wasInside = $inside
        Start-Sleep -Milliseconds $PollMilliseconds
    }
} finally {
    if ($isWave) {
        $player.Dispose()
    } else {
        $player.Stop()
        $player.Close()
    }
    $mutex.ReleaseMutex()
    $mutex.Dispose()
}
