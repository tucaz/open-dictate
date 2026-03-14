# open-dictate Windows Installation Script
# 
# This script works in TWO modes:
# 1. DOWNLOAD mode (default): Downloads latest release from GitHub
# 2. LOCAL mode: Installs from files in the same folder (for local builds)
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File install.ps1
#
# To uninstall:
#   powershell -ExecutionPolicy Bypass -File scripts/uninstall.ps1

param(
    [string]$InstallDir = "$env:LOCALAPPDATA\open-dictate",
    [switch]$AddToPath = $true,
    [string]$Version = "latest"  # "latest" or specific version like "1.0.0"
)

$ErrorActionPreference = "Stop"

# Colors for output
function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Success($msg) { Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Warning($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Error($msg) { Write-Host "[ERROR] $msg" -ForegroundColor Red }

# Detect mode: LOCAL if open-dictate.exe exists in same folder, otherwise DOWNLOAD
$ScriptDir = $PSScriptRoot
if (-not $ScriptDir) { $ScriptDir = (Get-Location).Path }

$LocalExe = Join-Path $ScriptDir "open-dictate.exe"
$IsLocalMode = Test-Path $LocalExe

Write-Host ""
Write-Host "open-dictate Windows Installer" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""

if ($IsLocalMode) {
    Write-Info "Mode: LOCAL (installing from files in this folder)"
} else {
    Write-Info "Mode: DOWNLOAD (fetching from GitHub releases)"
}
Write-Info "Install directory: $InstallDir"
Write-Host ""

# Check if running on Windows
if (-not $IsWindows -and $env:OS -ne "Windows_NT") {
    Write-Error "This installer is for Windows only."
    exit 1
}

# Config and model locations
$ConfigDir = "$env:APPDATA\open-dictate"
$ConfigFile = "$ConfigDir\config.json"
$ModelsDir = "$ConfigDir\models"

# Create directories
$BinDir = "$InstallDir\bin"
$dirs = @($InstallDir, $BinDir, $ConfigDir, $ModelsDir)
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Info "Created: $dir"
    }
}

# ============================================================================
# Install open-dictate.exe and whisper-cli
# ============================================================================

if ($IsLocalMode) {
    # LOCAL MODE: Copy files from release folder
    Write-Info "Copying files from local release..."
    
    # Copy open-dictate.exe
    Copy-Item "$ScriptDir\open-dictate.exe" "$BinDir\open-dictate.exe" -Force
    Write-Success "Copied open-dictate.exe"
    
    # Copy whisper-cli and DLLs
    $LocalBinDir = "$ScriptDir\bin"
    if (Test-Path $LocalBinDir) {
        $files = Get-ChildItem $LocalBinDir -File
        foreach ($file in $files) {
            Copy-Item $file.FullName "$BinDir\" -Force
            Write-Info "Copied $($file.Name)"
        }
        Write-Success "Copied whisper-cli and dependencies"
    } else {
        Write-Warning "Local bin folder not found at $LocalBinDir"
        Write-Info "You may need to download whisper-cli manually from:"
        Write-Info "  https://github.com/ggerganov/whisper.cpp/releases"
    }
} else {
    # DOWNLOAD MODE: Download from GitHub releases
    
    # Determine version to download
    if ($Version -eq "latest") {
        Write-Info "Checking for latest version..."
        try {
            $releasesUrl = "https://api.github.com/repos/tucaz/open-dictate/releases/latest"
            $release = Invoke-RestMethod -Uri $releasesUrl -Headers @{ "User-Agent" = "PowerShell" }
            $Version = $release.tag_name -replace '^v', ''
            Write-Info "Latest version: $Version"
        } catch {
            Write-Warning "Could not determine latest version, using 0.0.2"
            $Version = "0.0.2"
        }
    }
    
    $DownloadUrl = "https://github.com/tucaz/open-dictate/releases/download/v$Version/open-dictate-windows-v$Version.zip"
    $TempZip = "$env:TEMP\open-dictate-download.zip"
    $TempDir = "$env:TEMP\open-dictate-extract"
    
    # Check if already installed
    $ExistingExe = "$BinDir\open-dictate.exe"
    if (Test-Path $ExistingExe) {
        Write-Warning "open-dictate is already installed at $ExistingExe"
        $overwrite = Read-Host "Overwrite? (y/n)"
        if ($overwrite -ne 'y') {
            Write-Info "Installation cancelled."
            exit 0
        }
    }
    
    # Download release
    Write-Info "Downloading open-dictate v$Version..."
    Write-Info "URL: $DownloadUrl"
    try {
        Invoke-WebRequest -Uri $DownloadUrl -OutFile $TempZip -UseBasicParsing
        Write-Success "Downloaded"
    } catch {
        Write-Error "Failed to download: $_"
        Write-Info "Make sure the version exists at:"
        Write-Info "  https://github.com/tucaz/open-dictate/releases"
        exit 1
    }
    
    # Extract
    Write-Info "Extracting..."
    if (Test-Path $TempDir) {
        Remove-Item -Path $TempDir -Recurse -Force
    }
    Expand-Archive -Path $TempZip -DestinationPath $TempDir -Force
    
    # Support both zip layouts:
    # 1. Files extracted directly into $TempDir
    # 2. Files extracted into a single top-level folder under $TempDir
    $ExtractedRoot = $TempDir
    if (-not (Test-Path (Join-Path $ExtractedRoot "open-dictate.exe"))) {
        $NestedRoot = Get-ChildItem $TempDir -Directory |
            Where-Object { Test-Path (Join-Path $_.FullName "open-dictate.exe") } |
            Select-Object -First 1
        if ($NestedRoot) {
            $ExtractedRoot = $NestedRoot.FullName
        }
    }

    $ExtractedExe = Join-Path $ExtractedRoot "open-dictate.exe"
    if (-not (Test-Path $ExtractedExe)) {
        Write-Error "Downloaded release did not contain open-dictate.exe"
        exit 1
    }

    Copy-Item $ExtractedExe "$BinDir\" -Force
    Write-Success "Installed open-dictate.exe"
    
    $ExtractedBinDir = Join-Path $ExtractedRoot "bin"
    if (Test-Path $ExtractedBinDir) {
        Copy-Item (Join-Path $ExtractedBinDir "*") "$BinDir\" -Force
        Write-Success "Installed whisper-cli and dependencies"
    }
    
    # Cleanup
    Remove-Item $TempZip -Force -ErrorAction SilentlyContinue
    Remove-Item $TempDir -Recurse -Force -ErrorAction SilentlyContinue
}

# ============================================================================
# Download model (if not present)
# ============================================================================

$ModelSize = "base.en"
$ModelFile = "ggml-$ModelSize.bin"
$ModelPath = "$ModelsDir\$ModelFile"
$LegacyModelPath = "$InstallDir\models\$ModelFile"
$ModelUrl = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/$ModelFile"

if ((-not (Test-Path $ModelPath)) -and (Test-Path $LegacyModelPath)) {
    Copy-Item $LegacyModelPath $ModelPath -Force
    Write-Info "Copied existing model from legacy install location"
}

if (-not (Test-Path $ModelPath)) {
    Write-Info "Downloading default model ($ModelSize)..."
    Write-Info "This may take a few minutes (~150MB)..."
    try {
        Invoke-WebRequest -Uri $ModelUrl -OutFile $ModelPath -UseBasicParsing
        Write-Success "Model downloaded"
    } catch {
        Write-Warning "Failed to download model automatically."
        Write-Info "The model will be downloaded on first run."
    }
} else {
    Write-Info "Model already exists"
}

# ============================================================================
# Create config
# ============================================================================

if (-not (Test-Path $ConfigFile)) {
    $defaultConfig = @{
        hotkey = @{
            keyCode = 163  # Right Ctrl
            modifiers = @()
        }
        modelPath = $null
        modelSize = "base.en"
        language = "en"
        spokenPunctuation = $false
        maxRecordings = 0
    } | ConvertTo-Json -Depth 3
    
    $defaultConfig | Out-File -FilePath $ConfigFile -Encoding UTF8
    Write-Info "Created default config at $ConfigFile"
} else {
    Write-Info "Config already exists at $ConfigFile"
}

# ============================================================================
# Add to PATH
# ============================================================================

if ($AddToPath) {
    $UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($UserPath -notlike "*$BinDir*") {
        [Environment]::SetEnvironmentVariable("Path", "$UserPath;$BinDir", "User")
        Write-Success "Added to PATH (restart terminal to use)"
    } else {
        Write-Info "Already in PATH"
    }
}

# ============================================================================
# Create Start Menu shortcut
# ============================================================================

$StartMenuDir = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\open-dictate"
if (-not (Test-Path $StartMenuDir)) {
    New-Item -ItemType Directory -Path $StartMenuDir -Force | Out-Null
}

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$StartMenuDir\open-dictate.lnk")
$Shortcut.TargetPath = "$BinDir\open-dictate.exe"
$Shortcut.Arguments = "start"
$Shortcut.WorkingDirectory = $InstallDir

# Set icon if available
$IconPath = "$BinDir\icon.ico"
if (Test-Path $IconPath) {
    $Shortcut.IconLocation = $IconPath
}

$Shortcut.Save()
Write-Info "Created Start Menu shortcut"

# ============================================================================
# Done
# ============================================================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Info "Installation directory: $InstallDir"
Write-Info "Config file: $ConfigFile"
Write-Host ""
Write-Host "Usage:" -ForegroundColor Cyan
Write-Host "  open-dictate start              Start the daemon"
Write-Host "  open-dictate status             Show configuration"
Write-Host "  open-dictate set-hotkey f24     Change hotkey"
Write-Host "  open-dictate --help             Show all commands"
Write-Host ""
Write-Host "Default hotkey: Right Ctrl (hold to record, release to transcribe)" -ForegroundColor Yellow
Write-Host ""

# Offer to start now
$startNow = Read-Host "Start open-dictate now? (y/n)"
if ($startNow -eq 'y') {
    & "$BinDir\open-dictate.exe" start
}
