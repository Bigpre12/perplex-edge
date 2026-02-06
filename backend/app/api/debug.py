"""
Debug API endpoints for troubleshooting data issues.
"""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.core.database import get_db
from app.models import ModelPick, Player, Game, Team, Market

router = APIRouter(prefix="/api/debug", tags=["debug"])


@router.get("/model-picks-count")
async def debug_model_picks_count(
    sport_id: int = Query(30),
    hours_back: int = Query(24),
    db: AsyncSession = Depends(get_db)
):
    """Debug ModelPick counts with different time filters."""
    try:
        now = datetime.now(timezone.utc)
        
        # Count all ModelPicks for sport
        total_picks_result = await db.execute(
            select(func.count(ModelPick.id))
            .join(Game, ModelPick.game_id == Game.id)
            .where(Game.sport_id == sport_id)
        )
        total_picks = total_picks_result.scalar() or 0
        
        # Count recent ModelPicks (last 6 hours)
        six_hours_ago = now - timedelta(hours=6)
        recent_picks_result = await db.execute(
            select(func.count(ModelPick.id))
            .join(Game, ModelPick.game_id == Game.id)
            .where(and_(
                Game.sport_id == sport_id,
                ModelPick.generated_at > six_hours_ago
            ))
        )
        recent_picks = recent_picks_result.scalar() or 0
        
        # Count ModelPicks (last 24 hours)
        twenty_four_hours_ago = now - timedelta(hours=24)
        day_picks_result = await db.execute(
            select(func.count(ModelPick.id))
            .join(Game, ModelPick.game_id == Game.id)
            .where(and_(
                Game.sport_id == sport_id,
                ModelPick.generated_at > twenty_four_hours_ago
            ))
        )
        day_picks = day_picks_result.scalar() or 0
        
        # Count ModelPicks (last 72 hours)
        seventy_two_hours_ago = now - timedelta(hours=72)
        three_day_picks_result = await db.execute(
            select(func.count(ModelPick.id))
            .join(Game, ModelPick.game_id == Game.id)
            .where(and_(
                Game.sport_id == sport_id,
                ModelPick.generated_at > seventy_two_hours_ago
            ))
        )
        three_day_picks = three_day_picks_result.scalar() or 0
        
        # Get sample of recent picks
        sample_result = await db.execute(
            select(ModelPick, Player, Game)
            .join(Player, ModelPick.player_id == Player.id)
            .join(Game, ModelPick.game_id == Game.id)
            .where(and_(
                Game.sport_id == sport_id,
                ModelPick.generated_at > twenty_four_hours_ago
            ))
            .order_by(ModelPick.generated_at.desc())
            .limit(5)
        )
        sample_rows = sample_result.all()
        
        samples = []
        for pick, player, game in sample_rows:
            samples.append({
                "pick_id": pick.id,
                "player_name": player.name,
                "game_start": game.start_time.isoformat(),
                "generated_at": pick.generated_at.isoformat(),
                "expected_value": pick.expected_value,
                "line_value": pick.line_value
            })
        
        return {
            "sport_id": sport_id,
            "total_picks": total_picks,
            "recent_6h_picks": recent_picks,
            "last_24h_picks": day_picks,
            "last_72h_picks": three_day_picks,
            "sample_picks": samples,
            "now": now.isoformat()
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "sport_id": sport_id
        }


@router.get("/parlay-query-debug")
async def debug_parlay_query(
    sport_id: int = Query(30),
    db: AsyncSession = Depends(get_db)
):
    """Debug the exact query that parlay service uses."""
    try:
        from datetime import datetime, timezone, timedelta
        import random
        
        min_grade = "C"
        min_grade_numeric = {"A": 5, "B": 4, "C": 3, "D": 2, "F": 1}[min_grade]
        now = datetime.now(timezone.utc)
        now_naive = now.replace(tzinfo=None)  # Convert to naive for comparison
        
        # Use force_refresh logic (wider window)
        game_window_start = now_naive - timedelta(hours=2)
        game_window_end = now_naive + timedelta(hours=36)
        
        # Build the exact conditions from parlay service
        conditions = [
            Game.sport_id == sport_id,
            ModelPick.player_id.isnot(None),
            ModelPick.generated_at > now_naive - timedelta(hours=6),
        ]
        
        conditions.extend([
            Game.start_time > game_window_start,
            Game.start_time < game_window_end,
        ])
        
        # Run the exact query
        result = await db.execute(
            select(ModelPick, Player, Game, Team, Market)
            .join(Player, ModelPick.player_id == Player.id)
            .join(Game, ModelPick.game_id == Game.id)
            .outerjoin(Team, Player.team_id == Team.id)
            .join(Market, ModelPick.market_id == Market.id)
            .where(and_(*conditions))
            .order_by(ModelPick.generated_at.desc())
        )
        rows = result.all()
        
        debug_info = {
            "conditions_count": len(conditions),
            "conditions": [
                f"Game.sport_id == {sport_id}",
                "ModelPick.player_id.isnot(None)",
                f"ModelPick.generated_at > {(now_naive - timedelta(hours=6)).isoformat()}",
                f"Game.start_time > {game_window_start.isoformat()}",
                f"Game.start_time < {game_window_end.isoformat()}"
            ],
            "query_returned_rows": len(rows),
            "now": now.isoformat(),
            "game_window_start": game_window_start.isoformat(),
            "game_window_end": game_window_end.isoformat()
        }
        
        # Add sample rows if any
        if rows:
            samples = []
            for pick, player, game, team, market in rows[:5]:
                samples.append({
                    "pick_id": pick.id,
                    "player_name": player.name,
                    "game_start": game.start_time.isoformat(),
                    "pick_created": pick.generated_at.isoformat(),
                    "expected_value": pick.expected_value,
                    "line_value": pick.line_value,
                    "market_type": market.market_type
                })
            debug_info["sample_rows"] = samples
        else:
            debug_info["message"] = "No rows returned by query"
        
        return debug_info
        
    except Exception as e:
        return {
            "error": str(e),
            "sport_id": sport_id
        }
