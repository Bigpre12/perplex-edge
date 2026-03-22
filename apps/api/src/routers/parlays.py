from fastapi import APIRouter, Query, Depends
from typing import List, Dict, Any
from db.session import async_session_maker
from services.parlay_service import parlay_service
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
        async with async_session_maker() as session:
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
