from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession


@router.get("")
@router.get("/")
async def news(
    sport: str = Query("basketball_nba"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Injury).filter(Injury.sport == sport).order_by(desc(Injury.created_at))
    result = await db.execute(stmt)
    return result.scalars().all()
