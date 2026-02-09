"""
Main FastAPI application for the sports betting system
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.immediate_working import router

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

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Sports Betting Intelligence API", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": "2025-02-09T12:00:00Z"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
