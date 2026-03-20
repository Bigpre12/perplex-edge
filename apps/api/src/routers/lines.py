from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from models.line_move import LineMove
from schemas.line_move import LineMoveOut

router = APIRouter()

@router.get("", response_model=list[LineMoveOut])
async def line_movement(
    sport: str = Query("basketball_nba"),
    db: AsyncSession = Depends(get_db),
):
    try:
        stmt = select(LineMove).filter(LineMove.sport == sport).order_by(desc(LineMove.created_at))
        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception:
        return []
