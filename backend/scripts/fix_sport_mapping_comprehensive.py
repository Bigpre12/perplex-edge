"""
Comprehensive Sport Mapping Fix Script

This script fixes ALL sport mapping issues:
1. NBA players incorrectly assigned to NHL
2. NHL players incorrectly assigned to NBA  
3. Any other sport mapping inconsistencies
4. Updates all players to match their team's sport
5. Verifies and reports the fixes
"""

import asyncio
import logging
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fix_all_sport_mappings(db: AsyncSession):
    """Fix all sport mapping issues comprehensively."""
    
    logger.info("🔧 Starting comprehensive sport mapping fix...")
    
    # Track changes
    changes_made = {
        "nba_players_fixed": 0,
        "nhl_players_fixed": 0,
        "other_sports_fixed": 0,
        "total_players_fixed": 0,
        "errors": []
    }
    
    try:
        # Step 1: Fix NBA players incorrectly in NHL
        logger.info("🏀 Fixing NBA players incorrectly assigned to NHL...")
        
        # Get NBA teams
        nba_teams_result = await db.execute(
            select(Team).where(Team.sport_id == 30)  # NBA sport_id
        )
        nba_teams = nba_teams_result.scalars().all()
        nba_team_ids = [team.id for team in nba_teams]
        
        if nba_team_ids:
            # Find NBA players incorrectly assigned to NHL (sport_id=53)
            nba_players_in_nhl_result = await db.execute(
                select(Player)
                .where(
                    Player.team_id.in_(nba_team_ids),
                    Player.sport_id == 53  # Incorrectly assigned to NHL
                )
            )
            nba_players_in_nhl = nba_players_in_nhl_result.scalars().all()
            
            # Fix NBA players
            for player in nba_players_in_nhl:
                await db.execute(
                    update(Player)
                    .where(Player.id == player.id)
                    .values(sport_id=30)  # Correct NBA sport_id
                )
                changes_made["nba_players_fixed"] += 1
                logger.info(f"✅ Fixed NBA player: {player.name} (ID: {player.id})")
        
        # Step 2: Fix NHL players incorrectly in NBA
        logger.info("🏒 Fixing NHL players incorrectly assigned to NBA...")
        
        # Get NHL teams
        nhl_teams_result = await db.execute(
            select(Team).where(Team.sport_id == 53)  # NHL sport_id
        )
        nhl_teams = nhl_teams_result.scalars().all()
        nhl_team_ids = [team.id for team in nhl_teams]
        
        if nhl_team_ids:
            # Find NHL players incorrectly assigned to NBA (sport_id=30)
            nhl_players_in_nba_result = await db.execute(
                select(Player)
                .where(
                    Player.team_id.in_(nhl_team_ids),
                    Player.sport_id == 30  # Incorrectly assigned to NBA
                )
            )
            nhl_players_in_nba = nhl_players_in_nba_result.scalars().all()
            
            # Fix NHL players
            for player in nhl_players_in_nba:
                await db.execute(
                    update(Player)
                    .where(Player.id == player.id)
                    .values(sport_id=53)  # Correct NHL sport_id
                )
                changes_made["nhl_players_fixed"] += 1
                logger.info(f"✅ Fixed NHL player: {player.name} (ID: {player.id})")
        
        # Step 3: Fix ALL players to match their team's sport
        logger.info("🔄 Fixing ALL players to match their team's sport...")
        
        # Get all players with incorrect sport mappings
        incorrect_mappings_result = await db.execute(
            select(Player, Team)
            .join(Team, Player.team_id == Team.id)
            .where(Player.sport_id != Team.sport_id)
        )
        incorrect_mappings = incorrect_mappings_result.all()
        
        for player, team in incorrect_mappings:
            await db.execute(
                update(Player)
                .where(Player.id == player.id)
                .values(sport_id=team.sport_id)
            )
            changes_made["other_sports_fixed"] += 1
            logger.info(f"✅ Fixed {player.name} from sport_id={player.sport_id} to sport_id={team.sport_id} ({team.name})")
        
        # Step 4: Update related data (Lines, ModelPicks)
        logger.info("📊 Updating related data (Lines, ModelPicks)...")
        
        # Update Lines to match their game's sport
        lines_to_fix_result = await db.execute(
            select(Line, Game)
            .join(Game, Line.game_id == Game.id)
            .where(Line.sport_id != Game.sport_id)
        )
        lines_to_fix = lines_to_fix_result.all()
        
        for line, game in lines_to_fix:
            await db.execute(
                update(Line)
                .where(Line.id == line.id)
                .values(sport_id=game.sport_id)
            )
            logger.info(f"✅ Fixed Line {line.id} to sport_id={game.sport_id}")
        
        # Update ModelPicks to match their game's sport
        picks_to_fix_result = await db.execute(
            select(ModelPick, Game)
            .join(Game, ModelPick.game_id == Game.id)
            .where(ModelPick.sport_id != Game.sport_id)
        )
        picks_to_fix = picks_to_fix_result.all()
        
        for pick, game in picks_to_fix:
            await db.execute(
                update(ModelPick)
                .where(ModelPick.id == pick.id)
                .values(sport_id=game.sport_id)
            )
            logger.info(f"✅ Fixed ModelPick {pick.id} to sport_id={game.sport_id}")
        
        # Commit all changes
        await db.commit()
        
        # Calculate totals
        changes_made["total_players_fixed"] = (
            changes_made["nba_players_fixed"] + 
            changes_made["nhl_players_fixed"] + 
            changes_made["other_sports_fixed"]
        )
        
        logger.info("🎉 Sport mapping fix completed!")
        logger.info(f"📊 Summary: {changes_made}")
        
        return changes_made
        
    except Exception as e:
        logger.error(f"❌ Error fixing sport mappings: {e}")
        await db.rollback()
        changes_made["errors"].append(str(e))
        return changes_made

async def verify_sport_mappings(db: AsyncSession):
    """Verify sport mappings are correct."""
    
    logger.info("🔍 Verifying sport mappings...")
    
    verification_results = {
        "nba_players_in_nba": 0,
        "nba_players_in_nhl": 0,
        "nhl_players_in_nhl": 0,
        "nhl_players_in_nba": 0,
        "total_players": 0,
        "incorrect_mappings": 0
    }
    
    try:
        # Count NBA players
        nba_teams_result = await db.execute(
            select(Team).where(Team.sport_id == 30)
        )
        nba_teams = nba_teams_result.scalars().all()
        nba_team_ids = [team.id for team in nba_teams]
        
        if nba_team_ids:
            # NBA players correctly in NBA
            nba_players_in_nba_result = await db.execute(
                select(func.count(Player.id))
                .where(
                    Player.team_id.in_(nba_team_ids),
                    Player.sport_id == 30
                )
            )
            verification_results["nba_players_in_nba"] = nba_players_in_nba_result.scalar() or 0
            
            # NBA players incorrectly in NHL
            nba_players_in_nhl_result = await db.execute(
                select(func.count(Player.id))
                .where(
                    Player.team_id.in_(nba_team_ids),
                    Player.sport_id == 53
                )
            )
            verification_results["nba_players_in_nhl"] = nba_players_in_nhl_result.scalar() or 0
        
        # Count NHL players
        nhl_teams_result = await db.execute(
            select(Team).where(Team.sport_id == 53)
        )
        nhl_teams = nhl_teams_result.scalars().all()
        nhl_team_ids = [team.id for team in nhl_teams]
        
        if nhl_team_ids:
            # NHL players correctly in NHL
            nhl_players_in_nhl_result = await db.execute(
                select(func.count(Player.id))
                .where(
                    Player.team_id.in_(nhl_team_ids),
                    Player.sport_id == 53
                )
            )
            verification_results["nhl_players_in_nhl"] = nhl_players_in_nhl_result.scalar() or 0
            
            # NHL players incorrectly in NBA
            nhl_players_in_nba_result = await db.execute(
                select(func.count(Player.id))
                .where(
                    Player.team_id.in_(nhl_team_ids),
                    Player.sport_id == 30
                )
            )
            verification_results["nhl_players_in_nba"] = nhl_players_in_nba_result.scalar() or 0
        
        # Total players and incorrect mappings
        total_players_result = await db.execute(select(func.count(Player.id)))
        verification_results["total_players"] = total_players_result.scalar() or 0
        
        incorrect_mappings_result = await db.execute(
            select(func.count(Player.id))
            .select_from(
                select(Player.id)
                .join(Team, Player.team_id == Team.id)
                .where(Player.sport_id != Team.sport_id)
                .subquery()
            )
        )
        verification_results["incorrect_mappings"] = incorrect_mappings_result.scalar() or 0
        
        logger.info("✅ Sport mapping verification completed!")
        logger.info(f"📊 Results: {verification_results}")
        
        return verification_results
        
    except Exception as e:
        logger.error(f"❌ Error verifying sport mappings: {e}")
        return verification_results

async def main():
    """Main function to run the fix."""
    
    # Import here to avoid circular imports
    from app.core.database import get_db_session
    from app.models import Player, Team, Line, ModelPick, Game
    
    # Get database session
    async with get_db_session() as db:
        # Step 1: Fix mappings
        fix_results = await fix_all_sport_mappings(db)
        
        # Step 2: Verify fixes
        verification_results = await verify_sport_mappings(db)
        
        # Step 3: Report results
        logger.info("🎯 FINAL REPORT")
        logger.info(f"🔧 Fixes Applied: {fix_results}")
        logger.info(f"🔍 Verification: {verification_results}")
        
        # Check if successful
        if verification_results["incorrect_mappings"] == 0:
            logger.info("🎉 SUCCESS: All sport mappings are now correct!")
        else:
            logger.warning(f"⚠️  WARNING: {verification_results['incorrect_mappings']} incorrect mappings remain")

if __name__ == "__main__":
    asyncio.run(main())
