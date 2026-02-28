from fastapi import APIRouter, HTTPException, Body
from services.share_service import share_service
from typing import Dict, Any

router = APIRouter()

@router.post("/create")
async def create_share(prop_data: Dict[str, Any] = Body(...)):
    """Create a shareable link for a prop card"""
    try:
        share_id = await share_service.create_share(prop_data)
        return {"share_id": share_id, "url": f"/share/{share_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{share_id}")
async def get_share(share_id: str):
    """Get prop data for a share ID"""
    share = await share_service.get_share(share_id)
    if not share:
        raise HTTPException(status_code=404, detail="Share link not found")
    return share
