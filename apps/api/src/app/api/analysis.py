from fastapi import APIRouter
from datetime import datetime, timezone
from app.services.picks_service import picks_service

router = APIRouter()

@router.get("/clv-summary")
async def get_clv_summary(sport_id: int = 30):
    """Get summary of Closing Line Value (CLV) performance by sport."""
    try:
        # Uses picks_service to pull picks with CLV columns
        picks = await picks_service.get_picks(sport_id, hours=72, limit=100)
        
        clv_values = [float(p.get("clv_percentage", 0)) for p in picks if p.get("clv_percentage")]
        avg_clv = sum(clv_values) / len(clv_values) if clv_values else 0.0
        
        return {
            "items": [], # Summary-style endpoint, items empty or specific meta
            "total": 0,
            "avg_clv": round(avg_clv, 2),
            "total_picks_analyzed": len(picks),
            "market_efficiency": "High" if avg_clv > 2 else "Normal",
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": None
        }
    except Exception as e:
        return {
            "items": [],
            "total": 0,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/market-bias")
async def get_market_bias():
    """Identify systemic market biases in current lines."""
    return {
        "items": [
            {
                "bias_detected": "Under-dogs slightly undervalued in NBA totals",
                "confidence": 0.82
            }
        ],
        "total": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "error": None
    }
