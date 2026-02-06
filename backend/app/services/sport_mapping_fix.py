"""
Sport mapping fix service for correcting data integrity issues.

This module provides functions to fix sport mapping problems where players
are assigned wrong sport_id values based on their team's actual sport.
"""

import logging
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import SPORT_ID_TO_KEY, SPORT_KEY_TO_ID
from app.models import Player, ModelPick, PlayerHitRate, PlayerMarketHitRate, Injury, Team

logger = logging.getLogger(__name__)

async def check_sport_mapping_issues(db: AsyncSession) -> dict:
    """
    Check for sport mapping issues in the database.
    
    Returns:
        Dictionary with issue counts and details
    """
    issues = {
        'total_players_checked': 0,
        'mismatched_players': 0,
        'issues_by_sport': {},
        'sample_issues': []
    }
    
    try:
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
        
        issues['total_players_checked'] = len(all_players)
        
        # Find players with wrong sport_id
        mismatched_players = []
        for player_data in all_players:
            current_sport_id = player_data.sport_id
            team_sport_id = player_data.sport_id_1
            
            if current_sport_id != team_sport_id:
                mismatched_players.append({
                    'id': player_data.id,
                    'name': player_data.name,
                    'current_sport_id': current_sport_id,
                    'correct_sport_id': team_sport_id,
                    'team_name': player_data.name_1
                })
                
                # Group by sport for reporting
                current_key = SPORT_ID_TO_KEY.get(current_sport_id, 'unknown')
                correct_key = SPORT_ID_TO_KEY.get(team_sport_id, 'unknown')
                issue_key = f"{current_key} -> {correct_key}"
                
                if issue_key not in issues['issues_by_sport']:
                    issues['issues_by_sport'][issue_key] = 0
                issues['issues_by_sport'][issue_key] += 1
        
        issues['mismatched_players'] = len(mismatched_players)
        issues['sample_issues'] = mismatched_players[:10]  # First 10 for sample
        
        logger.info(f"Sport mapping check: {len(mismatched_players)} issues found out of {len(all_players)} players")
        
        return issues
        
    except Exception as e:
        logger.error(f"Error checking sport mapping issues: {e}")
        return {'error': str(e)}

async def fix_sport_mapping_issues(db: AsyncSession, max_fixes: int = 100) -> dict:
    """
    Fix sport mapping issues for players.
    
    Args:
        db: Database session
        max_fixes: Maximum number of players to fix in one run
        
    Returns:
        Dictionary with fix results
    """
    results = {
        'attempted_fixes': 0,
        'successful_fixes': 0,
        'failed_fixes': 0,
        'fixed_players': [],
        'errors': []
    }
    
    try:
        # Get players with wrong sport_id
        mismatched_players_query = select(
            Player.id, 
            Player.name, 
            Player.sport_id,
            Team.sport_id,
            Team.name
        ).join(Team, Player.team_id == Team.id).where(
            Player.sport_id != Team.sport_id
        ).limit(max_fixes)
        
        result = await db.execute(mismatched_players_query)
        mismatched_players = result.all()
        
        logger.info(f"Attempting to fix {len(mismatched_players)} sport mapping issues")
        
        for player_data in mismatched_players:
            player_id = player_data.id
            correct_sport_id = player_data.sport_id_1
            player_name = player_data.name
            
            try:
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
                
                results['successful_fixes'] += 1
                results['fixed_players'].append(player_name)
                
                logger.info(f"Fixed sport mapping for {player_name} (ID: {player_id})")
                
            except Exception as e:
                results['failed_fixes'] += 1
                results['errors'].append(f"Failed to fix {player_name}: {str(e)}")
                logger.error(f"Failed to fix sport mapping for {player_name}: {e}")
            
            results['attempted_fixes'] += 1
        
        # Commit all changes
        await db.commit()
        
        logger.info(f"Sport mapping fix completed: {results['successful_fixes']}/{results['attempted_fixes']} successful")
        
        return results
        
    except Exception as e:
        logger.error(f"Error during sport mapping fix: {e}")
        await db.rollback()
        results['error'] = str(e)
        return results

async def get_sport_mapping_health_check(db: AsyncSession) -> dict:
    """
    Get health check status for sport mapping.
    
    Returns:
        Health check result
    """
    try:
        issues = await check_sport_mapping_issues(db)
        
        if 'error' in issues:
            return {
                'status': 'critical',
                'message': f"Sport mapping check failed: {issues['error']}",
                'details': issues
            }
        
        total_players = issues.get('total_players_checked', 0)
        mismatched_count = issues.get('mismatched_players', 0)
        
        if mismatched_count == 0:
            return {
                'status': 'healthy',
                'message': f"All {total_players} players have correct sport mappings",
                'details': issues
            }
        elif mismatched_count < 10:
            return {
                'status': 'degraded',
                'message': f"Found {mismatched_count} players with wrong sport mappings out of {total_players}",
                'details': issues
            }
        else:
            return {
                'status': 'critical',
                'message': f"Found {mismatched_count} players with wrong sport mappings out of {total_players}",
                'details': issues
            }
            
    except Exception as e:
        logger.error(f"Error getting sport mapping health check: {e}")
        return {
            'status': 'critical',
            'message': f"Sport mapping health check failed: {str(e)}",
            'details': {'error': str(e)}
        }

# Known NBA players that were incorrectly assigned NHL sport_id
NBA_PLAYERS_TO_CHECK = [
    "Austin Reaves",
    "Derrick White", 
    "Rui Hachimura",
    "Jayson Tatum",
    "Jaylen Brown",
    "Marcus Smart",
    "Al Horford",
    "Robert Williams",
    "Malcolm Brogdon"
]

async def check_known_nba_players(db: AsyncSession) -> dict:
    """
    Check specific NBA players that were known to have wrong sport_id.
    
    Returns:
        Dictionary with check results
    """
    results = {
        'checked_players': 0,
        'found_issues': 0,
        'player_details': []
    }
    
    try:
        nba_sport_id = SPORT_KEY_TO_ID["basketball_nba"]
        nhl_sport_id = SPORT_KEY_TO_ID["icehockey_nhl"]
        
        for player_name in NBA_PLAYERS_TO_CHECK:
            # Find players by name
            player_query = select(Player).where(Player.name.ilike(f"%{player_name}%"))
            result = await db.execute(player_query)
            players = result.scalars().all()
            
            for player in players:
                results['checked_players'] += 1
                
                player_details = {
                    'name': player.name,
                    'id': player.id,
                    'current_sport_id': player.sport_id,
                    'is_nba': player.sport_id == nba_sport_id,
                    'is_nhl': player.sport_id == nhl_sport_id,
                    'needs_fix': player.sport_id != nba_sport_id
                }
                
                if player_details['needs_fix']:
                    results['found_issues'] += 1
                
                results['player_details'].append(player_details)
        
        logger.info(f"Known NBA players check: {results['found_issues']} issues found out of {results['checked_players']} checked")
        
        return results
        
    except Exception as e:
        logger.error(f"Error checking known NBA players: {e}")
        return {'error': str(e)}
