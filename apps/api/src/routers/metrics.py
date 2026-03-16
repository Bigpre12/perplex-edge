from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from services.dashboard import get_dashboard_metrics

router = APIRouter()

@router.get("")
async def metrics(db: Session = Depends(get_db)):
    return get_dashboard_metrics(db)
