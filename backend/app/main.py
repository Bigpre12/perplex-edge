"""Minimal FastAPI backend - no database, no scheduler."""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Perplex Engine",
    description="Sports betting analytics platform",
    version="0.1.0",
)

# CORS - allow all origins for now
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Perplex Engine API",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/ping")
async def ping():
    """Simple ping endpoint."""
    return {"ping": "pong"}


@app.get("/api/health")
async def api_health():
    """API health check (for frontend compatibility)."""
    return {"status": "ok", "api": True}
