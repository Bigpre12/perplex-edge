from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from typing import Optional, List, Dict
from pydantic import BaseModel

from services.oracle_service import oracle_service
from api_utils.auth_supabase import get_current_user_supabase

router = APIRouter(tags=["oracle"])

class ChatRequest(BaseModel):
    message: str
    sport: str = "basketball_nba"
    history: List[Dict] = []

class PropAnalysisRequest(BaseModel):
    prop_id: str
    sport: str

@router.post("/chat")
async def oracle_chat(
    body: ChatRequest,
    user: dict = Depends(get_current_user_supabase)
):
    """
    Streaming Oracle chat endpoint (SSE).
    """
    async def event_generator():
        async for chunk in oracle_service.chat(
            body.message, body.sport, body.history, user.get("id")
        ):
            # Format as SSE
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        yield "data: [DONE]\n\n"

    import json
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/suggestions")
async def get_oracle_suggestions(
    sport: str = Query("basketball_nba"),
    user: dict = Depends(get_current_user_supabase)
):
    """
    Get 5 predictive suggested questions based on live data.
    """
    suggestions = await oracle_service.get_suggestions(sport)
    return {"suggestions": suggestions}

@router.post("/analyze-prop")
async def analyze_prop(
    body: PropAnalysisRequest,
    user: dict = Depends(get_current_user_supabase)
):
    """
    Get a full Oracle analysis of a single prop.
    """
    # This can be a more detailed, non-streaming response
    # For now, we'll use a static prompt to the LLM (non-streaming)
    # or just return structured data that the frontend can pass to chat.
    return {
        "analysis": "Oracle is analyzing this prop. (Detailed analysis engine coming in Phase 12)",
        "status": "ready"
    }
