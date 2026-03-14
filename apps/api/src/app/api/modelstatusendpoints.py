from fastapi import APIRouter
from app.core.state import app_state

router = APIRouter()

@router.get("/model-status")
async def get_model_status():
    """Get the current health and status of the Model agent."""
    return {
        "status": "healthy",
        "last_check": app_state.last_health_check,
        "healing_actions": len(app_state.healing_actions),
        "metrics": app_state.system_metrics,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/decisions")
async def get_brain_decisions():
    """Get recent autonomous decisions made by the Brain."""
    return {
        "decisions": app_state.brain_decisions,
        "count": len(app_state.brain_decisions)
    }

@router.get("/healing-log")
async def get_healing_log():
    """Get history of self-healing actions taken by the system."""
    return {
        "actions": app_state.healing_actions
    }
