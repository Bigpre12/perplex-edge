"""
One-click sportsbook deeplinks router.
Given a player name, stat type, line, and sportsbook — returns a direct URL
that opens the betting slip pre-populated on the sportsbook's app/web.
"""
from fastapi import APIRouter, Query
from urllib.parse import quote
from typing import Optional

router = APIRouter(prefix="/deeplinks", tags=["deeplinks"])

SPORTSBOOK_TEMPLATES = {
    "fanduel": {
        "web": "https://sportsbook.fanduel.com/search?q={player_encoded}",
        "app_ios": "fanduel://sportsbook/search?q={player_encoded}",
        "logo": "🟣",
        "color": "#1975d2"
    },
    "draftkings": {
        "web": "https://sportsbook.draftkings.com/featured?q={player_encoded}",
        "app_ios": "draftkings://sportsbook/search?q={player_encoded}",
        "logo": "🟢",
        "color": "#53d337"
    },
    "betmgm": {
        "web": "https://sports.betmgm.com/en/sports/search?q={player_encoded}",
        "app_ios": "betmgm://sports/search?q={player_encoded}",
        "logo": "🟡",
        "color": "#d4af37"
    },
    "caesars": {
        "web": "https://sportsbook.caesars.com/us/nj/bet/#/search?q={player_encoded}",
        "app_ios": "caesars://search?q={player_encoded}",
        "logo": "🔵",
        "color": "#003087"
    },
    "prizepicks": {
        "web": "https://app.prizepicks.com/board",
        "app_ios": "prizepicks://board",
        "logo": "🟠",
        "color": "#ff6b00"
    },
    "underdog": {
        "web": "https://underdogfantasy.com/pick-em",
        "app_ios": "underdogfantasy://pick-em",
        "logo": "⚫",
        "color": "#ff4444"
    },
}


@router.get("/generate")
async def generate_deeplink(
    player_name: str = Query(..., description="Player full name"),
    stat_type: str = Query(..., description="Stat type e.g. points, rebounds"),
    line: float = Query(..., description="Prop line value"),
    side: str = Query("over", description="over or under"),
    sportsbook: str = Query(..., description="Sportsbook key e.g. fanduel"),
    odds: Optional[float] = Query(None, description="American odds"),
):
    sb = sportsbook.lower().replace(" ", "")
    template = SPORTSBOOK_TEMPLATES.get(sb)
    if not template:
        return {"error": f"Sportsbook '{sportsbook}' not supported", "supported": list(SPORTSBOOK_TEMPLATES.keys())}

    player_encoded = quote(player_name)
    web_url = template["web"].format(player_encoded=player_encoded)
    app_url = template["app_ios"].format(player_encoded=player_encoded)

    return {
        "player_name": player_name,
        "stat_type": stat_type,
        "line": line,
        "side": side,
        "odds": odds,
        "sportsbook": sportsbook,
        "web_url": web_url,
        "app_url": app_url,
        "display": template["logo"],
        "color": template["color"],
        "label": f"{side.upper()} {line} {stat_type.upper()} — {player_name}",
    }


@router.get("/all/{player_name}")
async def get_all_deeplinks(
    player_name: str,
    stat_type: str = Query("points"),
    line: float = Query(25.5),
    side: str = Query("over"),
):
    """Return deeplinks for ALL supported sportsbooks for a single prop."""
    results = []
    player_encoded = quote(player_name)
    for key, template in SPORTSBOOK_TEMPLATES.items():
        results.append({
            "sportsbook": key,
            "logo": template["logo"],
            "color": template["color"],
            "web_url": template["web"].format(player_encoded=player_encoded),
            "app_url": template["app_ios"].format(player_encoded=player_encoded),
            "label": f"{side.upper()} {line} {stat_type.upper()}",
        })
    return {"player_name": player_name, "links": results}
