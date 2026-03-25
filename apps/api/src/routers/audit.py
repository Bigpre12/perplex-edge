from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional
from db.session import get_db

router = APIRouter(prefix="/api/audit", tags=["audit"])

@router.get("")
async def get_audit(
    sport: Optional[str] = Query(default=None),
    book: Optional[str] = Query(default=None),
    grade: Optional[str] = Query(default=None),
    date_from: Optional[str] = Query(default=None),
    date_to: Optional[str] = Query(default=None),
    page: int = Query(default=1),
    limit: int = Query(default=50),
    db: AsyncSession = Depends(get_db)
):
    try:
        offset = (page - 1) * limit
        conditions = []
        from typing import Any
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        
        if sport:
            conditions.append("sport = :sport")
            params["sport"] = sport
        if book:
            conditions.append("book = :book")
            params["book"] = book
        if grade:
            conditions.append("grade = :grade")
            params["grade"] = grade
        if date_from:
            conditions.append("last_updated_at >= :date_from")
            params["date_from"] = date_from
        if date_to:
            conditions.append("last_updated_at <= :date_to")
            params["date_to"] = date_to
            
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # Count total rows
        count_sql = text(f"SELECT COUNT(*) FROM props_live WHERE {where_clause}")
        count_res = await db.execute(count_sql, params)
        total_count = count_res.scalar() or 0
        total_pages = (total_count + limit - 1) // limit

        query_sql = text(f"""
            SELECT 
                player_name, market_key, sport, book,
                line, odds_over, odds_under,
                confidence, grade,
                commence_time, last_updated_at,
                home_team, away_team
            FROM props_live
            WHERE {where_clause}
            ORDER BY last_updated_at DESC
            LIMIT :limit OFFSET :offset
        """)
        
        res = await db.execute(query_sql, params)
        rows = res.mappings().all()
        
        return {
            "rows": [dict(r) for r in rows],
            "total": total_count,
            "page": page,
            "pages": total_pages,
            "status": "ok" if rows else "no_data"
        }
    except Exception as e:
        return {
            "rows": [],
            "total": 0,
            "page": page,
            "pages": 0,
            "status": "error",
            "detail": str(e)
        }
