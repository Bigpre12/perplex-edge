class AsyncSession: pass
from fastapi import APIRouter, Depends
from sqlalchemy import select
from database import get_async_db
from models.bets import BetLog, BetResult
from collections import defaultdict

router = APIRouter(prefix="/api/performance", tags=["performance"])

@router.get("/{user_id}")
async def get_performance(user_id: str, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(
        select(BetLog)
        .where(BetLog.user_id == user_id, BetLog.result != BetResult.pending)
        .order_by(BetLog.placed_at.asc())
    )
    bets = result.scalars().all()
    if not bets:
        return {"empty": True}

    monthly = defaultdict(lambda: {"wins": 0, "losses": 0, "pl": 0.0})
    by_sport = defaultdict(lambda: {"wins": 0, "total": 0, "pl": 0.0})

    for b in bets:
        key = b.placed_at.strftime("%b %Y") if b.placed_at else "Unknown"
        monthly[key]["pl"] += b.profit_loss or 0
        if b.result == BetResult.win:
            monthly[key]["wins"] += 1
            by_sport[b.sport or "unknown"]["wins"] += 1
        else:
            monthly[key]["losses"] += 1
        by_sport[b.sport or "unknown"]["total"] += 1
        by_sport[b.sport or "unknown"]["pl"] += b.profit_loss or 0

    wins = sum(1 for b in bets if b.result == BetResult.win)
    total_pl = sum(b.profit_loss or 0 for b in bets)
    best = max(bets, key=lambda b: b.profit_loss or 0)
    worst = min(bets, key=lambda b: b.profit_loss or 0)

    return {
        "total_bets": len(bets),
        "wins": wins,
        "losses": len(bets) - wins,
        "win_rate": round(wins / len(bets) * 100, 1),
        "total_pl": round(total_pl, 2),
        "roi": round(total_pl / len(bets) * 100, 1),
        "best_bet": {"player": best.player_name, "prop": best.prop_type, "pl": best.profit_loss},
        "worst_bet": {"player": worst.player_name, "prop": worst.prop_type, "pl": worst.profit_loss},
        "monthly": [{"month": k, **v} for k, v in monthly.items()],
        "by_sport": [
            {
                "sport": k.replace("basketball_","").replace("americanfootball_","").upper(),
                **v,
                "win_rate": round(v["wins"] / max(v["total"], 1) * 100, 1)
            }
            for k, v in by_sport.items()
        ],
    }
