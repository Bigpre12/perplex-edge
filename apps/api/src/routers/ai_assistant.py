from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_db
from routers.auth_router import get_current_user
from models.users import User
from services.ai_service import ai_service
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/ai", tags=["ai"])

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
async def chat_with_perplex(
    request: ChatRequest = Body(...),
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Personalized AI chat endpoint. 
    Accepts user query and returns AI analysis based on market context and user record.
    """
    try:
        user_id = current_user.id if current_user else None
        response = await ai_service.chat(
            user_query=request.message,
            db=db,
            user_id=user_id
        )
        return {"status": "success", "response": response}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI Assistant temporary failure: {str(e)}"
        )
