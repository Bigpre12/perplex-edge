from fastapi import APIRouter, HTTPException, Depends
import os
from utils.supabase_proxy import supabase

# Define the Master Admin Emails who have access to this portal
AUTHORIZED_ADMINS = ["preio@example.com", "oracle@perplexedge.com"]

def verify_admin(user_email: str):
    if user_email not in AUTHORIZED_ADMINS:
        raise HTTPException(status_code=403, detail="You do not have Command Center clearance.")
    return True

@router.get("/dashboard-stats")
async def get_dashboard_stats(email: str):
    """Returns overarching SaaS metrics: Total Users, Pro Users, Monthly Revenue Estimate"""
    verify_admin(email)
    
    try:
        # Fetch all authenticated users via the Supabase Admin API
        users_response = supabase.auth.admin.list_users()
        all_users = users_response.users
        
        total_users = len(all_users)
        pro_users = 0
        
        for u in all_users:
            if u.app_metadata and u.app_metadata.get("tier") == "pro":
                pro_users += 1
                
        # Calculate rough MRR based on a $49/mo price point
        mrr = pro_users * 49
        
        return {
            "total_users": total_users,
            "pro_subscriptions": pro_users,
            "estimated_mrr": f"${mrr}",
            "system_health": "Optimal",
            "active_services": ["Odds API Sync", "AI Chatbot", "Web Push", "Email Cron"]
        }
        
    except Exception as e:
        print(f"Admin Error: {e}")
        # Return mock data for local development if the Service Key isn't populated
        return {
            "total_users": 142,
            "pro_subscriptions": 28,
            "estimated_mrr": "$1,372",
            "system_health": "Mock Mode",
            "active_services": ["Odds API Sync", "AI Chatbot", "Web Push", "Email Cron"]
        }
