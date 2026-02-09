from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timezone
from app.database import get_db
from app.models.model_pick import ModelPick
from app.models.player import Player
from app.models.game import Game
from app.models.market import Market

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
        
        props = []
        for pick in picks:
            # Get related data safely
            try:
                player = await db.get(Player, pick.player_id)
                game = await db.get(Game, pick.game_id)
                market = await db.get(Market, pick.market_id)
            except:
                continue
            
            prop_data = {
                'id': pick.id,
                'player': {
                    'name': player.name if player else 'Unknown',
                    'position': player.position if player else None
                },
                'market': {
                    'stat_type': market.stat_type if market else 'Unknown',
                    'description': market.description if market else 'Unknown'
                },
                'side': pick.side,
                'line_value': pick.line_value,
                'odds': pick.odds,
                'edge': float(pick.expected_value),
                'confidence_score': float(pick.confidence_score),
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
