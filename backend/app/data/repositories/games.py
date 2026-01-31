"""
Game Repository - Database operations for games.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.game import Game
from app.data.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class GameRepository(BaseRepository[Game]):
    """Repository for Game database operations."""
    
    model = Game
    
    async def get_by_external_id(
        self,
        sport_id: int,
        external_game_id: str,
    ) -> Optional[Game]:
        """Get a game by its external ID and sport."""
        result = await self.db.execute(
            select(Game).where(
                and_(
                    Game.sport_id == sport_id,
                    Game.external_game_id == external_game_id,
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_sport(
        self,
        sport_id: int,
        limit: int = 100,
    ) -> List[Game]:
        """Get all games for a sport."""
        result = await self.db.execute(
            select(Game)
            .where(Game.sport_id == sport_id)
            .order_by(Game.start_time)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_today_games(
        self,
        sport_id: int,
    ) -> List[Game]:
        """Get today's games for a sport."""
        now = datetime.now(timezone.utc)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        result = await self.db.execute(
            select(Game)
            .where(
                and_(
                    Game.sport_id == sport_id,
                    Game.start_time >= start_of_day,
                    Game.start_time < end_of_day,
                )
            )
            .order_by(Game.start_time)
        )
        return list(result.scalars().all())
    
    async def get_upcoming_games(
        self,
        sport_id: int,
        hours_ahead: int = 24,
        limit: int = 50,
    ) -> List[Game]:
        """Get upcoming games within N hours."""
        now = datetime.now(timezone.utc)
        cutoff = now + timedelta(hours=hours_ahead)
        
        result = await self.db.execute(
            select(Game)
            .where(
                and_(
                    Game.sport_id == sport_id,
                    Game.start_time >= now,
                    Game.start_time <= cutoff,
                    Game.status == "scheduled",
                )
            )
            .order_by(Game.start_time)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_with_lines(
        self,
        game_id: int,
    ) -> Optional[Game]:
        """Get a game with its lines eagerly loaded."""
        result = await self.db.execute(
            select(Game)
            .options(selectinload(Game.lines))
            .where(Game.id == game_id)
        )
        return result.scalar_one_or_none()
    
    async def get_games_in_range(
        self,
        sport_id: int,
        start_time: datetime,
        end_time: datetime,
    ) -> List[Game]:
        """Get games within a time range."""
        result = await self.db.execute(
            select(Game)
            .where(
                and_(
                    Game.sport_id == sport_id,
                    Game.start_time >= start_time,
                    Game.start_time < end_time,
                )
            )
            .order_by(Game.start_time)
        )
        return list(result.scalars().all())
    
    async def upsert_game(
        self,
        sport_id: int,
        external_game_id: str,
        home_team_id: int,
        away_team_id: int,
        start_time: datetime,
        status: str = "scheduled",
    ) -> Game:
        """
        Insert or update a game.
        
        If game exists (by sport_id + external_game_id), update it.
        Otherwise, create a new game.
        """
        existing = await self.get_by_external_id(sport_id, external_game_id)
        
        if existing:
            # Update existing game
            existing.home_team_id = home_team_id
            existing.away_team_id = away_team_id
            existing.start_time = start_time
            existing.status = status
            await self.db.flush()
            return existing
        else:
            # Create new game
            return await self.create(
                sport_id=sport_id,
                external_game_id=external_game_id,
                home_team_id=home_team_id,
                away_team_id=away_team_id,
                start_time=start_time,
                status=status,
            )
    
    async def update_status(
        self,
        game_id: int,
        status: str,
    ) -> Optional[Game]:
        """Update game status."""
        return await self.update_by_id(game_id, status=status)
    
    async def get_by_team(
        self,
        team_id: int,
        limit: int = 20,
    ) -> List[Game]:
        """Get recent games for a team."""
        result = await self.db.execute(
            select(Game)
            .where(
                or_(
                    Game.home_team_id == team_id,
                    Game.away_team_id == team_id,
                )
            )
            .order_by(Game.start_time.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
