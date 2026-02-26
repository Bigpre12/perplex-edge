# Perplex Edge Frontend Deployment Script (Vercel)
Write-Host "Initializing Vercel Deployment for Perplex Edge Frontend..." -ForegroundColor Cyan

# Install Vercel CLI globally if not already present
Write-Host "Checking for Vercel CLI..."
npm install -g vercel

# Execute the production deployment
Write-Host "Deploying to Vercel..." -ForegroundColor Yellow
vercel --prod

Write-Host "Frontend Deployment Complete! Your application is live." -ForegroundColor Green
