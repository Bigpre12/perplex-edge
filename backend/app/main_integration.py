"""
Main Integration - All brain services and enhanced APIs
"""

from app.api.players_enhanced import router as enhanced_players_router
from app.api.teams_enhanced import router as enhanced_teams_router
from app.api.statistics import router as statistics_router
from app.api.active_monitoring import router as active_monitoring_router
from app.api.sports_intelligence import router as sports_intelligence_router
from app.services.active_line_brain import active_line_brain
from app.services.sports_intelligence_brain import sports_intelligence_brain
from app.services.cache_service import cache_service

# Export all components for main.py integration
__all__ = [
    "enhanced_players_router",
    "enhanced_teams_router", 
    "statistics_router",
    "active_monitoring_router",
    "sports_intelligence_router",
    "active_line_brain",
    "sports_intelligence_brain",
    "cache_service"
]
