"""
Performance Attribution API - Factor breakdown for picks
"""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.performance_attribution import PerformanceAttribution

router = APIRouter(prefix = " / api / attribution", tags = ["attribution"])

@router.get(" / pick / {pick_id}")
async def analyze_pick_attribution(pick_id: int,
 db: AsyncSession = Depends(get_db)):
 """Analyze performance attribution for a specific pick."""
 try:
 attribution = PerformanceAttribution()
 analysis = await attribution.analyze_pick_attribution(db, pick_id)
 return analysis
 except Exception as e:
 return {
 "status": "error",
 "message": str(e),
 "timestamp": datetime.now(timezone.utc).isoformat()
 }

@router.get(" / batch / {sport_id}")
async def analyze_batch_attribution(sport_id: int = Path(description = "Sport ID"),
 limit: int = Query(default = 50, description = "Number of picks to analyze"),
 db: AsyncSession = Depends(get_db)):
 """Analyze performance attribution for multiple picks."""
 try:
 attribution = PerformanceAttribution()
 batch_analysis = await attribution.analyze_batch_attribution(db, sport_id, limit)
 return batch_analysis
 except Exception as e:
 return {
 "status": "error",
 "message": str(e),
 "timestamp": datetime.now(timezone.utc).isoformat()
 }
