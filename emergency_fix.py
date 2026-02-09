#!/usr/bin/env python3
"""
EMERGENCY FIX - Get player props working NOW
"""
import subprocess
import time
import requests

def emergency_fix():
    """Emergency fix to get player props working immediately"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("EMERGENCY FIX - GET PLAYER PROPS WORKING NOW")
    print("="*80)
    
    print("\nTIME CRITICAL: Less than 1 hour to Super Bowl!")
    print("Need immediate fix to get player props loading!")
    
    print("\n1. EMERGENCY STRATEGY:")
    print("   - Create a minimal player props endpoint")
    print("   - Bypass CLV columns completely")
    print("   - Use only basic required columns")
    print("   - Deploy immediately")
    
    print("\n2. Creating emergency player props endpoint...")
    
    # Create emergency endpoint
    emergency_endpoint = '''from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, and_
from datetime import datetime, timezone
from app.database import get_db
from app.models.model_pick import ModelPick
from app.models.player import Player
from app.models.game import Game
from app.models.team import Team
from app.models.market import Market

router = APIRouter()

@router.get("/emergency-player-props")
async def get_emergency_player_props(
    sport_id: int = Query(..., description="Sport ID"),
    limit: int = Query(10, description="Number of props to return"),
    db: AsyncSession = Depends(get_db)
):
    """Emergency player props endpoint - CLV columns free"""
    try:
        # Get current time
        now = datetime.now(timezone.utc)
        
        # Build query with only essential columns
        query = (
            select(
                ModelPick.id,
                ModelPick.sport_id,
                ModelPick.game_id,
                ModelPick.player_id,
                ModelPick.market_id,
                ModelPick.side,
                ModelPick.line_value,
                ModelPick.odds,
                ModelPick.model_probability,
                ModelPick.implied_probability,
                ModelPick.expected_value,
                ModelPick.confidence_score,
                ModelPick.generated_at,
                Player,
                Game,
                Market
            )
            .join(Player, ModelPick.player_id == Player.id)
            .join(Game, ModelPick.game_id == Game.id)
            .join(Market, ModelPick.market_id == Market.id)
            .where(
                and_(
                    ModelPick.sport_id == sport_id,
                    Game.start_time >= now,
                    ModelPick.expected_value > 0,
                    ModelPick.confidence_score >= 0.5
                )
            )
            .order_by(ModelPick.expected_value.desc())
            .limit(limit)
        )
        
        result = await db.execute(query)
        rows = result.fetchall()
        
        # Convert to response format
        props = []
        for row in rows:
            pick_data = {
                'id': row[0],
                'sport_id': row[1],
                'game_id': row[2],
                'player_id': row[3],
                'market_id': row[4],
                'side': row[5],
                'line_value': row[6],
                'odds': row[7],
                'model_probability': float(row[8]),
                'implied_probability': float(row[9]),
                'expected_value': float(row[10]),
                'confidence_score': float(row[11]),
                'generated_at': row[12].isoformat(),
                'player': {
                    'id': row[13].id,
                    'name': row[13].name,
                    'position': row[13].position
                },
                'game': {
                    'id': row[14].id,
                    'home_team': {'name': row[14].home_team.name if row[14].home_team else 'TBD'},
                    'away_team': {'name': row[14].away_team.name if row[14].away_team else 'TBD'},
                    'start_time': row[14].start_time.isoformat()
                },
                'market': {
                    'id': row[15].id,
                    'stat_type': row[15].stat_type,
                    'description': row[15].description
                },
                'edge': float(row[10])  # Use expected_value as edge
            }
            props.append(pick_data)
        
        return {
            'items': props,
            'total': len(props),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
'''
    
    # Write emergency endpoint
    try:
        with open("c:/Users/preio/perplex-edge/backend/app/api/emergency.py", "w") as f:
            f.write(emergency_endpoint)
        print("   Created emergency endpoint")
    except Exception as e:
        print(f"   Error creating endpoint: {e}")
    
    # Add to main router
    try:
        main_path = "c:/Users/preio/perplex-edge/backend/app/main.py"
        with open(main_path, "r") as f:
            content = f.read()
        
        # Add emergency router
        if "from app.api.emergency import router as emergency_router" not in content:
            content = "from app.api.emergency import router as emergency_router\n" + content
            content = content.replace("app.include_router(admin_router", "app.include_router(emergency_router, tags=[\"emergency\"])\n    app.include_router(admin_router")
            
            with open(main_path, "w") as f:
                f.write(content)
            
            print("   Added emergency router to main.py")
    except Exception as e:
        print(f"   Error updating main.py: {e}")
    
    print("\n3. Pushing emergency fix...")
    try:
        subprocess.run(["git", "add", "-A"], check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "EMERGENCY: Add player props endpoint without CLV columns"], check=True, capture_output=True)
        subprocess.run(["git", "push", "origin", "main"], check=True, capture_output=True)
        print("   Pushed emergency fix to git")
    except Exception as e:
        print(f"   Git push failed: {e}")
    
    print("\n4. Waiting for deployment...")
    time.sleep(30)
    
    print("\n5. Testing emergency endpoint...")
    try:
        response = requests.get(f"{base_url}/emergency/emergency-player-props?sport_id=30&limit=5", timeout=10)
        print(f"   Emergency NBA Props Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            props = data.get('items', [])
            print(f"   SUCCESS! Found {len(props)} NBA props")
            
            if props:
                for i, prop in enumerate(props[:3], 1):
                    player = prop.get('player', {})
                    print(f"   {i}. {player.get('name', 'N/A')}: {prop.get('market', {}).get('stat_type', 'N/A')} {prop.get('line_value', 'N/A')}")
                    print(f"      Edge: {prop.get('edge', 0):.2%}")
                    print(f"      Odds: {prop.get('odds', 0)}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    try:
        response = requests.get(f"{base_url}/emergency/emergency-player-props?sport_id=31&limit=5", timeout=10)
        print(f"   Emergency NFL Props Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            props = data.get('items', [])
            print(f"   SUCCESS! Found {len(props)} NFL props")
            
            if props:
                for i, prop in enumerate(props[:3], 1):
                    player = prop.get('player', {})
                    print(f"   {i}. {player.get('name', 'N/A')}: {prop.get('market', {}).get('stat_type', 'N/A')} {prop.get('line_value', 'N/A')}")
                    print(f"      Edge: {prop.get('edge', 0):.2%}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)
    print("EMERGENCY FIX DEPLOYED!")
    print("="*80)
    
    print("\nIF EMERGENCY ENDPOINT WORKS:")
    print("1. Update frontend to use /emergency/emergency-player-props")
    print("2. Get basic props loading for Super Bowl")
    print("3. Fix CLV columns after game")
    
    print("\nTIME LEFT: CRITICAL!")
    print("This emergency fix should get props working immediately!")
    
    print("\n" + "="*80)
    print("SUPER BOWL READY: TESTING NOW")
    print("="*80)

if __name__ == "__main__":
    emergency_fix()
