#!/usr/bin/env python3
"""
Props Verification Script

Checks that props exist for all configured sports.
Run daily to monitor data quality and ETL health.

Usage:
    python scripts/verify_props.py
    python scripts/verify_props.py --hours 24
"""

import argparse
import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.plan_limits import ALL_SPORTS
from app.core.constants import SPORT_ID_TO_KEY, SPORT_KEY_TO_NAME


# All sports we expect to have props for
EXPECTED_SPORTS = ALL_SPORTS


async def verify_props(hours: int = 24, verbose: bool = True) -> dict:
    """
    Verify that props exist for all configured sports.
    
    Args:
        hours: Look back this many hours for props
        verbose: Print detailed output
        
    Returns:
        Dict with verification results
    """
    # Create async engine
    engine = create_async_engine(
        settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
        echo=False
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "hours_checked": hours,
        "sports_with_props": [],
        "sports_missing_props": [],
        "sports_unknown": [],
        "total_props": 0,
        "healthy": True,
    }
    
    async with async_session() as session:
        # Query props count per sport
        query = text("""
            SELECT 
                sport_id, 
                COUNT(*) as prop_count,
                MAX(created_at) as last_prop_time
            FROM player_props 
            WHERE event_time >= NOW() - INTERVAL ':hours hours'
            GROUP BY sport_id
            ORDER BY sport_id
        """.replace(":hours", str(hours)))
        
        result = await session.execute(query)
        rows = result.fetchall()
        
        # Build dict of sport_id -> count
        props_by_sport = {}
        for row in rows:
            sport_id, count, last_time = row
            props_by_sport[sport_id] = {
                "count": count,
                "last_prop_time": last_time.isoformat() if last_time else None
            }
            results["total_props"] += count
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"Props Verification Report - Last {hours} hours")
            print(f"{'='*60}\n")
        
        # Check each expected sport
        for sport_id in EXPECTED_SPORTS:
            sport_key = SPORT_ID_TO_KEY.get(sport_id, f"unknown_{sport_id}")
            sport_name = SPORT_KEY_TO_NAME.get(sport_key, sport_key)
            
            if sport_id in props_by_sport:
                info = props_by_sport[sport_id]
                results["sports_with_props"].append({
                    "sport_id": sport_id,
                    "sport_key": sport_key,
                    "sport_name": sport_name,
                    "count": info["count"],
                    "last_prop_time": info["last_prop_time"],
                })
                if verbose:
                    print(f"  ✓ {sport_name:20} ({sport_key:30}): {info['count']:,} props")
            else:
                results["sports_missing_props"].append({
                    "sport_id": sport_id,
                    "sport_key": sport_key,
                    "sport_name": sport_name,
                })
                results["healthy"] = False
                if verbose:
                    print(f"  ✗ {sport_name:20} ({sport_key:30}): NO PROPS ⚠️")
        
        # Check for props in unexpected sports
        for sport_id, info in props_by_sport.items():
            if sport_id not in EXPECTED_SPORTS:
                sport_key = SPORT_ID_TO_KEY.get(sport_id, f"unknown_{sport_id}")
                sport_name = SPORT_KEY_TO_NAME.get(sport_key, sport_key)
                results["sports_unknown"].append({
                    "sport_id": sport_id,
                    "sport_key": sport_key,
                    "sport_name": sport_name,
                    "count": info["count"],
                })
                if verbose:
                    print(f"  ? {sport_name:20} ({sport_key:30}): {info['count']:,} props (not in config)")
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"Summary:")
            print(f"  Total props: {results['total_props']:,}")
            print(f"  Sports with data: {len(results['sports_with_props'])}/{len(EXPECTED_SPORTS)}")
            print(f"  Sports missing: {len(results['sports_missing_props'])}")
            if results["sports_missing_props"]:
                print(f"\n  ⚠️  Missing sports:")
                for sport in results["sports_missing_props"]:
                    print(f"      - {sport['sport_name']} (ID: {sport['sport_id']})")
            print(f"\n  Status: {'✓ HEALTHY' if results['healthy'] else '✗ UNHEALTHY'}")
            print(f"{'='*60}\n")
    
    await engine.dispose()
    return results


async def main():
    parser = argparse.ArgumentParser(description="Verify props exist for all sports")
    parser.add_argument("--hours", type=int, default=24, help="Hours to look back (default: 24)")
    parser.add_argument("--quiet", action="store_true", help="Suppress output, just return exit code")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    results = await verify_props(hours=args.hours, verbose=not args.quiet and not args.json)
    
    if args.json:
        import json
        print(json.dumps(results, indent=2))
    
    # Exit with error code if unhealthy
    sys.exit(0 if results["healthy"] else 1)


if __name__ == "__main__":
    asyncio.run(main())
