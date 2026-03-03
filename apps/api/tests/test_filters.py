import asyncio
import json
from app.antigravity_edge_config import get_edge_config

async def test_immediate_slate():
    from services.picks_service import picks_service
    from api.immediate_working import transform_validation_to_prop
    
    cfg = get_edge_config().Feed
    print(f"Current Config - Min Edge: {cfg.min_edge_percent}%, Max Juice: {cfg.max_juice}")
    
    picks = await picks_service.get_high_ev_picks(min_ev=2.0, hours=168)
    print(f"Total RAW picks from DB: {len(picks)}")
    
    transformed = []
    for p in picks:
        prop = transform_validation_to_prop(p, 'basketball_nba')
        if prop is not None:
            transformed.append(prop)
            
    print(f"Remaining after Edge/Juice filter: {len(transformed)}")
    if transformed:
        for t in transformed[:3]:
            print(f"- {t['player_name']} | Edge: {t['edge']*100:.1f}% | Odds: {t['odds']}")

if __name__ == '__main__':
    asyncio.run(test_immediate_slate())
