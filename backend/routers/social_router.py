from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_db
from routers.auth_router import get_current_user
from models.users import User
from services.social_service import social_service
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/social", tags=["social"])

class ShareCreate(BaseModel):
    title: str
    content: Optional[str] = None
    slip_id: Optional[int] = None

@router.post("/share", status_code=status.HTTP_201_CREATED)
async def share_intel(
    share_data: ShareCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    try:
        post = await social_service.create_share(
            db=db,
            user_id=current_user.id,
            title=share_data.title,
            content=share_data.content,
            slip_id=share_data.slip_id
        )
        return {"status": "success", "post_id": post.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/feed")
async def get_community_feed(
    db: AsyncSession = Depends(get_async_db),
    limit: int = 20,
    offset: int = 0
):
    posts = await social_service.get_feed(db, limit, offset)
    return posts

@router.post("/like/{post_id}")
async def like_post(
    post_id: int,
    current_user: User = Depends(get_current_user), # Require login to like
    db: AsyncSession = Depends(get_async_db)
):
    success = await social_service.like_post(db, post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"status": "success"}
