"""Quick diagnostic: test that all routers import cleanly."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

modules = [
    ("config", "from core.config import settings"),
    ("database", "from db.session import engine, Base, async_session_maker"),
    ("models.users", "import models.users"),
    ("models.props", "import models.props"),
    ("models.brain", "import models.brain"),
    ("models.bets", "import models.bets"),
    ("models.analytical", "import models.analytical"),
    ("models.__init__", "import models"),
    ("routers.props", "from routers import props"),
    ("routers.live", "from routers import live"),
    ("routers.hit_rate", "from routers import hit_rate"),
    ("routers.line_movement", "from routers import line_movement"),
    ("routers.sharp_money", "from routers import sharp_money"),
    ("routers.whale", "from routers import whale"),
    ("routers.steam", "from routers import steam"),
    ("routers.clv", "from routers import clv"),
    ("routers.oracle", "from routers import oracle"),
    ("routers.auth", "from routers import auth"),
    ("routers.stripe_router", "from routers import stripe_router"),
    ("routers.search", "from routers import search"),
    ("routers.injuries", "from routers import injuries"),
    ("routers.ev_calculator", "from routers import ev_calculator"),
    ("routers.brain_router", "from routers import brain_router"),
    ("routers.parlay_suggestions", "from routers import parlay_suggestions"),
    ("routers.user_router", "from routers import user_router"),
    ("routers.api_tier_router", "from routers import api_tier_router"),
]

failed = []
for name, stmt in modules:
    try:
        exec(stmt)
        print(f"  ✅ {name}")
    except Exception as e:
        print(f"  ❌ {name}: {e}")
        failed.append((name, str(e)))

print(f"\n{'='*50}")
if failed:
    print(f"FAILED: {len(failed)} modules")
    for n, e in failed:
        print(f"  - {n}: {e}")
else:
    print("ALL IMPORTS OK ✅")
    print("Server should start cleanly.")
