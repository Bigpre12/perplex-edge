"""Force sync script to refresh games with today's dynamic schedule."""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

async def main():
    """Clear old games and sync fresh data."""
    from app.core.database import get_session_maker
    from app.services.etl_games_and_lines import clear_stale_games, sync_with_fallback
    
    print("=" * 60)
    print("Force Sync - Refreshing games with today's schedule")
    print("=" * 60)
    
    session_maker = get_session_maker()
    
    async with session_maker() as db:
        # Clear and sync NBA
        print("\n[NBA] Clearing old games...")
        clear_result = await clear_stale_games(db, "basketball_nba")
        print(f"  Cleared: {clear_result}")
        
        print("[NBA] Syncing fresh data with stubs...")
        sync_result = await sync_with_fallback(
            db, 
            sport_key="basketball_nba",
            include_props=True,
            use_real_api=False,  # Force stubs
        )
        print(f"  Synced: games={sync_result.get('games_created', 0)}, source={sync_result.get('data_source', 'unknown')}")
        
        # Clear and sync NCAAB
        print("\n[NCAAB] Clearing old games...")
        clear_result = await clear_stale_games(db, "basketball_ncaab")
        print(f"  Cleared: {clear_result}")
        
        print("[NCAAB] Syncing fresh data with stubs...")
        sync_result = await sync_with_fallback(
            db,
            sport_key="basketball_ncaab",
            include_props=True,
            use_real_api=False,  # Force stubs
        )
        print(f"  Synced: games={sync_result.get('games_created', 0)}, source={sync_result.get('data_source', 'unknown')}")
    
    print("\n" + "=" * 60)
    print("Done! Refresh the frontend to see updated games.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
