import logging
import json
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from sqlalchemy import select, insert, update
from db.session import async_session_maker
from models.unified import UnifiedOdds
from models.brain import CLVRecord
from services.cache import cache

logger = logging.getLogger(__name__)

class BrainCLVTracker:
    """
    Layer 5: CLV Brain
    Tracks Opening vs Closing lines to prove edge.
    """

    async def record_opening_line(self, odds_list: List[Any]):
        """
        If we haven't seen this selection before, record it as the 'Opening' line.
        """
        for odds in odds_list:
            # Handle both objects and dicts
            is_dict = isinstance(odds, dict)
            sport = odds["sport"] if is_dict else odds.sport
            event_id = odds["event_id"] if is_dict else odds.event_id
            market_key = odds["market_key"] if is_dict else odds.market_key
            outcome_key = odds["outcome_key"] if is_dict else odds.outcome_key
            bookmaker = odds["bookmaker"] if is_dict else odds.bookmaker
            line = odds["line"] if is_dict else odds.line
            price = odds["price"] if is_dict else odds.price
            
            open_key = f"clv:open:{sport}:{event_id}:{market_key}:{outcome_key}:{bookmaker}"
            exists = await cache.get(open_key)
            if not exists:
                opening_data = {
                    "line": float(line) if line else 0.0,
                    "price": float(price),
                    "ts": datetime.now(timezone.utc).timestamp()
                }
                await cache.set(open_key, json.dumps(opening_data), 86400 * 3) # Keep for 3 days
                logger.debug(f"CLV: Recorded opener for {event_id} {outcome_key}")

    async def record_closing_line(self, sport: str, event_id: str):
        """
        Record the current lines as 'Closing' lines. 
        Usually called right before game start.
        """
        async with async_session_maker() as session:
            try:
                # 1. Get current (closing) odds from DB
                stmt = select(UnifiedOdds).where(
                    UnifiedOdds.sport == sport,
                    UnifiedOdds.event_id == event_id
                )
                result = await session.execute(stmt)
                closing_odds_list = result.scalars().all()
                
                records = []
                for close_odds in closing_odds_list:
                    open_key = f"clv:open:{close_odds.sport}:{close_odds.event_id}:{close_odds.market_key}:{close_odds.outcome_key}:{close_odds.bookmaker}"
                    open_raw = await cache.get(open_key)
                    
                    if open_raw:
                        open_data = json.loads(open_raw)
                        
                        close_line = float(close_odds.line) if close_odds.line else 0.0
                        open_line = open_data["line"]
                        
                        # Calculate CLV percentage
                        clv_percentage = 0.0
                        if open_line != 0:
                            clv_percentage = ((close_line - open_line) / open_line) * 100
                        
                        # Simplistic beat check for now (over/under logic differs)
                        clv_beat = close_line > open_line
                        
                        records.append({
                            "sport": sport,
                            "event_id": event_id,
                            "market_key": close_odds.market_key,
                            "selection": close_odds.outcome_key,
                            "opening_line": open_line,
                            "opening_price": open_data["price"],
                            "closing_line": close_line,
                            "closing_price": float(close_odds.price),
                            "clv_beat": clv_beat,
                            "clv_percentage": clv_percentage
                        })

                if records:
                    await session.execute(insert(CLVRecord).values(records))
                    await session.commit()
                    logger.info(f"CLV: Persisted {len(records)} records for event {event_id}")

            except Exception as e:
                await session.rollback()
                logger.error(f"CLV: Tracking failed for {event_id}: {e}")

brain_clv_tracker = BrainCLVTracker()
