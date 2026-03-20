import json
import logging
from datetime import datetime, timezone
from typing import AsyncGenerator, List, Optional, Dict, Any

from core.config import settings
from services.props_service import props_service
from services.steam_service import steam_service
from services.whale_service import detect_whale_signals
from services.injury_service import injury_service
from services.brain_service import brain_service

# We'll use openai for the streaming implementation as requested
try:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
except ImportError:
    client = None
    logging.warning("OpenAI library not installed. Oracle chat will be disabled.")

logger = logging.getLogger(__name__)

class OracleService:
    def __init__(self):
        self.client = client

    async def build_context(self, sport: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Pull all live data to inject as LLM context"""
        try:
            # Fetch data from existing services
            # Note: We use the already built async services
            top_props = await props_service.get_all_props(sport)
            # Limit context size
            top_props_sample = top_props[:15] if top_props else []
            
            # 2. Fetch live signals (Whale & Steam)
            whale_signals = await detect_whale_signals(sport)
            
            # 3. Fetch Brain Metrics
            metrics = await brain_service.get_metrics(sport)
            
            # 4. Fetch Injuries
            injuries = await injury_service.get_injuries(sport)
            
            # 5. Fetch Top EV Signals (Fix #11 logic)
            from routers.ev import get_top_ev
            ev_data = await get_top_ev(sport=sport, limit=15)
            ev_signals = ev_data.get("data", [])
            
            # 5. Fetch last 10 steam events from DB using async session
            from db.session import async_session_maker
            from models.brain import SteamEvent
            from sqlalchemy import select, desc
            
            steam_events = []
            try:
                async with async_session_maker() as session:
                    stmt = select(SteamEvent).where(SteamEvent.sport == sport).order_by(desc(SteamEvent.created_at)).limit(10)
                    res = await session.execute(stmt)
                    steam_events = [{
                        "player": s.player_name,
                        "move": s.description,
                        "severity": s.severity,
                        "time": s.created_at.isoformat() if s.created_at else ""
                    } for s in res.scalars().all()]
            except Exception as steam_err:
                logger.warning(f"Oracle: could not fetch steam events: {steam_err}")

            context = {
                "sport": sport,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "top_props": top_props_sample,
                "ev_signals": ev_signals, # Fix #11
                "brain_metrics": metrics,
                "whale_signals": whale_signals[:10],
                "steam_events": steam_events,
                "injuries": injuries[:10] if isinstance(injuries, list) else [],
                "note": "All data is real-time from the Lucrix pipeline. Whale signals indicate heavy sharp money."
            }
            
            if user_id:
                # Add bankroll/parlay context if implemented
                pass
                
            return context
        except Exception as e:
            logger.error(f"Error building Oracle context: {e}")
            return {"sport": sport, "error": "Context build failed", "timestamp": datetime.now(timezone.utc).isoformat()}

    async def chat(self, messages: List[Dict], sport: str, user_id: Optional[str] = None) -> AsyncGenerator[str, None]:
        """Stream response from LLM with injected context"""
        if not self.client:
            yield "Oracle is currently unavailable (API client not configured)."
            return

        context = await self.build_context(sport, user_id)
        
        # Extract last user message for specific data fetching if needed
        # (Already happening in build_context for the general sport)
        
        system_prompt = f"""
You are Oracle, the AI assistant built into Lucrix, a professional sports betting analytics platform.
You provide data-driven insights grounded in the real-time context provided below.

ACTIVE SPORT: {context['sport']}
CURRENT TIME: {context['timestamp']}

TOP PROPS RIGHT NOW:
{json.dumps(context['top_props'], indent=2)}

POSITIVE EV SIGNALS (Sharp Edge):
{json.dumps(context['ev_signals'], indent=2)}

INJURIES:
{json.dumps(context['injuries'], indent=2)}

BRAIN METRICS:
{json.dumps(context['brain_metrics'], indent=2)}

WHALE SIGNALS (Sharp Money):
{json.dumps(context['whale_signals'], indent=2)}

RULES:
- Refer to yourself as Oracle. Never reveal you are an AI or LLM.
- Be direct, confident, and data-driven. Use real numbers from the context.
- Never guarantee outcomes or use terms like "lock" or "guaranteed".
- If a player is injured (see INJURIES), flag it immediately if they are mentioned or relevant.
- Always include: "Bet responsibly. Not financial advice." when giving specific picks.
- Keep responses concise but information-dense.
- If data is missing for a specific query, state it clearly rather than guessing.
"""
        try:
            # We insert the system prompt at the beginning of the conversation
            full_messages = [
                {"role": "system", "content": system_prompt},
                *messages[-10:] # Limit to last 10 for tokens
            ]

            stream = await self.client.chat.completions.create(
                model=settings.ORACLE_MODEL,
                messages=full_messages,
                stream=True,
                max_tokens=settings.ORACLE_MAX_TOKENS,
                temperature=settings.ORACLE_TEMPERATURE
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Oracle chat error: {e}")
            yield f"Oracle encountered an error: {str(e)}"

    async def get_suggestions(self, sport: str) -> List[str]:
        """Generate smart suggestions based on live data"""
        # Static defaults for now, can be LLM-generated in Phase 13
        return [
            f"What are the best {sport.replace('_', ' ')} props tonight?",
            "Is there any elite steam detected?",
            "Are there any high-impact injuries I should know about?",
            "Build me a 3-leg parlay with high brain scores",
            "Show me props with positive EV"
        ]

oracle_service = OracleService()
chat = oracle_service.chat
get_suggestions = oracle_service.get_suggestions
build_context = oracle_service.build_context
