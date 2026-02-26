#!/usr/bin/env bash
# =============================================================
# Perplex Edge — Free Stack Migration Script
# Migrates from Railway to Render + Supabase + Upstash
# =============================================================

set -euo pipefail

echo "=========================================="
echo "  Perplex Edge — Free Stack Migration"
echo "=========================================="
echo ""

# --- Step 1: Supabase ---
echo "Step 1: Supabase (Database)"
echo "  1. Sign up at https://supabase.com"
echo "  2. Create a New Project"
echo "  3. Go to Project Settings > Database"
echo "  4. Copy the Connection String (URI)"
echo "  5. Set it in your .env or Render dashboard:"
echo ""
echo "     DATABASE_URL=postgresql+asyncpg://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres"
echo ""

# --- Step 2: Upstash ---
echo "Step 2: Upstash (Redis Cache)"
echo "  1. Sign up at https://upstash.com"
echo "  2. Create a new Redis database (free tier = 10k commands/day)"
echo "  3. Copy the Redis URL from the dashboard"
echo "  4. Set it in your .env or Render dashboard:"
echo ""
echo "     REDIS_URL=rediss://default:[TOKEN]@[REGION].upstash.io:6379"
echo ""

# --- Step 3: Render ---
echo "Step 3: Render (Backend Hosting)"
echo "  1. Sign up at https://render.com"
echo "  2. New > Web Service > Connect your GitHub repo"
echo "  3. Settings:"
echo "     - Root Directory: backend"
echo "     - Build Command: pip install -r requirements.txt"
echo "     - Start Command: uvicorn app.main:app --host 0.0.0.0 --port \$PORT"
echo "  4. Environment tab: Add all vars from .env"
echo "  5. Deploy"
echo ""

# --- Step 4: UptimeRobot (Keep-Alive) ---
echo "Step 4: UptimeRobot (Keep Render Alive)"
echo "  1. Sign up at https://uptimerobot.com (free)"
echo "  2. Add New Monitor > HTTP(s)"
echo "  3. URL: https://your-app.onrender.com/immediate/status"
echo "  4. Interval: 5 minutes"
echo "  5. This prevents Render free tier from sleeping"
echo ""

# --- Step 5: API Keys ---
echo "Step 5: Get Your Free API Keys"
echo "  Required (already working):"
echo "    - ESPN: No key needed ✓"
echo "    - TheSportsDB: Free key '1' already set ✓"
echo ""
echo "  Optional (sign up when ready):"
echo "    - The Odds API: https://the-odds-api.com (500 credits/mo)"
echo "    - TheRundown: https://therundown.io/api (20k pts/day)"
echo "    - BallDontLie: https://www.balldontlie.io (free forever)"
echo "    - MySportsFeeds: https://www.mysportsfeeds.com (free personal)"
echo "    - SportsGameOdds: https://sportsgameodds.com (1k objs/mo)"
echo ""

# --- Step 6: Run Migrations ---
echo "Step 6: Run Database Migrations"
echo "  After setting DATABASE_URL to Supabase, run:"
echo ""
echo "    cd backend"
echo "    alembic upgrade head"
echo ""

echo "=========================================="
echo "  Migration Complete! Final Stack:"
echo "  Frontend:  Vercel (free)"
echo "  Backend:   Render (free)"
echo "  Database:  Supabase (free 500MB)"
echo "  Cache:     Upstash (free 10k/day)"
echo "  Monitor:   UptimeRobot (free)"
echo "  Total:     \$0/month"
echo "=========================================="
