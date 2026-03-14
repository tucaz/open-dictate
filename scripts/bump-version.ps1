# open-dictate Version Bumper
# Usage:
#   .\scripts\bump-version.ps1
#   .\scripts\bump-version.ps1 -Part minor
#   .\scripts\bump-version.ps1 -Version 1.2.3
#   .\scripts\bump-version.ps1 -DryRun
#
# Default behavior:
# - Reads src/version.py
# - Bumps the patch version (x.y.Z -> x.y.(Z+1))
# - Updates:
#   - src/version.py
#   - pyproject.toml
#   - scripts/install.ps1 fallback version

param(
    [ValidateSet("patch", "minor", "major")]
    [string]$Part = "patch",
    [string]$Version = $null,
    [switch]$DryRun = $false
)

$ErrorActionPreference = "Stop"

function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Success($msg) { Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Warning($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }

$repoRoot = Join-Path $PSScriptRoot ".."
$versionFile = Join-Path $repoRoot "src\version.py"
$pyprojectFile = Join-Path $repoRoot "pyproject.toml"
$installScriptFile = Join-Path $PSScriptRoot "install.ps1"

foreach ($file in @($versionFile, $pyprojectFile, $installScriptFile)) {
    if (-not (Test-Path $file)) {
        throw "Required file not found: $file"
    }
}

function Get-CurrentVersion {
    param([string]$FilePath)

    $content = Get-Content $FilePath -Raw
    if ($content -match 'VERSION\s*=\s*["''](\d+\.\d+\.\d+)["'']') {
        return $matches[1]
    }

    throw "Could not find VERSION in $FilePath"
}

function Get-NextVersion {
    param(
        [string]$CurrentVersion,
        [string]$BumpPart
    )

    $parts = $CurrentVersion.Split(".")
    if ($parts.Length -ne 3) {
        throw "Expected semantic version x.y.z, got: $CurrentVersion"
    }

    $major = [int]$parts[0]
    $minor = [int]$parts[1]
    $patch = [int]$parts[2]

    switch ($BumpPart) {
        "major" { return "{0}.0.0" -f ($major + 1) }
        "minor" { return "{0}.{1}.0" -f $major, ($minor + 1) }
        default { return "{0}.{1}.{2}" -f $major, $minor, ($patch + 1) }
    }
}

function Replace-Once {
    param(
        [string]$Content,
        [string]$Pattern,
        [string]$Replacement,
        [string]$Label
    )

    $updated = [regex]::Replace($Content, $Pattern, $Replacement, 1)
    if ($updated -eq $Content) {
        throw "Could not update $Label"
    }

    return $updated
}

$currentVersion = Get-CurrentVersion -FilePath $versionFile
$targetVersion = if ($Version) { $Version } else { Get-NextVersion -CurrentVersion $currentVersion -BumpPart $Part }

if ($targetVersion -notmatch '^\d+\.\d+\.\d+$') {
    throw "Version must match x.y.z, got: $targetVersion"
}

Write-Info "Current version: $currentVersion"
Write-Info "Target version:  $targetVersion"

$versionContent = Get-Content $versionFile -Raw
$pyprojectContent = Get-Content $pyprojectFile -Raw
$installScriptContent = Get-Content $installScriptFile -Raw

$updatedVersionContent = Replace-Once `
    -Content $versionContent `
    -Pattern 'VERSION\s*=\s*["'']\d+\.\d+\.\d+["'']' `
    -Replacement "VERSION = `"$targetVersion`"" `
    -Label "src/version.py"

$updatedPyprojectContent = Replace-Once `
    -Content $pyprojectContent `
    -Pattern '(?m)^version = "\d+\.\d+\.\d+"\r?$' `
    -Replacement "version = `"$targetVersion`"" `
    -Label "pyproject.toml"

$updatedInstallScriptContent = Replace-Once `
    -Content $installScriptContent `
    -Pattern '(?m)^(\s*Write-Warning "Could not determine latest version, using )\d+\.\d+\.\d+(")\r?$' `
    -Replacement ('${1}' + $targetVersion + '${2}') `
    -Label "scripts/install.ps1 warning message"

$updatedInstallScriptContent = Replace-Once `
    -Content $updatedInstallScriptContent `
    -Pattern '(?m)^(\s*\$Version = ")\d+\.\d+\.\d+(")\r?$' `
    -Replacement ('${1}' + $targetVersion + '${2}') `
    -Label "scripts/install.ps1 fallback assignment"

if ($DryRun) {
    Write-Warning "Dry run only. No files were changed."
    return
}

Set-Content -Path $versionFile -Value $updatedVersionContent -NoNewline
Set-Content -Path $pyprojectFile -Value $updatedPyprojectContent -NoNewline
Set-Content -Path $installScriptFile -Value $updatedInstallScriptContent -NoNewline

Write-Success "Updated version files to $targetVersion"
Write-Host "  - src/version.py"
Write-Host "  - pyproject.toml"
Write-Host "  - scripts/install.ps1"
