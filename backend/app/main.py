"""
Main FastAPI application for the sports betting system
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.immediate_working import router
from app.api.validation_endpoints import router as validation_router
from app.api.track_record_endpoints import router as track_record_router
from app.api.model_status_endpoints import router as model_status_router

app = FastAPI(
    title="Sports Betting Intelligence API",
    description="Comprehensive sports betting analytics and intelligence platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the immediate working router
app.include_router(router, prefix="/immediate", tags=["immediate"])

# Include the validation router
app.include_router(validation_router, prefix="/validation", tags=["validation"])

# Include the track record router
app.include_router(track_record_router, prefix="/track-record", tags=["track-record"])

# Include the model status router
app.include_router(model_status_router, prefix="/status", tags=["status"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Sports Betting Intelligence API", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from datetime import datetime, timezone
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat(), "version": "1.0.2"}

if __name__ == "__main__":
    import uvicorn
    # Use Railway's PORT or default to 8000
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
