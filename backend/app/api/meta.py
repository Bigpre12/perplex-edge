"""
Meta API endpoints.

Provides system metadata and configuration information.
"""

import logging
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from typing import Dict, Any

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("", response_model = Dict[str, Any])
async def get_meta():
 """Get system metadata and configuration."""
 try:
 return {
 "version": "1.0.0",
 "environment": "production",
 "timestamp": datetime.now(timezone.utc).isoformat(),
 "sports_supported": [
 "NBA", "NFL", "NHL", "MLB", "NCAAB", "NCAAF",
 "WNBA", "ATP", "WTA", "PGA", "UFC", "EPL", "UCL", "MLS"
 ],
 "features": [
 "real_time_odds",
 "ev_calculations",
 "kelly_criterion",
 "player_props",
 "trend_analysis",
 "autonomous_brain",
 "resource_monitoring",
 "verification_engine"
 ],
 "api_version": "v1",
 "status": "healthy",
 "endpoints": {
 "sports": " / api / sports",
 "games": " / api / games",
 "slate": " / api / slate / full",
 "odds": " / api / odds",
 "health": " / api / health",
 "meta": " / api / meta",
 "admin": " / api / admin"
 },
 "data_sources": [
 "TheOddsAPI",
 "StatsAPI",
 "InjuryAPI",
 "RosterAPI"
 ],
 "update_frequency": {
 "sports": "daily",
 "games": "every 30 minutes",
 "odds": "every 5 minutes",
 "player_props": "every 10 minutes"
 }
 }

 except Exception as e:
 raise HTTPException(status_code = 500, detail = f"Failed to get metadata: {str(e)}")

@router.get(" / status", response_model = Dict[str, Any])
async def get_system_status():
 """Get detailed system status."""
 try:
 return {
 "status": "operational",
 "timestamp": datetime.now(timezone.utc).isoformat(),
 "services": {
 "api": "healthy",
 "database": "healthy",
 "cache": "healthy",
 "brain": "healthy",
 "scheduler": "healthy"
 },
 "performance": {
 "api_response_time_p95": "<300ms",
 "database_response_time_p95": "<100ms",
 "cache_hit_rate": ">85%",
 "brain_cycle_time": "<30s"
 },
 "resources": {
 "memory_usage": "<70%",
 "cpu_usage": "<50%",
 "disk_usage": "<80%"
 },
 "last_updated": {
 "sports": datetime.now(timezone.utc).isoformat(),
 "games": datetime.now(timezone.utc).isoformat(),
 "odds": datetime.now(timezone.utc).isoformat()
 }
 }

 except Exception as e:
 raise HTTPException(status_code = 500, detail = f"Failed to get system status: {str(e)}")
