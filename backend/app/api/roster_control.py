"""
Roster Control API - 2026 Trade Management
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.roster_manager_2026 import roster_manager_2026

router = APIRouter(prefix = " / api / roster", tags = ["roster - control"])

@router.get(" / status")
async def get_roster_status():
 """Get current roster management status."""
 try:
 return {
 "timestamp": datetime.now(timezone.utc).isoformat(),
 "roster_control": {
 "status": "active",
 "version": "2026.2.0",
 "last_update": roster_manager_2026.last_update,
 "total_trades_processed": len(roster_manager_2026.trades_2026),
 "capabilities": [
 "2026_trade_processing",
 "roster_validation",
 "team_management",
 "trade_history_tracking",
 "integrity_checks"
 ]
 }
 }

 except Exception as e:
 raise HTTPException(status_code = 500, detail = f"Roster status error: {e}")

@router.post(" / process - 2026 - trades")
async def process_2026_trades(db: AsyncSession = Depends(get_db)):
 """Process all 2026 trades and update rosters."""
 try:
 result = await roster_manager_2026.process_2026_trades(db)

 return {
 "timestamp": datetime.now(timezone.utc).isoformat(),
 "action": "2026_trades_processed",
 "result": result,
 "message": f"Processed {result['processed_trades']} / {result['total_trades']} trades"
 }

 except Exception as e:
 raise HTTPException(status_code = 500, detail = f"Trade processing error: {e}")

@router.get(" / current - rosters")
async def get_current_rosters(sport_id: int = Query(30, description = "Sport ID(30 = NBA, 32 = NCAA, 53 = NHL)"),
 db: AsyncSession = Depends(get_db)):
 """Get current rosters with 2026 trades applied."""
 try:
 rosters = await roster_manager_2026.get_current_rosters(db, sport_id)

 return {
 "timestamp": datetime.now(timezone.utc).isoformat(),
 "sport_id": sport_id,
 "rosters": rosters
 }

 except Exception as e:
 raise HTTPException(status_code = 500, detail = f"Roster retrieval error: {e}")

@router.get(" / trade - history")
async def get_trade_history(limit: int = Query(50, description = "Maximum number of trades to return"),
 db: AsyncSession = Depends(get_db)):
 """Get recent trade history."""
 try:
 history = await roster_manager_2026.get_trade_history(db, limit)

 return {
 "timestamp": datetime.now(timezone.utc).isoformat(),
 "trade_history": history
 }

 except Exception as e:
 raise HTTPException(status_code = 500, detail = f"Trade history error: {e}")

@router.get(" / validate - rosters")
async def validate_rosters(db: AsyncSession = Depends(get_db)):
 """Validate roster integrity."""
 try:
 validation = await roster_manager_2026.validate_rosters(db)

 return {
 "timestamp": datetime.now(timezone.utc).isoformat(),
 "roster_validation": validation
 }

 except Exception as e:
 raise HTTPException(status_code = 500, detail = f"Roster validation error: {e}")

@router.get(" / 2026 - trades")
async def get_2026_trades():
 """Get list of all 2026 trades."""
 try:
 return {
 "timestamp": datetime.now(timezone.utc).isoformat(),
 "total_trades": len(roster_manager_2026.trades_2026),
 "trades_2026": roster_manager_2026.trades_2026,
 "trade_summary": {
 "blockbuster_trades": len([t for t in roster_manager_2026.trades_2026 if t["trade_type"] =  = "blockbuster"]),
 "transfers": len([t for t in roster_manager_2026.trades_2026 if t["trade_type"] =  = "transfer"]),
 "high_impact_trades": len([t for t in roster_manager_2026.trades_2026 if t["impact"] =  = "high"])
 }
 }

 except Exception as e:
 raise HTTPException(status_code = 500, detail = f"2026 trades error: {e}")

@router.post(" / force - roster - update")
async def force_roster_update(sport_id: int = Query(30, description = "Sport ID to update"),
 db: AsyncSession = Depends(get_db)):
 """Force immediate roster update for a sport."""
 try:
 # Process trades first
 await roster_manager_2026.process_2026_trades(db)

 # Get updated rosters
 rosters = await roster_manager_2026.get_current_rosters(db, sport_id)

 return {
 "timestamp": datetime.now(timezone.utc).isoformat(),
 "action": "force_roster_update",
 "sport_id": sport_id,
 "rosters": rosters,
 "message": f"Force updated rosters for sport {sport_id}"
 }

 except Exception as e:
 raise HTTPException(status_code = 500, detail = f"Force roster update error: {e}")

@router.get(" / team - roster / {team_name}")
async def get_team_roster(team_name: str,
 db: AsyncSession = Depends(get_db)):
 """Get detailed roster for a specific team."""
 try:
 result = await db.execute(text(f"""
 SELECT
 p.name as player_name,
 p.position,
 p.jersey_number,
 p.height,
 p.weight,
 p.college,
 p.draft_year,
 p.updated_at
 FROM players p
 JOIN teams t ON p.team_id = t.id
 WHERE t.name = '{team_name}' OR t.abbreviation = '{team_name}'
 ORDER BY p.name
 """))

 rows = result.fetchall()

 players = [
 {
 "name": row[0],
 "position": row[1],
 "jersey_number": row[2],
 "height": row[3],
 "weight": row[4],
 "college": row[5],
 "draft_year": row[6],
 "last_updated": row[7].isoformat() if row[7] else None
 }
 for row in rows
 ]

 return {
 "timestamp": datetime.now(timezone.utc).isoformat(),
 "team_name": team_name,
 "total_players": len(players),
 "players": players
 }

 except Exception as e:
 raise HTTPException(status_code = 500, detail = f"Team roster error: {e}")

@router.get(" / player / {player_name}")
async def get_player_info(player_name: str,
 db: AsyncSession = Depends(get_db)):
 """Get detailed information for a specific player."""
 try:
 result = await db.execute(text(f"""
 SELECT
 p.name,
 p.position,
 p.jersey_number,
 p.height,
 p.weight,
 p.college,
 p.draft_year,
 t.name as current_team,
 t.abbreviation as team_abbr,
 p.updated_at
 FROM players p
 LEFT JOIN teams t ON p.team_id = t.id
 WHERE p.name = '{player_name}'
 """))

 row = result.fetchone()

 if not row:
 raise HTTPException(status_code = 404, detail = f"Player {player_name} not found")

 # Get trade history for this player
 trade_result = await db.execute(text(f"""
 SELECT
 from_team,
 to_team,
 trade_date,
 trade_type
 FROM trade_history
 WHERE player_name = '{player_name}'
 ORDER BY trade_date DESC
 """))

 trade_rows = trade_result.fetchall()

 trade_history = [
 {
 "from_team": tr[0],
 "to_team": tr[1],
 "trade_date": tr[2].isoformat(),
 "trade_type": tr[3]
 }
 for tr in trade_rows
 ]

 return {
 "timestamp": datetime.now(timezone.utc).isoformat(),
 "player_info": {
 "name": row[0],
 "position": row[1],
 "jersey_number": row[2],
 "height": row[3],
 "weight": row[4],
 "college": row[5],
 "draft_year": row[6],
 "current_team": row[7],
 "team_abbr": row[8],
 "last_updated": row[9].isoformat() if row[9] else None,
 "trade_history": trade_history
 }
 }

 except HTTPException:
 raise
 except Exception as e:
 raise HTTPException(status_code = 500, detail = f"Player info error: {e}")
