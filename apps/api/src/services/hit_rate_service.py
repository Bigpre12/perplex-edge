import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func, desc, and_, case, Integer
from db.session import async_session_maker
from models.brain import ModelPick
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class HitRateService:
    """
    Historical Performance Engine (LUCRIX Analytics)
    Calculates Win Rate, ROI, Streaks and Player Accuracy.
    """

    async def get_summary(self, sport: str = "all") -> Dict[str, Any]:
        async with async_session_maker() as session:
            try:
                # 1. Base query for graded picks
                filters = [ModelPick.won != None]
                if sport != "all":
                    filters.append(ModelPick.sport_key == sport)
                
                # 2. Aggregates
                stmt = select(
                    func.count(ModelPick.id).label("total"),
                    func.sum(case((ModelPick.won == True, 1), else_=0)).label("wins"),
                    func.sum(ModelPick.profit_loss).label("net_profit"),
                    func.avg(ModelPick.ev_percentage).label("avg_ev")
                ).where(and_(*filters))
                
                res = await session.execute(stmt)
                summary = res.mappings().one()
                
                total = summary["total"] or 0
                wins = summary["wins"] or 0
                profit = summary["net_profit"] or 0.0
                
                # Accuracy & ROI
                win_rate = round((wins / total * 100), 1) if total > 0 else 0
                roi = round((profit / total * 100), 1) if total > 0 else 0 # Assuming 1 unit per bet
                
                # 3. Current Streak (Last 10)
                streak_stmt = select(ModelPick.won).where(and_(*filters)).order_by(desc(ModelPick.created_at)).limit(10)
                streak_res = await session.execute(streak_stmt)
                streak_history = streak_res.scalars().all()
                
                wins_in_streak = len([w for w in streak_history if w])
                streak_label = f"{wins_in_streak}/{len(streak_history)}" if streak_history else "0/0"
                
                return {
                    "overall_hit_rate": win_rate,
                    "roi": roi,
                    "graded_picks": total,
                    "streak": streak_label,
                    "status": "healthy" if total > 0 else "awaiting_ingest",
                    "last_updated": datetime.now(timezone.utc).isoformat()
                }
            except Exception as e:
                logger.error(f"HitRateService summary failed: {e}")
                return {"error": str(e), "status": "error"}

    async def get_player_breakdown(self, sport: str = "all", slate_only: bool = False) -> List[Dict[str, Any]]:
        async with async_session_maker() as session:
            try:
                # Basic breakdown grouping by player and market
                filters = [ModelPick.won != None]
                if sport != "all":
                    filters.append(ModelPick.sport_key == sport)
                
                # Group by player/stat
                stmt = select(
                    ModelPick.player_name,
                    ModelPick.stat_type,
                    func.count(ModelPick.id).label("sample_size"),
                    func.sum(case((ModelPick.won == True, 1), else_=0)).label("wins"),
                ).where(and_(*filters)).group_by(ModelPick.player_name, ModelPick.stat_type).order_by(desc("sample_size")).limit(100)
                
                res = await session.execute(stmt)
                rows = res.all()
                
                results = []
                for r in rows:
                    win_rate = round((r.wins / r.sample_size * 100), 1)
                    
                    # Confidence Tier
                    if r.sample_size >= 100:
                        tier = "High Confidence"
                    elif r.sample_size >= 25:
                        tier = "Reliable"
                    elif r.sample_size >= 10:
                        tier = "Early Read"
                    else:
                        tier = "Limited Sample"
                        
                    results.append({
                        "player": r.player_name,
                        "prop_type": r.stat_type,
                        "hit_rate": win_rate,
                        "sample_size": r.sample_size,
                        "confidence_badge": tier,
                        "streak": "N/A" # Simplified for breakdown
                    })
                
                return results
            except Exception as e:
                logger.error(f"HitRateService breakdown failed: {e}")
                return []

    async def get_trend_data(self, sport: str = "all") -> List[Dict[str, Any]]:
        """Provides daily win-rate trend for charts."""
        async with async_session_maker() as session:
            try:
                # Group by day
                stmt = select(
                    func.date_trunc('day', ModelPick.created_at).label('day'),
                    func.count(ModelPick.id).label('total'),
                    func.sum(case((ModelPick.won == True, 1), else_=0)).label('wins')
                ).where(ModelPick.won != None).group_by('day').order_by('day').limit(30)
                
                res = await session.execute(stmt)
                rows = res.all()
                
                return [
                    {
                        "date": r.day.strftime("%Y-%m-%d") if r.day else "Unknown",
                        "win_rate": round((r.wins / r.total * 100), 1) if r.total > 0 else 0
                    }
                    for r in rows
                ]
            except Exception as e:
                logger.error(f"HitRateService trends failed: {e}")
                return []

hit_rate_service = HitRateService()
get_summary = hit_rate_service.get_summary
get_player_breakdown = hit_rate_service.get_player_breakdown
get_trend_data = hit_rate_service.get_trend_data
