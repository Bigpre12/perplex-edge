import asyncio
import logging
import sys

# Fix Windows asyncio event loop for psycopg - MUST be before any other imports
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import init_db
from app.api import api_router
from app.scheduler import start_background_tasks, stop_background_tasks

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting Perplex Engine...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Scheduler enabled: {settings.scheduler_enabled}")
    
    # Log masked database URL for debugging
    db_url = settings.database_url_async
    if "@" in db_url:
        masked_url = db_url.split("@")[0].rsplit(":", 1)[0] + ":***@" + db_url.split("@")[1]
    else:
        masked_url = "invalid-url-format"
    logger.info(f"Database URL: {masked_url}")
    
    try:
        await init_db()
        logger.info("Database connected successfully")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        logger.warning("App will start without database - some features unavailable")
    
    # Start background tasks if scheduler is enabled
    background_tasks = []
    if settings.scheduler_enabled:
        try:
            background_tasks = start_background_tasks()
            logger.info(f"Started {len(background_tasks)} background tasks")
        except Exception as e:
            logger.warning(f"Failed to start background tasks: {e}")
    else:
        logger.info("Scheduler disabled via SCHEDULER_ENABLED=false")
    
    logger.info("Perplex Engine started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Perplex Engine...")
    
    if background_tasks:
        await stop_background_tasks(background_tasks)
    
    logger.info("Perplex Engine shut down")


app = FastAPI(
    title="Perplex Engine",
    description="Sports betting analytics platform",
    version="0.1.0",
    docs_url="/docs",  # Always enable for debugging
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    # Check database connectivity
    db_status = "unknown"
    try:
        from sqlalchemy import text
        from app.core.database import get_engine
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)[:100]}"
    
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": "0.1.0",
        "database": db_status,
        "scheduler_enabled": settings.scheduler_enabled,
    }


@app.get("/ping")
async def ping():
    """Simple ping endpoint - no dependencies."""
    return {"ping": "pong"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Perplex Engine API",
        "docs": "/docs",
        "health": "/health",
        "ping": "/ping",
    }
