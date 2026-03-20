import logging
import json
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from sqlalchemy import select, insert, update
from db.session import async_session_maker
from models.unified import UnifiedOdds
from models.brain import CLVRecord
from services.persistence_helpers import insert_clv_trades
from services.cache import cache

logger = logging.getLogger(__name__)

class BrainCLVTracker:
    """
    Layer 5: CLV Brain
    Tracks Opening vs Closing lines to prove institutional-grade edge.
    """

    async def record_opening_line(self, odds_list: List[Any]):
        """
        Records the first seen odds for a selection as the 'Opening' line.
        """
        for odds in odds_list:
            def get_val(obj, key):
                if isinstance(obj, dict): return obj.get(key)
                return getattr(obj, key, None)

            sport = get_val(odds, "sport")
            event_id = get_val(odds, "event_id")
            market_key = get_val(odds, "market_key")
            outcome_key = get_val(odds, "outcome_key") # over/under
            bookmaker = get_val(odds, "bookmaker")
            line = get_val(odds, "line")
            price = get_val(odds, "price")
            player_name = get_val(odds, "player_name")
            
            # Key includes player name if it exists (for props)
            player_slug = player_name.replace(" ", "_").lower() if player_name else "team"
            open_key = f"clv:open:{sport}:{event_id}:{market_key}:{outcome_key}:{player_slug}:{bookmaker}"
            
            exists = await cache.get(open_key)
            if not exists:
                opening_data = {
                    "line": float(line) if line else 0.0,
                    "price": float(price),
                    "ts": datetime.now(timezone.utc).timestamp()
                }
                await cache.set(open_key, json.dumps(opening_data), 86400 * 3)
                logger.debug(f"CLV: Recorded opener for {event_id} {player_slug} {outcome_key}")

    def _calculate_clv(self, open_line, open_price, close_line, close_price, side):
        """
        Institutional CLV Logic:
        1. If line moved in our favor (e.g. Over 10 -> Over 9.5), thats a beat.
        2. If line is the same, but price improved (e.g. -110 -> +100), thats a beat.
        """
        side = side.lower()
        beat = False
        
        # Line Movement check
        if side == "over" or side == "home" or side == "away":
            # For 'Over', a lower closing line is better for the gambler 
            # (Wait, usually CLV is Closing vs Opening. If closing is 10.5 and opening was 9.5, 
            # and we bet Over 9.5, we beat the closing line by 1.0)
            if open_line < close_line: beat = True
            elif open_line == close_line and close_price < open_price: beat = True
        elif side == "under":
            # For 'Under', a higher closing line is better
            if open_line > close_line: beat = True
            elif open_line == close_line and close_price < open_price: beat = True
            
        # CLV % calculation (simplistic delta)
        diff = abs(close_line - open_line)
        perc = (diff / open_line * 100) if open_line != 0 else 0.0
        
        return beat, perc

    async def track_closing_lines(self, props: List[Any], mode: str = "multi"):
        """
        Called by background loop to snapshot closing lines for current props.
        """
        from models.unified import UnifiedOdds
        async with async_session_maker() as session:
            try:
                for p in props:
                    # Find Pinnacle (sharp) closing odds for this prop
                    stmt = select(UnifiedOdds).where(
                        and_(
                            UnifiedOdds.event_id == p.game_id,
                            UnifiedOdds.market_key == p.stat_type,
                            UnifiedOdds.player_name == p.player_name
                        )
                    )
                    res = await session.execute(stmt)
                    odds = res.scalars().all()
                    
                    if not odds: continue
                    
                    # We look for the 'opening' record from our cache
                    # Note: props usually only have one side per entry or handled by DB 
                    # For now, we compare the current DB state (odds) against the opener
                    for o in odds:
                        player_slug = o.player_name.replace(" ", "_").lower() if o.player_name else "team"
                        open_key = f"clv:open:{o.sport}:{o.event_id}:{o.market_key}:{o.outcome_key}:{player_slug}:{o.bookmaker}"
                        open_raw = await cache.get(open_key)
                        
                        if open_raw:
                            open_data = json.loads(open_raw)
                            beat, perc = self._calculate_clv(
                                open_data["line"], open_data["price"],
                                float(o.line) if o.line else 0.0, float(o.price),
                                o.outcome_key
                            )
                            
                            # Update the PropLine entry
                            p.closing_line = float(o.line) if o.line else 0.0
                            p.clv_val = perc
                            p.beat_closing_line = beat
                
                await session.commit()
                logger.info(f"CLV: Batch tracking completed for {len(props)} items")
            except Exception as e:
                await session.rollback()
                logger.error(f"CLV: Batch tracking failed: {e}")

    async def record_closing_line(self, sport: str, event_id: str):
        # Legacy method for main markets, updated to use new logic
        async with async_session_maker() as session:
            stmt = select(UnifiedOdds).where(UnifiedOdds.event_id == event_id)
            res = await session.execute(stmt)
            odds = res.scalars().all()
            
            records = []
            for o in odds:
                player_slug = o.player_name.replace(" ", "_").lower() if o.player_name else "team"
                open_key = f"clv:open:{o.sport}:{o.event_id}:{o.market_key}:{o.outcome_key}:{player_slug}:{o.bookmaker}"
                open_raw = await cache.get(open_key)
                if open_raw:
                    open_data = json.loads(open_raw)
                    beat, perc = self._calculate_clv(
                        open_data["line"], open_data["price"],
                        float(o.line) if o.line else 0.0, float(o.price),
                        o.outcome_key
                    )
                    records.append(CLVRecord(
                        sport=o.sport, event_id=o.event_id, market_key=o.market_key,
                        selection=o.player_name or o.outcome_key,
                        opening_line=open_data["line"], opening_price=open_data["price"],
                        closing_line=float(o.line) if o.line else 0.0, closing_price=float(o.price),
                        clv_beat=beat, clv_percentage=perc
                    ))
            if records:
                # Convert Pydantic/dataclass instance to dict if necessary, 
                # but CLVRecord is an Alchemist model, so we need dicts for insert_clv_records
                # helper uses ins_obj.values(records) which expects dicts.
                record_dicts = []
                for r in records:
                    record_dicts.append({
                        "sport": r.sport,
                        "event_id": r.event_id,
                        "market_key": r.market_key,
                        "selection": r.selection,
                        "opening_line": r.opening_line,
                        "opening_price": r.opening_price,
                        "closing_line": r.closing_line,
                        "closing_price": r.closing_price,
                        "clv_beat": r.clv_beat,
                        "clv_percentage": r.clv_percentage
                    })
                await insert_clv_trades(record_dicts)

brain_clv_tracker = BrainCLVTracker()

brain_clv_tracker = BrainCLVTracker()
