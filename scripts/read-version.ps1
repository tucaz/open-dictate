# open-dictate Version Reader
# Reads the VERSION from src/version.py
#
# Usage:
#   .\scripts\read-version.ps1
#   Returns: 0.13.0

$versionFile = "$PSScriptRoot\..\src\version.py"

if (-not (Test-Path $versionFile)) {
    Write-Error "version.py not found at $versionFile"
    exit 1
}

$content = Get-Content $versionFile -Raw

# Match VERSION = "x.y.z" or VERSION = 'x.y.z'
if ($content -match 'VERSION\s*=\s*["''](.+?)["'']') {
    $version = $matches[1]
    Write-Output $version
} else {
    Write-Error "Could not find VERSION in $versionFile"
    exit 1
}
