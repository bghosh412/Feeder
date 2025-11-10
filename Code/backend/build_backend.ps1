# Fish Feeder Backend Build Script (PowerShell)
# Usage: Run in backend folder. Choose mode: 'api' or 'battery'
# Example: .\build_backend.ps1 api

param(
    [string]$mode = "api"
)

Write-Host "\n=== Fish Feeder Backend Build Script ===\n" -ForegroundColor Cyan

# Step 1: Download MicroPython dependencies
Write-Host "Step 1: Downloading MicroPython dependencies..." -ForegroundColor Yellow
npm run download:deps

# Step 2: Build dist folder for selected mode
Write-Host "\nStep 2: Building dist folder for mode: $mode..." -ForegroundColor Yellow
if ($mode -eq "battery") {
    npm run build:battery
} else {
    npm run build:api
}

# Step 3: Show dist folder contents
Write-Host "\nStep 3: Listing dist folder contents..." -ForegroundColor Yellow
Get-ChildItem -Recurse .\dist | Format-Table

Write-Host "\n=== Build Complete! ===\n" -ForegroundColor Green
Write-Host "Deploy files from the dist folder to your ESP32 using ampy or mpremote." -ForegroundColor Cyan
Write-Host "See dist/README.md for upload instructions.\n" -ForegroundColor Cyan
