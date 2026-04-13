# start.ps1
Write-Host "Starting Perplex Edge..." -ForegroundColor Cyan

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1. Kill any existing processes on ports 8000 and 3300
Write-Host "Cleaning up ports 8000 and 3300..." -ForegroundColor Gray
$ports = @(3300, 3000, 8080)
foreach ($port in $ports) {
    $proc = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($proc) {
        foreach ($p in $proc) {
            try {
                Stop-Process -Id $p.OwningProcess -Force -ErrorAction SilentlyContinue
            }
            catch {}
        }
    }
}

# 2. Start FastAPI in a new window
Write-Host "Launching Backend (FastAPI)..." -ForegroundColor Green
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$repoRoot'; py run_api.py"
) -WindowStyle Normal

Start-Sleep -Seconds 2

# 3. Start Next.js in a new window
Write-Host "Cleaning Next.js cache..." -ForegroundColor Gray
Remove-Item -Path (Join-Path $repoRoot "apps\web\.next") -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "Launching Frontend (Next.js)..." -ForegroundColor Green
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$repoRoot'; npm run web"
) -WindowStyle Normal

# 4. Wait for Backend Health
Write-Host "Waiting for Backend Health..." -ForegroundColor Cyan
$maxRetries = 10
$retryCount = 0
$healthy = $false

while ($retryCount -lt $maxRetries -and -not $healthy) {
    try {
        $resp = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing -ErrorAction Stop
        if ($resp.StatusCode -eq 200) {
            $healthy = $true
        }
    }
    catch {
        $retryCount++
        Start-Sleep -Seconds 2
    }
}

if ($healthy) {
    Write-Host "`nAll servers are stabilized!" -ForegroundColor Green
    Write-Host "Frontend: http://localhost:3000" -ForegroundColor Yellow
    Write-Host "Backend:  http://localhost:8080/api/health" -ForegroundColor Yellow
} else {
    Write-Host "`nBackend failed to stabilize. Check server_boot.log" -ForegroundColor Red
}
