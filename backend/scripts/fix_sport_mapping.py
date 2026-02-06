#!/usr/bin/env python3
"""
Fix sport mapping issue where NBA players are incorrectly assigned NHL sport_id.

This script corrects data integrity issues by:
1. Identifying NBA players with wrong sport_id (53 instead of 30)
2. Updating their sport_id to correct NBA value (30)
3. Updating related records (model_picks, player_hit_rates, etc.)
"""

import asyncio
import logging
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session_maker
from app.core.constants import SPORT_ID_TO_KEY, SPORT_KEY_TO_ID
from app.models import Player, ModelPick, PlayerHitRate, PlayerMarketHitRate, Injury

logger = logging.getLogger(__name__)

# Known NBA players that were incorrectly assigned NHL sport_id
NBA_PLAYERS_TO_FIX = {
    "Austin Reaves": 762,
    "Derrick White": 735, 
    "Rui Hachimura": 763,
    "Jayson Tatum": 759,
    # Add more as discovered
}

async def fix_nba_player_sport_ids():
    """Fix NBA players that have incorrect NHL sport_id."""
    
    session_maker = get_session_maker()
    
    async with session_maker() as db:
        logger.info("Starting sport mapping fix for NBA players...")
        
        # Get all NBA teams to identify NBA players
        nba_sport_id = SPORT_KEY_TO_ID["basketball_nba"]
        nhl_sport_id = SPORT_KEY_TO_ID["icehockey_nhl"]
        
        # Find players with wrong sport_id (NBA players with NHL sport_id)
        wrong_players_query = select(Player).where(
            Player.sport_id == nhl_sport_id
        ).join(Player.team).where(
            Player.team.has(sport_id=nba_sport_id)
        )
        
        result = await db.execute(wrong_players_query)
        wrong_players = result.scalars().all()
        
        logger.info(f"Found {len(wrong_players)} NBA players with incorrect NHL sport_id")
        
        if not wrong_players:
            logger.info("No sport mapping issues found!")
            return
        
        # Fix each player
        fixed_count = 0
        for player in wrong_players:
            logger.info(f"Fixing player: {player.name} (ID: {player.id})")
            
            # Update player sport_id
            await db.execute(
                update(Player)
                .where(Player.id == player.id)
                .values(sport_id=nba_sport_id)
            )
            
            # Update related ModelPick records
            await db.execute(
                update(ModelPick)
                .where(ModelPick.player_id == player.id)
                .values(sport_id=nba_sport_id)
            )
            
            # Update PlayerHitRate records
            await db.execute(
                update(PlayerHitRate)
                .where(PlayerHitRate.player_id == player.id)
                .values(sport_id=nba_sport_id)
            )
            
            # Update PlayerMarketHitRate records
            await db.execute(
                update(PlayerMarketHitRate)
                .where(PlayerMarketHitRate.player_id == player.id)
                .values(sport_id=nba_sport_id)
            )
            
            # Update Injury records
            await db.execute(
                update(Injury)
                .where(Injury.player_id == player.id)
                .values(sport_id=nba_sport_id)
            )
            
            fixed_count += 1
            logger.info(f"Fixed {player.name} - updated all related records")
        
        # Commit all changes
        await db.commit()
        
        logger.info(f"Successfully fixed {fixed_count} NBA players")
        logger.info("Sport mapping fix completed!")

async def verify_fix():
    """Verify the fix worked correctly."""
    
    session_maker = get_session_maker()
    
    async with session_maker() as db:
        nba_sport_id = SPORT_KEY_TO_ID["basketball_nba"]
        nhl_sport_id = SPORT_KEY_TO_ID["icehockey_nhl"]
        
        # Check for any remaining NBA players with NHL sport_id
        remaining_wrong_query = select(Player).where(
            Player.sport_id == nhl_sport_id
        ).join(Player.team).where(
            Player.team.has(sport_id=nba_sport_id)
        )
        
        result = await db.execute(remaining_wrong_query)
        remaining_wrong = result.scalars().all()
        
        if remaining_wrong:
            logger.error(f"Still found {len(remaining_wrong)} players with wrong sport_id:")
            for player in remaining_wrong:
                logger.error(f"  - {player.name} (ID: {player.id})")
        else:
            logger.info("✅ Verification passed! No NBA players with NHL sport_id found.")
        
        # Check NBA players count
        nba_players_query = select(Player).where(Player.sport_id == nba_sport_id)
        result = await db.execute(nba_players_query)
        nba_players = result.scalars().all()
        
        logger.info(f"Total NBA players in database: {len(nba_players)}")

async def main():
    """Main function to run the sport mapping fix."""
    logging.basicConfig(level=logging.INFO)
    
    try:
        await fix_nba_player_sport_ids()
        await verify_fix()
        logger.info("Sport mapping fix completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during sport mapping fix: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
