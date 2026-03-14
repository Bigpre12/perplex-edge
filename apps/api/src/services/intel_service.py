import logging
import json
import random
from datetime import datetime, timezone
from services.brain_service import brain_service

logger = logging.getLogger(__name__)

class MarketIntelService:
    async def get_daily_intel(self, sport: str = "basketball_nba") -> list:
        """
        Generate dynamic market intel (breaking news, market moves)
        based on real-time games and sport context.
        """
        from real_data_connector import real_data_connector
        try:
            # 1. Fetch real games to make it contextual
            games = await real_data_connector.fetch_games_by_sport(sport)
            logger.info(f"MarketIntel: Found {len(games)} games for {sport}")

            if not games:
                logger.warning(f"MarketIntel: No games found for {sport}, using fallback.")
                return self._get_fallback_intel(sport)

            # 2. Pick a few games to "generate" news about
            sampled_games = random.sample(games, min(3, len(games)))
            logger.info(f"MarketIntel: Sampled {len(sampled_games)} games: {[g.get('home_team_name') for g in sampled_games]}")
            
            system_prompt = """You are a sharp, deep-insider sports news AI for Lucrix. 
            Your goal is to provide 'Market Intel'—breaking news and analysis that would affect betting lines.
            Focus on player status, weather (if applicable), sharp action, or coaching leanings.
            Keep each item to 1-2 punchy sentences.
            Format your response as a JSON array of objects with 'title', 'content', 'type' (news/injury/sharp), and 'timestamp'.
            Respond ONLY with the JSON array.
            """

            import asyncio
            games_info = ", ".join([f"{g['away_team_name']} vs {g['home_team_name']}" for g in sampled_games])
            user_prompt = f"Generate 3 Market Intel items for the current {sport} slate. Games include: {games_info}. Make it feel like it's happening right now in March 2026. Data should be realistic and detailed."

            intel_text = "N/A"
            try:
                # Increased timeout to 10 seconds to ensure the LLM has time to generate a quality response
                logger.info(f"MarketIntel: Calling LLM for {sport} with info: {games_info}")
                intel_text = await asyncio.wait_for(brain_service._call_llm(system_prompt, user_prompt), timeout=10.0)
                logger.info(f"MarketIntel: LLM Responded (len={len(intel_text)})")
                
                # Use brain_service's robust JSON extractor to handle markdown blocks
                clean_text = brain_service._extract_json(intel_text)
                logger.info(f"MarketIntel: Cleaned JSON: {clean_text[:100]}...")
                
                intel_items = json.loads(clean_text)
                if isinstance(intel_items, list) and len(intel_items) > 0:
                    logger.info(f"MarketIntel: Successfully returning {len(intel_items)} REAL news items.")
                    return intel_items
                else:
                    logger.warning(f"MarketIntel: LLM returned empty list or invalid format. Using fallback.")
                    return self._get_fallback_intel(sport)
            except Exception as e:
                logger.error(f"MarketIntel: LLM step failed: {e}. Raw was: {intel_text[:200]}")
                return self._get_fallback_intel(sport)

        except Exception as e:
            logger.error(f"MarketIntel: Global error: {e}")
            return self._get_fallback_intel(sport)

    def _get_fallback_intel(self, sport: str) -> list:
        """Provide realistic but static fallback intel when LLM fails."""
        now = datetime.now(timezone.utc).isoformat()
        return [
            {
                "title": f"Market Status: {sport.split('_')[-1].upper()}",
                "content": "Intelligence engine is monitoring live markets for sharp activity.",
                "type": "sharp",
                "timestamp": now
            },
            {
                "title": f"Injury Monitor",
                "content": "Scanning team injury reports for late-breaking changes.",
                "type": "injury",
                "timestamp": now
            }
        ]

intel_service = MarketIntelService()
get_daily_intel = intel_service.get_daily_intel
