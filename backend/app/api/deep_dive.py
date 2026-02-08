"""
Deep Dive API endpoints — comprehensive analysis of injuries, starters, and market factors.

Provides detailed insights for:
 - Injury analysis and impact on prop lines
 - Starter / bench changes and minutes adjustments
 - Team matchup analysis
 - Market sentiment and line movements
 - Historical performance trends
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.deep_dive_service import deep_dive_service

router = APIRouter()

@router.get(" / injuries", tags = ["deep - dive"])
async def get_injury_analysis(sport_id: int = Query(..., description = "Sport ID(30 = NBA, 31 = NFL, etc.)"),
 db: AsyncSession = Depends(get_db)):
 """
 Get comprehensive injury analysis for a sport.

 Returns detailed injury information including:
 - Player injury status and probability
 - Impact score on team performance
 - Affected teammates and line adjustments
 - Replacement player analysis
 """
 try:
 injuries = await deep_dive_service.analyze_injuries(db, sport_id)

 return {
 "sport_id": sport_id,
 "injuries": [
 {
 "player": impact.player_name,
 "status": impact.status,
 "detail": impact.status_detail,
 "probability": impact.probability,
 "is_starter": impact.is_starter,
 "impact_score": impact.impact_score,
 "affected_teammates": impact.affected_teammates,
 "replacement": impact.minutes_replacement,
 "line_adjustments": impact.line_adjustment
 }
 for impact in injuries
 ],
 "summary": {
 "total_injuries": len(injuries),
 "significant_injuries": len([i for i in injuries if i.impact_score > 0.5]),
 "starters_out": len([i for i in injuries if i.is_starter and i.status in ["OUT", "DOUBTFUL"]])
 }
 }
 except Exception as e:
 raise HTTPException(status_code = 500, detail = f"Failed to analyze injuries: {str(e)}")

@router.get(" / starters", tags = ["deep - dive"])
async def get_starter_changes(sport_id: int = Query(..., description = "Sport ID(30 = NBA, 31 = NFL, etc.)"),
 db: AsyncSession = Depends(get_db)):
 """
 Get recent starter / bench changes for a sport.

 Returns information about:
 - Players moving from starter to bench
 - Players moving from bench to starter
 - Expected minutes changes
 - Impact on prop lines
 """
 try:
 changes = await deep_dive_service.analyze_starter_changes(db, sport_id)

 return {
 "sport_id": sport_id,
 "changes": [
 {
 "player": change.player_name,
 "role_change": f"{change.old_role} → {change.new_role}",
 "minutes_impact": change.minutes_change,
 "prop_impacts": change.impact_on_props,
 "reason": change.reason
 }
 for change in changes
 ],
 "summary": {
 "total_changes": len(changes),
 "promotions": len([c for c in changes if c.new_role =  = "starter"]),
 "demotions": len([c for c in changes if c.new_role =  = "bench"])
 }
 }
 except Exception as e:
 raise HTTPException(status_code = 500, detail = f"Failed to analyze starter changes: {str(e)}")

@router.get(" / matchup / {game_id}", tags = ["deep - dive"])
async def get_matchup_analysis(game_id: str,
 db: AsyncSession = Depends(get_db)):
 """
 Get deep matchup analysis for a specific game.

 Returns comprehensive matchup data including:
 - Team pace and defensive ratings
 - Home court advantage calculation
 - Key player matchups to watch
 - Historical performance trends
 """
 try:
 matchup = await deep_dive_service.analyze_matchup(db, game_id)

 return {
 "game_id": game_id,
 "matchup": {
 "home_team": matchup.home_team,
 "away_team": matchup.away_team,
 "home_advantage": matchup.home_advantage,
 "pace_rating": matchup.pace_rating,
 "defensive_ratings": {
 "home": matchup.defensive_rating[0],
 "away": matchup.defensive_rating[1]
 },
 "key_matchups": matchup.key_matchups,
 "betting_trends": matchup.betting_trends
 }
 }
 except ValueError as e:
 raise HTTPException(status_code = 404, detail = str(e))
 except Exception as e:
 raise HTTPException(status_code = 500, detail = f"Failed to analyze matchup: {str(e)}")

@router.get(" / sentiment / {game_id}", tags = ["deep - dive"])
async def get_market_sentiment(game_id: str,
 db: AsyncSession = Depends(get_db)):
 """
 Get market sentiment analysis for a specific game.

 Returns market intelligence including:
 - Line movements over time
 - Betting volume analysis
 - Sharp money indicators
 - Public betting percentages
 """
 try:
 sentiment = await deep_dive_service.analyze_market_sentiment(db, game_id)

 return {
 "game_id": game_id,
 "sport": sentiment.sport,
 "line_movements": sentiment.line_movements,
 "volume_analysis": sentiment.volume_analysis,
 "sharp_money": sentiment.sharp_money,
 "public_percentage": sentiment.public_percentage
 }
 except ValueError as e:
 raise HTTPException(status_code = 404, detail = str(e))
 except Exception as e:
 raise HTTPException(status_code = 500, detail = f"Failed to analyze market sentiment: {str(e)}")

@router.get(" / comprehensive", tags = ["deep - dive"])
async def get_comprehensive_analysis(sport_id: int = Query(..., description = "Sport ID(30 = NBA, 31 = NFL, etc.)"),
 game_id: str = Query(None, description = "Optional: Specific game ID for deeper analysis"),
 db: AsyncSession = Depends(get_db)):
 """
 Get comprehensive deep dive analysis.

 Combines all analysis types into a single response:
 - Injury analysis
 - Starter changes
 - Market sentiment(if game_id provided)
 - Matchup analysis(if game_id provided)
 """
 try:
 analysis = await deep_dive_service.get_comprehensive_analysis(db, sport_id, game_id)

 return {
 "sport_id": sport_id,
 "game_id": game_id,
 "timestamp": "2025 - 02 - 06T01:00:00Z", # Would use real timestamp
 "data": analysis
 }
 except Exception as e:
 raise HTTPException(status_code = 500, detail = f"Failed to get comprehensive analysis: {str(e)}")

@router.get(" / impact - alerts", tags = ["deep - dive"])
async def get_impact_alerts(sport_id: int = Query(..., description = "Sport ID(30 = NBA, 31 = NFL, etc.)"),
 min_impact: float = Query(0.7, description = "Minimum impact score(0.0 - 1.0)"),
 db: AsyncSession = Depends(get_db)):
 """
 Get high - impact alerts for significant changes.

 Returns only the most impactful events that could affect betting:
 - Major injuries(impact > 0.7)
 - Significant starter changes
 - Unusual line movements
 """
 try:
 injuries = await deep_dive_service.analyze_injuries(db, sport_id)
 starter_changes = await deep_dive_service.analyze_starter_changes(db, sport_id)

 # Filter for high - impact events
 major_injuries = [i for i in injuries if i.impact_score > = min_impact]

 alerts = []

 # Injury alerts
 for injury in major_injuries:
 alerts.append({
 "type": "injury",
 "severity": "critical" if injury.impact_score > 0.9 else "high",
 "player": injury.player_name,
 "status": injury.status,
 "impact": injury.impact_score,
 "affected_props": list(injury.line_adjustment.keys()),
 "message": f"{injury.player_name} ({injury.status}) - {injury.status_detail}"
 })

 # Starter change alerts
 for change in starter_changes:
 if abs(change.minutes_change) > 10: # Significant minutes change
 alerts.append({
 "type": "starter_change",
 "severity": "medium",
 "player": change.player_name,
 "change": f"{change.old_role} → {change.new_role}",
 "minutes_impact": change.minutes_change,
 "message": f"{change.player_name} moving to {change.new_role}"
 })

 return {
 "sport_id": sport_id,
 "min_impact_threshold": min_impact,
 "alerts": sorted(alerts, key = lambda x: x.get("impact", 0), reverse = True),
 "summary": {
 "total_alerts": len(alerts),
 "critical_alerts": len([a for a in alerts if a.get("severity") =  = "critical"]),
 "injury_alerts": len([a for a in alerts if a["type"] =  = "injury"])
 }
 }
 except Exception as e:
 raise HTTPException(status_code = 500, detail = f"Failed to get impact alerts: {str(e)}")
