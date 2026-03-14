class AsyncSession: pass
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from database import get_async_db
from models.props import PropLine

router = APIRouter(prefix="/api/streaks", tags=["streaks"])

@router.get("/{player_id}")
async def get_player_streak(
    player_id: str,
    prop_type: str = Query(...),
    line: float = Query(...),
    db: AsyncSession = Depends(get_async_db),
):
    result = await db.execute(
        select(PropLine)
        .where(
            PropLine.player_name == player_id,
            PropLine.stat_type == prop_type,
            PropLine.is_settled == True,
        )
        .order_by(PropLine.start_time.desc())
        .limit(20)
    )
    props = result.scalars().all()

    if not props:
        return {"player_name": player_id, "streak": 0, "direction": None, "label": None}

    direction = "over" if props[0].line >= line else "under"
    streak = 0
    for p in props:
        hit = p.line >= line
        if (direction == "over" and hit) or (direction == "under" and not hit):
            streak += 1
        else:
            break

    label = None
    if streak >= 3:
        emoji = "🔥" if direction == "over" else "❄️"
        label = f"{emoji} {streak} straight {direction}s"

    return {"player_name": player_id, "streak": streak, "direction": direction, "label": label}
