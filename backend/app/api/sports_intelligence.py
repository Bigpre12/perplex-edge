"""
Sports Intelligence API - Real-time news, weather, and decision-making endpoints.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.sports_intelligence_brain import sports_intelligence_brain
from app.services.cache_service import cache_service

router = APIRouter(prefix="/api/intelligence", tags=["sports-intelligence"])

@router.get("/status")
async def get_intelligence_brain_status():
    """Get current sports intelligence brain status and metrics."""
    try:
        status = sports_intelligence_brain.get_status()
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "brain_status": status,
            "message": "Sports intelligence brain operational" if status["is_running"] else "Brain stopped"
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "brain_status": {"is_running": False, "error": str(e)}
        }

@router.get("/news")
async def get_sports_news(
    limit: int = Query(default=20, le=100),
    sentiment: str = Query(None, description="Filter by sentiment: positive, negative, neutral"),
    category: str = Query(None, description="Filter by category: injury, trade, suspension, personal, performance"),
    min_impact: float = Query(default=0.3, description="Minimum impact score"),
    db: AsyncSession = Depends(get_db)
):
    """Get recent sports news with impact analysis."""
    try:
        # Try cache first
        cached_data = await cache_service.get("intelligence_news")
        if cached_data:
            news_items = cached_data
        else:
            # Fallback to brain data
            news_items = [
                {
                    "source": n.source,
                    "title": n.title,
                    "content": n.content[:200] + "..." if len(n.content) > 200 else n.content,
                    "players_mentioned": n.players_mentioned,
                    "teams_mentioned": n.teams_mentioned,
                    "impact_score": n.impact_score,
                    "sentiment": n.sentiment,
                    "category": n.category,
                    "confidence": n.confidence,
                    "timestamp": n.timestamp.isoformat()
                }
                for n in list(sports_intelligence_brain.news_items)[-50:]
            ]
        
        # Apply filters
        if sentiment:
            news_items = [n for n in news_items if n.get("sentiment") == sentiment]
        
        if category:
            news_items = [n for n in news_items if n.get("category") == category]
        
        news_items = [n for n in news_items if abs(n.get("impact_score", 0)) >= min_impact]
        
        # Sort by impact and timestamp
        news_items.sort(key=lambda x: (abs(x.get("impact_score", 0)), x.get("timestamp", "")), reverse=True)
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_news": len(news_items),
            "filters": {
                "sentiment": sentiment,
                "category": category,
                "min_impact": min_impact,
                "limit": limit
            },
            "news": news_items[:limit]
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "news": []
        }

@router.get("/weather")
async def get_weather_conditions(
    condition: str = Query(None, description="Filter by condition: clear, rain, snow, windy, extreme"),
    impact: str = Query(None, description="Filter by impact: over_favoring, under_favoring, neutral"),
    db: AsyncSession = Depends(get_db)
):
    """Get weather conditions for active games with impact analysis."""
    try:
        # Try cache first
        cached_data = await cache_service.get("intelligence_weather")
        if cached_data:
            weather_data = cached_data
        else:
            # Fallback to brain data
            weather_data = [
                {
                    "game_id": game_id,
                    "venue": weather.venue,
                    "temperature": weather.temperature,
                    "humidity": weather.humidity,
                    "wind_speed": weather.wind_speed,
                    "precipitation": weather.precipitation,
                    "condition": weather.condition,
                    "impact_on_over_under": weather.impact_on_over_under,
                    "reasoning": weather.reasoning,
                    "timestamp": weather.timestamp.isoformat()
                }
                for game_id, weather in sports_intelligence_brain.weather_conditions.items()
            ]
        
        # Apply filters
        if condition:
            weather_data = [w for w in weather_data if w.get("condition") == condition]
        
        if impact:
            weather_data = [w for w in weather_data if w.get("impact_on_over_under") == impact]
        
        # Sort by timestamp
        weather_data.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_conditions": len(weather_data),
            "filters": {
                "condition": condition,
                "impact": impact
            },
            "weather": weather_data
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "weather": []
        }

@router.get("/recommendations")
async def get_intelligence_recommendations(
    recommendation: str = Query(None, description="Filter by recommendation: over, under, pass, avoid"),
    min_confidence: float = Query(default=0.7, description="Minimum confidence level"),
    min_impact: float = Query(default=0.3, description="Minimum expected impact"),
    limit: int = Query(default=15, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get AI decision recommendations with reasoning."""
    try:
        # Try cache first
        cached_data = await cache_service.get("intelligence_recommendations")
        if cached_data:
            recommendations = cached_data
        else:
            # Fallback to brain data
            recommendations = [
                {
                    "player_id": rec.player_id,
                    "player_name": rec.player_name,
                    "stat_type": rec.stat_type,
                    "current_line": rec.current_line,
                    "recommendation": rec.recommendation,
                    "confidence": rec.confidence,
                    "expected_impact": rec.expected_impact,
                    "reasoning": rec.reasoning,
                    "factors": rec.factors,
                    "timestamp": rec.timestamp.isoformat()
                }
                for rec in list(sports_intelligence_brain.decision_recommendations.values())
            ]
        
        # Apply filters
        if recommendation:
            recommendations = [r for r in recommendations if r.get("recommendation") == recommendation]
        
        recommendations = [r for r in recommendations if r.get("confidence", 0) >= min_confidence]
        recommendations = [r for r in recommendations if abs(r.get("expected_impact", 0)) >= min_impact]
        
        # Sort by confidence and impact
        recommendations.sort(key=lambda x: (x.get("confidence", 0), abs(x.get("expected_impact", 0))), reverse=True)
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_recommendations": len(recommendations),
            "filters": {
                "recommendation": recommendation,
                "min_confidence": min_confidence,
                "min_impact": min_impact,
                "limit": limit
            },
            "recommendations": recommendations[:limit]
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "recommendations": []
        }

@router.get("/git-status")
async def get_git_integration_status():
    """Get git integration status and history."""
    try:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "git_status": sports_intelligence_brain.get_status()["git_status"],
            "code_updates": sports_intelligence_brain.code_updates,
            "last_push": sports_intelligence_brain.last_git_push.isoformat() if sports_intelligence_brain.last_git_push else None,
            "total_pushes": sports_intelligence_brain.git_pushes,
            "auto_push_enabled": sports_intelligence_brain.auto_git_push
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e)
        }

@router.post("/start-intelligence")
async def start_intelligence_monitoring():
    """Start the sports intelligence monitoring brain."""
    try:
        if sports_intelligence_brain.is_running:
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": "Sports intelligence brain already running",
                "status": sports_intelligence_brain.get_status()
            }
        
        # Start monitoring in background
        import asyncio
        asyncio.create_task(sports_intelligence_brain.start_monitoring())
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Sports intelligence monitoring started",
            "status": sports_intelligence_brain.get_status()
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "message": "Failed to start intelligence monitoring"
        }

@router.post("/stop-intelligence")
async def stop_intelligence_monitoring():
    """Stop the sports intelligence monitoring brain."""
    try:
        await sports_intelligence_brain.stop_monitoring()
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Sports intelligence monitoring stopped",
            "status": sports_intelligence_brain.get_status()
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "message": "Failed to stop intelligence monitoring"
        }

@router.post("/force-git-push")
async def force_git_push():
    """Force an immediate git push with current changes."""
    try:
        await sports_intelligence_brain.push_changes_to_git()
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Git push completed",
            "git_status": sports_intelligence_brain.get_status()["git_status"]
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "message": "Failed to force git push"
        }
