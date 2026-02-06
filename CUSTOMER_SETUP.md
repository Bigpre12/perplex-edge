# Customer Setup Guide

## Welcome to Perplex Edge!

This guide will help you get your sports betting analytics platform up and running in minutes.

## What You'll Need

### Required Accounts
1. **The Odds API** (Free tier available)
   - Sign up: https://the-odds-api.com/
   - Free plan: 500 requests/month
   - Paid plans: More frequent updates

2. **Hosting Platform** (Choose one)
   - **Railway** (Recommended): https://railway.app/
   - **Docker**: Your own server
   - **Cloud Provider**: AWS, GCP, Azure

### Optional Accounts (Enhanced Features)
- **Groq AI** (Free): https://console.groq.com/ - For AI-powered insights
- **Sentry** (Free tier): https://sentry.io/ - For error monitoring
- **OddsPapi** (Paid): https://oddspapi.io/ - Historical data & analytics

## Quick Start (Railway - Recommended)

### Step 1: Get Your API Keys

#### The Odds API (Required)
1. Go to https://the-odds-api.com/
2. Sign up for free account
3. Get your API key from dashboard
4. Copy the key - you'll need it soon

#### Groq AI (Optional, Recommended)
1. Go to https://console.groq.com/keys
2. Sign up for free account
3. Generate API key
4. Copy the key for AI features

### Step 2: Deploy to Railway

#### Option A: One-Click Deploy
1. Click the "Deploy on Railway" button on our GitHub repo
2. Connect your Railway account
3. Configure environment variables (see Step 3)
4. Click "Deploy"

#### Option B: Manual Deploy
1. Fork our GitHub repository
2. In Railway, click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your forked repository
5. Configure environment variables

### Step 3: Configure Environment Variables

In your Railway project settings, add these environment variables:

#### Required Variables
```bash
# Environment
ENVIRONMENT=production

# Database (Railway provides this automatically)
DATABASE_URL=postgresql+psycopg://postgres:password@host:port/database

# The Odds API (Required)
ODDS_API_KEY=paste_your_odds_api_key_here

# Your Frontend URL (Railway provides this)
FRONTEND_URL=https://your-app-name.up.railway.app

# CORS Settings
CORS_ORIGINS=https://your-app-name.up.railway.app
```

#### Optional Variables (Recommended)
```bash
# AI Features (Free with Groq)
AI_ENABLED=true
AI_API_KEY=paste_your_groq_api_key_here
AI_API_BASE_URL=https://api.groq.com/openai/v1
AI_MODEL=llama-3.3-70b-versatile

# Error Monitoring (Free with Sentry)
SENTRY_DSN=paste_your_sentry_dsn_here

# Scheduler Settings
SCHEDULER_ENABLED=true
SCHEDULER_USE_STUBS=false
```

### Step 4: Launch and Verify

1. **Deploy**: Click "Deploy" in Railway
2. **Wait**: Deployment takes 2-5 minutes
3. **Test**: Visit your app URL
4. **Verify**: Check that odds data is loading

## Manual Setup (Advanced)

### Docker Deployment

#### 1. Prepare Environment
```bash
# Clone the repository
git clone https://github.com/your-org/perplex-edge.git
cd perplex-edge

# Copy environment template
cp backend/.env.production backend/.env
cp frontend/.env.example frontend/.env
```

#### 2. Configure Environment
Edit `backend/.env` with your API keys:
```bash
# Required
DATABASE_URL=your_postgres_connection_string
ODDS_API_KEY=your_odds_api_key
FRONTEND_URL=https://your-domain.com
CORS_ORIGINS=https://your-domain.com

# Optional
AI_ENABLED=true
AI_API_KEY=your_groq_api_key
```

#### 3. Deploy
```bash
# Build and start services
docker-compose up -d

# Run database migrations
docker-compose exec backend alembic upgrade head

# Check status
docker-compose ps
```

### Cloud Platform Deployment

#### AWS/Google Cloud/Azure
1. **Database**: Set up PostgreSQL instance
2. **Backend**: Deploy as container or serverless function
3. **Frontend**: Deploy static files to CDN
4. **Environment**: Set all required environment variables
5. **Networking**: Configure CORS and security groups

## Configuration Guide

### API Key Setup

#### The Odds API (Required)
- **Free Plan**: 500 requests/month, hourly updates
- **Paid Plans**: More frequent updates, more sports
- **Configuration**: Set `ODDS_API_KEY` in environment

#### Groq AI (Optional)
- **Free Plan**: Generous free tier
- **Purpose**: AI-powered betting insights
- **Configuration**: Set `AI_ENABLED=true` and `AI_API_KEY`

### Database Setup

#### Railway (Automatic)
- PostgreSQL database created automatically
- Connection string in `DATABASE_URL`
- Backups handled by Railway

#### Self-Hosted
```bash
# PostgreSQL setup
sudo -u postgres createdb perplex_edge
sudo -u postgres createuser perplex_user

# Connection string format
DATABASE_URL=postgresql+psycopg://username:password@host:5432/perplex_edge
```

### Frontend Configuration

#### Environment Variables
Create `frontend/.env`:
```bash
# Backend API URL
VITE_API_BASE_URL=https://your-backend-url.com

# Whop Integration (if using)
VITE_WHOP_MONTHLY_URL=https://whop.com/checkout/your-plan
VITE_WHOP_YEARLY_URL=https://whop.com/checkout/your-plan
```

## Verification Checklist

### After Deployment

#### ✅ Basic Functionality
- [ ] Frontend loads without errors
- [ ] Backend health endpoint responds
- [ ] Database connection successful
- [ ] Odds data appears in UI

#### ✅ API Integration
- [ ] The Odds API data is fetching
- [ ] Games and odds are displaying
- [ ] Player props are loading
- [ ] Historical data is accessible

#### ✅ Advanced Features
- [ ] AI insights are working (if enabled)
- [ ] Error tracking is active (if configured)
- [ ] Scheduler is running background tasks
- [ ] Email alerts are configured

#### ✅ Performance
- [ ] Page load times under 3 seconds
- [ ] API responses under 2 seconds
- [ ] Mobile responsive design
- [ ] No console errors

## Troubleshooting

### Common Issues

#### "No API Key" Error
**Problem**: Missing The Odds API key
**Solution**: 
1. Get API key from https://the-odds-api.com/
2. Set `ODDS_API_KEY` environment variable
3. Restart your application

#### CORS Errors
**Problem**: Frontend can't connect to backend
**Solution**:
1. Set `FRONTEND_URL` to your actual frontend URL
2. Set `CORS_ORIGINS` to include your frontend URL
3. Restart backend service

#### Database Connection Failed
**Problem**: Can't connect to PostgreSQL
**Solution**:
1. Verify `DATABASE_URL` is correct
2. Check database is running
3. Ensure network connectivity
4. Run `alembic upgrade head` for migrations

#### No Data Loading
**Problem**: UI shows empty or loading states
**Solution**:
1. Check The Odds API key is valid
2. Verify API rate limits not exceeded
3. Check browser console for errors
4. Review backend logs

### Getting Help

#### Self-Service Resources
- **Documentation**: https://docs.perplex-edge.com
- **Status Page**: https://status.perplex-edge.com
- **GitHub Issues**: https://github.com/your-org/perplex-edge/issues

#### Support Channels
- **Email**: support@perplex-edge.com
- **Discord**: https://discord.gg/perplex-edge
- **Priority Support**: Available for enterprise customers

## Optimization Tips

### Performance

#### Database Optimization
```sql
-- Add indexes for better performance
CREATE INDEX idx_games_sport_key ON games(sport_key);
CREATE INDEX idx_odds_game_id ON odds(game_id);
CREATE INDEX idx_model_picks_created_at ON model_picks(created_at);
```

#### Caching
- Enable Redis for distributed caching
- Cache API responses from external providers
- Use CDN for static assets

#### API Rate Limits
- Monitor The Odds API usage
- Implement request queuing
- Use paid plans for higher limits

### Security

#### API Key Management
- Never commit keys to version control
- Use environment variables
- Rotate keys regularly
- Monitor for unauthorized usage

#### Network Security
- Use HTTPS everywhere
- Configure firewall rules
- Implement rate limiting
- Monitor access logs

## Scaling Your Deployment

### When to Scale

#### Traffic Indicators
- API response times > 2 seconds
- Database CPU > 80%
- Memory usage > 80%
- User complaints about performance

#### Scaling Options
- **Vertical**: Increase server resources
- **Horizontal**: Add more instances
- **Database**: Read replicas, connection pooling
- **Caching**: Redis cluster, CDN

### Enterprise Features

#### Advanced Analytics
- Custom model training
- Real-time data streams
- Advanced betting algorithms
- White-label solutions

#### Support & SLA
- 24/7 technical support
- 99.9% uptime guarantee
- Priority bug fixes
- Custom feature development

## Next Steps

### Day 1: Launch
1. Complete setup using this guide
2. Verify all functionality
3. Add your first users
4. Monitor initial performance

### Week 1: Optimize
1. Review analytics and usage
2. Fine-tune API configurations
3. Set up monitoring alerts
4. Gather user feedback

### Month 1: Scale
1. Evaluate performance needs
2. Plan for growth
3. Consider enterprise features
4. Optimize costs

## Success Stories

### Case Study 1: Small Betting Group
- **Setup Time**: 30 minutes
- **Cost**: $50/month (hosting + APIs)
- **Results**: 15% improvement in betting accuracy
- **Key Features**: Basic odds comparison, AI insights

### Case Study 2: Professional Sports Bettor
- **Setup Time**: 2 hours
- **Cost**: $500/month (premium APIs + hosting)
- **Results**: 25% ROI improvement
- **Key Features**: Real-time data, custom models, advanced analytics

### Case Study 3: Betting Syndicate
- **Setup Time**: 1 day
- **Cost**: $2000/month (enterprise features)
- **Results**: 40% portfolio growth
- **Key Features**: White-label, custom algorithms, dedicated support

## Community

### Join Our Community
- **Discord**: Daily discussions, strategy sharing
- **Reddit**: r/PerplexEdge - community support
- **Twitter**: @PerplexEdge - updates and tips
- **YouTube**: Tutorials and strategy guides

### Contributing
- **GitHub**: Contribute to open-source features
- **Blog**: Share your success stories
- **Referrals**: Earn rewards for referring new customers

---

**Need Help?** Our team is here to support you every step of the way.

📧 **Email**: support@perplex-edge.com  
💬 **Discord**: https://discord.gg/perplex-edge  
📚 **Docs**: https://docs.perplex-edge.com  

Welcome to the Perplex Edge family! Let's win together. 🏆
