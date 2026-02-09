# Railway Deployment PowerShell Script
Write-Host "🚀 Railway Deployment Script" -ForegroundColor Green
Write-Host "========================" -ForegroundColor Green

Write-Host ""
Write-Host "Step 1: Installing Railway CLI..." -ForegroundColor Yellow
try {
    npm install -g @railway/cli
    Write-Host "✅ Railway CLI installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install Railway CLI" -ForegroundColor Red
    Write-Host "Please install Node.js and npm first" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 2: Login to Railway..." -ForegroundColor Yellow
Write-Host "Running: railway login" -ForegroundColor Cyan
try {
    railway login
    Write-Host "✅ Successfully logged into Railway!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to login to Railway" -ForegroundColor Red
    Write-Host "Please check your internet connection" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 3: Link project..." -ForegroundColor Yellow
Write-Host "Running: railway link" -ForegroundColor Cyan
try {
    railway link
    Write-Host "✅ Project linked successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to link project" -ForegroundColor Red
    Write-Host "Make sure you're in the correct directory" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 4: Deploy to Railway..." -ForegroundColor Yellow
Write-Host "Running: railway up" -ForegroundColor Cyan
try {
    railway up
    Write-Host "✅ Deployment started successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to deploy" -ForegroundColor Red
    Write-Host "Check your Procfile and dependencies" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 5: Set Environment Variables..." -ForegroundColor Yellow
Write-Host "Please set these variables in Railway dashboard:" -ForegroundColor Cyan
Write-Host "  DATABASE_URL=<Railway PostgreSQL URL>" -ForegroundColor White
Write-Host "  THE_ODDS_API_KEY=<from the-odds-api.com>" -ForegroundColor White
Write-Host "  SPORTSDATA_API_KEY=<from sportsdata.io>" -ForegroundColor White
Write-Host "  ENVIRONMENT=production" -ForegroundColor White

Write-Host ""
Write-Host "Step 6: Verify Deployment..." -ForegroundColor Yellow
Write-Host "Run: railway status" -ForegroundColor Cyan
Write-Host "Test: curl https://your-app-name.railway.app/health" -ForegroundColor Cyan
Write-Host "Test: curl https://your-app-name.railway.app/immediate/picks" -ForegroundColor Cyan

Write-Host ""
Write-Host "🎉 Your sports betting platform will be live!" -ForegroundColor Green
Write-Host "========================" -ForegroundColor Green

Read-Host "Press Enter to exit"
