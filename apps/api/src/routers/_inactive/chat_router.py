from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
import httpx
import os
from openai import AsyncOpenAI
from database import get_db
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/api/chat", tags=["Oracle AI Chat"])
limiter = Limiter(key_func=get_remote_address)

# Load Groq Async Client (using OpenAI SDK compatibility)
AI_API_KEY = os.environ.get("AI_API_KEY", "sk_mock_api_key_only")
client = AsyncOpenAI(api_key=AI_API_KEY, base_url="https://api.groq.com/openai/v1")

class ChatRequest(BaseModel):
    message: str
    user_id: str

@router.post("/ask-oracle")
@limiter.limit("5/minute")
async def ask_oracle(request: Request, req: ChatRequest, db: Session = Depends(get_db)):
    try:
        # 1. Fetch the live "Immediate Working Player Props" from the local engine
        # We call the exact function directly rather than routing via localhost to avoid Cloud/Railway blocking itself
        from api.immediate_working import get_working_player_props_immediate
        import asyncio
        
        live_data = await get_working_player_props_immediate(sport_key="basketball_nba", limit=15)
        market_context = f"Here is the LIVE EV Prop Data for the slate right now:\n{str(live_data)}"

        # 2. Build the System Prompt
        system_prompt = f"""
        You are the 'Lucrix Oracle', an elite, institutional-grade sports betting AI assistant.
        You specialize in Advanced Expected Value (+EV) data, arbitrage, and sharp line movement.
        Your tone is highly professional, data-centric, and concise. You do not give financial advice, only mathematical probability analysis.
        
        {market_context}
        
        Answer the user's query using strictly the LIVE data provided above. 
        Focus on identifying specific discrepancies between sportsbook odds and our model's simulated probabilities.
        Highlight any edge >= 5% or confidence >= 65% as 'Prime Sharp Action'.
        If the data doesn't contain the answer, say you don't have enough edge data on that specific market yet.
        """

        # 3. Call Groq Llama 3
        completion = await client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": req.message}
            ],
            temperature=0.3,
            max_tokens=500
        )

        reply = completion.choices[0].message.content
        return {"reply": reply}

    except Exception as e:
        error_msg = str(e)
        print(f"Oracle Error: {error_msg}")
        if "rate_limit_exceeded" in error_msg.lower() or "429" in error_msg:
            return {"reply": "I'm currently assisting too many users. Please wait a moment and try again!"}
        raise HTTPException(status_code=500, detail=error_msg)
