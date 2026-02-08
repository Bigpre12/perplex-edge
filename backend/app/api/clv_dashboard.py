"""
CLV Dashboard API - Track Closing Line Value and prove model edge
"""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.clv_tracker import CLVTracker

router = APIRouter(prefix = " / api / clv", tags = ["clv"])

@router.get(" / dashboard")
async def get_clv_dashboard(sport_id: int = Query(default = 30, description = "Sport ID filter"),
 days_back: int = Query(default = 30, description = "Days to analyze"),
 db: AsyncSession = Depends(get_db)):
 """Get comprehensive CLV dashboard data."""
 try:
 tracker = CLVTracker()
 dashboard_data = await tracker.get_clv_dashboard(db, sport_id, days_back)
 return dashboard_data
 except Exception as e:
 return {
 "status": "error",
 "message": str(e),
 "timestamp": datetime.now(timezone.utc).isoformat()
 }

@router.get(" / leaderboard")
async def get_clv_leaderboard(sport_id: int = Query(default = None, description = "Sport ID filter"),
 min_bets: int = Query(default = 10, description = "Minimum bets to qualify"),
 db: AsyncSession = Depends(get_db)):
 """Get CLV leaderboard for top performers."""
 try:
 tracker = CLVTracker()
 leaderboard_data = await tracker.get_clv_leaderboard(db, sport_id, min_bets)
 return leaderboard_data
 except Exception as e:
 return {
 "status": "error",
 "message": str(e),
 "timestamp": datetime.now(timezone.utc).isoformat()
 }

@router.get(" / track / {pick_id}")
async def track_pick_clv(pick_id: int,
 closing_odds: int = Query(default = None, description = "Closing odds for CLV calculation"),
 db: AsyncSession = Depends(get_db)):
 """Track CLV for a specific pick."""
 try:
 tracker = CLVTracker()
 clv_data = await tracker.track_pick_clv(db, pick_id, closing_odds)
 return clv_data
 except Exception as e:
 return {
 "status": "error",
 "message": str(e),
 "timestamp": datetime.now(timezone.utc).isoformat()
 }
