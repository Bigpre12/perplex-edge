"""
Data Integrity API - Comprehensive Data Correction Endpoints
"""

import random
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db
from app.services.data_integrity_fixer import data_integrity_fixer

router = APIRouter(prefix = " / api / data - integrity", tags = ["data - integrity"])

@router.get(" / diagnose")
async def diagnose_corruption(db: AsyncSession = Depends(get_db)):
 """Diagnose all data corruption issues."""
 try:
 diagnosis = await data_integrity_fixer.diagnose_data_corruption(db)

 return {
 "timestamp": datetime.now(timezone.utc).isoformat(),
 "data_integrity_diagnosis": diagnosis,
 "summary": {
 "total_sports_checked": len(diagnosis["affected_sports"]),
 "corrupted_sports": len([s for s, status in diagnosis["affected_sports"].items() if status =  = "CORRUPTED"]),
 "recommended_actions": len(diagnosis["recommended_actions"])
 }
 }

 except Exception as e:
 raise HTTPException(status_code = 500, detail = f"Diagnosis failed: {e}")

@router.post(" / fix - sport / {sport_id}")
async def fix_sport_data(sport_id: int,
 db: AsyncSession = Depends(get_db)):
 """Fix data corruption for a specific sport."""
 try:
 # Step 1: Fix sport mapping
 fix_result = await data_integrity_fixer.fix_sport_mapping(db, sport_id)

 # Step 2: Generate correct picks
 if fix_result.get("status") =  = "fixed":
 generation_result = await data_integrity_fixer.generate_correct_picks(db, sport_id)
 fix_result["pick_generation"] = generation_result

 # Step 3: Validate fix
 validation_result = await data_integrity_fixer.validate_fix(db, sport_id)
 fix_result["validation"] = validation_result

 return {
 "timestamp": datetime.now(timezone.utc).isoformat(),
 "sport_fix_result": fix_result,
 "sport_name": {30: "NBA", 32: "NCAA Basketball", 53: "NHL"}[sport_id]
 }

 except Exception as e:
 raise HTTPException(status_code = 500, detail = f"Sport fix failed: {e}")

@router.post(" / fix - all - sports")
async def fix_all_sports(db: AsyncSession = Depends(get_db)):
 """Fix data corruption for all sports."""
 try:
 sports = [30, 32, 53] # NBA, NCAA, NHL
 results = {}

 for sport_id in sports:
 # Fix sport mapping
 fix_result = await data_integrity_fixer.fix_sport_mapping(db, sport_id)

 # Generate correct picks
 if fix_result.get("status") =  = "fixed":
 generation_result = await data_integrity_fixer.generate_correct_picks(db, sport_id)
 fix_result["pick_generation"] = generation_result

 # Validate fix
 validation_result = await data_integrity_fixer.validate_fix(db, sport_id)
 fix_result["validation"] = validation_result

 results[sport_id] = fix_result

 return {
 "timestamp": datetime.now(timezone.utc).isoformat(),
 "all_sports_fix_results": results,
 "summary": {
 "total_sports": len(sports),
 "successfully_fixed": len([r for r in results.values() if r.get("validation", {}).get("is_fixed")]),
 "still_corrupted": len([r for r in results.values() if not r.get("validation", {}).get("is_fixed")])
 }
 }

 except Exception as e:
 raise HTTPException(status_code = 500, detail = f"All sports fix failed: {e}")

@router.get(" / validate - sport / {sport_id}")
async def validate_sport_data(sport_id: int,
 db: AsyncSession = Depends(get_db)):
 """Validate data integrity for a specific sport."""
 try:
 validation = await data_integrity_fixer.validate_fix(db, sport_id)

 return {
 "timestamp": datetime.now(timezone.utc).isoformat(),
 "sport_validation": validation,
 "sport_name": {30: "NBA", 32: "NCAA Basketball", 53: "NHL"}[sport_id]
 }

 except Exception as e:
 raise HTTPException(status_code = 500, detail = f"Validation failed: {e}")

@router.get(" / validate - all - sports")
async def validate_all_sports(db: AsyncSession = Depends(get_db)):
 """Validate data integrity for all sports."""
 try:
 sports = [30, 32, 53] # NBA, NCAA, NHL
 results = {}

 for sport_id in sports:
 validation = await data_integrity_fixer.validate_fix(db, sport_id)
 results[sport_id] = validation

 return {
 "timestamp": datetime.now(timezone.utc).isoformat(),
 "all_sports_validation": results,
 "summary": {
 "total_sports": len(sports),
 "all_clean": all(r.get("is_fixed", False) for r in results.values()),
 "corrupted_sports": [sport_id for sport_id, r in results.items() if not r.get("is_fixed", False)]
 }
 }

 except Exception as e:
 raise HTTPException(status_code = 500, detail = f"All validation failed: {e}")

@router.get(" / sport - status / {sport_id}")
async def get_sport_status(sport_id: int,
 db: AsyncSession = Depends(get_db)):
 """Get detailed status for a specific sport."""
 try:
 # Get current players
 result = await db.execute(text(f"""
 SELECT DISTINCT p.name, COUNT( * ) as pick_count
 FROM model_picks mp
 JOIN players p ON mp.player_id = p.id
 JOIN games g ON mp.game_id = g.id
 WHERE g.sport_id = {sport_id}
 GROUP BY p.name
 ORDER BY pick_count DESC
 LIMIT 20
 """))

 players = [{"name": row[0], "pick_count": row[1]} for row in result.fetchall()]

 # Get games
 result = await db.execute(text(f"""
 SELECT id, start_time FROM games
 WHERE sport_id = {sport_id}
 AND start_time > NOW() - INTERVAL '24 hours'
 AND start_time < NOW() + INTERVAL '48 hours'
 ORDER BY start_time
 LIMIT 10
 """))

 games = [{"game_id": row[0], "start_time": row[1].isoformat()} for row in result.fetchall()]

 # Get pick count
 result = await db.execute(text(f"""
 SELECT COUNT( * ) FROM model_picks mp
 JOIN games g ON mp.game_id = g.id
 WHERE g.sport_id = {sport_id}
 """))

 total_picks = result.fetchone()[0]

 return {
 "timestamp": datetime.now(timezone.utc).isoformat(),
 "sport_id": sport_id,
 "sport_name": {30: "NBA", 32: "NCAA Basketball", 53: "NHL"}[sport_id],
 "total_picks": total_picks,
 "total_players": len(players),
 "total_games": len(games),
 "top_players": players[:10],
 "upcoming_games": games[:5]
 }

 except Exception as e:
 raise HTTPException(status_code = 500, detail = f"Sport status failed: {e}")

@router.post(" / emergency - fix")
async def emergency_fix(db: AsyncSession = Depends(get_db)):
 """Emergency fix for all data corruption issues."""
 try:
 # Step 1: Diagnose all issues
 diagnosis = await data_integrity_fixer.diagnose_data_corruption(db)

 # Step 2: Fix all corrupted sports
 sports_to_fix = [
 sport_id for sport_id, status in diagnosis["affected_sports"].items()
 if status =  = "CORRUPTED"
 ]

 fix_results = {}
 for sport_id in sports_to_fix:
 fix_result = await data_integrity_fixer.fix_sport_mapping(db, sport_id)

 if fix_result.get("status") =  = "fixed":
 generation_result = await data_integrity_fixer.generate_correct_picks(db, sport_id)
 fix_result["pick_generation"] = generation_result

 validation_result = await data_integrity_fixer.validate_fix(db, sport_id)
 fix_result["validation"] = validation_result

 fix_results[sport_id] = fix_result

 # Step 3: Final validation
 final_validation = {}
 for sport_id in [30, 32, 53]:
 validation = await data_integrity_fixer.validate_fix(db, sport_id)
 final_validation[sport_id] = validation

 return {
 "timestamp": datetime.now(timezone.utc).isoformat(),
 "emergency_fix_completed": True,
 "initial_diagnosis": diagnosis,
 "fix_results": fix_results,
 "final_validation": final_validation,
 "summary": {
 "sports_fixed": len(fix_results),
 "all_clean": all(r.get("is_fixed", False) for r in final_validation.values()),
 "total_issues_resolved": len([r for r in fix_results.values() if r.get("status") =  = "fixed"])
 }
 }

 except Exception as e:
 raise HTTPException(status_code = 500, detail = f"Emergency fix failed: {e}")
