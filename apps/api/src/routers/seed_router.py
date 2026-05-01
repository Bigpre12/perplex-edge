# apps/api/src/routers/seed_router.py
import os
import asyncio
from fastapi import APIRouter, Header, HTTPException, Depends
from sqlalchemy import text
from db.session import AsyncSessionLocal
from services.seed_scheduler import run_seed_pipeline

router = APIRouter(prefix="/api/seed", tags=["seed"])

ADMIN_SECRET = os.getenv("ADMIN_SECRET")

async def verify_admin(x_admin_key: str = Header(None)):
    """
    Security middleware to ensure only authorized admins can trigger seeding.
    """
    if not ADMIN_SECRET:
        # If no secret is configured, deny all requests for safety
        raise HTTPException(status_code=500, detail="ADMIN_SECRET environment variable is missing on server.")
    if x_admin_key != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Access denied: Invalid X-Admin-Key.")

@router.post("/run")
async def trigger_seed_pipeline(admin: None = Depends(verify_admin)):
    """
    Manually trigger the full PrizePicks -> Grader -> Hit Rate pipeline.
    Runs as a background task to prevent request timeouts.
    """
    asyncio.create_task(run_seed_pipeline())
    return {
        "status": "triggered",
        "message": "PrizePicks seed pipeline execution started in background."
    }

@router.get("/status")
async def get_seed_status():
    """
    Return summary metrics from the pp_projections_staging table.
    """
    async with AsyncSessionLocal() as session:
        try:
            res = await session.execute(text("""
                SELECT 
                    COUNT(*) as total,
                    COALESCE(SUM(CASE WHEN graded = TRUE THEN 1 ELSE 0 END), 0) as graded,
                    COALESCE(SUM(CASE WHEN graded = FALSE THEN 1 ELSE 0 END), 0) as ungraded
                FROM pp_projections_staging
            """))
            stats = res.fetchone()
            
            # Hit rate count
            hr_res = await session.execute(text("SELECT COUNT(*) FROM player_mc_hit_rates"))
            hr_count = hr_res.scalar() or 0
            
            return {
                "projections": {
                    "total": stats.total or 0,
                    "graded": int(stats.graded),
                    "ungraded": int(stats.ungraded),
                },
                "hit_rates_tracked": hr_count,
                "engine": "v3-brains-empirical"
            }
        except Exception as e:
            return {
                "error": "Table not initialized or query failed",
                "details": str(e)
            }
