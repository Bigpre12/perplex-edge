# services/props_models.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class PropRecord:
    sport: str
    league: str
    game_id: str
    game_start_time: datetime

    player_id: str
    player_name: str
    team: str

    market_key: str
    market_label: str
    line: float

    book: str
    odds_over: int
    odds_under: int

    implied_over: Optional[float]
    implied_under: Optional[float]
