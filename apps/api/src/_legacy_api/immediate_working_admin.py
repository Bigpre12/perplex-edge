class AsyncSession: pass
from fastapi import APIRouter, Body, HTTPException, Header, Depends
import logging
import os
import json
from datetime import datetime, timezone
from sqlalchemy import text
from database import async_engine, get_async_db
from app.antigravity_edge_config import invalidate_config_cache, get_edge_config
from models.users import UserOverride
from sqlalchemy.future import select
from sqlalchemy import delete
from datetime import timedelta

logger = logging.getLogger(__name__)
router = APIRouter()

async def verify_admin_key(x_admin_key: str = Header(None)):
    expected_key = os.getenv("ADMIN_SECRET_KEY", "123")
    if not x_admin_key or x_admin_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid or missing X-Admin-Key")

@router.post("/grant-access")
async def grant_access(
    payload: dict = Body(...),
    admin_check: None = Depends(verify_admin_key),
    db: AsyncSession = Depends(get_async_db)
):
    """Grant free elite/pro tier access to any user email."""
    email = payload.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
        
    tier = payload.get("tier", "elite")
    note = payload.get("note", "")
    expires_days = payload.get("expires_days")

    expires_at = None
    if expires_days:
        expires_at = datetime.now(timezone.utc) + timedelta(days=int(expires_days))

    async with db.begin():
        # SQLite Upsert logic
        stmt = select(UserOverride).where(UserOverride.email == email)
        result = await db.execute(stmt)
        record = result.scalar_one_or_none()
        
        if record:
            record.tier = tier
            record.note = note
            record.expires_at = expires_at
            record.granted_by = "admin"
        else:
            new_override = UserOverride(
                email=email,
                tier=tier,
                note=note,
                expires_at=expires_at,
                granted_by="admin"
            )
            db.add(new_override)
            
    return {
        "status": "granted",
        "email": email,
        "tier": tier,
        "expires_at": expires_at.isoformat() if expires_at else "never",
        "note": note
    }

@router.delete("/revoke-access")
async def revoke_access(
    email: str,
    admin_check: None = Depends(verify_admin_key),
    db: AsyncSession = Depends(get_async_db)
):
    """Revoke manual access override."""
    async with db.begin():
        await db.execute(delete(UserOverride).where(UserOverride.email == email))
        
    return {"status": "revoked", "email": email}

@router.get("/access-list")
async def list_access(
    admin_check: None = Depends(verify_admin_key),
    db: AsyncSession = Depends(get_async_db)
):
    """List all manual access overrides."""
    result = await db.execute(select(UserOverride).order_by(UserOverride.created_at.desc()))
    overrides = result.scalars().all()
    
    return {
        "users": [
            {
                "email": o.email,
                "tier": o.tier,
                "note": o.note,
                "expires_at": o.expires_at.isoformat() if o.expires_at else "never",
                "created_at": o.created_at.isoformat()
            }
            for o in overrides
        ],
        "total": len(overrides)
    }

@router.post("/antigravity/config")
async def update_antigravity_config(
    payload: dict = Body(...),
    admin_check: None = Depends(verify_admin_key)
):
    """Update edge config in DB — takes effect on next request."""
    try:
        # Get current config for audit (before update)
        current_cfg = await get_edge_config()
        prev_values = json.dumps(current_cfg.__dict__)

        async with async_engine.begin() as conn:
            fields = []
            values = {}
            change_summary = []
            
            for key, val in payload.items():
                if isinstance(val, list):
                    stored_val = json.dumps(val)
                else:
                    stored_val = val
                
                fields.append(f"{key} = :{key}")
                values[key] = stored_val
                change_summary.append(f"{key}->{val}")
            
            fields.append("updated_at = :updated_at")
            values["updated_at"] = datetime.now(timezone.utc)
            
            # 1. Update the config
            await conn.execute(
                text(f"UPDATE edge_config SET {', '.join(fields)} WHERE id = 1"),
                values
            )

            # 2. Log to history
            audit_values = {
                "config_id": 1,
                "change_summary": ", ".join(change_summary),
                "previous_values": prev_values,
                "new_values": json.dumps(payload)
            }
            await conn.execute(
                text("""
                    INSERT INTO edge_config_history (config_id, change_summary, previous_values, new_values)
                    VALUES (:config_id, :change_summary, :previous_values, :new_values)
                """),
                audit_values
            )

        invalidate_config_cache()
        return {"status": "updated", "fields": list(payload.keys())}
    except Exception as e:
        logger.error(f"Failed to update edge config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/antigravity/config")
async def get_antigravity_config_route():
    """See current live config."""
    cfg = await get_edge_config()
    return cfg.__dict__
