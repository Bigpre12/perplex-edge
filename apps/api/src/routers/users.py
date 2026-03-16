from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from models.user import User
from schemas.user import UserOut

router = APIRouter()

@router.get("/me", response_model=UserOut)
async def me(db: Session = Depends(get_db)):
    user = db.query(User).first()
    if not user:
        user = User(id="demo-user", email="demo@example.com", role="admin", tier="pro")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
