# start-api.ps1
# LUCRIX Backend Process Manager

Write-Host "--- LUCRIX API PROCESS MANAGER ---" -ForegroundColor Cyan

# 1. Load .env if it exists
if (Test-Path ".env") {
    Write-Host "Loading environment from .env..." -ForegroundColor Gray
    Get-Content .env | ForEach-Object {
        if ($_ -match "^(?<name>[^#\s=]+)=(?<value>.*)$") {
            $name = $Matches.name.Trim()
            $value = $Matches.value.Trim().Trim("'").Trim('"')
            [System.Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
}

# 2. Main Execution Loop (Auto-Restart)
$RestartCount = 0

while ($true) {
    Write-Host "Starting Lucrix API (Attempt $($RestartCount + 1))..." -ForegroundColor Green
    
    # Run the python app
    cd src
    py main.py
    cd ..
    
    $ExitCode = $LASTEXITCODE
    Write-Host "API Process Exited with code $ExitCode" -ForegroundColor Yellow
    
    if ($ExitCode -eq 0) {
        Write-Host "Clean shutdown. Exiting manager." -ForegroundColor Cyan
        break
    }
    
    $RestartCount++
    Write-Host "Waiting 5 seconds before restart..." -ForegroundColor Gray
    Start-Sleep -Seconds 5
}
