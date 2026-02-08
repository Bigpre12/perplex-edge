"""
Debug EV Calculation API - Diagnose impossible EV values
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import ModelPick, Player, Team, Market
from app.services.model import compute_ev

router = APIRouter(prefix = " / debug", tags = ["debug"])

@router.get(" / ev - analysis / {sport_id}")
async def debug_ev_analysis(sport_id: int,
 limit: int = Query(default = 10, description = "Number of picks to analyze"),
 db: AsyncSession = Depends(get_db)):
 """Debug EV calculation to identify impossible values."""
 try:
 debug_info = {
 "timestamp": datetime.now(timezone.utc).isoformat(),
 "sport_id": sport_id,
 "analysis": {},
 "sample_picks": [],
 "recommendations": []
 }

 # Get sample picks with full data
 query = select(ModelPick).options(selectinload(ModelPick.player).selectinload(Player.team),
 selectinload(ModelPick.market)).where(ModelPick.sport_id =  = sport_id).order_by(desc(ModelPick.expected_value)).limit(limit)

 result = await db.execute(query)
 picks = result.scalars().all()

 analysis = {
 "total_picks_analyzed": len(picks),
 "ev_distribution": {
 "over_10_percent": 0,
 "over_5_percent": 0,
 "over_3_percent": 0,
 "realistic_1_3_percent": 0,
 "under_1_percent": 0,
 "negative_ev": 0
 },
 "probability_analysis": {
 "over_80_percent": 0,
 "over_70_percent": 0,
 "over_60_percent": 0,
 "realistic_50_60_percent": 0,
 "under_50_percent": 0
 },
 "calculation_errors": []
 }

 for pick in picks:
 # Get pick data
 pick_data = {
 "id": pick.id,
 "player_name": pick.player.name if pick.player else "Unknown",
 "team_name": pick.player.team.name if pick.player and pick.player.team else "Unknown",
 "stat_type": pick.market.stat_type if pick.market else "unknown",
 "line_value": pick.line_value,
 "side": pick.side,
 "odds": pick.odds,
 "expected_value": pick.expected_value,
 "model_probability": pick.model_probability,
 "implied_probability": pick.implied_probability,
 "confidence_score": pick.confidence_score
 }

 # Calculate what EV SHOULD be
 if pick.odds and pick.model_probability:
 calculated_ev = compute_ev(pick.model_probability, int(pick.odds))
 pick_data["calculated_ev"] = calculated_ev

 # Check for calculation errors
 if abs(calculated_ev - pick.expected_value) > 0.01:
 pick_data["calculation_error"] = True
 pick_data["error_amount"] = abs(calculated_ev - pick.expected_value)
 analysis["calculation_errors"].append({
 "pick_id": pick.id,
 "player": pick.player.name if pick.player else "Unknown",
 "stored_ev": pick.expected_value,
 "calculated_ev": calculated_ev,
 "difference": pick.expected_value - calculated_ev
 })
 else:
 pick_data["calculation_error"] = False
 else:
 pick_data["calculated_ev"] = None
 pick_data["calculation_error"] = False

 # Categorize EV values
 ev = pick.expected_value
 if ev > 0.10:
 analysis["ev_distribution"]["over_10_percent"] + = 1
 elif ev > 0.05:
 analysis["ev_distribution"]["over_5_percent"] + = 1
 elif ev > 0.03:
 analysis["ev_distribution"]["over_3_percent"] + = 1
 elif 0.01 < = ev < = 0.03:
 analysis["ev_distribution"]["realistic_1_3_percent"] + = 1
 elif ev < 0.01:
 analysis["ev_distribution"]["under_1_percent"] + = 1

 if ev < 0:
 analysis["ev_distribution"]["negative_ev"] + = 1

 # Categorize probabilities
 if pick.model_probability:
 prob = pick.model_probability
 if prob > 0.80:
 analysis["probability_analysis"]["over_80_percent"] + = 1
 elif prob > 0.70:
 analysis["probability_analysis"]["over_70_percent"] + = 1
 elif prob > 0.60:
 analysis["probability_analysis"]["over_60_percent"] + = 1
 elif 0.50 < = prob < = 0.60:
 analysis["probability_analysis"]["realistic_50_60_percent"] + = 1
 else:
 analysis["probability_analysis"]["under_50_percent"] + = 1

 debug_info["sample_picks"].append(pick_data)

 # Generate recommendations
 recommendations = []

 if analysis["ev_distribution"]["over_10_percent"] > 0:
 recommendations.append("CRITICAL: Database contains EV > 10% - mathematically impossible")
 recommendations.append("Action: Recalculate all EV values with proper probability calibration")

 if analysis["ev_distribution"]["over_5_percent"] > len(picks) * 0.1:
 recommendations.append("WARNING: More than 10% of picks have EV > 5% - extremely unlikely")
 recommendations.append("Action: Review model probability calibration")

 if analysis["probability_analysis"]["over_80_percent"] > len(picks) * 0.2:
 recommendations.append("CAUTION: More than 20% of picks have model probability > 80%")
 recommendations.append("Action: Model may be overconfident - add regression to mean")

 if len(analysis["calculation_errors"]) > 0:
 recommendations.append(f"ERROR: {len(analysis['calculation_errors'])} picks have EV calculation mismatches")
 recommendations.append("Action: Fix EV calculation formula or database corruption")

 if not recommendations:
 recommendations.append("OK: EV values appear to be in realistic ranges")

 debug_info["analysis"] = analysis
 debug_info["recommendations"] = recommendations

 return debug_info

 except Exception as e:
 return {
 "timestamp": datetime.now(timezone.utc).isoformat(),
 "error": str(e),
 "analysis": "Failed to analyze EV calculations"
 }
