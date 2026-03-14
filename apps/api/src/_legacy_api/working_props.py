class AsyncSession: pass
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, and_
from datetime import datetime, timezone
from database import get_db
from models.model_pick import ModelPick
from models.player import Player
from models.game import Game
from models.market import Market

router = APIRouter()

@router.get("/working-player-props")
async def get_working_player_props(
    sport_id: int = Query(..., description="Sport ID"),
    limit: int = Query(20, description="Number of props to return"),
    db: AsyncSession = Depends(get_db)
):
    """Working player props endpoint - minimal and reliable"""
    try:
        # Get current time
        now = datetime.now(timezone.utc)
        
        # Simple query - no CLV columns
        query = select(ModelPick).where(
            and_(
                ModelPick.sport_id == sport_id,
                ModelPick.expected_value > 0,
                ModelPick.confidence_score > 0.5
            )
        ).order_by(ModelPick.expected_value.desc()).limit(limit)
        
        result = await db.execute(query)
        picks = result.scalars().all()
        
        from services.dvp_service import get_dvp_rating
        from services.player_stats_service import player_stats_service
        
        props = []
        for pick in picks:
            try:
                player = await db.get(Player, pick.player_id)
                game = await db.get(Game, pick.game_id)
                market = await db.get(Market, pick.market_id)
            except:
                continue
            
            # Enrich with DvP
            if player and game and market:
                # Get the sport from the game or assume based on sport_id
                sport_map = {1: "NBA", 2: "NFL", 3: "MLB", 4: "NHL"}
                sport = sport_map.get(pick.sport_id, "NBA")
                
                # Determine opponent
                opponent = "Unknown"
                if game:
                    opponent = game.away_team if game.home_team == player.team else game.home_team
                
                dvp = get_dvp_rating(sport, opponent, player.position or "PG")
                usage = await player_stats_service.get_player_usage_data(player.name, sport)
                
                prop_data = {
                    'id': pick.id,
                    'player': {
                        'name': player.name,
                        'position': player.position,
                        'team': player.team
                    },
                    'market': {
                        'stat_type': market.stat_type,
                        'description': market.description
                    },
                    'side': pick.side,
                    'line_value': pick.line_value,
                    'odds': pick.odds,
                    'edge': float(pick.expected_value),
                    'confidence_score': float(pick.confidence_score),
                    'matchup': {
                        'def_rank_vs_pos': dvp['rank'],
                        'rating': dvp['rating'],
                        'color': dvp['color'],
                        'opponent': opponent,
                        'last_5_hit_rate': "3/5" # Mocked for now
                    },
                    'usage': usage,
                    'generated_at': pick.generated_at.isoformat() if pick.generated_at else None
                }
                props.append(prop_data)

        
        return {
            'items': props,
            'total': len(props),
            'sport_id': sport_id,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        # Return empty result instead of error
        return {
            'items': [],
            'total': 0,
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
