import pytest
from httpx import AsyncClient
from main import app
from schemas.unified import PropLiveSchema, EvEdgeSchema, WhaleEventSchema, ClvTradeSchema
from typing import List

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_props_live_schema():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/props/live?sport=basketball_nba")
    assert response.status_code == 200
    data = response.json()
    # If no data, that's fine, but if data exists, it must match schema
    if data:
        for item in data:
            PropLiveSchema.model_validate(item)

@pytest.mark.asyncio
async def test_intel_ev_top_schema():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/intel/ev-top?sport=basketball_nba")
    assert response.status_code == 200
    data = response.json()
    if data:
        for item in data:
            EvEdgeSchema.model_validate(item)
            assert "trend" in item
            assert isinstance(item["trend"], list)

@pytest.mark.asyncio
async def test_whale_live_schema():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/whale/live?sport=basketball_nba")
    assert response.status_code == 200
    data = response.json()
    if data:
        for item in data:
            WhaleEventSchema.model_validate(item)

@pytest.mark.asyncio
async def test_clv_history_schema():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/clv/history?sport=basketball_nba")
    assert response.status_code == 200
    data = response.json()
    if data:
        for item in data:
            ClvTradeSchema.model_validate(item)

@pytest.mark.asyncio
async def test_no_mock_data_contamination():
    """Verify that common mock strings are not present in core responses."""
    endpoints = [
        "/api/props/live",
        "/api/intel/ev-top",
        "/api/whale/live"
    ]
    mock_markers = ["MOCK_PLAYER", "TEST_TEAM", "MOCK_BOOK"]
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        for ep in endpoints:
            response = await ac.get(f"{ep}?sport=basketball_nba")
            text = response.text.upper()
            for marker in mock_markers:
                assert marker not in text, f"Mock data detected in {ep}: {marker}"
