"""
Line Repository - Database operations for betting lines.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.line import Line
from app.data.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class LineRepository(BaseRepository[Line]):
    """Repository for Line database operations."""
    
    model = Line
    
    async def get_current_lines_for_game(
        self,
        game_id: int,
    ) -> List[Line]:
        """Get all current lines for a game."""
        result = await self.db.execute(
            select(Line)
            .where(
                and_(
                    Line.game_id == game_id,
                    Line.is_current == True,
                )
            )
            .order_by(Line.sportsbook)
        )
        return list(result.scalars().all())
    
    async def get_lines_by_market(
        self,
        game_id: int,
        market_id: int,
        current_only: bool = True,
    ) -> List[Line]:
        """Get lines for a specific game and market."""
        conditions = [
            Line.game_id == game_id,
            Line.market_id == market_id,
        ]
        if current_only:
            conditions.append(Line.is_current == True)
        
        result = await self.db.execute(
            select(Line)
            .where(and_(*conditions))
            .order_by(Line.sportsbook)
        )
        return list(result.scalars().all())
    
    async def get_player_prop_lines(
        self,
        game_id: int,
        player_id: int,
        current_only: bool = True,
    ) -> List[Line]:
        """Get prop lines for a specific player in a game."""
        conditions = [
            Line.game_id == game_id,
            Line.player_id == player_id,
        ]
        if current_only:
            conditions.append(Line.is_current == True)
        
        result = await self.db.execute(
            select(Line)
            .where(and_(*conditions))
            .order_by(Line.market_id, Line.sportsbook)
        )
        return list(result.scalars().all())
    
    async def get_fresh_lines(
        self,
        game_id: int,
        max_age_minutes: int = 30,
    ) -> List[Line]:
        """Get lines that were fetched recently."""
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=max_age_minutes)
        
        result = await self.db.execute(
            select(Line)
            .where(
                and_(
                    Line.game_id == game_id,
                    Line.is_current == True,
                    Line.fetched_at >= cutoff,
                )
            )
        )
        return list(result.scalars().all())
    
    async def mark_old_lines_inactive(
        self,
        game_id: int,
        market_id: int,
        sportsbook: str,
    ) -> int:
        """Mark old lines as inactive before inserting new ones."""
        result = await self.db.execute(
            update(Line)
            .where(
                and_(
                    Line.game_id == game_id,
                    Line.market_id == market_id,
                    Line.sportsbook == sportsbook,
                    Line.is_current == True,
                )
            )
            .values(is_current=False)
        )
        await self.db.flush()
        return result.rowcount
    
    async def insert_new_line(
        self,
        game_id: int,
        market_id: int,
        sportsbook: str,
        odds: float,
        side: str,
        line_value: Optional[float] = None,
        player_id: Optional[int] = None,
    ) -> Line:
        """
        Insert a new line, marking old lines as inactive.
        
        This handles the common pattern of:
        1. Mark existing lines for this game/market/book as inactive
        2. Insert the new line as current
        """
        # Mark old lines inactive
        await self.mark_old_lines_inactive(game_id, market_id, sportsbook)
        
        # Create new line
        return await self.create(
            game_id=game_id,
            market_id=market_id,
            sportsbook=sportsbook,
            odds=odds,
            side=side,
            line_value=line_value,
            player_id=player_id,
            is_current=True,
            fetched_at=datetime.now(timezone.utc),
        )
    
    async def bulk_insert_lines(
        self,
        lines_data: List[dict],
    ) -> List[Line]:
        """
        Bulk insert lines.
        
        Each item in lines_data should have:
        - game_id, market_id, sportsbook, odds, side
        - Optional: line_value, player_id
        """
        now = datetime.now(timezone.utc)
        for item in lines_data:
            item.setdefault("is_current", True)
            item.setdefault("fetched_at", now)
        
        return await self.create_many(lines_data)
    
    async def get_line_history(
        self,
        game_id: int,
        market_id: int,
        sportsbook: str,
        limit: int = 20,
    ) -> List[Line]:
        """Get historical line movements for a game/market/book."""
        result = await self.db.execute(
            select(Line)
            .where(
                and_(
                    Line.game_id == game_id,
                    Line.market_id == market_id,
                    Line.sportsbook == sportsbook,
                )
            )
            .order_by(Line.fetched_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_best_odds(
        self,
        game_id: int,
        market_id: int,
        side: str,
    ) -> Optional[Line]:
        """Get the best current odds for a game/market/side across all books."""
        result = await self.db.execute(
            select(Line)
            .where(
                and_(
                    Line.game_id == game_id,
                    Line.market_id == market_id,
                    Line.side == side,
                    Line.is_current == True,
                )
            )
            .order_by(Line.odds.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
