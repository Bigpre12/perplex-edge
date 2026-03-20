from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import asyncio
from services.monte_carlo import monte_carlo_engine, SimLeg

router = APIRouter()

class LegRequest(BaseModel):
    player_name: str
    market: str
    line: float
    side: str
    over_price: int
    under_price: int
    historical_hit_rate: Optional[float] = None

class SimulationRequest(BaseModel):
    legs: List[LegRequest]
    stake: float = 100.0
    simulations: int = 10000

class SimulationResponse(BaseModel):
    simulations: int
    win_rate: float
    expected_value: float
    roi: float
    max_drawdown: float
    break_even_rate: float
    edge: float
    confidence: str
    historical_hit_rate: Optional[float]
    true_probability: float
    blend_method: str
    legs: int

@router.post("/", response_model=SimulationResponse)
async def simulate(request: SimulationRequest):
    """
    Run a Monte Carlo simulation for a prop or parlay.
    """
    if not request.legs:
        raise HTTPException(status_code=400, detail="No legs provided")

    try:
        # Convert Pydantic to Service Dataclasses
        service_legs = [
            SimLeg(
                player_name=l.player_name,
                market=l.market,
                line=l.line,
                side=l.side,
                over_price=l.over_price,
                under_price=l.under_price,
                historical_hit_rate=l.historical_hit_rate
            ) for l in request.legs
        ]

        # Run in thread executor as it's CPU-bound
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            monte_carlo_engine.run_simulation, 
            service_legs, 
            request.stake, 
            request.simulations
        )

        return SimulationResponse(
            simulations=result.simulations,
            win_rate=result.win_rate,
            expected_value=result.expected_value,
            roi=result.roi,
            max_drawdown=result.max_drawdown,
            break_even_rate=result.break_even_rate,
            edge=result.edge,
            confidence=result.confidence,
            historical_hit_rate=result.historical_hit_rate,
            true_probability=result.true_probability,
            blend_method=result.blend_method,
            legs=result.legs
        )

    except Exception as e:
        import traceback
        print(f"Simulation Error: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
