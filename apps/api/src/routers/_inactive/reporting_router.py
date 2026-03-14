class AsyncSession: pass
from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse, StreamingResponse
from database import get_async_db
from routers.auth import get_current_user
from services.ledger_service import ledger_service
import io
import csv
import json

router = APIRouter(prefix="/reporting", tags=["reporting"])

@router.get("/export/csv")
async def export_ledger_csv(
    db: AsyncSession = Depends(get_async_db),
    user: dict = Depends(get_current_user)
):
    """Export the user's betting ledger as institutional-grade CSV."""
    slips = await ledger_service.get_user_ledger(db, user['id'])
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Date", "Bookmaker", "Odds", "Type", "Status", "Profit/Loss"])
    
    for s in slips:
        # Simplified profit calc logic (matches LedgerService)
        profit = 0
        if s.status == "won":
            profit = (s.total_odds/100) if s.total_odds > 0 else (100/abs(s.total_odds))
        elif s.status == "lost":
            profit = -1.0
            
        writer.writerow([
            s.id, s.placed_at.isoformat() if s.placed_at else "", s.sportsbook, s.total_odds, s.slip_type, s.status, round(profit, 2)
        ])
    
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=perplex_ledger_{user['username']}.csv"}
    )

@router.get("/export/json")
async def export_ledger_json(
    db: AsyncSession = Depends(get_async_db),
    user: dict = Depends(get_current_user)
):
    """Export the user's betting ledger as structured JSON for institutional audits."""
    slips = await ledger_service.get_user_ledger(db, user['id'])
    data = []
    for s in slips:
         data.append({
             "id": s.id,
             "placed_at": s.placed_at.isoformat() if s.placed_at else "",
             "sportsbook": s.sportsbook,
             "total_odds": s.total_odds,
             "slip_type": s.slip_type,
             "status": s.status
         })
    return JSONResponse(content=data)
