# apps/api/src/services/prizepicks_collector.py
import httpx
import logging
import unicodedata
import re
from datetime import datetime
from sqlalchemy import text
from db.session import async_session_maker

logger = logging.getLogger(__name__)

def normalize_player_name(name: str) -> str:
    """
    Normalize player names for matching: lowercase, strip accents, remove suffixes.
    Example: 'Luka Dončić Jr.' -> 'luka doncic'
    """
    if not name:
        return ""
    # Lowercase and strip whitespace
    name = name.lower().strip()
    # Normalize unicode (strip accents)
    name = "".join(
        c for c in unicodedata.normalize("NFD", name)
        if unicodedata.category(c) != "Mn"
    )
    # Remove suffixes like jr, sr, iii, iv, v
    name = re.sub(r"\s+(jr|sr|iii|iv|v)$", "", name)
    # Remove special characters except spaces
    name = re.sub(r"[^a-z\s]", "", name)
    # Collapse multiple spaces
    name = re.sub(r"\s+", " ", name)
    return name.strip()

async def fetch_prizepicks_board():
    """
    Fetch the current PrizePicks board and return a list of parsed projections.
    """
    url = "https://api.prizepicks.com/projections?per_page=250&single_stat=true"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.error(f"Failed to fetch PrizePicks board: {e}")
            return []

    projections = data.get("data", [])
    included = data.get("included", [])
    
    # Map player IDs to names from the 'included' section
    players = {}
    for item in included:
        if item.get("type") == "new_player":
            players[item.get("id")] = item.get("attributes", {}).get("name")

    parsed = []
    for proj in projections:
        attr = proj.get("attributes", {})
        rel = proj.get("relationships", {})
        
        player_id = rel.get("new_player", {}).get("data", {}).get("id")
        player_name = players.get(player_id)
        
        if not player_name:
            continue
            
        parsed.append({
            "id": str(proj.get("id")),
            "player_name": player_name,
            "stat_type": attr.get("stat_type"),
            "line_score": float(attr.get("line_score", 0)),
            "league": attr.get("league"),
            "game_time": attr.get("start_time"),
        })
    
    return parsed

async def upsert_projections(projections):
    """
    Upsert projections into pp_projections_staging.
    Does not overwrite already-graded rows.
    """
    if not projections:
        return
        
    async with async_session_maker() as session:
        count = 0
        for p in projections:
            try:
                # We use ON CONFLICT DO NOTHING to avoid overwriting or re-inserting graded rows
                # since the 'id' is unique from PrizePicks.
                sql = text("""
                    INSERT INTO pp_projections_staging 
                    (id, player_name, stat_type, line_score, league, game_time)
                    VALUES (:id, :player_name, :stat_type, :line_score, :league, :game_time)
                    ON CONFLICT (id) DO NOTHING
                """)
                # Convert ISO string to datetime if needed, though Postgres handles it well
                game_time = p["game_time"]
                if isinstance(game_time, str):
                    try:
                        game_time = datetime.fromisoformat(game_time.replace("Z", "+00:00"))
                    except ValueError:
                        pass

                result = await session.execute(sql, {
                    "id": p["id"],
                    "player_name": p["player_name"],
                    "stat_type": p["stat_type"],
                    "line_score": p["line_score"],
                    "league": p["league"],
                    "game_time": game_time
                })
                if result.rowcount > 0:
                    count += 1
            except Exception as e:
                logger.error(f"Error upserting PP projection {p['id']}: {e}")
        
        await session.commit()
        logger.info(f"PrizePicks Collector: Upserted {count} new projections.")

async def run_collector():
    """Entry point for the collector task."""
    logger.info("PrizePicks Collector: Starting board fetch...")
    projections = await fetch_prizepicks_board()
    await upsert_projections(projections)
    logger.info(f"PrizePicks Collector: Finished. Found {len(projections)} total projections.")
