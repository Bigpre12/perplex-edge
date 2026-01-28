"""ETL sync service for fetching and storing data."""

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Sport, Team, Game, Market, Line, Player
from app.etl.odds_api import (
    OddsAPIClient,
    SPORT_KEYS,
    parse_game_from_odds,
    parse_lines_from_odds,
)

logger = logging.getLogger(__name__)


class SyncService:
    """Service for syncing data from external APIs to database."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_sport(self, name: str, league_code: str) -> Sport:
        """Get or create a sport record."""
        result = await self.db.execute(
            select(Sport).where(Sport.league_code == league_code)
        )
        sport = result.scalar_one_or_none()

        if not sport:
            sport = Sport(name=name, league_code=league_code)
            self.db.add(sport)
            await self.db.flush()
            logger.info(f"Created sport: {name} ({league_code})")

        return sport

    async def get_or_create_team(
        self,
        sport_id: int,
        team_name: str,
        external_id: Optional[str] = None,
    ) -> Team:
        """Get or create a team record."""
        external_id = external_id or team_name.lower().replace(" ", "_")
        
        result = await self.db.execute(
            select(Team).where(
                Team.sport_id == sport_id,
                Team.external_team_id == external_id,
            )
        )
        team = result.scalar_one_or_none()

        if not team:
            # Generate abbreviation from team name
            words = team_name.split()
            abbr = "".join(w[0].upper() for w in words[-2:]) if len(words) > 1 else team_name[:3].upper()
            
            team = Team(
                sport_id=sport_id,
                external_team_id=external_id,
                name=team_name,
                abbreviation=abbr,
            )
            self.db.add(team)
            await self.db.flush()
            logger.info(f"Created team: {team_name}")

        return team

    async def get_or_create_market(
        self,
        sport_id: int,
        market_type: str,
        stat_type: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Market:
        """Get or create a market record."""
        result = await self.db.execute(
            select(Market).where(
                Market.sport_id == sport_id,
                Market.market_type == market_type,
                Market.stat_type == stat_type,
            )
        )
        market = result.scalar_one_or_none()

        if not market:
            market = Market(
                sport_id=sport_id,
                market_type=market_type,
                stat_type=stat_type,
                description=description,
            )
            self.db.add(market)
            await self.db.flush()
            logger.info(f"Created market: {market_type} {stat_type or ''}")

        return market

    async def sync_odds_for_sport(self, sport_name: str) -> dict[str, int]:
        """
        Sync odds for a specific sport from The Odds API.
        
        Returns:
            Dict with counts of synced items
        """
        sport_key = SPORT_KEYS.get(sport_name.upper())
        if not sport_key:
            raise ValueError(f"Unknown sport: {sport_name}")

        # Get or create sport
        sport = await self.get_or_create_sport(sport_name, sport_key)

        # Ensure base markets exist
        market_map = {}
        for market_type in ["moneyline", "spread", "total"]:
            market = await self.get_or_create_market(sport.id, market_type)
            market_map[market_type] = market.id

        stats = {"games": 0, "lines": 0, "teams": 0}

        async with OddsAPIClient() as client:
            games_data = await client.get_odds(sport_key)

            for game_data in games_data:
                # Get or create teams
                home_team = await self.get_or_create_team(
                    sport.id, game_data["home_team"]
                )
                away_team = await self.get_or_create_team(
                    sport.id, game_data["away_team"]
                )

                # Get or create game
                result = await self.db.execute(
                    select(Game).where(
                        Game.sport_id == sport.id,
                        Game.external_game_id == game_data["id"],
                    )
                )
                game = result.scalar_one_or_none()

                if not game:
                    game = Game(
                        sport_id=sport.id,
                        external_game_id=game_data["id"],
                        home_team_id=home_team.id,
                        away_team_id=away_team.id,
                        start_time=datetime.fromisoformat(
                            game_data["commence_time"].replace("Z", "+00:00")
                        ),
                        status="scheduled",
                    )
                    self.db.add(game)
                    await self.db.flush()
                    stats["games"] += 1

                # Mark old lines as not current
                await self.db.execute(
                    update(Line)
                    .where(Line.game_id == game.id, Line.is_current == True)
                    .values(is_current=False)
                )

                # Parse and insert new lines
                lines = parse_lines_from_odds(game_data, game.id, market_map)
                for line_data in lines:
                    line = Line(**line_data)
                    self.db.add(line)
                    stats["lines"] += 1

        await self.db.commit()
        logger.info(f"Synced {sport_name}: {stats}")
        return stats

    async def sync_all_sports(self) -> dict[str, dict[str, int]]:
        """Sync odds for all configured sports."""
        results = {}
        for sport_name in SPORT_KEYS.keys():
            try:
                results[sport_name] = await self.sync_odds_for_sport(sport_name)
            except Exception as e:
                logger.error(f"Failed to sync {sport_name}: {e}")
                results[sport_name] = {"error": str(e)}
        return results
