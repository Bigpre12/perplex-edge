# Perplex Edge Backend Deployment Script (Google Cloud Run)
Write-Host "Initializing Google Cloud Run Deployment for Perplex Edge..." -ForegroundColor Cyan

# Ensure the user is authenticated to GCP
Write-Host "Checking GCP authentication..."
gcloud auth login

# Define project and region variables (User can adjust these)
$PROJECT_ID = "perplex-edge-production"
$REGION = "us-central1"
$SERVICE_NAME = "perplex-edge-backend"

# Build and submit the Docker image via Google Cloud Build
Write-Host "Submitting Docker Build to Google Cloud..." -ForegroundColor Yellow
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy the tagged image to Cloud Run
Write-Host "Deploying to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $SERVICE_NAME `
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME `
  --platform managed `
  --region $REGION `
  --allow-unauthenticated `
  --port 8080 `
  --memory 1Gi

Write-Host "Backend Deployment Complete!" -ForegroundColor Green
