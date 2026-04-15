import logging
from datetime import datetime, timezone
from typing import List, Dict, Any
from services.espn_client import espn_client

logger = logging.getLogger(__name__)

class NewsService:
    async def get_news(self, sport: str) -> List[Dict[str, Any]]:
        """
        Fetch and normalize news from ESPN for a given sport.
        Maps to the schema expected by the frontend Intellectual Hub.
        """
        try:
            raw_articles = await espn_client.fetch_news(sport)
            articles = []
            for art in raw_articles:
                # Normalize ESPN article structure
                links = art.get("links", {})
                web_link = links.get("web", {}) if isinstance(links, dict) else {}
                
                # Heuristic for impact (could be improved with NLP)
                headline = art.get("headline", art.get("title", "No Title"))
                impact = "LOW"
                if any(word in headline.upper() for word in ["OUT", "INJURED", "TRADE", "SUSPENDED", "CRITICAL"]):
                    impact = "HIGH"
                elif any(word in headline.upper() for word in ["QUESTIONABLE", "DOUBTFUL", "PROBABLE"]):
                    impact = "MEDIUM"

                articles.append({
                    "id": art.get("id"),
                    "headline": headline,
                    "summary": art.get("description", "Market intel captured from institutional wire."),
                    "timestamp": art.get("published", datetime.now(timezone.utc).isoformat()),
                    "url": web_link.get("href", "#"),
                    "category": sport.split("_")[-1].upper() if "_" in sport else "GENERAL",
                    "impact": impact,
                    "source": art.get("source", "ESPN")
                })
            return articles
        except Exception as e:
            logger.error(f"NewsService: Failed to fetch news for {sport}: {e}")
            return []

news_service = NewsService()
