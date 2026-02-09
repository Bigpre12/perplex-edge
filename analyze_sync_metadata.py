#!/usr/bin/env python3
"""
SYNC METADATA ANALYSIS - Comprehensive analysis of the sync_metadata table
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
import json

async def analyze_sync_metadata():
    """Analyze the sync_metadata table structure and data"""
    
    # Database connection
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found")
        return
    
    try:
        conn = await asyncpg.connect(db_url)
        print("Connected to database")
        
        # Get all sync metadata data
        sync_data = await conn.fetch("""
            SELECT * FROM sync_metadata 
            ORDER BY last_updated DESC
        """)
        
        print("SYNC METADATA TABLE ANALYSIS")
        print("="*80)
        
        print(f"\nTotal Sync Records: {len(sync_data)}")
        
        # Overall sync statistics
        overall = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_syncs,
                COUNT(DISTINCT sport_key) as unique_sports,
                COUNT(DISTINCT data_type) as unique_data_types,
                COUNT(DISTINCT source) as unique_sources,
                SUM(games_count) as total_games,
                SUM(lines_count) as total_lines,
                SUM(props_count) as total_props,
                SUM(picks_count) as total_picks,
                AVG(sync_duration_seconds) as avg_sync_duration,
                MAX(sync_duration_seconds) as max_sync_duration,
                MIN(sync_duration_seconds) as min_sync_duration,
                COUNT(CASE WHEN is_healthy = true THEN 1 END) as healthy_syncs,
                COUNT(CASE WHEN is_healthy = false THEN 1 END) as unhealthy_syncs,
                COUNT(CASE WHEN error_message IS NOT NULL THEN 1 END) as syncs_with_errors,
                COUNT(CASE WHEN games_count > 0 THEN 1 END) as syncs_with_games,
                COUNT(CASE WHEN lines_count > 0 THEN 1 END) as syncs_with_lines,
                COUNT(CASE WHEN props_count > 0 THEN 1 END) as syncs_with_props,
                COUNT(CASE WHEN picks_count > 0 THEN 1 END) as syncs_with_picks
            FROM sync_metadata
        """)
        
        print(f"\nOverall Sync Statistics:")
        print(f"  Total Syncs: {overall['total_syncs']}")
        print(f"  Unique Sports: {overall['unique_sports']}")
        print(f"  Unique Data Types: {overall['unique_data_types']}")
        print(f"  Unique Sources: {overall['unique_sources']}")
        print(f"  Total Games: {overall['total_games']}")
        print(f"  Total Lines: {overall['total_lines']}")
        print(f"  Total Props: {overall['total_props']}")
        print(f"  Total Picks: {overall['total_picks']}")
        print(f"  Avg Sync Duration: {overall['avg_sync_duration']:.2f} seconds")
        print(f"  Max Sync Duration: {overall['max_sync_duration']:.2f} seconds")
        print(f"  Min Sync Duration: {overall['min_sync_duration']:.2f} seconds")
        print(f"  Healthy Syncs: {overall['healthy_syncs']}")
        print(f"  Unhealthy Syncs: {overall['unhealthy_syncs']}")
        print(f"  Syncs with Errors: {overall['syncs_with_errors']}")
        print(f"  Syncs with Games: {overall['syncs_with_games']}")
        print(f"  Syncs with Lines: {overall['syncs_with_lines']}")
        print(f"  Syncs with Props: {overall['syncs_with_props']}")
        print(f"  Syncs with Picks: {overall['syncs_with_picks']}")
        
        # Sync by sport
        by_sport = await conn.fetch("""
            SELECT 
                sport_key,
                COUNT(*) as total_syncs,
                COUNT(DISTINCT data_type) as unique_data_types,
                SUM(games_count) as total_games,
                SUM(lines_count) as total_lines,
                SUM(props_count) as total_props,
                SUM(picks_count) as total_picks,
                AVG(sync_duration_seconds) as avg_sync_duration,
                MAX(sync_duration_seconds) as max_sync_duration,
                MIN(sync_duration_seconds) as min_sync_duration,
                COUNT(CASE WHEN is_healthy = true THEN 1 END) as healthy_syncs,
                COUNT(CASE WHEN is_healthy = false THEN 1 END) as unhealthy_syncs,
                COUNT(CASE WHEN error_message IS NOT NULL THEN 1 END) as syncs_with_errors,
                MIN(last_updated) as first_sync,
                MAX(last_updated) as last_sync
            FROM sync_metadata
            GROUP BY sport_key
            ORDER BY total_games DESC, total_lines DESC
        """)
        
        print(f"\nSync Performance by Sport:")
        for sport in by_sport:
            print(f"  {sport['sport_key']}:")
            print(f"    Total Syncs: {sport['total_syncs']}")
            print(f"    Data Types: {sport['unique_data_types']}")
            print(f"    Games: {sport['total_games']}")
            print(f"    Lines: {sport['total_lines']}")
            print(f"    Props: {sport['total_props']}")
            print(f"    Picks: {sport['total_picks']}")
            print(f"    Avg Duration: {sport['avg_sync_duration']:.2f}s")
            print(f"    Duration Range: {sport['min_sync_duration']:.2f}s - {sport['max_sync_duration']:.2f}s")
            print(f"    Healthy: {sport['healthy_syncs']}, Unhealthy: {sport['unhealthy_syncs']}")
            print(f"    Errors: {sport['syncs_with_errors']}")
            print(f"    Period: {sport['first_sync']} to {sport['last_sync']}")
        
        # Sync by data type
        by_data_type = await conn.fetch("""
            SELECT 
                data_type,
                COUNT(*) as total_syncs,
                COUNT(DISTINCT sport_key) as unique_sports,
                SUM(games_count) as total_games,
                SUM(lines_count) as total_lines,
                SUM(props_count) as total_props,
                SUM(picks_count) as total_picks,
                AVG(sync_duration_seconds) as avg_sync_duration,
                MAX(sync_duration_seconds) as max_sync_duration,
                MIN(sync_duration_seconds) as min_sync_duration,
                COUNT(CASE WHEN is_healthy = true THEN 1 END) as healthy_syncs,
                COUNT(CASE WHEN is_healthy = false THEN 1 END) as unhealthy_syncs,
                COUNT(CASE WHEN error_message IS NOT NULL THEN 1 END) as syncs_with_errors
            FROM sync_metadata
            GROUP BY data_type
            ORDER BY total_syncs DESC
        """)
        
        print(f"\nSync Performance by Data Type:")
        for data_type in by_data_type:
            print(f"  {data_type['data_type']}:")
            print(f"    Total Syncs: {data_type['total_syncs']}")
            print(f"    Unique Sports: {data_type['unique_sports']}")
            print(f"    Games: {data_type['total_games']}")
            print(f"    Lines: {data_type['total_lines']}")
            print(f"    Props: {data_type['total_props']}")
            print(f"    Picks: {data_type['total_picks']}")
            print(f"    Avg Duration: {data_type['avg_sync_duration']:.2f}s")
            print(f"    Duration Range: {data_type['min_sync_duration']:.2f}s - {data_type['max_sync_duration']:.2f}s")
            print(f"    Healthy: {data_type['healthy_syncs']}, Unhealthy: {data_type['unhealthy_syncs']}")
            print(f"    Errors: {data_type['syncs_with_errors']}")
        
        # Sync by source
        by_source = await conn.fetch("""
            SELECT 
                source,
                COUNT(*) as total_syncs,
                COUNT(DISTINCT sport_key) as unique_sports,
                SUM(games_count) as total_games,
                SUM(lines_count) as total_lines,
                SUM(props_count) as total_props,
                SUM(picks_count) as total_picks,
                AVG(sync_duration_seconds) as avg_sync_duration,
                MAX(sync_duration_seconds) as max_sync_duration,
                MIN(sync_duration_seconds) as min_sync_duration,
                COUNT(CASE WHEN is_healthy = true THEN 1 END) as healthy_syncs,
                COUNT(CASE WHEN is_healthy = false THEN 1 END) as unhealthy_syncs,
                COUNT(CASE WHEN error_message IS NOT NULL THEN 1 END) as syncs_with_errors
            FROM sync_metadata
            GROUP BY source
            ORDER BY total_syncs DESC
        """)
        
        print(f"\nSync Performance by Source:")
        for source in by_source:
            print(f"  {source['source']}:")
            print(f"    Total Syncs: {source['total_syncs']}")
            print(f"    Unique Sports: {source['unique_sports']}")
            print(f"    Games: {source['total_games']}")
            print(f"    Lines: {source['total_lines']}")
            print(f"    Props: {source['total_props']}")
            print(f"    Picks: {source['total_picks']}")
            print(f"    Avg Duration: {source['avg_sync_duration']:.2f}s")
            print(f"    Duration Range: {source['min_sync_duration']:.2f}s - {source['max_sync_duration']:.2f}s")
            print(f"    Healthy: {source['healthy_syncs']}, Unhealthy: {source['unhealthy_syncs']}")
            print(f"    Errors: {source['syncs_with_errors']}")
        
        # Health analysis
        health_analysis = await conn.fetch("""
            SELECT 
                is_healthy,
                COUNT(*) as total_syncs,
                COUNT(DISTINCT sport_key) as unique_sports,
                SUM(games_count) as total_games,
                SUM(lines_count) as total_lines,
                SUM(props_count) as total_props,
                SUM(picks_count) as total_picks,
                AVG(sync_duration_seconds) as avg_sync_duration,
                COUNT(CASE WHEN error_message IS NOT NULL THEN 1 END) as syncs_with_errors,
                COUNT(CASE WHEN games_count > 0 THEN 1 END) as syncs_with_games,
                COUNT(CASE WHEN lines_count > 0 THEN 1 END) as syncs_with_lines,
                COUNT(CASE WHEN props_count > 0 THEN 1 END) as syncs_with_props,
                COUNT(CASE WHEN picks_count > 0 THEN 1 END) as syncs_with_picks
            FROM sync_metadata
            GROUP BY is_healthy
            ORDER BY is_healthy DESC
        """)
        
        print(f"\nHealth Analysis:")
        for health in health_analysis:
            health_status = "Healthy" if health['is_healthy'] else "Unhealthy"
            print(f"  {health_status}:")
            print(f"    Total Syncs: {health['total_syncs']}")
            print(f"    Unique Sports: {health['unique_sports']}")
            print(f"    Games: {health['total_games']}")
            print(f"    Lines: {health['total_lines']}")
            print(f"    Props: {health['total_props']}")
            print(f"    Picks: {health['total_picks']}")
            print(f"    Avg Duration: {health['avg_sync_duration']:.2f}s")
            print(f"    Errors: {health['syncs_with_errors']}")
            print(f"    With Data: Games({health['syncs_with_games']}) Lines({health['syncs_with_lines']}) Props({health['syncs_with_props']}) Picks({health['syncs_with_picks']})")
        
        # Performance analysis by duration
        performance_analysis = await conn.fetch("""
            SELECT 
                CASE 
                    WHEN sync_duration_seconds < 1 THEN 'Fast (< 1s)'
                    WHEN sync_duration_seconds < 5 THEN 'Normal (1-5s)'
                    WHEN sync_duration_seconds < 10 THEN 'Slow (5-10s)'
                    ELSE 'Very Slow (> 10s)'
                END as performance_category,
                COUNT(*) as total_syncs,
                COUNT(DISTINCT sport_key) as unique_sports,
                SUM(games_count) as total_games,
                SUM(lines_count) as total_lines,
                SUM(props_count) as total_props,
                SUM(picks_count) as total_picks,
                AVG(sync_duration_seconds) as avg_sync_duration,
                COUNT(CASE WHEN is_healthy = true THEN 1 END) as healthy_syncs,
                COUNT(CASE WHEN is_healthy = false THEN 1 END) as unhealthy_syncs,
                COUNT(CASE WHEN error_message IS NOT NULL THEN 1 END) as syncs_with_errors
            FROM sync_metadata
            GROUP BY performance_category
            ORDER BY avg_sync_duration ASC
        """)
        
        print(f"\nPerformance Analysis by Duration:")
        for perf in performance_analysis:
            print(f"  {perf['performance_category']}:")
            print(f"    Total Syncs: {perf['total_syncs']}")
            print(f"    Unique Sports: {perf['unique_sports']}")
            print(f"    Games: {perf['total_games']}")
            print(f"    Lines: {perf['total_lines']}")
            print(f"    Props: {perf['total_props']}")
            print(f"    Picks: {perf['total_picks']}")
            print(f"    Avg Duration: {perf['avg_sync_duration']:.2f}s")
            print(f"    Healthy: {perf['healthy_syncs']}, Unhealthy: {perf['unhealthy_syncs']}")
            print(f"    Errors: {perf['syncs_with_errors']}")
        
        # Recent sync activity
        recent = await conn.fetch("""
            SELECT * FROM sync_metadata 
            ORDER BY last_updated DESC 
            LIMIT 10
        """)
        
        print(f"\nRecent Sync Activity:")
        for sync in recent:
            print(f"  - {sync['sport_key']} ({sync['data_type']}):")
            print(f"    Last Updated: {sync['last_updated']}")
            print(f"    Duration: {sync['sync_duration_seconds']:.2f}s")
            print(f"    Data: Games({sync['games_count']}) Lines({sync['lines_count']}) Props({sync['props_count']}) Picks({sync['picks_count']})")
            print(f"    Source: {sync['source']}")
            print(f"    Health: {'Healthy' if sync['is_healthy'] else 'Unhealthy'}")
            if sync['error_message']:
                print(f"    Error: {sync['error_message']}")
        
        # Sync efficiency analysis
        efficiency_analysis = await conn.fetch("""
            SELECT 
                sport_key,
                data_type,
                sync_duration_seconds,
                games_count,
                lines_count,
                props_count,
                picks_count,
                (games_count + lines_count + props_count + picks_count) as total_records,
                CASE 
                    WHEN sync_duration_seconds > 0 THEN 
                        (games_count + lines_count + props_count + picks_count)::float / sync_duration_seconds 
                    ELSE 0 
                END as records_per_second,
                is_healthy,
                last_updated
            FROM sync_metadata
            WHERE sync_duration_seconds > 0
            ORDER BY records_per_second DESC
            LIMIT 10
        """)
        
        print(f"\nSync Efficiency Analysis (Top 10):")
        for efficiency in efficiency_analysis:
            print(f"  {efficiency['sport_key']} ({efficiency['data_type']}):")
            print(f"    Records/sec: {efficiency['records_per_second']:.2f}")
            print(f"    Total Records: {efficiency['total_records']}")
            print(f"    Duration: {efficiency['sync_duration_seconds']:.2f}s")
            print(f"    Health: {'Healthy' if efficiency['is_healthy'] else 'Unhealthy'}")
            print(f"    Last Sync: {efficiency['last_updated']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(analyze_sync_metadata())
