# open-dictate Windows Release Builder
# Usage: .\scripts\build-release.ps1 [-Version "1.0.0"]
#
# This script:
# 1. Builds open-dictate.exe using PyInstaller
# 2. Downloads whisper-cli.exe + required DLLs
# 3. Packages everything into a release folder
# 4. Creates a zip file for distribution

param(
    [string]$Version = $null,
    [switch]$SkipBuild = $false,
    [string]$OutputDir = "$PSScriptRoot\..\release"
)

$ErrorActionPreference = "Stop"

# Colors for output
function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Success($msg) { Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Warning($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Error($msg) { Write-Host "[ERROR] $msg" -ForegroundColor Red }

# Get version from git or parameter
function Get-Version {
    param([string]$RequestedVersion)
    
    if ($RequestedVersion) {
        return $RequestedVersion
    }
    
    # Try to get from git tag
    try {
        $gitTag = git describe --tags --exact-match 2>$null
        if ($gitTag) {
            return $gitTag -replace '^v', ''
        }
    } catch {}
    
    # Try to get from version.py
    $versionFile = "$PSScriptRoot\..\src\version.py"
    if (Test-Path $versionFile) {
        $content = Get-Content $versionFile -Raw
        # Match VERSION = "x.y.z" or VERSION = 'x.y.z'
        if ($content -match 'VERSION\s*=\s*["''](.+?)["'']') {
            return $matches[1]
        }
    }
    
    return "0.0.0"
}

# Create release directory structure
function Initialize-ReleaseDir($ReleaseDir) {
    Write-Info "Creating release directory: $ReleaseDir"
    
    if (Test-Path $ReleaseDir) {
        Write-Info "Cleaning existing release directory..."
        Remove-Item -Path $ReleaseDir -Recurse -Force
    }
    
    New-Item -ItemType Directory -Path $ReleaseDir -Force | Out-Null
    New-Item -ItemType Directory -Path "$ReleaseDir\bin" -Force | Out-Null
    
    return $ReleaseDir
}

# Build open-dictate.exe
function Build-Executable($ProjectRoot) {
    Write-Info "Building open-dictate.exe..."
    
    Push-Location $ProjectRoot
    try {
        # Run build.py - capture output but don't treat stderr as error
        $process = Start-Process -FilePath "python" -ArgumentList "build.py" -Wait -PassThru -NoNewWindow
        $exitCode = $process.ExitCode
        
        if ($exitCode -ne 0) {
            Write-Error "Build failed with exit code $exitCode"
            exit 1
        }
        
        if (-not (Test-Path "$ProjectRoot\dist\open-dictate.exe")) {
            Write-Error "Build completed but executable not found at $ProjectRoot\dist\open-dictate.exe"
            exit 1
        }
        
        Write-Success "Build successful"
        return "$ProjectRoot\dist\open-dictate.exe"
    } finally {
        Pop-Location
    }
}

# Download whisper-cli and dependencies
function Download-Whisper($ReleaseDir) {
    Write-Info "Downloading whisper-cli and dependencies..."
    
    $binDir = "$ReleaseDir\bin"
    $whisperVersion = "v1.8.3"
    $whisperUrl = "https://github.com/ggml-org/whisper.cpp/releases/download/$whisperVersion/whisper-bin-x64.zip"
    $tempZip = "$env:TEMP\whisper-bin-x64.zip"
    $tempDir = "$env:TEMP\whisper-bin-release"
    
    # Download
    Write-Info "Downloading from $whisperUrl..."
    try {
        Invoke-WebRequest -Uri $whisperUrl -OutFile $tempZip -UseBasicParsing
    } catch {
        Write-Error "Failed to download whisper-cli: $_"
        exit 1
    }
    
    # Extract
    Write-Info "Extracting whisper-cli..."
    if (Test-Path $tempDir) {
        Remove-Item -Path $tempDir -Recurse -Force
    }
    Expand-Archive -Path $tempZip -DestinationPath $tempDir -Force
    
    # Copy required files
    $sourceDir = "$tempDir\Release"
    $requiredFiles = @(
        "whisper-cli.exe",
        "whisper.dll",
        "ggml.dll",
        "ggml-base.dll",
        "ggml-cpu.dll",
        "SDL2.dll"
    )
    
    foreach ($file in $requiredFiles) {
        $source = "$sourceDir\$file"
        if (Test-Path $source) {
            Copy-Item $source $binDir
            Write-Info "Copied $file"
        } else {
            Write-Warning "Missing: $file"
        }
    }
    
    # Cleanup
    Remove-Item $tempZip -Force -ErrorAction SilentlyContinue
    Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    
    Write-Success "whisper-cli downloaded"
}

# Copy additional files to release
function Copy-ReleaseFiles($ProjectRoot, $ReleaseDir) {
    Write-Info "Copying release files..."
    
    # README
    if (Test-Path "$ProjectRoot\README.md") {
        Copy-Item "$ProjectRoot\README.md" $ReleaseDir
    }
    
    # License (if exists)
    if (Test-Path "$ProjectRoot\LICENSE") {
        Copy-Item "$ProjectRoot\LICENSE" $ReleaseDir
    }
    
    # Install script
    if (Test-Path "$ProjectRoot\scripts\install.ps1") {
        Copy-Item "$ProjectRoot\scripts\install.ps1" "$ReleaseDir\install.ps1"
    }
    
    # Icon for shortcuts
    if (Test-Path "$ProjectRoot\icon.ico") {
        Copy-Item "$ProjectRoot\icon.ico" "$ReleaseDir\bin\icon.ico"
        Write-Info "Copied icon.ico"
    }
    
    Write-Success "Files copied"
}

# Calculate file hash
function Get-FileHashString($Path) {
    $hashObj = Get-FileHash -Path $Path -Algorithm SHA256
    return $hashObj.Hash
}

# Create release info file
function Write-ReleaseInfo($ReleaseDir, $Version, $ExePath) {
    Write-Info "Creating release info..."
    
    $exeHash = Get-FileHashString $ExePath
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    $infoLines = @(
        "open-dictate Windows Release"
        "=========================="
        ""
        "Version: $Version"
        "Built: $timestamp"
        ""
        "Files"
        "-----"
        "- open-dictate.exe (SHA256: $exeHash)"
        "- bin/whisper-cli.exe + dependencies"
        "- README.md"
        "- install.ps1"
        ""
        "Installation"
        "------------"
        "Option 1: Run install.ps1 for automatic installation"
        "Option 2: Copy bin\* to %LOCALAPPDATA%\open-dictate\bin\ and run open-dictate.exe"
        ""
        "Usage"
        "-----"
        "open-dictate start              Start the daemon"
        "open-dictate status             Check configuration"
        "open-dictate set-hotkey f13     Change hotkey"
        "open-dictate --help             Show all commands"
        ""
        "Requirements"
        "------------"
        "- Windows 10 or 11"
        "- Microphone access enabled"
        ""
        "Attribution"
        "-----------"
        "Original macOS app: https://github.com/human37/open-wispr"
        "Windows port: https://github.com/tucaz/open-dictate"
        "Speech recognition: https://github.com/ggerganov/whisper.cpp"
    )
    $info = $infoLines -join "`n"
    
    $info | Out-File -FilePath "$ReleaseDir\RELEASE.txt" -Encoding UTF8
    
    # Also create a JSON version for programmatic access
    $jsonInfo = @{
        version = $Version
        built = $timestamp
        files = @{
            "open-dictate.exe" = @{ sha256 = $exeHash }
        }
    } | ConvertTo-Json
    
    $jsonInfo | Out-File -FilePath "$ReleaseDir\release.json" -Encoding UTF8
    
    Write-Success "Release info created"
}

# Create zip archive
function Create-Zip($ReleaseDir, $Version) {
    Write-Info "Creating zip archive..."
    
    $zipName = "open-dictate-windows-v$Version.zip"
    $zipPath = "$ReleaseDir\..\$zipName"
    
    # Remove existing zip
    if (Test-Path $zipPath) {
        Remove-Item $zipPath -Force
    }
    
    # Create zip (using Compress-Archive)
    $parentDir = Split-Path $ReleaseDir -Parent
    $dirName = Split-Path $ReleaseDir -Leaf
    
    Compress-Archive -Path "$ReleaseDir\*" -DestinationPath $zipPath -Force
    
    Write-Success "Created: $zipName"
    
    # Calculate zip hash
    $zipHash = Get-FileHashString $zipPath
    Write-Info "Zip SHA256: $zipHash"
    
    return $zipPath
}

# Print summary
function Write-Summary($Version, $ReleaseDir, $ZipPath, $ExePath) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Release Build Complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Version: $Version" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Output Files:" -ForegroundColor Cyan
    Write-Host "  Release folder: $ReleaseDir"
    Write-Host "  Zip archive:    $ZipPath"
    Write-Host "  Executable:     $ExePath"
    Write-Host ""
    Write-Host "Contents:" -ForegroundColor Cyan
    Get-ChildItem $ReleaseDir | ForEach-Object {
        $size = if ($_.PSIsContainer) { "<dir>" } else { "$([math]::Round($_.Length/1KB, 1)) KB" }
        Write-Host "  $($_.Name) ($size)"
    }
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "  1. Test the executable: $ReleaseDir\open-dictate.exe start"
    Write-Host "  2. Upload to GitHub Releases: $ZipPath"
    Write-Host ""
}

# ==================== Main ====================

Write-Host ""
Write-Host "open-dictate Windows Release Builder" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Determine version
$Version = Get-Version -RequestedVersion $Version
Write-Info "Building version: $Version"

# Project root
$ProjectRoot = Resolve-Path "$PSScriptRoot\.."
Write-Info "Project root: $ProjectRoot"

# Release directory
$ReleaseDir = "$OutputDir\open-dictate-v$Version"
Write-Info "Release directory: $ReleaseDir"

# Initialize
Initialize-ReleaseDir $ReleaseDir

# Build executable (or skip if requested)
if (-not $SkipBuild) {
    $ExePath = Build-Executable $ProjectRoot
} else {
    Write-Info "Skipping build, using existing executable..."
    $ExePath = "$ProjectRoot\dist\open-dictate.exe"
    if (-not (Test-Path $ExePath)) {
        Write-Error "No existing executable found at $ExePath"
        exit 1
    }
}

# Copy executable
Copy-Item $ExePath $ReleaseDir
Write-Success "Copied open-dictate.exe"

# Download whisper-cli
Download-Whisper $ReleaseDir

# Copy additional files
Copy-ReleaseFiles $ProjectRoot $ReleaseDir

# Create release info
$ExeInRelease = "$ReleaseDir\open-dictate.exe"
Write-ReleaseInfo $ReleaseDir $Version $ExeInRelease

# Create zip
$ZipPath = Create-Zip $ReleaseDir $Version

# Summary
Write-Summary $Version $ReleaseDir $ZipPath $ExeInRelease

Write-Success "Done!"
