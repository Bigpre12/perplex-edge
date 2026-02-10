"""
Frontend FastAPI application for Sports Betting Intelligence
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI(title="Sports Betting Intelligence Frontend")

# Serve static files (if any exist)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    """Serve the main HTML file"""
    return FileResponse("index.html")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "frontend", "timestamp": "2026-02-10T01:58:00Z"}

if __name__ == "__main__":
    import uvicorn
    # Always use Railway's PORT
    port = int(os.environ.get("PORT", 8000))
    print(f"Frontend starting on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
