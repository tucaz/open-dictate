# open-dictate Windows Uninstallation Script
# Run with: powershell -ExecutionPolicy Bypass -File uninstall.ps1

param(
    [switch]$KeepRecordings = $false,
    [switch]$KeepModels = $false
)

$ErrorActionPreference = "SilentlyContinue"

# Colors for output
function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Success($msg) { Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Warning($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }

Write-Info "Uninstalling open-dictate..."

# Stop any running instances
$processes = Get-Process | Where-Object { $_.ProcessName -like "*open-dictate*" }
foreach ($proc in $processes) {
    Write-Info "Stopping process: $($proc.ProcessName)"
    Stop-Process -Id $proc.Id -Force
}

# Directories to remove
$dirsToRemove = @()

# Install directory
$installDir = "$env:LOCALAPPDATA\open-dictate"
if (Test-Path $installDir) {
    if ($KeepModels -or $KeepRecordings) {
        # Remove selectively
        $binDir = "$installDir\bin"
        if (Test-Path $binDir) {
            Remove-Item $binDir -Recurse -Force
            Write-Info "Removed: $binDir"
        }
    } else {
        $dirsToRemove += $installDir
    }
}

# Config directory
$configDir = "$env:APPDATA\open-dictate"
if (Test-Path $configDir) {
    if ($KeepModels -and $KeepRecordings) {
        Write-Warning "Keeping config directory as requested: $configDir"
    } else {
        $dirsToRemove += $configDir
    }
}

# Remove directories
foreach ($dir in $dirsToRemove) {
    if (Test-Path $dir) {
        Remove-Item $dir -Recurse -Force
        Write-Info "Removed: $dir"
    }
}

# Remove Start Menu shortcuts
$startMenuDir = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\open-dictate"
if (Test-Path $startMenuDir) {
    Remove-Item $startMenuDir -Recurse -Force
    Write-Info "Removed Start Menu shortcuts"
}

# Remove startup shortcut
$startupShortcut = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\open-dictate.lnk"
if (Test-Path $startupShortcut) {
    Remove-Item $startupShortcut -Force
    Write-Info "Removed startup shortcut"
}

# Remove from PATH
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
$newPath = $currentPath -replace ";$env:LOCALAPPDATA\open-dictate\bin", ""
if ($newPath -ne $currentPath) {
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    Write-Info "Removed from PATH"
}

Write-Success "Uninstallation complete!"
Write-Info "open-dictate has been removed from your system."

if ($KeepRecordings -or $KeepModels) {
    Write-Info ""
    Write-Info "Note: Some files were kept as requested."
    if ($KeepRecordings) { Write-Info "  - Recordings were kept in: $configDir\recordings" }
    if ($KeepModels) { Write-Info "  - Models were kept in: $configDir\models" }
}
