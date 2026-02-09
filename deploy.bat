@echo off
echo 🚀 Railway Deployment Script
echo ========================

echo.
echo Step 1: Login to Railway
echo Please run this command in PowerShell as Administrator:
echo Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
echo.
echo Then run: railway login
echo.

echo Step 2: Link your project
echo Run: railway link
echo.

echo Step 3: Deploy to Railway
echo Run: railway up
echo.

echo Step 4: Set Environment Variables
echo Run these commands:
echo railway variables set DATABASE_URL="your_railway_postgres_url"
echo railway variables set THE_ODDS_API_KEY="your_odds_api_key"
echo railway variables set SPORTSDATA_API_KEY="your_sportsdata_api_key"
echo railway variables set ENVIRONMENT="production"
echo.

echo Step 5: Verify Deployment
echo Run: railway status
echo.
echo Test your deployment:
echo curl https://your-app-name.railway.app/health
echo curl https://your-app-name.railway.app/immediate/picks
echo.

echo 🎉 Your sports betting platform will be live!
echo ========================
pause
