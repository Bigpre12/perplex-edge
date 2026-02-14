# Railway Deployment Guide
## Production Deployment for Sports Betting Platform

### 🚀 Quick Deploy Steps

1. **Push to Railway**
   ```bash
   railway login
   railway link
   railway up
   ```

2. **Set Environment Variables**
   In Railway dashboard → Settings → Variables:
   ```
   DATABASE_URL=<Railway PostgreSQL URL>
   THE_ODDS_API_KEY=<from the-odds-api.com>
   SPORTSDATA_API_KEY=<from sportsdata.io>
   ENVIRONMENT=production
   ```

3. **Configure Health Check**
   - Health check endpoint: `/health`
   - Expected response: `{"status": "healthy"}`
   - Check interval: 30 seconds

### 📊 API Keys Required

**The Odds API** (the-odds-api.com):
- Free tier: 500 requests/month
- Paid tier: $10/month for 25,000 requests
- Sign up: https://the-odds-api.com/

**SportsDataIO** (sportsdata.io):
- NBA API: $50/month
- NFL API: $50/month
- Sign up: https://sportsdata.io/

### 🔧 Production Configuration

**Procfile** (already created):
```
web: uvicorn app.main:app --host=0.0.0.0 --port=${PORT:-8001}
```

**Environment Variables**:
- `PORT`: Railway automatically sets this
- `DATABASE_URL`: Railway PostgreSQL connection string
- `THE_ODDS_API_KEY`: Your The Odds API key
- `SPORTSDATA_API_KEY`: Your SportsDataIO API key
- `ENVIRONMENT`: Set to "production"

### 🌐 Endpoints Available

**Core API**:
- `/immediate/picks` - Get calibrated picks (2-4% EV)
- `/immediate/games` - Game schedules and results
- `/immediate/user-bets` - User betting history
- `/health` - Health check endpoint

**Track Record**:
- `/track-record/track-record` - Complete transparent track record
- `/track-record/performance` - Performance metrics
- `/track-record/recent` - Recent graded picks
- `/track-record/bookmakers` - Performance by bookmaker

**Validation**:
- `/validation/picks` - Validated picks with real data
- `/validation/performance` - Model performance metrics

### 📱 Testing Production

1. **Health Check**:
   ```bash
   curl https://your-app.railway.app/health
   ```

2. **API Test**:
   ```bash
   curl https://your-app.railway.app/immediate/picks
   ```

3. **Track Record**:
   ```bash
   curl https://your-app.railway.app/track-record/track-record
   ```

### 💰 Business Metrics

**Expected Performance**:
- EV Range: 2-4% (realistic)
- Hit Rate: 52-56% (industry standard)
- CLV: +1-3% (positive closing line value)
- ROI: 2-8% (return on investment)

**Customer Pricing**:
- Discord: $20-30/month
- Whop: $25-35/month
- Premium: $50-100/month

### 🎯 Success Metrics

**Technical**:
- 99%+ uptime
- <100ms response time
- All endpoints returning 200 OK

**Business**:
- 100+ graded picks before launch
- Positive CLV demonstrated
- Transparent track record built

### 🔍 Monitoring

**Health Checks**:
- `/health` endpoint
- Railway built-in monitoring
- Error tracking in logs

**Performance**:
- Track record accuracy
- API response times
- Database connection status

### 🚨 Troubleshooting

**Common Issues**:
1. **502 Errors**: Check PORT environment variable
2. **Database Issues**: Verify DATABASE_URL format
3. **API Failures**: Check API keys are valid
4. **CORS Issues**: Update allowed origins in production

**Log Commands**:
```bash
railway logs
railway status
```

### 📈 Scaling

**Database**:
- Railway PostgreSQL scales automatically
- Connection pooling configured

**API**:
- Railway auto-scales based on traffic
- Load balancing handled automatically

**Next Steps**:
1. Deploy to Railway
2. Add real API keys
3. Start grading picks
4. Build customer base

**Your sports betting platform is production-ready! 🎉**
