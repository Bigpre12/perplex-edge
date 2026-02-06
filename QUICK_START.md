# 🚀 Quick Start Guide

Get Perplex Edge running in production in under 5 minutes.

## ⚡ One-Click Deploy (Recommended)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https%3A%2F%2Fgithub.com%2Fyour-org%2Fperplex-edge)

### Steps:
1. **Click the button** above
2. **Connect Railway** account
3. **Get API key** from [The Odds API](https://the-odds-api.com/)
4. **Set environment variables** (see below)
5. **Click Deploy** - Live in 2-5 minutes!

## 🔧 Manual Setup

### Prerequisites
- The Odds API key (required)
- Railway account (recommended) or Docker

### Step 1: Get API Keys

#### Required: The Odds API
```bash
# 1. Sign up at https://the-odds-api.com/
# 2. Get your free API key (500 requests/month)
# 3. Copy the key for step 2
```

#### Optional: Groq AI (for insights)
```bash
# 1. Sign up at https://console.groq.com/keys
# 2. Get free API key
# 3. Enable AI features later if desired
```

### Step 2: Deploy

#### Option A: Railway (Recommended)
```bash
# 1. Fork the repository
# 2. Connect to Railway
# 3. Set environment variables (see below)
# 4. Deploy automatically
```

#### Option B: Docker
```bash
# 1. Clone repository
git clone https://github.com/your-org/perplex-edge.git
cd perplex-edge

# 2. Copy environment template
cp .env.production.template .env

# 3. Edit with your API keys
nano .env

# 4. Deploy
docker-compose -f docker-compose.production.yml up -d
```

### Step 3: Configure Environment Variables

#### Required Variables
```bash
# Core Configuration
ENVIRONMENT=production
ODDS_API_KEY=your_odds_api_key_here
FRONTEND_URL=https://your-app-name.up.railway.app
CORS_ORIGINS=https://your-app-name.up.railway.app
VITE_API_BASE_URL=https://your-backend-name.up.railway.app

# Database (Railway provides automatically)
DATABASE_URL=postgresql+psycopg://user:pass@host:port/db
```

#### Optional Variables (Recommended)
```bash
# AI Features
AI_ENABLED=true
AI_API_KEY=your_groq_api_key_here

# Error Monitoring
SENTRY_DSN=your_sentry_dsn_here

# Caching
REDIS_URL=redis://host:port/db
```

### Step 4: Verify Deployment

#### Health Checks
```bash
# Backend health
curl https://your-backend-url.up.railway.app/health

# Expected response
{
  "status": "healthy",
  "timestamp": "2025-01-01T12:00:00Z",
  "version": "0.1.0"
}
```

#### Frontend Access
```bash
# Visit your app
https://your-app-name.up.railway.app

# Should see:
# - Sports betting interface
# - Live odds data
# - AI recommendations (if enabled)
```

## 🎯 Common Setup Issues

### Issue: "No API Key" Error
**Solution**: Set `ODDS_API_KEY` environment variable

### Issue: CORS Errors
**Solution**: Set `FRONTEND_URL` and `CORS_ORIGINS` correctly

### Issue: Database Connection Failed
**Solution**: Verify `DATABASE_URL` is correct and database is running

### Issue: Frontend Can't Reach Backend
**Solution**: Set `VITE_API_BASE_URL` to your backend URL

## 📱 What You Get

### Core Features
- ✅ **Live Odds** - Real-time sports betting odds
- ✅ **AI Insights** - ML-powered recommendations
- ✅ **Player Props** - Advanced player analytics
- ✅ **Injury Tracking** - Impact analysis
- ✅ **Historical Data** - Performance trends

### Sports Supported
- 🏀 **NBA** - Basketball
- 🏈 **NFL** - Football
- 🎓 **NCAAB** - College Basketball
- ⚾ **MLB** - Baseball
- 🏒 **NHL** - Hockey

### API Integrations
- **The Odds API** (required) - Live odds
- **Groq AI** (optional) - Smart insights
- **Sentry** (optional) - Error monitoring
- **Redis** (optional) - Performance caching

## 🔧 Advanced Configuration

### Custom Domain
```bash
# 1. Update environment variables
FRONTEND_URL=https://yourdomain.com
CORS_ORIGINS=https://yourdomain.com

# 2. Configure DNS
# Point your domain to Railway/deployment URL
```

### Enhanced Features
```bash
# Enable all optional features
AI_ENABLED=true
SENTRY_DSN=your_sentry_dsn
REDIS_URL=redis://host:port/db

# Additional APIs
ODDSPAPI_API_KEY=your_oddspapi_key
STATS_API_KEY=your_stats_key
INJURY_API_KEY=your_injury_key
```

### Performance Optimization
```bash
# Database optimization
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Caching
REDIS_TTL=3600
CACHE_ENABLED=true

# Rate limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=100
```

## 🆘 Need Help?

### Documentation
- **[Full Deployment Guide](DEPLOYMENT.md)** - Detailed instructions
- **[Customer Setup Guide](CUSTOMER_SETUP.md)** - Complete walkthrough
- **[API Documentation](https://your-app-url.up.railway.app/docs)** - Interactive API docs

### Support
- **Email**: support@perplex-edge.com
- **Discord**: https://discord.gg/perplex-edge
- **Issues**: https://github.com/your-org/perplex-edge/issues

### Troubleshooting
```bash
# Check logs (Railway)
# Click on your service > Logs tab

# Check logs (Docker)
docker-compose logs -f

# Health check endpoint
curl https://your-app-url.up.railway.app/health

# Database connectivity
curl https://your-app-url.up.railway.app/health/database
```

## 🎉 Success!

You now have a fully functional sports betting analytics platform running in production!

### Next Steps
1. **Explore the UI** - Check out odds and recommendations
2. **Configure Alerts** - Set up betting notifications
3. **Add More Sports** - Enable additional leagues
4. **Customize Settings** - Tailor to your preferences
5. **Upgrade Features** - Add AI insights and advanced analytics

### Performance Tips
- **Monitor API Usage** - Stay within The Odds API limits
- **Enable Caching** - Improve response times with Redis
- **Set Up Monitoring** - Track performance with Sentry
- **Regular Backups** - Protect your data

---

**🚀 Your sports betting analytics platform is ready!**

**Questions?** We're here to help at support@perplex-edge.com
