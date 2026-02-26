from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import httpx
import os
from openai import AsyncOpenAI
from database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/chat", tags=["Oracle AI Chat"])

# Load OpenAI Async Client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk_mock_api_key_only")
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

class ChatRequest(BaseModel):
    message: str
    user_id: str

@router.post("/ask-oracle")
async def ask_oracle(req: ChatRequest, db: Session = Depends(get_db)):
    try:
        # 1. Fetch the live "Immediate Working Player Props" from the local engine
        # We query our own API to get the current EV data to feed to the LLM
        async with httpx.AsyncClient() as http_client:
            live_props_response = await http_client.get("http://localhost:8000/immediate/working-player-props?limit=15")
            
            if live_props_response.status_code == 200:
                live_data = live_props_response.json()
                market_context = f"Here is the LIVE EV Prop Data for the slate right now:\n{str(live_data)}"
            else:
                market_context = "Warning: Live EV data is currently unavailable."

        # 2. Build the System Prompt
        system_prompt = f"""
        You are the 'Perplex Oracle', an elite, institutional-grade sports betting AI assistant.
        You specialize in Advanced Expected Value (+EV) data, arbitrage, and sharp line movement.
        Your tone is highly professional, data-centric, and concise. You do not give financial advice, only mathematical probability analysis.
        
        {market_context}
        
        Answer the user's query using strictly the LIVE data provided above. If the data doesn't contain the answer, say you don't have enough edge data on that specific market yet.
        """

        # 3. Call OpenAI gpt-4o-mini (or gpt-4-turbo)
        completion = await client.chat.completions.create(
            model="gpt-4o-mini",
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
        print(f"Oracle Error: {e}")
        raise HTTPException(status_code=500, detail="The Oracle is currently recalibrating. Try again shortly.")
