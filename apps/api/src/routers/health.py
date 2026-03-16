from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def meta_health():
    return {"status": "healthy"}

@router.get("/summary")
async def meta_summary():
    return {"status": "ok", "app": "LUCRIX"}
