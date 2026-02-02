"""Startup script for Windows compatibility with psycopg async."""
import asyncio
import os
import sys
from pathlib import Path

# Fix Windows asyncio event loop BEFORE any other imports
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import uvicorn

if __name__ == "__main__":
    # Get the backend directory for reload watching
    backend_dir = Path(__file__).parent
    
    # Enable reload only in development (disable in production/Railway)
    is_dev = os.getenv("ENV", "dev") == "dev"
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",  # Clear reload messages
        reload=is_dev,
        reload_includes=["*.py", "*.json", "*.csv"] if is_dev else None,  # Watch Python and data files
        reload_dirs=[str(backend_dir)] if is_dev else None,  # Watch backend directory
        reload_excludes=["__pycache__", ".git", "*.pyc", ".pytest_cache"] if is_dev else None,  # Exclude noisy dirs
        loop="asyncio",
    )
