#!/usr/bin/env python3
"""
USERS ANALYSIS - Comprehensive analysis of the users table
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
import json

async def analyze_users():
    """Analyze the users table structure and data"""
    
    # Database connection
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found")
        return
    
    try:
        conn = await asyncpg.connect(db_url)
        print("Connected to database")
        
        # Get all users data
        users = await conn.fetch("""
            SELECT * FROM users 
            ORDER BY id
        """)
        
        print("USERS TABLE ANALYSIS")
        print("="*80)
        
        print(f"\nTotal Users: {len(users)}")
        
        # Analyze by plan
        by_plan = await conn.fetch("""
            SELECT 
                plan,
                COUNT(*) as total_users,
                COUNT(CASE WHEN trial_ends_at > NOW() THEN 1 END) as trial_users,
                COUNT(CASE WHEN trial_ends_at <= NOW() THEN 1 END) as expired_trials,
                COUNT(CASE WHEN whoop_membership_id IS NOT NULL THEN 1 END) as whoop_members,
                COUNT(CASE WHEN whoop_membership_id IS NULL THEN 1 END) as non_whoop_members,
                COUNT(CASE WHEN props_viewed_today > 0 THEN 1 END) as active_today,
                AVG(props_viewed_today) as avg_props_viewed,
                MIN(created_at) as first_user,
                MAX(created_at) as last_user,
                AVG(EXTRACT(DAY FROM (NOW() - created_at))) as avg_days_active
            FROM users
            GROUP BY plan
            ORDER BY total_users DESC
        """)
        
        print(f"\nUsers by Plan:")
        for plan in by_plan:
            print(f"  {plan['plan']}:")
            print(f"    Total Users: {plan['total_users']}")
            print(f"    Trial Users: {plan['trial_users']}")
            print(f"    Expired Trials: {plan['expired_trials']}")
            print(f"    WHOOP Members: {plan['whoop_members']}")
            print(f"    Non-WHOOP Members: {plan['non_whoop_members']}")
            print(f"    Active Today: {plan['active_today']}")
            print(f"    Avg Props Viewed: {plan['avg_props_viewed']:.1f}")
            print(f"    Period: {plan['first_user']} to {plan['last_user']}")
            print(f"    Avg Days Active: {plan['avg_days_active']:.1f}")
        
        # Analyze by trial status
        trial_analysis = await conn.fetch("""
            SELECT 
                CASE 
                    WHEN trial_ends_at > NOW() THEN 'Active Trial'
                    WHEN trial_ends_at <= NOW() THEN 'Expired Trial'
                    WHEN trial_ends_at IS NULL THEN 'No Trial'
                    ELSE 'Unknown'
                END as trial_status,
                COUNT(*) as total_users,
                COUNT(DISTINCT plan) as unique_plans,
                COUNT(CASE WHEN whoop_membership_id IS NOT NULL THEN 1 END) as whoop_members,
                COUNT(CASE WHEN props_viewed_today > 0 THEN 1 END) as active_today,
                AVG(props_viewed_today) as avg_props_viewed,
                MIN(created_at) as first_user,
                MAX(created_at) as last_user
            FROM users
            GROUP BY trial_status
            ORDER BY total_users DESC
        """)
        
        print(f"\nUsers by Trial Status:")
        for trial in trial_analysis:
            print(f"  {trial['trial_status']}:")
            print(f"    Total Users: {trial['total_users']}")
            print(f"    Unique Plans: {trial['unique_plans']}")
            print(f"    WHOOP Members: {trial['whoop_members']}")
            print(f"    Active Today: {trial['active_today']}")
            print(f"    Avg Props Viewed: {trial['avg_props_viewed']:.1f}")
            print(f"    Period: {trial['first_user']} to {trial['last_user']}")
        
        # Analyze by WHOOP membership
        whoop_analysis = await conn.fetch("""
            SELECT 
                CASE 
                    WHEN whoop_membership_id IS NOT NULL THEN 'WHOOP Member'
                    ELSE 'Non-WHOOP'
                END as whoop_status,
                COUNT(*) as total_users,
                COUNT(DISTINCT plan) as unique_plans,
                COUNT(CASE WHEN trial_ends_at > NOW() THEN 1 END) as trial_users,
                COUNT(CASE WHEN props_viewed_today > 0 THEN 1 END) as active_today,
                AVG(props_viewed_today) as avg_props_viewed,
                MIN(created_at) as first_user,
                MAX(created_at) as last_user
            FROM users
            GROUP BY whoop_status
            ORDER BY total_users DESC
        """)
        
        print(f"\nUsers by WHOOP Status:")
        for whoop in whoop_analysis:
            print(f"  {whoop['whoop_status']}:")
            print(f"    Total Users: {whoop['total_users']}")
            print(f"    Unique Plans: {whoop['unique_plans']}")
            print(f"    Trial Users: {whoop['trial_users']}")
            print(f"    Active Today: {whoop['active_today']}")
            print(f"    Avg Props Viewed: {whoop['avg_props_viewed']:.1f}")
            print(f"    Period: {whoop['first_user']} to {whoop['last_user']}")
        
        # Analyze by activity level
        activity_analysis = await conn.fetch("""
            SELECT 
                CASE 
                    WHEN props_viewed_today = 0 THEN 'Inactive'
                    WHEN props_viewed_today BETWEEN 1 AND 5 THEN 'Low Activity'
                    WHEN props_viewed_today BETWEEN 6 AND 15 THEN 'Medium Activity'
                    WHEN props_viewed_today BETWEEN 16 AND 50 THEN 'High Activity'
                    ELSE 'Very High Activity'
                END as activity_level,
                COUNT(*) as total_users,
                COUNT(DISTINCT plan) as unique_plans,
                COUNT(CASE WHEN whoop_membership_id IS NOT NULL THEN 1 END) as whoop_members,
                COUNT(CASE WHEN trial_ends_at > NOW() THEN 1 END) as trial_users,
                AVG(props_viewed_today) as avg_props_viewed,
                MIN(created_at) as first_user,
                MAX(created_at) as last_user
            FROM users
            GROUP BY activity_level
            ORDER BY avg_props_viewed DESC
        """)
        
        print(f"\nUsers by Activity Level:")
        for activity in activity_analysis:
            print(f"  {activity['activity_level']}:")
            print(f"    Total Users: {activity['total_users']}")
            print(f"    Unique Plans: {activity['unique_plans']}")
            print(f"    WHOOP Members: {activity['whoop_members']}")
            print(f"    Trial Users: {activity['trial_users']}")
            print(f"    Avg Props Viewed: {activity['avg_props_viewed']:.1f}")
            print(f"    Period: {activity['first_user']} to {activity['last_user']}")
        
        # Analyze creation patterns
        creation_analysis = await conn.fetch("""
            SELECT 
                DATE(created_at) as creation_date,
                COUNT(*) as users_created,
                COUNT(DISTINCT plan) as unique_plans,
                COUNT(CASE WHEN trial_ends_at > NOW() THEN 1 END) as trial_users,
                COUNT(CASE WHEN whoop_membership_id IS NOT NULL THEN 1 END) as whoop_members,
                COUNT(CASE WHEN props_viewed_today > 0 THEN 1 END) as active_today,
                AVG(props_viewed_today) as avg_props_viewed
            FROM users
            GROUP BY DATE(created_at)
            ORDER BY creation_date DESC
            LIMIT 10
        """)
        
        print(f"\nUser Creation Analysis:")
        for creation in creation_analysis:
            print(f"  {creation['creation_date']}:")
            print(f"    Users Created: {creation['users_created']}")
            print(f"    Unique Plans: {creation['unique_plans']}")
            print(f"    Trial Users: {creation['trial_users']}")
            print(f"    WHOOP Members: {creation['whoop_members']}")
            print(f"    Active Today: {creation['active_today']}")
            print(f"    Avg Props Viewed: {creation['avg_props_viewed']:.1f}")
        
        # Analyze email domains
        email_analysis = await conn.fetch("""
            SELECT 
                SPLIT_PART(email, '@', 2) as email_domain,
                COUNT(*) as total_users,
                COUNT(DISTINCT plan) as unique_plans,
                COUNT(CASE WHEN whoop_membership_id IS NOT NULL THEN 1 END) as whoop_members,
                COUNT(CASE WHEN trial_ends_at > NOW() THEN 1 END) as trial_users,
                COUNT(CASE WHEN props_viewed_today > 0 THEN 1 END) as active_today,
                MIN(created_at) as first_user,
                MAX(created_at) as last_user
            FROM users
            WHERE email IS NOT NULL
            GROUP BY email_domain
            HAVING COUNT(*) > 1
            ORDER BY total_users DESC
            LIMIT 10
        """)
        
        print(f"\nEmail Domain Analysis:")
        for email in email_analysis:
            print(f"  {email['email_domain']}:")
            print(f"    Total Users: {email['total_users']}")
            print(f"    Unique Plans: {email['unique_plans']}")
            print(f"    WHOOP Members: {email['whoop_members']}")
            print(f"    Trial Users: {email['trial_users']}")
            print(f"    Active Today: {email['active_today']}")
            print(f"    Period: {email['first_user']} to {email['last_user']}")
        
        # Analyze props reset patterns
        reset_analysis = await conn.fetch("""
            SELECT 
                CASE 
                    WHEN props_reset_date IS NULL THEN 'Never Reset'
                    WHEN props_reset_date >= NOW() - INTERVAL '7 days' THEN 'Last 7 Days'
                    WHEN props_reset_date >= NOW() - INTERVAL '30 days' THEN 'Last 30 Days'
                    WHEN props_reset_date >= NOW() - INTERVAL '90 days' THEN 'Last 90 Days'
                    ELSE 'Older than 90 Days'
                END as reset_category,
                COUNT(*) as total_users,
                COUNT(DISTINCT plan) as unique_plans,
                COUNT(CASE WHEN whoop_membership_id IS NOT NULL THEN 1 END) as whoop_members,
                COUNT(CASE WHEN trial_ends_at > NOW() THEN 1 END) as trial_users,
                COUNT(CASE WHEN props_viewed_today > 0 THEN 1 END) as active_today,
                AVG(props_viewed_today) as avg_props_viewed
            FROM users
            GROUP BY reset_category
            ORDER BY total_users DESC
        """)
        
        print(f"\nProps Reset Analysis:")
        for reset in reset_analysis:
            print(f"  {reset['reset_category']}:")
            print(f"    Total Users: {reset['total_users']}")
            print(f"    Unique Plans: {reset['unique_plans']}")
            print(f"    WHOOP Members: {reset['whoop_members']}")
            print(f"    Trial Users: {reset['trial_users']}")
            print(f"    Active Today: {reset['active_today']}")
            print(f"    Avg Props Viewed: {reset['avg_props_viewed']:.1f}")
        
        # Recent users
        recent = await conn.fetch("""
            SELECT * FROM users 
            ORDER BY created_at DESC, updated_at DESC 
            LIMIT 5
        """)
        
        print(f"\nRecent Users:")
        for user in recent:
            print(f"  - {user['first_name']} {user['last_name']} ({user['email']})")
            print(f"    Plan: {user['plan']}")
            print(f"    Trial Ends: {user['trial_ends_at']}")
            print(f"    WHOOP Member: {'Yes' if user['whoop_membership_id'] else 'No'}")
            print(f"    Props Viewed Today: {user['props_viewed_today']}")
            print(f"    Props Reset: {user['props_reset_date']}")
            print(f"    Created: {user['created_at']}")
            print(f"    Updated: {user['updated_at']}")
        
        # Users by ID range
        id_analysis = await conn.fetch("""
            SELECT 
                MIN(id) as min_id,
                MAX(id) as max_id,
                COUNT(*) as total_users,
                MAX(id) - MIN(id) + 1 as id_range,
                ROUND(COUNT(*) * 100.0 / (MAX(id) - MIN(id) + 1), 2) as id_density,
                COUNT(DISTINCT plan) as unique_plans
            FROM users
        """)
        
        print(f"\nID Range Analysis:")
        for analysis in id_analysis:
            print(f"  ID Range: {analysis['min_id']} to {analysis['max_id']}")
            print(f"  Total Users: {analysis['total_users']}")
            print(f"  Range Size: {analysis['id_range']}")
            print(f"  ID Density: {analysis['id_density']:.2f}%")
            print(f"  Unique Plans: {analysis['unique_plans']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(analyze_users())
