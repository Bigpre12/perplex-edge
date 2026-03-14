import json
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.antigravity_edge_config import get_edge_config, EdgeModelName

router = APIRouter(prefix="/api/config", tags=["config"])

# Optional: We can persist the config to a local JSON file so it survives Uvicorn reloads.
CONFIG_FILE = "edge_settings_storage.json"

class ConfigUpdateModel(BaseModel):
    active_edge_model: EdgeModelName
    min_edge_percent: float
    max_edge_percent: float
    min_games_sample: int
    min_bets_volume: int
    max_juice: float
    include_main_lines: bool
    discord_webhook_url: Optional[str] = ""

def save_config_to_disk(config_obj):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump({
                "active_edge_model": config_obj.active_edge_model,
                "min_edge_percent": config_obj.min_edge_percent,
                "max_edge_percent": config_obj.max_edge_percent,
                "min_games_sample": config_obj.min_games_sample,
                "min_bets_volume": config_obj.min_bets_volume,
                "max_juice": config_obj.max_juice,
                "include_main_lines": config_obj.include_main_lines,
                "discord_webhook_url": config_obj.discord_webhook_url
            }, f)
    except Exception as e:
        print(f"Warning: Failed to persist config to disk: {e}")

@router.get("/")
async def read_config():
    """Return the active AI edge finding configuration parameters."""
    config = get_edge_config()
    return {
        "active_edge_model": config.active_edge_model,
        "min_edge_percent": config.min_edge_percent,
        "max_edge_percent": config.max_edge_percent,
        "min_games_sample": config.min_games_sample,
        "min_bets_volume": config.min_bets_volume,
        "max_juice": config.max_juice,
        "include_main_lines": config.include_main_lines,
        "discord_webhook_url": config.discord_webhook_url
    }

@router.post("/")
async def update_config(payload: ConfigUpdateModel):
    """Mutate the active configuration. Affects the /working-player-props endpoint downstream."""
    config = get_edge_config()
    
    config.active_edge_model = payload.active_edge_model
    config.min_edge_percent = payload.min_edge_percent
    config.max_edge_percent = payload.max_edge_percent
    config.min_games_sample = payload.min_games_sample
    config.min_bets_volume = payload.min_bets_volume
    config.max_juice = payload.max_juice
    config.include_main_lines = payload.include_main_lines
    config.discord_webhook_url = payload.discord_webhook_url
    
    # Save the mutation to a local file so changes survive development restarts
    save_config_to_disk(config)

    return {"status": "success", "message": "Edge engine configuration updated in real-time."}
