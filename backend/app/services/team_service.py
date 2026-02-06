"""
Team data service for parlay calculations.
"""

from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

async def get_player_team_data(
    db: AsyncSession, 
    player_id: int
) -> Dict[str, Any]:
    """Get team data for a player."""
    try:
        sql = text("""
            SELECT p.id as player_id, p.name as player_name,
                   t.id as team_id, t.name as team_name, t.abbr as team_abbr,
                   g.id as game_id, g.start_time as game_start
            FROM players p
            JOIN teams t ON p.team_id = t.id
            JOIN games g ON p.team_id = g.home_team_id OR p.team_id = g.away_team_id
            WHERE p.id = :player_id
            AND g.start_time > NOW() - INTERVAL '48 hours'
            ORDER BY g.start_time ASC
            LIMIT 1
        """)
        
        result = await db.execute(sql, {"player_id": player_id})
        row = result.fetchone()
        
        if row:
            return {
                "player_id": row[0],
                "player_name": row[1],
                "team_id": row[2],
                "team_name": row[3],
                "team_abbr": row[4] or "UNK",
                "game_id": row[5],
                "game_start": row[6]
            }
        else:
            return {
                "player_id": player_id,
                "team_abbr": "UNK",
                "game_id": None
            }
            
    except Exception as e:
        return {
            "player_id": player_id,
            "team_abbr": "UNK",
            "game_id": None
        }


async def calculate_odds_from_line(line_value: float) -> int:
    """Calculate American odds from line value."""
    # Simplified odds calculation - would be more sophisticated in production
    if line_value <= 0:
        return -110
    elif line_value < 1:
        return -110
    elif line_value < 5:
        return -110
    elif line_value < 10:
        return -110
    else:
        return -110


async def calculate_win_probability(edge: float) -> float:
    """Calculate win probability from edge."""
    # Simplified probability calculation
    # Edge of 0.05 (5%) corresponds to ~55% win probability
    base_prob = 0.5
    prob_adjustment = edge * 0.5  # Rough scaling
    return min(0.95, max(0.05, base_prob + prob_adjustment))
