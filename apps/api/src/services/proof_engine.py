import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func, and_, case
from db.session import async_session_maker
from models.brain import ModelPick

logger = logging.getLogger(__name__)

class ProofEngine:
    """
    The Proof Engine establishes market credibility by generating 
    verifiable track records and performance metrics.
    """
    
    async def get_performance_metrics(self, days: int = 30, sport: str = None):
        """Calculate aggregate performance metrics for the track record."""
        async with async_session_maker() as session:
            try:
                lookback = datetime.now(timezone.utc) - timedelta(days=days)
                
                # Base filters
                filters = [ModelPick.status == 'settled', ModelPick.created_at >= lookback]
                if sport:
                    filters.append(ModelPick.sport_key == sport)
                
                # Metrics query
                stmt = select(
                    func.count(ModelPick.id).label('total_picks'),
                    func.sum(case((ModelPick.won == True, 1), else_=0)).label('wins'),
                    func.avg(ModelPick.ev_percentage).label('avg_ev'),
                    func.avg(ModelPick.clv_percentage).label('avg_clv'),
                    func.sum(ModelPick.profit_loss).label('total_profit')
                ).where(and_(*filters))
                
                result = await session.execute(stmt)
                metrics = result.mappings().one()
                
                total = metrics['total_picks'] or 0
                wins = metrics['wins'] or 0
                win_rate = (wins / total * 100) if total > 0 else 0
                
                # If no real data, return empty metrics structure
                if total == 0:
                    return {
                        "period_days": days,
                        "total_picks": 0,
                        "wins": 0,
                        "win_rate": 0,
                        "avg_ev": 0,
                        "avg_clv": 0,
                        "total_profit_units": 0,
                        "is_mock": False,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                
                return {
                    "period_days": days,
                    "total_picks": total,
                    "wins": wins,
                    "win_rate": round(win_rate, 2),
                    "avg_ev": round(metrics['avg_ev'] or 0, 2),
                    "avg_clv": round(metrics['avg_clv'] or 0, 2),
                    "total_profit_units": round(metrics['total_profit'] or 0, 2),
                    "is_mock": False,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            except Exception as e:
                logger.error(f"ProofEngine metrics failed: {e}")
                return {"error": str(e)}

    async def get_recent_results(self, limit: int = 20):
        """Fetch the most recent graded picks for the public results page."""
        async with async_session_maker() as session:
            try:
                stmt = select(ModelPick).where(ModelPick.status == 'settled').order_by(ModelPick.created_at.desc()).limit(limit)
                result = await session.execute(stmt)
                picks = result.scalars().all()
                
                if not picks:
                    return []
                
                return [
                    {
                        "player": p.player_name,
                        "stat": p.stat_type,
                        "line": p.line,
                        "odds": p.odds,
                        "result": "WIN" if p.won else "LOSS",
                        "actual": p.actual_value,
                        "clv": p.clv_percentage,
                        "date": p.created_at.isoformat() if p.created_at else None
                    } for p in picks
                ]
            except Exception as e:
                logger.error(f"ProofEngine results failed: {e}")
                return []

proof_engine = ProofEngine()
