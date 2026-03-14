# apps/api/src/routers/news.py
# Real sports news via ESPN + injury alerts — powers the ticker

from fastapi import APIRouter
import httpx
from datetime import datetime, timezone
import logging

router = APIRouter(tags=["news"])
logger = logging.getLogger(__name__)

# Correct ESPN news endpoints for different sports
ESPN_NEWS_URLS = {
    "NBA": "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/news",
    "NFL": "https://site.api.espn.com/apis/site/v2/sports/football/nfl/news",
    "MLB": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/news",
    "NHL": "https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/news",
    "WNBA": "https://site.api.espn.com/apis/site/v2/sports/basketball/wnba/news",
}

@router.get("/ticker")
async def get_ticker_items(sports: str = "NBA,NFL,MLB"):
    """
    Returns flat list of ticker items combining:
    - Breaking news headlines
    - Injury alerts
    - Line movement alerts
    """
    sport_list = [s.strip().upper() for s in sports.split(",")]
    items = []

    async with httpx.AsyncClient(timeout=15) as client:
        for sport in sport_list:
            url = ESPN_NEWS_URLS.get(sport)
            if not url:
                continue
            try:
                r = await client.get(url, params={"limit": 10})
                if r.status_code != 200:
                    continue
                data = r.json()
                # Process individual articles
                for article in data.get("articles", [])[:8]:
                    headline = article.get("headline", "")
                    desc = article.get("description", "")
                    published = article.get("published", "")
                    
                    # Enhanced detection logic for injury-related items
                    injury_keywords = ["injur", "out", "questionable", "doubtful", "ir ", "surgery", "ruled out", "day-to-day", "sidelined"]
                    is_injury = any(kw in headline.lower() or kw in (desc or "").lower() for kw in injury_keywords)
                    
                    # Enhanced detection for lineup changes/trades
                    lineup_keywords = ["starting", "lineup", "trade", "sign", "waive", "roster", "transfer"]
                    is_lineup = any(kw in headline.lower() for kw in lineup_keywords)

                    # Assign visual tags and icons
                    tag = "INJURY" if is_injury else ("LINEUP" if is_lineup else "NEWS")
                    icon = "🚨" if is_injury else ("📋" if is_lineup else "⚡")

                    items.append({
                        "id": article.get("id", f"{sport}-{published}"),
                        "sport": sport,
                        "type": tag,  # Match frontend "type"
                        "icon": icon,
                        "message": headline, # Match frontend "message"
                        "description": desc[:120] if desc else "",
                        "published": published,
                        "link": article.get("links", {}).get("web", {}).get("href", ""),
                        "is_injury": is_injury,
                        "is_lineup": is_lineup,
                    })
            except Exception as e:
                logger.error(f"[NEWS] {sport} fetch failed: {e}")
                continue

    # Sort primarily by time, most recent first
    items.sort(key=lambda x: x.get("published", ""), reverse=True)
    return {
        "items": items, 
        "count": len(items), 
        "fetched_at": datetime.now(timezone.utc).isoformat()
    }
