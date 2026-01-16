# sync weekly notes to OneDrive and network share
# double-click this file or create a shortcut to it

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Push-Location $scriptDir
try {
    Write-Host "Syncing weekly notes..." -ForegroundColor Cyan
    Write-Host ""
    uv run export-weekly --sync --force
    Write-Host ""
    Write-Host "Done! Notes available at:" -ForegroundColor Green
    Write-Host "  Network: \\RBO-S1\mbospace\foconnell\weekly_meeting" -ForegroundColor Yellow
    Write-Host "  OneDrive: synced automatically" -ForegroundColor Yellow
    Write-Host ""
} finally {
    Pop-Location
}

Write-Host "Press any key to close..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
