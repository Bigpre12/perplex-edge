# apps/api/src/services/line_movement_service.py
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from sqlalchemy import select, func, and_
from db.session import async_session_maker
from models.unified import LineTick

logger = logging.getLogger(__name__)

class LineMovementService:
    async def get_active_moves(self, sport: str, lookback_minutes: int = 15) -> List[Dict[str, Any]]:
        """
        Detect significant line movements (Steam/Whales) in the last N minutes.
        1. Query recent LineTicks.
        2. Group by (prop/event).
        3. Identify trend (direction, velocity).
        """
        async with async_session_maker() as session:
            now = datetime.now(timezone.utc)
            start_time = now - timedelta(minutes=lookback_minutes)
            
            # Subquery to find the earliest and latest price for each book/prop in the window
            # For simplicity, we'll just get all ticks and compute in memory
            stmt = select(LineTick).where(
                and_(
                    LineTick.sport == sport,
                    LineTick.created_at >= start_time
                )
            ).order_by(LineTick.created_at.desc())
            
            result = await session.execute(stmt)
            ticks = result.scalars().all()
            
            if not ticks:
                return []
            
            # Grouping: (event_id, player, market) -> book -> [ticks]
            grouped = {}
            for t in ticks:
                key = (t.event_id, t.player_name, t.market_key, t.outcome_key)
                if key not in grouped:
                    grouped[key] = {}
                if t.bookmaker not in grouped[key]:
                    grouped[key][t.bookmaker] = []
                grouped[key][t.bookmaker].append(t)
            
            moves = []
            for key, books in grouped.items():
                event_id, player, market, outcome = key
                
                total_move = 0
                books_moving = 0
                max_velocity = 0
                
                for book, b_ticks in books.items():
                    if len(b_ticks) < 2:
                        continue
                        
                    # b_ticks is ordered by created_at desc (latest first)
                    latest = b_ticks[0]
                    earliest = b_ticks[-1]
                    
                    price_diff = float(latest.price) - float(earliest.price)
                    if abs(price_diff) >= 5: # Threshold: 5 cents
                        total_move += price_diff
                        books_moving += 1
                        max_velocity = max(max_velocity, abs(price_diff))
                
                if books_moving >= 2 or (books_moving == 1 and max_velocity >= 15):
                    # Signal detected
                    type = "STEAM" if books_moving >= 3 else "WHALE" if max_velocity >= 20 else "MOVE"
                    
                    # Estimate "Average Line" if line exists
                    latest_line = next((float(b[0].line) for b in books.values() if b[0].line), 0.0)
                    
                    moves.append({
                        "id": f"{event_id}_{player}_{market}_{outcome}",
                        "player": player,
                        "market": market.replace("player_", "").replace("_", " ").title(),
                        "outcome": outcome.title(),
                        "line": latest_line,
                        "type": type,
                        "intensity": min(100, int(abs(total_move) * 2)),
                        "direction": "UP" if total_move > 0 else "DOWN",
                        "books_count": books_moving,
                        "timestamp": books[next(iter(books))][0].created_at.isoformat()
                    })
                    
            # Sort by intensity (strongest moves first)
            moves.sort(key=lambda x: x["intensity"], reverse=True)
            return moves[:20]

line_movement_service = LineMovementService()
