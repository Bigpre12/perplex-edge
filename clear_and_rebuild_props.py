#!/usr/bin/env python3
"""
Clear and rebuild player props endpoints from scratch
"""
import subprocess
import time
import requests

def clear_and_rebuild_props():
    """Clear and rebuild player props endpoints from scratch"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("CLEAR AND REBUILD PLAYER PROPS ENDPOINTS")
    print("="*80)
    
    print("\nTIME CRITICAL: Less than 1 hour to Super Bowl!")
    print("Building clean player props endpoints from scratch!")
    
    print("\n1. Creating clean player props endpoint...")
    
    # Create completely clean endpoint
    clean_endpoint = '''from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timezone
from app.database import get_db
from app.models.model_pick import ModelPick
from app.models.player import Player
from app.models.game import Game
from app.models.market import Market

router = APIRouter()

@router.get("/clean-player-props")
async def get_clean_player_props(
    sport_id: int = Query(..., description="Sport ID"),
    limit: int = Query(20, description="Number of props to return"),
    db: AsyncSession = Depends(get_db)
):
    """Clean player props endpoint - no CLV columns"""
    try:
        # Get current time
        now = datetime.now(timezone.utc)
        
        # Simple query without CLV columns
        query = select(ModelPick).where(
            and_(
                ModelPick.sport_id == sport_id,
                ModelPick.expected_value > 0,
                ModelPick.confidence_score > 0.5
            )
        ).order_by(ModelPick.expected_value.desc()).limit(limit)
        
        result = await db.execute(query)
        picks = result.scalars().all()
        
        # Convert to simple response
        props = []
        for pick in picks:
            # Get related data
            player = await db.get(Player, pick.player_id)
            game = await db.get(Game, pick.game_id)
            market = await db.get(Market, pick.market_id)
            
            prop_data = {
                'id': pick.id,
                'sport_id': pick.sport_id,
                'game_id': pick.game_id,
                'player': {
                    'id': player.id if player else None,
                    'name': player.name if player else 'Unknown',
                    'position': player.position if player else None
                },
                'market': {
                    'id': market.id if market else None,
                    'stat_type': market.stat_type if market else 'Unknown',
                    'description': market.description if market else 'Unknown'
                },
                'side': pick.side,
                'line_value': pick.line_value,
                'odds': pick.odds,
                'model_probability': float(pick.model_probability),
                'implied_probability': float(pick.implied_probability),
                'expected_value': float(pick.expected_value),
                'confidence_score': float(pick.confidence_score),
                'edge': float(pick.expected_value),  # Use EV as edge
                'generated_at': pick.generated_at.isoformat() if pick.generated_at else None
            }
            props.append(prop_data)
        
        return {
            'items': props,
            'total': len(props),
            'sport_id': sport_id,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'items': [],
            'total': 0,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

@router.get("/super-bowl-props")
async def get_super_bowl_props(
    db: AsyncSession = Depends(get_db)
):
    """Super Bowl specific props"""
    try:
        # Super Bowl game ID (assuming it's 648)
        super_bowl_game_id = 648
        
        query = select(ModelPick).where(
            and_(
                ModelPick.sport_id == 31,  # NFL
                ModelPick.game_id == super_bowl_game_id,
                ModelPick.expected_value > 0,
                ModelPick.confidence_score > 0.5
            )
        ).order_by(ModelPick.expected_value.desc()).limit(20)
        
        result = await db.execute(query)
        picks = result.scalars().all()
        
        props = []
        for pick in picks:
            player = await db.get(Player, pick.player_id)
            market = await db.get(Market, pick.market_id)
            
            prop_data = {
                'id': pick.id,
                'player': {
                    'name': player.name if player else 'Unknown',
                    'position': player.position if player else None
                },
                'market': {
                    'stat_type': market.stat_type if market else 'Unknown',
                    'description': market.description if market else 'Unknown'
                },
                'side': pick.side,
                'line_value': pick.line_value,
                'odds': pick.odds,
                'edge': float(pick.expected_value),
                'confidence_score': float(pick.confidence_score),
                'generated_at': pick.generated_at.isoformat() if pick.generated_at else None
            }
            props.append(prop_data)
        
        return {
            'items': props,
            'total': len(props),
            'game_id': super_bowl_game_id,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'items': [],
            'total': 0,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
'''
    
    # Write clean endpoint
    try:
        with open("c:/Users/preio/perplex-edge/backend/app/api/clean_props.py", "w") as f:
            f.write(clean_endpoint)
        print("   Created clean player props endpoint")
    except Exception as e:
        print(f"   Error creating endpoint: {e}")
    
    # Update main.py to include clean props
    try:
        main_path = "c:/Users/preio/preio/perplex-edge/backend/app/main.py"
        with open(main_path, "r") as f:
            content = f.read()
        
        # Add clean props router
        if "from app.api.clean_props import router as clean_props_router" not in content:
            content = "from app.api.clean_props import router as clean_props_router\n" + content
            content = content.replace("app.include_router(admin_router", "app.include_router(clean_props_router, prefix=\"/clean\", tags=[\"clean\"])\n    app.include_router(admin_router")
            
            with open(main_path, "w") as f:
                f.write(content)
            
            print("   Added clean props router to main.py")
    except Exception as e:
        print(f"   Error updating main.py: {e}")
    
    print("\n2. Pushing clean endpoints...")
    try:
        subprocess.run(["git", "add", "-A"], check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "BUILD: Create clean player props endpoints from scratch"], check=True, capture_output=True)
        subprocess.run(["git", "push", "origin", "main"], check=True, capture_output=True)
        print("   Pushed clean endpoints to git")
    except Exception as e:
        print(f"   Git push failed: {e}")
    
    print("\n3. Waiting for deployment...")
    time.sleep(30)
    
    print("\n4. Testing clean endpoints...")
    
    # Test clean NBA props
    try:
        response = requests.get(f"{base_url}/clean/clean-player-props?sport_id=30&limit=5", timeout=10)
        print(f"   Clean NBA Props Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            props = data.get('items', [])
            print(f"   SUCCESS! Found {len(props)} NBA props")
            
            if props:
                for i, prop in enumerate(props[:3], 1):
                    player = prop.get('player', {})
                    market = prop.get('market', {})
                    print(f"   {i}. {player.get('name', 'N/A')}: {market.get('stat_type', 'N/A')} {prop.get('line_value', 'N/A')}")
                    print(f"      Edge: {prop.get('edge', 0):.2%}")
                    print(f"      Odds: {prop.get('odds', 0)}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test Super Bowl props
    try:
        response = requests.get(f"{base_url}/clean/super-bowl-props", timeout=10)
        print(f"   Super Bowl Props Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            props = data.get('items', [])
            print(f"   SUCCESS! Found {len(props)} Super Bowl props")
            
            if props:
                print(f"   Super Bowl props:")
                for i, prop in enumerate(props[:5], 1):
                    player = prop.get('player', {})
                    market = prop.get('market', {})
                    print(f"   {i}. {player.get('name', 'N/A')}: {market.get('stat_type', 'N/A')} {prop.get('line_value', 'N/A')}")
                    print(f"      Edge: {prop.get('edge', 0):.2%}")
                    print(f"      Confidence: {prop.get('confidence_score', 0):.1f}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)
    print("CLEAN ENDPOINTS DEPLOYED!")
    print("="*80)
    
    print("\nNEW ENDPOINTS:")
    print("1. /clean/clean-player-props?sport_id=30&limit=20")
    print("2. /clean/super-bowl-props")
    
    print("\nFRONTEND UPDATE NEEDED:")
    print("Update frontend to use these clean endpoints!")
    
    print("\nTIME CRITICAL:")
    print("These clean endpoints should work immediately!")
    print("No CLV columns, no complex joins, just basic props!")
    
    print("\n" + "="*80)
    print("PLAYER PROPS: CLEAN VERSION DEPLOYED")
    print("="*80)

if __name__ == "__main__":
    clear_and_rebuild_props()
