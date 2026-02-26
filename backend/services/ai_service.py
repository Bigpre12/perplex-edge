import os
import json
import httpx
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.props import PropLine
from models.bets import BetSlip, BetLog
from models.users import User

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.groq_key = os.getenv("AI_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1/chat/completions" if self.groq_key else "https://api.openai.com/v1/chat/completions"

    async def get_market_context(self, db: AsyncSession) -> str:
        """Fetch top EV props to provide market context to the AI."""
        # Note: In a real system we'd join with PropOdds but for now let's get PropLines
        stmt = select(PropLine).where(PropLine.is_active == True).limit(5)
        result = await db.execute(stmt)
        props = result.scalars().all()
        
        context = "Current Market Highlights:\n"
        for p in props:
            context += f"- {p.player_name}: {p.stat_type} line {p.line} ({p.sport_key})\n"
        return context

    async def get_user_context(self, db: AsyncSession, user_id: int) -> str:
        """Fetch user performance stats to personalize the AI response."""
        stmt = select(BetSlip).where(BetSlip.user_id == user_id).limit(10)
        result = await db.execute(stmt)
        slips = result.scalars().all()
        
        wins = len([s for s in slips if s.status == "won"])
        losses = len([s for s in slips if s.status == "lost"])
        
        context = f"User Performance Context:\n- Record: {wins}W - {losses}L\n"
        if slips:
            context += f"- Recent Bet Types: {', '.join(set([s.slip_type for s in slips]))}\n"
        return context

    async def chat(self, user_query: str, db: AsyncSession, user_id: Optional[int] = None) -> str:
        """Generate an AI response using market and user context."""
        market_context = await self.get_market_context(db)
        user_context = ""
        if user_id:
            user_context = await self.get_user_context(db, user_id)

        system_prompt = f"""
You are Perplex AI, the specialized intelligence assistant for the Perplex Edge sports betting platform.
Your goal is to provide sharp, data-driven analysis to help users find value in the markets.

{market_context}
{user_context}

Be concise, technical, and objective. Avoid generic advice. Use specific numbers when available.
If a user asks about their performance, refer to the provided user context.
"""

        api_key = self.groq_key or self.openai_key
        if not api_key:
            return "AI Service Error: No API key configured."

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama3-70b-8192" if self.groq_key else "gpt-4-turbo-preview",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            "temperature": 0.5,
            "max_tokens": 500
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.base_url, headers=headers, json=payload, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"AI Chat Error: {e}")
            return f"Error interacting with AI brain: {str(e)}"

ai_service = AIService()
