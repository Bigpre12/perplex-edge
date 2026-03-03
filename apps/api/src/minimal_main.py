"""
Minimal FastAPI app for Railway testing
"""
from fastapi import FastAPI
import os

app = FastAPI(title="Sports Betting API", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Sports Betting Intelligence API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": "2026-02-09T21:00:00Z"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
