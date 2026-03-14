import sys
import os

sys.path.append('.')

routers = [
    'props', 'live', 'hit_rate', 'line_movement', 'sharp_money', 
    'whale', 'steam', 'clv', 'oracle', 'auth_router', 'stripe_router',
    'search', 'injuries', 'ev_calculator', 'brain_router', 'parlay_suggestions',
    'analytics_router', 'stats', 'players', 'arbitrage', 'edges', 'slate',
    'h2h', 'dfs', 'dvp', 'systems', 'weather', 'referees', 'line_shopping_router',
    'kelly_router', 'sgp_router', 'hedge_router', 'deeplinks', 'splits',
    'alt_lines', 'middle_boost', 'best_book', 'news'
]

for r in routers:
    try:
        print(f"Testing routers.{r}...", end=' ')
        exec(f"from routers import {r}")
        print("✅ OK")
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        # Usually one failure will trigger the rest if it's a package issue, 
        # but let's see if we can continue.
