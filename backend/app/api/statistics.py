"""
Statistics API - Player and team statistics with advanced analytics
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import Player, Team, Sport, Game, ModelPick

router = APIRouter(prefix="/api/statistics", tags=["statistics"])

@router.get("/players/{player_id}")
async def get_player_statistics(
    player_id: int,
    season: int = Query(None, description="Filter by season"),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed statistics for a specific player."""
    try:
        # Get player info
        player_result = await db.execute(
            select(Player)
            .options(
                selectinload(Player.team).selectinload(Team.sport)
            )
            .where(Player.id == player_id)
        )
        player = player_result.scalar_one_or_none()
        
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        
        # Get player statistics
        stats = []
        try:
            from app.models import PlayerStat
            stats_query = select(PlayerStat).where(PlayerStat.player_id == player_id)
            
            if season:
                stats_query = stats_query.where(PlayerStat.season == season)
            
            stats_query = stats_query.order_by(PlayerStat.season.desc())
            stats_result = await db.execute(stats_query.limit(100))
            stats = stats_result.scalars().all()
        except ImportError:
            # PlayerStat model not available
            pass
        
        # Get recent picks for context
        picks_result = await db.execute(
            select(ModelPick)
            .options(selectinload(ModelPick.market))
            .where(ModelPick.player_id == player_id)
            .order_by(ModelPick.generated_at.desc())
            .limit(10)
        )
        picks = picks_result.scalars().all()
        
        # Format statistics
        stats_data = []
        for stat in stats:
            stat_data = {
                "season": stat.season,
                "games_played": stat.games_played,
                "minutes_per_game": stat.minutes_per_game,
                "points_per_game": stat.points_per_game,
                "rebounds_per_game": stat.rebounds_per_game,
                "assists_per_game": stat.assists_per_game,
                "steals_per_game": stat.steals_per_game,
                "blocks_per_game": stat.blocks_per_game,
                "turnovers_per_game": stat.turnovers_per_game,
                "field_goals_made": stat.field_goals_made,
                "field_goals_attempted": stat.field_goals_attempted,
                "field_goal_percentage": stat.field_goal_percentage,
                "three_pointers_made": stat.three_pointers_made,
                "three_pointers_attempted": stat.three_pointers_attempted,
                "three_point_percentage": stat.three_point_percentage,
                "free_throws_made": stat.free_throws_made,
                "free_throws_attempted": stat.free_throws_attempted,
                "free_throw_percentage": stat.free_throw_percentage,
                "offensive_rebounds": stat.offensive_rebounds,
                "defensive_rebounds": stat.defensive_rebounds,
                "total_rebounds": stat.total_rebounds,
                "personal_fouls": stat.personal_fouls,
                "points": stat.points
            }
            stats_data.append(stat_data)
        
        # Format recent picks
        recent_picks = []
        for pick in picks:
            pick_data = {
                "id": pick.id,
                "stat_type": pick.market.stat_type if pick.market else None,
                "line_value": pick.line_value,
                "side": pick.side,
                "model_projection": pick.model_projection,
                "expected_value": pick.expected_value,
                "confidence_score": pick.confidence_score,
                "generated_at": pick.generated_at.isoformat() if pick.generated_at else None
            }
            recent_picks.append(pick_data)
        
        return {
            "player_id": player_id,
            "player_name": player.name,
            "position": player.position,
            "team_name": player.team.name if player.team else None,
            "sport_name": player.team.sport.name if player.team and player.team.sport else None,
            "statistics": stats_data,
            "recent_picks": recent_picks,
            "total_seasons": len(stats_data),
            "filters": {
                "season": season
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/players/{player_id}/career")
async def get_player_career_stats(player_id: int, db: AsyncSession = Depends(get_db)):
    """Get career summary statistics for a player."""
    try:
        # Get player info
        player_result = await db.execute(
            select(Player)
            .options(selectinload(Player.team))
            .where(Player.id == player_id)
        )
        player = player_result.scalar_one_or_none()
        
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        
        # Calculate career totals
        career_stats = {}
        try:
            from app.models import PlayerStat
            from sqlalchemy import func
            
            stats_result = await db.execute(
                select(
                    func.count(PlayerStat.season).label('seasons_played'),
                    func.sum(PlayerStat.games_played).label('total_games'),
                    func.avg(PlayerStat.points_per_game).label('avg_points'),
                    func.avg(PlayerStat.rebounds_per_game).label('avg_rebounds'),
                    func.avg(PlayerStat.assists_per_game).label('avg_assists'),
                    func.avg(PlayerStat.field_goal_percentage).label('avg_fg_pct'),
                    func.sum(PlayerStat.points).label('total_points')
                )
                .where(PlayerStat.player_id == player_id)
            )
            career_data = stats_result.first()
            
            if career_data and career_data.seasons_played:
                career_stats = {
                    "seasons_played": career_data.seasons_played,
                    "total_games": career_data.total_games or 0,
                    "career_points_per_game": round(career_data.avg_points or 0, 2),
                    "career_rebounds_per_game": round(career_data.avg_rebounds or 0, 2),
                    "career_assists_per_game": round(career_data.avg_assists or 0, 2),
                    "career_field_goal_percentage": round(career_data.avg_fg_pct or 0, 3),
                    "total_points": career_data.total_points or 0
                }
        except ImportError:
            # PlayerStat model not available
            pass
        
        # Get best season
        best_season = None
        try:
            from app.models import PlayerStat
            
            best_result = await db.execute(
                select(PlayerStat)
                .where(PlayerStat.player_id == player_id)
                .order_by(desc(PlayerStat.points_per_game))
                .limit(1)
            )
            best_season_data = best_result.scalar_one_or_none()
            
            if best_season_data:
                best_season = {
                    "season": best_season_data.season,
                    "points_per_game": best_season_data.points_per_game,
                    "rebounds_per_game": best_season_data.rebounds_per_game,
                    "assists_per_game": best_season_data.assists_per_game
                }
        except ImportError:
            pass
        
        return {
            "player_id": player_id,
            "player_name": player.name,
            "position": player.position,
            "team_name": player.team.name if player.team else None,
            "career_statistics": career_stats,
            "best_season": best_season
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/teams/{team_id}")
async def get_team_statistics(
    team_id: int,
    season: int = Query(None, description="Filter by season"),
    limit: int = Query(default=15, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get statistics for all players on a team."""
    try:
        # Get team info
        team_result = await db.execute(
            select(Team)
            .options(selectinload(Team.sport))
            .where(Team.id == team_id)
        )
        team = team_result.scalar_one_or_none()
        
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        # Get team players with statistics
        players_stats = []
        try:
            from app.models import PlayerStat
            
            players_result = await db.execute(
                select(Player)
                .options(
                    selectinload(Player.team),
                    selectinload(Player.player_stats)
                )
                .where(Player.team_id == team_id)
                .order_by(Player.name)
                .limit(1000)
            )
            players = players_result.scalars().all()
            
            for player in players:
                # Get player stats
                stats_query = select(PlayerStat).where(PlayerStat.player_id == player.id)
                
                if season:
                    stats_query = stats_query.where(PlayerStat.season == season)
                
                stats_query = stats_query.order_by(PlayerStat.season.desc())
                stats_result = await db.execute(stats_query)
                stats = stats_result.scalars().all()
                
                if stats:
                    # Use most recent season stats
                    recent_stat = stats[0]
                    
                    player_stat = {
                        "player_id": player.id,
                        "player_name": player.name,
                        "position": player.position,
                        "jersey_number": player.jersey_number,
                        "season": recent_stat.season,
                        "games_played": recent_stat.games_played,
                        "points_per_game": recent_stat.points_per_game,
                        "rebounds_per_game": recent_stat.rebounds_per_game,
                        "assists_per_game": recent_stat.assists_per_game,
                        "field_goal_percentage": recent_stat.field_goal_percentage,
                        "minutes_per_game": recent_stat.minutes_per_game
                    }
                    players_stats.append(player_stat)
        except ImportError:
            # PlayerStat model not available, fallback to basic player info
            players_result = await db.execute(
                select(Player)
                .where(Player.team_id == team_id)
                .order_by(Player.name)
                .limit(limit)
            )
            players = players_result.scalars().all()
            
            for player in players:
                player_stat = {
                    "player_id": player.id,
                    "player_name": player.name,
                    "position": player.position,
                    "jersey_number": player.jersey_number
                }
                players_stats.append(player_stat)
        
        # Sort by points per game if available
        players_stats.sort(
            key=lambda x: x.get("points_per_game", 0), 
            reverse=True
        )
        
        return {
            "team_id": team_id,
            "team_name": team.name,
            "sport_name": team.sport.name if team.sport else None,
            "players": players_stats[:limit],
            "total_players": len(players_stats),
            "filters": {
                "season": season,
                "limit": limit
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/league/leaders")
async def get_league_leaders(
    category: str = Query(default="points_per_game", description="Statistical category"),
    season: int = Query(None, description="Filter by season"),
    limit: int = Query(default=10, le=50),
    min_games: int = Query(default=10, description="Minimum games played"),
    db: AsyncSession = Depends(get_db)
):
    """Get league leaders for various statistical categories."""
    try:
        # Validate category
        valid_categories = [
            "points_per_game", "rebounds_per_game", "assists_per_game",
            "steals_per_game", "blocks_per_game", "field_goal_percentage",
            "three_point_percentage", "free_throw_percentage", "minutes_per_game"
        ]
        
        if category not in valid_categories:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
            )
        
        leaders = []
        try:
            from app.models import PlayerStat
            
            # Build query
            query = select(PlayerStat, Player)
            query = query.join(Player, PlayerStat.player_id == Player.id)
            query = query.options(selectinload(Player.team))
            query = query.where(PlayerStat.games_played >= min_games)
            
            if season:
                query = query.where(PlayerStat.season == season)
            
            # Order by the requested category
            if hasattr(PlayerStat, category):
                query = query.order_by(desc(getattr(PlayerStat, category)))
            
            query = query.limit(limit)
            
            result = await db.execute(query)
            rows = result.all()
            
            for stat, player in rows:
                leader_data = {
                    "rank": len(leaders) + 1,
                    "player_id": player.id,
                    "player_name": player.name,
                    "position": player.position,
                    "team_name": player.team.name if player.team else None,
                    "team_abbreviation": player.team.abbreviation if player.team else None,
                    "season": stat.season,
                    "games_played": stat.games_played,
                    "category": category,
                    "value": getattr(stat, category, 0)
                }
                leaders.append(leader_data)
                
        except ImportError:
            # PlayerStat model not available
            raise HTTPException(
                status_code=503,
                detail="Statistics data not available"
            )
        
        return {
            "category": category,
            "season": season,
            "leaders": leaders,
            "total_leaders": len(leaders),
            "filters": {
                "min_games": min_games,
                "limit": limit
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/season/{season}/summary")
async def get_season_summary(season: int, db: AsyncSession = Depends(get_db)):
    """Get comprehensive season statistics summary."""
    try:
        # Get season overview
        summary = {
            "season": season,
            "total_games": 0,
            "total_players": 0,
            "league_averages": {},
            "top_performers": {},
            "team_standings": []
        }
        
        try:
            from app.models import PlayerStat, Game
            from sqlalchemy import func
            
            # Get total games played in season
            games_result = await db.execute(
                select(func.count(Game.id))
                .where(
                    and_(
                        func.extract('year', Game.start_time) == season,
                        Game.status == 'completed'
                    )
                )
            )
            summary["total_games"] = games_result.scalar() or 0
            
            # Get total players with stats
            players_result = await db.execute(
                select(func.count(func.distinct(PlayerStat.player_id)))
                .where(PlayerStat.season == season)
            )
            summary["total_players"] = players_result.scalar() or 0
            
            # Get league averages
            averages_result = await db.execute(
                select(
                    func.avg(PlayerStat.points_per_game).label('avg_points'),
                    func.avg(PlayerStat.rebounds_per_game).label('avg_rebounds'),
                    func.avg(PlayerStat.assists_per_game).label('avg_assists'),
                    func.avg(PlayerStat.field_goal_percentage).label('avg_fg_pct')
                )
                .where(PlayerStat.season == season)
            )
            averages = averages_result.first()
            
            if averages:
                summary["league_averages"] = {
                    "points_per_game": round(averages.avg_points or 0, 2),
                    "rebounds_per_game": round(averages.avg_rebounds or 0, 2),
                    "assists_per_game": round(averages.avg_assists or 0, 2),
                    "field_goal_percentage": round(averages.avg_fg_pct or 0, 3)
                }
            
            # Get top performers for key categories
            categories = ["points_per_game", "rebounds_per_game", "assists_per_game"]
            
            for category in categories:
                leaders_result = await db.execute(
                    select(PlayerStat, Player)
                    .join(Player, PlayerStat.player_id == Player.id)
                    .options(selectinload(Player.team))
                    .where(
                        and_(
                            PlayerStat.season == season,
                            PlayerStat.games_played >= 10
                        )
                    )
                    .order_by(desc(getattr(PlayerStat, category)))
                    .limit(5)
                )
                leaders = leaders_result.all()
                
                top_performers = []
                for stat, player in leaders:
                    performer_data = {
                        "player_id": player.id,
                        "player_name": player.name,
                        "team_name": player.team.name if player.team else None,
                        "value": getattr(stat, category, 0)
                    }
                    top_performers.append(performer_data)
                
                summary["top_performers"][category] = top_performers
                
        except ImportError:
            # PlayerStat model not available
            pass
        
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
