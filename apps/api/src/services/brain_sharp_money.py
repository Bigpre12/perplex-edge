import logging
import json
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from sqlalchemy import select, insert
from db.session import async_session_maker
from models.unified import UnifiedOdds
from models.brain import SharpSignal
from services.cache import cache

logger = logging.getLogger(__name__)

class SharpMoneyBrain:
    """
    Layer 1: Sharp Money Brain
    Detects steam moves, sharp line movement, and global consensus shifts.
    """
    
    # Threshold for a "Steam" move (e.g. 0.5 points or 20 cents movement in < 15 mins)
    STEAM_THRESHOLD_LINE = 0.5
    STEAM_THRESHOLD_ODDS = 25 # American odds points
    STEAM_TIMEFRAME_MINS = 15

    async def detect_signals(self, sport: str, event_id: str = None):
        """
        Analyzes the current UnifiedOdds for a sport/event and compares with last seen state in Redis.
        """
        async with async_session_maker() as session:
            try:
                # 1. Fetch current odds from DB
                stmt = select(UnifiedOdds).where(UnifiedOdds.sport == sport)
                if event_id:
                    stmt = stmt.where(UnifiedOdds.event_id == event_id)
                
                result = await session.execute(stmt)
                current_odds_list = result.scalars().all()
                
                signals_to_create = []
                
                for odds in current_odds_list:
                    # Create a unique key for this specific line
                    track_key = f"sharp:track:{odds.sport}:{odds.event_id}:{odds.market_key}:{odds.outcome_key}:{odds.bookmaker}"
                    
                    # 2. Get previous state from Redis
                    prev_state_raw = await cache.get(track_key)
                    last_seen_ts = datetime.now(timezone.utc).timestamp()
                    
                    current_state = {
                        "line": float(odds.line) if odds.line else 0.0,
                        "price": float(odds.price),
                        "ts": last_seen_ts
                    }
                    
                    if prev_state_raw:
                        prev_state = json.loads(prev_state_raw)
                        elapsed_mins = (last_seen_ts - prev_state["ts"]) / 60
                        
                        # 3. Detect Movements
                        line_delta = abs(current_state["line"] - prev_state["line"])
                        price_delta = abs(current_state["price"] - prev_state["price"]) # assuming decimal
                        
                        # Quick Steam Detection
                        if elapsed_mins <= self.STEAM_TIMEFRAME_MINS:
                            is_steam = False
                            if odds.line and line_delta >= self.STEAM_THRESHOLD_LINE:
                                is_steam = True
                            elif price_delta > 0.15: # Significant decimal price move
                                is_steam = True
                                
                            if is_steam:
                                signals_to_create.append({
                                    "sport": odds.sport,
                                    "event_id": odds.event_id,
                                    "market_key": odds.market_key,
                                    "selection": odds.outcome_key,
                                    "signal_type": "steam",
                                    "severity": line_delta if odds.line else price_delta,
                                    "bookmakers_involved": [odds.bookmaker]
                                })
                                logger.info(f"SharpBrain: detected STEAM on {odds.sport} {odds.event_id} {odds.outcome_key}")

                    # 4. Update Redis for next time
                    await cache.set(track_key, json.dumps(current_state), 3600) # Keep tracking state for an hour

                # 5. Persist signals if any
                if signals_to_create:
                    # Insert ignoring duplicates for now or just bulk add
                    # For simplicity, we create a new entry for each distinct move
                    await session.execute(insert(SharpSignal).values(signals_to_create))
                    await session.commit()
                    logger.info(f"SharpBrain: Persisted {len(signals_to_create)} sharp signals.")

            except Exception as e:
                await session.rollback()
                logger.error(f"SharpBrain: Detection failed: {e}")

sharp_money_brain = SharpMoneyBrain()
