# install.ps1 - Cross-platform zero-privilege installer for Windows GitHub Copilot CLI
$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Installing project-bootstrap GitHub Copilot CLI Extension" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$CopilotExtDir = Join-Path $HOME ".copilot\extensions\project-bootstrap"
$ParentDir = Split-Path -Parent $CopilotExtDir

# 1. Ensure ~/.copilot/extensions directory exists
if (-not (Test-Path $ParentDir)) {
    Write-Host "Creating Copilot extensions root: $ParentDir" -ForegroundColor Gray
    New-Item -ItemType Directory -Force -Path $ParentDir | Out-Null
}

# 2. Remove existing link or junction if present
if (Test-Path $CopilotExtDir) {
    Write-Host "Removing existing extension target at $CopilotExtDir..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $CopilotExtDir
}

# 3. Create NTFS Directory Junction (Works on Windows without Administrator privileges!)
try {
    New-Item -ItemType Junction -Path $CopilotExtDir -Target $PSScriptRoot | Out-Null
    Write-Host "✅ NTFS Junction created:" -ForegroundColor Green
    Write-Host "   Target: $CopilotExtDir" -ForegroundColor White
    Write-Host "   Source: $PSScriptRoot" -ForegroundColor White
} catch {
    Write-Host "⚠️  Junction creation encountered an issue: $_" -ForegroundColor Yellow
    Write-Host "Attempting fallback to directory copy..." -ForegroundColor Yellow
    Copy-Item -Recurse -Force $PSScriptRoot $CopilotExtDir
    Write-Host "✅ Extension directory copied to $CopilotExtDir" -ForegroundColor Green
}

Write-Host ""
Write-Host "Installation complete! To use with Copilot CLI:" -ForegroundColor Green
Write-Host "  1. Open PowerShell in any project directory" -ForegroundColor White
Write-Host "  2. Run 'copilot'" -ForegroundColor White
Write-Host "  3. Ask Copilot: 'Bootstrap this repo as a software engineering workspace'" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Cyan
