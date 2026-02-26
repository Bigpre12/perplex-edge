import logging
import json
import random
from datetime import datetime, timezone
from services.brain_service import brain_service
from real_data_connector import real_data_connector

logger = logging.getLogger(__name__)

class MarketIntelService:
    async def get_daily_intel(self, sport_key: str = "basketball_nba") -> list:
        """
        Generate dynamic market intel (breaking news, market moves)
        based on real-time games and sport context.
        """
        try:
            # 1. Fetch real games to make it contextual
            games = await real_data_connector.fetch_games_by_sport(sport_key)

            if not games:
                return self._get_fallback_intel(sport_key)

            # 2. Pick a few games to "generate" news about
            sampled_games = random.sample(games, min(3, len(games)))
            
            system_prompt = """You are a sharp, deep-insider sports news AI for Perplex Edge. 
            Your goal is to provide 'Market Intel'—breaking news and analysis that would affect betting lines.
            Focus on player status, weather (if applicable), sharp action, or coaching leanings.
            Keep each item to 1-2 punchy sentences.
            Format your response as a JSON array of objects with 'title', 'content', 'type' (news/injury/sharp), and 'timestamp'.
            Respond ONLY with the JSON array.
            """

            import asyncio
            games_info = ", ".join([f"{g['away_team_name']} vs {g['home_team_name']}" for g in sampled_games])
            user_prompt = f"Generate 3 Market Intel items for the current {sport_key} slate. Games include: {games_info}. Make it feel like it's happening right now in February 2026."

            try:
                # Add a strict 2-second timeout to the LLM call to prevent infinite unresponsiveness
                intel_text = await asyncio.wait_for(brain_service._call_llm(system_prompt, user_prompt), timeout=2.0)
                clean_text = intel_text.replace("```json", "").replace("```", "").strip()
                intel_items = json.loads(clean_text)
                return intel_items
            except Exception as e:
                logger.error(f"Failed to fetch or parse LLM intel response: {e}, falling back to static.")
                return self._get_fallback_intel(sport_key)

        except Exception as e:
            logger.error(f"Error in get_daily_intel: {e}")
            return self._get_fallback_intel(sport_key)

    def _get_fallback_intel(self, sport_key: str) -> list:
        """Static fallback items if LLM fails or no games."""
        sport_name = sport_key.split("_")[1].upper() if "_" in sport_key else sport_key.upper()
        return [
            {
                "title": f"Heavy Sharp Action on {sport_name}",
                "content": f"Vegas reporting heavy concentration of professional money on {sport_name} totals this evening.",
                "type": "sharp",
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            {
                "title": "Injury Update",
                "content": f"Multiple key starters in {sport_name} are listed as game-time decisions. Lines are currently static but expected to move.",
                "type": "injury",
                "timestamp": (datetime.now(timezone.utc)).isoformat()
            }
        ]

intel_service = MarketIntelService()
