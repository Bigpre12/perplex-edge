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
    async def get_outliers(
        self, 
        sport: str = "all", 
        min_hit_rate: float = 0.70, 
        window: int = 10,
        market: str = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Premium Prop Outliers Engine.
        Finds players hitting specific markets at high rates.
        """
        async with async_session_maker() as session:
            try:
                from models.prop import PropLine
                
                # 1. Query settled prop lines for historical performance
                filters = [PropLine.is_settled == True]
                if sport != "all":
                    filters.append(PropLine.sport_key == sport)
                if market:
                    filters.append(PropLine.stat_type == market)
                
                # Fetch recent historical data
                stmt = select(PropLine).where(and_(*filters)).order_by(desc(PropLine.start_time)).limit(2000)
                res = await session.execute(stmt)
                all_settled = res.scalars().all()
                
                # 2. Group and Calculate Hit Rates
                player_groups = {}
                for p in all_settled:
                    key = (p.player_name, p.stat_type, p.line)
                    if key not in player_groups:
                        player_groups[key] = {
                            "player_name": p.player_name,
                            "team": p.team,
                            "sport": p.sport_key,
                            "market": p.stat_type,
                            "line": p.line,
                            "results": [],
                            "last_updated": p.created_at
                        }
                    player_groups[key]["results"].append(p.hit)
                
                outliers = []
                for key, data in player_groups.items():
                    results = data["results"][:window] # Only take the desired window
                    if not results: continue
                    
                    hits = sum(1 for r in results if r)
                    total = len(results)
                    hit_rate = hits / total
                    
                    if hit_rate >= min_hit_rate and total >= min(window, 5): 
                        # Calculate Streak
                        streak = 0
                        for r in results:
                            if r: streak += 1
                            else: break
                        
                        # Calculate Trend
                        trend = "stable"
                        if len(results) >= 4:
                            recent = results[:len(results)//2]
                            older = results[len(results)//2:]
                            r_rate = sum(1 for r in recent if r) / len(recent)
                            o_rate = sum(1 for r in older if r) / len(older)
                            if r_rate > o_rate: trend = "up"
                            elif r_rate < o_rate: trend = "down"
                        
                        # Confidence
                        if total >= 15: conf = "high"
                        elif total >= 8: conf = "reliable"
                        elif total >= 4: conf = "early"
                        else: conf = "limited"
                        
                        outliers.append({
                            "player_name": data["player_name"],
                            "team": data["team"],
                            "sport": data["sport"],
                            "market": data["market"],
                            "line": data["line"],
                            "hit_rate": round(hit_rate * 100, 1),
                            "hits": hits,
                            "total": total,
                            "streak": streak,
                            "trend": trend,
                            "results": results, 
                            "confidence": conf,
                            "last_updated": data["last_updated"].isoformat() if data["last_updated"] else None
                        })
                
                outliers.sort(key=lambda x: (x["hit_rate"], x["streak"]), reverse=True)
                return outliers[:limit]
            except Exception as e:
                logger.error(f"HitRateService outliers failed: {e}")
                return []

hit_rate_service = HitRateService()
