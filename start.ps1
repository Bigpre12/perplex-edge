# start.ps1
Write-Host "Starting Perplex Edge..." -ForegroundColor Cyan

# 1. Kill any existing processes on ports 8000 and 3300
Write-Host "Cleaning up ports 8000 and 3300..." -ForegroundColor Gray
$ports = @(3300, 3000, 8000)
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
    "cd 'C:\Users\preio\OneDrive\Documents\Untitled\perplex_engine\perplex-edge\apps\api\src'; ..\..\..\.venv\Scripts\python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
) -WindowStyle Normal

Start-Sleep -Seconds 2

# 3. Start Next.js in a new window
Write-Host "Launching Frontend (Next.js)..." -ForegroundColor Green
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd 'C:\Users\preio\OneDrive\Documents\Untitled\perplex_engine\perplex-edge\apps\web'; npm run dev"
) -WindowStyle Normal

Write-Host "`nAll servers are starting!" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Yellow # Typical Next.js dev port
Write-Host "Backend:  http://localhost:8000/api/health" -ForegroundColor Yellow
Write-Host "Docs:     http://localhost:8000/docs" -ForegroundColor Yellow
