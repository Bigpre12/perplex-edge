from fastapi import APIRouter, Query, Depends
from typing import List, Dict, Any, Optional
from db.session import AsyncSessionLocal
from services.parlay_service import parlay_service
from services.monte_carlo_service import monte_carlo_service
from schemas.universal import UniversalResponse, ResponseMeta
from middleware.request_id import get_request_id
from models.brain import UnifiedEVSignal
from sqlalchemy import select, desc

router = APIRouter(tags=["parlays"])

@router.get("", response_model=UniversalResponse[dict])
@router.get("/", response_model=UniversalResponse[dict])
async def get_parlay_suggestions(
    sport: str = Query("basketball_nba"),
    min_edge: float = Query(2.0),
    limit: int = Query(10)
):
    """
    Returns correlated parlay suggestions generated from high-EV props.
    """
    try:
        async with AsyncSessionLocal() as session:
            # 1. Fetch high-EV props for the sport
            stmt = select(UnifiedEVSignal).where(
                UnifiedEVSignal.sport == sport,
                UnifiedEVSignal.edge_percent >= min_edge
            ).order_by(desc(UnifiedEVSignal.edge_percent)).limit(50)
            
            res = await session.execute(stmt)
            props = res.scalars().all()
            
            if not props:
                return UniversalResponse(
                    status="no_data",
                    meta=ResponseMeta(request_id=get_request_id(), source="parlay_engine", db_rows=0),
                    data=[]
                )

            # 2. Convert to dicts for the service
            prop_dicts = []
            for p in props:
                prop_dicts.append({
                    "id": p.id,
                    "sport": p.sport,
                    "game_id": p.event_id,
                    "market_key": p.market_key,
                    "player_name": p.player_name,
                    "side": p.outcome_key,
                    "odds": float(p.price),
                    "edge": float(p.edge_percent)
                })

            # 3. Use parlay_service to bundle
            bundles = parlay_service.suggest_bundles(prop_dicts)
            results = bundles[:limit]

            return UniversalResponse(
                status="ok" if results else "no_data",
                meta=ResponseMeta(
                    source="parlay_engine",
                    db_rows=len(results),
                    request_id=get_request_id()
                ),
                data=results
            )
    except Exception as e:
        import logging
        logging.error(f"Parlay Router Error: {e}")
        return UniversalResponse(
            status="error",
            message=str(e),
            meta=ResponseMeta(request_id=get_request_id()),
            data=[]
        )

@router.post("/simulate")
async def simulate_parlay(payload: Dict[str, Any]):
    """
    Runs a Monte Carlo simulation for a given set of parlay legs.
    """
    try:
        legs = payload.get("legs", [])
        n_sims = payload.get("n_sims", 10000)
        
        # Ensure legs have required simulation fields (mean/std) if missing
        # For a real parlay matrix, we'd pull these from the model or historical data.
        # Here we apply a realistic default based on the hit rate if provided.
        for leg in legs:
            if "mean" not in leg:
                # If historical_hit_rate is 50%, mean is roughly the line
                leg["mean"] = leg.get("line", 0)
                leg["std_dev"] = abs(leg["mean"]) * 0.15 if leg["mean"] != 0 else 1.0
                leg["distribution"] = "normal"

        results = monte_carlo_service.simulate_parlay(legs, n_sims=n_sims)
        
        # Format for frontend expectations (page.tsx Line 72-81)
        return {
            "roi": results["parlay_ev"] * 100,
            "edge": results["parlay_ev"],
            "win_rate": results["parlay_hit_rate"],
            "expected_value": results["parlay_ev"],
            "true_probability": results["parlay_hit_rate"],
            "confidence": "high" if results["parlay_ev"] > 0.05 else "medium",
            "max_drawdown": 0.15, # Placeholder
            "leg_results": results["leg_results"]
        }
    except Exception as e:
        import logging
        logging.error(f"Simulation API Error: {e}")
        return {"error": str(e), "roi": 0, "edge": 0}
