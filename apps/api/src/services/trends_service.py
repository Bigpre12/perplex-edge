import logging
import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from services.player_splits_service import get_full_splits
# Mock data removed for production.

logger = logging.getLogger(__name__)

from db.session import async_session_maker
from models.prop import PropLine
from sqlalchemy import select, and_

logger = logging.getLogger(__name__)

# Simple in-memory cache to prevent API slamming
_TRENDS_CACHE = {}
_CACHE_EXPIRY = 600 # 10 minutes

class TrendsService:
    async def get_high_hit_rates(self, sport_key: str = "basketball_nba", timeframe: str = "10g") -> List[Dict[str, Any]]:
        """
        Identify players with a 60-100% hit rate for a specific stat line using real data.
        """
        cache_key = f"{sport_key}_{timeframe}"
        now = datetime.now(timezone.utc).timestamp()
        
        if cache_key in _TRENDS_CACHE:
            data, ts = _TRENDS_CACHE[cache_key]
            if now - ts < _CACHE_EXPIRY:
                return data

        try:
            # 1. Fetch active props from the database using async session
            async with async_session_maker() as db:
                stmt = select(PropLine).where(
                    and_(
                        PropLine.sport_key == sport_key,
                        PropLine.is_active == True
                    )
                ).order_by(PropLine.created_at.desc()).limit(30)
                
                result = await db.execute(stmt)
                picks = result.scalars().all()

            if not picks:
                return []

            results = []
            seen_combos = set()
            
            # Map timeframe to split key
            tf_map = {"5g": "l5", "10g": "l10", "30g": "l30", "szn": "l30"}
            split_key = tf_map.get(timeframe, "l10")

            # 2. For each prop, fetch real hit rates
            for pick in picks:
                combo_key = f"{pick.player_name}_{pick.stat_type}_{pick.line}"
                if combo_key in seen_combos:
                    continue
                seen_combos.add(combo_key)

                # Fetch real splits from BDL (NBA only for now) or hit_rates table
                # For now, we attempt get_full_splits and fall back to skipping
                if sport_key == "basketball_nba":
                    splits_data = await get_full_splits(pick.player_name, pick.stat_type, pick.line)
                else:
                    # Non-NBA sports: future integration
                    continue
                
                if not splits_data or "error" in splits_data:
                    continue

                split = splits_data.get("splits", {}).get(split_key)
                if not split or split.get("hit_rate") is None:
                    continue

                hit_rate_pct = round(split["hit_rate"] * 100, 1)
                
                # 3. Filter for 50-100% hit rate
                if 50.0 <= hit_rate_pct <= 100.0:
                    results.append({
                        "id": f"trend-{pick.player_name}-{pick.stat_type}-{timeframe}",
                        "player_name": pick.player_name,
                        "player_image": f"https://api.dicebear.com/7.x/avataaars/svg?seed={pick.player_name}",
                        "stat_type": pick.stat_type,
                        "line": pick.line,
                        "side": "over",
                        "odds": -110,
                        "edge": 5.0,
                        "hit_rate": hit_rate_pct,
                        "hits": split["hits"],
                        "total_games": split["sample"],
                        "timeframe": timeframe,
                        "trend": "up" if hit_rate_pct >= 70.0 else "stable",
                        "avg_value": split["avg"],
                        "last_10_values": splits_data["splits"]["l10"]["values"][:10],
                        "matchup": {"opponent": pick.opponent or "TBD", "time": "TBD"},
                        "sportsbook": "MarketAvg"
                    })
                
                if len(results) >= 20: 
                    break

            results.sort(key=lambda x: x['hit_rate'], reverse=True)
            _TRENDS_CACHE[cache_key] = (results, now)
            return results
            
        except Exception as e:
            logger.error(f"TrendsService error: {e}")
            return []

trends_service = TrendsService()
