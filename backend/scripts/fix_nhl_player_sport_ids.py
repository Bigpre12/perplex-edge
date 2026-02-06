#!/usr/bin/env python3
"""
Fix NHL players that might have been assigned wrong sport_id.

This script ensures NHL players have correct sport_id (53) and fixes any
NBA players that were incorrectly assigned to NHL.
"""

import asyncio
import logging
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session_maker
from app.core.constants import SPORT_ID_TO_KEY, SPORT_KEY_TO_ID
from app.models import Player, ModelPick, PlayerHitRate, PlayerMarketHitRate, Injury, Team

logger = logging.getLogger(__name__)

async def fix_nhl_player_sport_ids():
    """Ensure NHL players have correct sport_id."""
    
    session_maker = get_session_maker()
    
    async with session_maker() as db:
        logger.info("Starting NHL sport mapping verification...")
        
        nhl_sport_id = SPORT_KEY_TO_ID["icehockey_nhl"]
        
        # Get all NHL teams
        nhl_teams_query = select(Team).where(Team.sport_id == nhl_sport_id)
        result = await db.execute(nhl_teams_query)
        nhl_teams = result.scalars().all()
        
        nhl_team_ids = [team.id for team in nhl_teams]
        logger.info(f"Found {len(nhl_teams)} NHL teams")
        
        # Find NHL players with wrong sport_id
        wrong_nhl_players_query = select(Player).where(
            Player.team_id.in_(nhl_team_ids)
        ).where(
            Player.sport_id != nhl_sport_id
        )
        
        result = await db.execute(wrong_nhl_players_query)
        wrong_nhl_players = result.scalars().all()
        
        logger.info(f"Found {len(wrong_nhl_players)} NHL players with wrong sport_id")
        
        if not wrong_nhl_players:
            logger.info("No NHL sport mapping issues found!")
            return
        
        # Fix each NHL player
        fixed_count = 0
        for player in wrong_nhl_players:
            logger.info(f"Fixing NHL player: {player.name} (ID: {player.id})")
            
            # Update player sport_id
            await db.execute(
                update(Player)
                .where(Player.id == player.id)
                .values(sport_id=nhl_sport_id)
            )
            
            # Update related ModelPick records
            await db.execute(
                update(ModelPick)
                .where(ModelPick.player_id == player.id)
                .values(sport_id=nhl_sport_id)
            )
            
            # Update PlayerHitRate records
            await db.execute(
                update(PlayerHitRate)
                .where(PlayerHitRate.player_id == player.id)
                .values(sport_id=nhl_sport_id)
            )
            
            # Update PlayerMarketHitRate records
            await db.execute(
                update(PlayerMarketHitRate)
                .where(PlayerMarketHitRate.player_id == player.id)
                .values(sport_id=nhl_sport_id)
            )
            
            # Update Injury records
            await db.execute(
                update(Injury)
                .where(Injury.player_id == player.id)
                .values(sport_id=nhl_sport_id)
            )
            
            fixed_count += 1
            logger.info(f"Fixed NHL player {player.name} - updated all related records")
        
        # Commit all changes
        await db.commit()
        
        logger.info(f"Successfully fixed {fixed_count} NHL players")

async def verify_sport_mappings():
    """Verify all sport mappings are correct."""
    
    session_maker = get_session_maker()
    
    async with session_maker() as db:
        logger.info("Verifying all sport mappings...")
        
        # Check NBA players
        nba_sport_id = SPORT_KEY_TO_ID["basketball_nba"]
        nba_teams_query = select(Team).where(Team.sport_id == nba_sport_id)
        result = await db.execute(nba_teams_query)
        nba_teams = result.scalars().all()
        
        nba_team_ids = [team.id for team in nba_teams]
        
        # Find NBA players with wrong sport_id
        wrong_nba_players_query = select(Player).where(
            Player.team_id.in_(nba_team_ids)
        ).where(
            Player.sport_id != nba_sport_id
        )
        
        result = await db.execute(wrong_nba_players_query)
        wrong_nba_players = result.scalars().all()
        
        if wrong_nba_players:
            logger.error(f"Found {len(wrong_nba_players)} NBA players with wrong sport_id:")
            for player in wrong_nba_players:
                logger.error(f"  - {player.name} (Team ID: {player.team_id}, Sport ID: {player.sport_id})")
        else:
            logger.info("✅ All NBA players have correct sport_id")
        
        # Check NHL players
        nhl_sport_id = SPORT_KEY_TO_ID["icehockey_nhl"]
        nhl_teams_query = select(Team).where(Team.sport_id == nhl_sport_id)
        result = await db.execute(nhl_teams_query)
        nhl_teams = result.scalars().all()
        
        nhl_team_ids = [team.id for team in nhl_teams]
        
        # Find NHL players with wrong sport_id
        wrong_nhl_players_query = select(Player).where(
            Player.team_id.in_(nhl_team_ids)
        ).where(
            Player.sport_id != nhl_sport_id
        )
        
        result = await db.execute(wrong_nhl_players_query)
        wrong_nhl_players = result.scalars().all()
        
        if wrong_nhl_players:
            logger.error(f"Found {len(wrong_nhl_players)} NHL players with wrong sport_id:")
            for player in wrong_nhl_players:
                logger.error(f"  - {player.name} (Team ID: {player.team_id}, Sport ID: {player.sport_id})")
        else:
            logger.info("✅ All NHL players have correct sport_id")

async def main():
    """Main function to run the sport mapping fix."""
    logging.basicConfig(level=logging.INFO)
    
    try:
        await fix_nhl_player_sport_ids()
        await verify_sport_mappings()
        logger.info("Sport mapping verification completed!")
        
    except Exception as e:
        logger.error(f"Error during sport mapping fix: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
