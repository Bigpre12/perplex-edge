import json
import logging
from datetime import datetime, timezone
from typing import AsyncGenerator, List, Optional, Dict, Any
from itertools import islice

from core.config import settings
from services.props_service import props_service
from services.steam_service import steam_service
from services.whale_service import detect_whale_signals
from services.injury_service import injury_service
from services.brain_service import brain_service
from services.llm.model_policy import sanitize_llm_payload, log_sanitizer_drops

# We'll use openai for the streaming implementation as requested
try:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
except ImportError:
    client = None
    logging.warning("OpenAI library not installed. Oracle chat will be disabled.")

logger = logging.getLogger(__name__)
logger.info("LLM model-policy sanitizer enabled for oracle_service")

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
            top_props_sample = list(islice(top_props, 15)) if top_props else []
            
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
                "whale_signals": list(islice(whale_signals, 10)) if isinstance(whale_signals, list) else [],
                "steam_events": steam_events,
                "injuries": list(islice(injuries, 10)) if isinstance(injuries, list) else [],
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
            # Final safety check before calling client
            if not self.client or not hasattr(self.client, 'chat'):
                yield "Oracle is currently unavailable (API client not configured)."
                return

            # Use islice to avoid slice operator issues
            msg_list: List[Dict[str, str]] = list(islice(messages, max(0, len(messages)-10), len(messages)))
            
            payload = {
                "model": settings.ORACLE_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    *msg_list,
                ],
                "stream": True,
                "max_tokens": settings.ORACLE_MAX_TOKENS,
                "temperature": settings.ORACLE_TEMPERATURE,
            }
            payload, dropped = sanitize_llm_payload(settings.ORACLE_MODEL, payload)
            log_sanitizer_drops("oracle_service", "openai_sdk", settings.ORACLE_MODEL, dropped)

            stream = await self.client.chat.completions.create(**payload)

            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Oracle chat error: {e}")
            yield f"Oracle encountered an error: {str(e)}"

    async def get_suggestions(self, sport: str) -> List[str]:
        """Generate smart suggestions based on live data"""
        try:
            context = await self.build_context(sport)
            suggestions = []
            
            # 1. EV Suggestion
            if context.get("ev_signals"):
                best = context["ev_signals"][0]
                p_name = best.get('player_name') or "this player"
                edge = best.get('edge_percent') or "high"
                suggestions.append(f"Is {p_name}'s {edge}% EV edge a sharp play?")
            
            # 2. Injury Suggestion
            if context.get("injuries"):
                inj = context["injuries"][0]
                suggestions.append(f"How does the {inj.get('player')} ({inj.get('status')}) impact today's {sport.split('_')[-1].upper()} slate?")
                
            # 3. Steam/Whale Suggestion
            if context.get("whale_signals") or context.get("steam_events"):
                signals = context.get("whale_signals", []) + context.get("steam_events", [])
                if signals:
                    s = signals[0]
                    p_name = s.get('player') or s.get('player_name')
                    suggestions.append(f"Analyze the sharp movement on {p_name}.")

            # 4. Defaults
            suggestions.append(f"Build me a high-confidence {sport.split('_')[-1].upper()} parlay.")
            suggestions.append(f"What are the top arbitrage spots in {sport.split('_')[-1].upper()}?")
            
            return list(islice(suggestions, 5))
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return [
                f"What are the best {sport.replace('_', ' ')} props tonight?",
                "Show me props with high positive EV",
                "Are there any whale signals detected?",
                "Analyze recent injury impact",
                "Show me institutional arbitrage"
            ]

oracle_service = OracleService()
chat = oracle_service.chat
get_suggestions = oracle_service.get_suggestions
build_context = oracle_service.build_context
