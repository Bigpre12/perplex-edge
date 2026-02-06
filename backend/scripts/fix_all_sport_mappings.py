#!/usr/bin/env python3
"""
Comprehensive sport mapping fix for all players.

This script ensures all players have correct sport_id based on their team's sport.
It fixes data integrity issues where players were assigned wrong sport IDs.
"""

import asyncio
import logging
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session_maker
from app.core.constants import SPORT_ID_TO_KEY, SPORT_KEY_TO_ID
from app.models import Player, ModelPick, PlayerHitRate, PlayerMarketHitRate, Injury, Team

logger = logging.getLogger(__name__)

async def fix_all_player_sport_mappings():
    """Fix sport mappings for ALL players based on their team's sport."""
    
    session_maker = get_session_maker()
    
    async with session_maker() as db:
        logger.info("Starting comprehensive sport mapping fix...")
        
        # Get all players with their team sport
        players_with_teams_query = select(
            Player.id, 
            Player.name, 
            Player.sport_id,
            Team.sport_id,
            Team.name
        ).join(Team, Player.team_id == Team.id)
        
        result = await db.execute(players_with_teams_query)
        all_players = result.all()
        
        logger.info(f"Checking {len(all_players)} players for sport mapping issues...")
        
        # Find players with wrong sport_id
        players_to_fix = []
        for player_data in all_players:
            current_sport_id = player_data.sport_id
            team_sport_id = player_data.sport_id_1
            
            if current_sport_id != team_sport_id:
                players_to_fix.append({
                    'id': player_data.id,
                    'name': player_data.name,
                    'current_sport_id': current_sport_id,
                    'correct_sport_id': team_sport_id,
                    'team_name': player_data.name_1
                })
        
        logger.info(f"Found {len(players_to_fix)} players with wrong sport_id")
        
        if not players_to_fix:
            logger.info("✅ All players have correct sport mappings!")
            return
        
        # Group by sport for reporting
        sport_issues = {}
        for player in players_to_fix:
            current_key = SPORT_ID_TO_KEY.get(player['current_sport_id'], 'unknown')
            correct_key = SPORT_ID_TO_KEY.get(player['correct_sport_id'], 'unknown')
            
            issue_key = f"{current_key} -> {correct_key}"
            if issue_key not in sport_issues:
                sport_issues[issue_key] = []
            sport_issues[issue_key].append(player['name'])
        
        # Report issues by sport
        logger.info("Sport mapping issues found:")
        for issue, players in sport_issues.items():
            logger.info(f"  {issue}: {len(players)} players")
            for player_name in players[:5]:  # Show first 5
                logger.info(f"    - {player_name}")
            if len(players) > 5:
                logger.info(f"    ... and {len(players) - 5} more")
        
        # Fix each player
        fixed_count = 0
        for player in players_to_fix:
            player_id = player['id']
            correct_sport_id = player['correct_sport_id']
            
            logger.info(f"Fixing {player['name']} (ID: {player_id}) "
                       f"from sport {player['current_sport_id']} to {correct_sport_id}")
            
            # Update player sport_id
            await db.execute(
                update(Player)
                .where(Player.id == player_id)
                .values(sport_id=correct_sport_id)
            )
            
            # Update related ModelPick records
            await db.execute(
                update(ModelPick)
                .where(ModelPick.player_id == player_id)
                .values(sport_id=correct_sport_id)
            )
            
            # Update PlayerHitRate records
            await db.execute(
                update(PlayerHitRate)
                .where(PlayerHitRate.player_id == player_id)
                .values(sport_id=correct_sport_id)
            )
            
            # Update PlayerMarketHitRate records
            await db.execute(
                update(PlayerMarketHitRate)
                .where(PlayerMarketHitRate.player_id == player_id)
                .values(sport_id=correct_sport_id)
            )
            
            # Update Injury records
            await db.execute(
                update(Injury)
                .where(Injury.player_id == player_id)
                .values(sport_id=correct_sport_id)
            )
            
            fixed_count += 1
        
        # Commit all changes
        await db.commit()
        
        logger.info(f"Successfully fixed {fixed_count} players")

async def verify_all_mappings():
    """Verify all sport mappings are now correct."""
    
    session_maker = get_session_maker()
    
    async with session_maker() as db:
        logger.info("Verifying all sport mappings...")
        
        # Check for any remaining mismatches
        mismatched_players_query = select(
            Player.id, 
            Player.name, 
            Player.sport_id,
            Team.sport_id
        ).join(Team, Player.team_id == Team.id).where(
            Player.sport_id != Team.sport_id
        )
        
        result = await db.execute(mismatched_players_query)
        remaining_mismatches = result.all()
        
        if remaining_mismatches:
            logger.error(f"❌ Still found {len(remaining_mismatches)} players with wrong sport_id:")
            for player in remaining_mismatches:
                logger.error(f"  - {player.name}: {player.sport_id} != {player.sport_id_1}")
        else:
            logger.info("✅ All players have correct sport mappings!")
        
        # Report player counts by sport
        logger.info("Player counts by sport:")
        for sport_id, sport_key in SPORT_ID_TO_KEY.items():
            players_query = select(Player).where(Player.sport_id == sport_id)
            result = await db.execute(players_query)
            count = len(result.scalars().all())
            logger.info(f"  {sport_key} (ID {sport_id}): {count} players")

async def main():
    """Main function to run the comprehensive sport mapping fix."""
    logging.basicConfig(level=logging.INFO)
    
    try:
        await fix_all_player_sport_mappings()
        await verify_all_mappings()
        logger.info("🎉 Comprehensive sport mapping fix completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during sport mapping fix: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
