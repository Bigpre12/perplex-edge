class AsyncSession: pass
from sqlalchemy import select, desc
from models.social import SharedIntel
from models.bets import BetSlip
from models.users import User
from typing import List, Optional

class SocialService:
    async def create_share(self, db: AsyncSession, user_id: int, title: str, content: str, slip_id: Optional[int] = None):
        """Create a new community share post."""
        new_post = SharedIntel(
            user_id=user_id,
            slip_id=slip_id,
            title=title,
            content=content
        )
        db.add(new_post)
        await db.commit()
        await db.refresh(new_post)
        return new_post

    async def get_feed(self, db: AsyncSession, limit: int = 20, offset: int = 0):
        """Retrieve the global community feed with user details."""
        # Note: In a real app we'd join with User to get author info
        stmt = (
            select(SharedIntel, User.username)
            .join(User, SharedIntel.user_id == User.id)
            .order_by(desc(SharedIntel.created_at))
            .limit(limit)
            .offset(offset)
        )
        result = await db.execute(stmt)
        posts = []
        for post, username in result.all():
            post_dict = {
                "id": post.id,
                "user_id": post.user_id,
                "username": username,
                "slip_id": post.slip_id,
                "title": post.title,
                "content": post.content,
                "likes_count": post.likes_count,
                "comments_count": post.comments_count,
                "created_at": post.created_at
            }
            posts.append(post_dict)
        return posts

    async def like_post(self, db: AsyncSession, post_id: int):
        """Increment like count for a post."""
        stmt = select(SharedIntel).where(SharedIntel.id == post_id)
        result = await db.execute(stmt)
        post = result.scalar_one_or_none()
        if post:
            post.likes_count += 1
            await db.commit()
            return True
        return False

social_service = SocialService()
