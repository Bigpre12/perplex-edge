# Frontend Deployment Instructions

## Prerequisites
✅ Railway CLI installed (v4.29.0)

## Steps to Deploy Frontend

### 1. Login to Railway
Open PowerShell and run:
```powershell
cd c:\Users\preio\perplex-edge\frontend
railway login
```
This will open a browser window for authentication.

### 2. Link the Project
```powershell
railway link
```
This will link the frontend directory to a Railway project.

### 3. Deploy the Frontend
```powershell
railway up
```
This will build and deploy the frontend to Railway.

### 4. Verify Deployment
After deployment, Railway will provide a URL like:
`https://<project-name>-<random>.up.railway.app`

## What's Been Fixed
- ✅ Added Railway configuration (railway.toml)
- ✅ Fixed hardcoded localhost URLs
- ✅ Guarded all console.log statements with DEV check
- ✅ Nginx configured to proxy API requests to backend

## Expected Behavior
Once deployed, the frontend will:
- Serve the React app via nginx
- Proxy all `/api/*` requests to the backend
- Use the production backend URL automatically

## Current Status
- Backend: ✅ Running at https://railway-engine-production.up.railway.app
- Frontend: ⏳ Ready for deployment
