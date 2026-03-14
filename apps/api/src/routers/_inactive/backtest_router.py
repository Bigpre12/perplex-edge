class AsyncSession: pass
from fastapi import APIRouter, Depends, HTTPException
from database import get_async_db
from routers.auth import get_current_user
from services.backtest_service import backtest_service
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/backtest", tags=["backtest"])

class BacktestRequest(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    initial_bankroll: float = 1000.0
    min_ev: float = 3.0
    bet_sizing_model: str = "fixed" # fixed, kelly, half_kelly
    unit_size: float = 1.0
    sport_filter: Optional[List[str]] = None

@router.post("/run")
async def run_backtest(
    request: BacktestRequest,
    db: AsyncSession = Depends(get_async_db),
    user: dict = Depends(get_current_user)
):
    """
    Trigger a historical strategy simulation.
    """
    # Default to last 30 days if no dates provided
    start = request.start_date or (datetime.now() - timedelta(days=30))
    end = request.end_date or datetime.now()
    
    try:
        results = await backtest_service.run_simulation(
            db=db,
            start_date=start,
            end_date=end,
            initial_bankroll=request.initial_bankroll,
            min_ev=request.min_ev,
            bet_sizing_model=request.bet_sizing_model,
            unit_size=request.unit_size,
            sport_filter=request.sport_filter
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_backtest_history(user: dict = Depends(get_current_user)):
    """
    Retrieve historical backtest summary results for the user.
    """
    # This would typically fetch from a 'backtest_results' table
    # For now, returning a structural placeholder
    return {
        "user_id": user['id'],
        "history": [
            {"id": 1, "name": "NBA Kelly Strategy", "return": "14.2%", "date": "2026-02-25"},
            {"id": 2, "name": "NHL Fixed Unit", "return": "5.1%", "date": "2026-02-24"}
        ]
    }
