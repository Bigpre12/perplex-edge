# Railway Deployment Instructions
## 🚀 Deploy Your Sports Betting Platform to Production

### ⚠️ PowerShell Execution Policy Fix
First, you need to enable script execution in PowerShell:

```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 📋 Step-by-Step Deployment

#### 1. Install Railway CLI
```bash
npm install -g @railway/cli
```

#### 2. Login to Railway
```bash
railway login
```
This will open a browser for authentication.

#### 3. Link Your Project
```bash
cd c:\Users\preio\preio\perplex-edge
railway link
```
This connects your local repo to Railway.

#### 4. Deploy to Railway
```bash
railway up
```
This builds and deploys your application.

#### 5. Set Environment Variables
```bash
# Get your Railway PostgreSQL URL from Railway dashboard
railway variables set DATABASE_URL="postgresql://user:password@host:port/database"

# Set your API keys
railway variables set THE_ODDS_API_KEY="your_odds_api_key"
railway variables set SPORTSDATA_API_KEY="your_sportsdata_api_key"

# Set production environment
railway variables set ENVIRONMENT="production"
```

#### 6. Verify Deployment
```bash
# Check deployment status
railway status

# View logs
railway logs

# Test your live endpoints
curl https://your-app-name.railway.app/health
curl https://your-app-name.railway.app/immediate/picks
curl https://your-app-name.railway.app/track-record/track-record
```

### 🔧 Environment Variables Details

**Required Variables:**
- `DATABASE_URL`: Railway PostgreSQL connection string
- `THE_ODDS_API_KEY`: Get from https://the-odds-api.com/
- `SPORTSDATA_API_KEY`: Get from https://sportsdata.io/
- `ENVIRONMENT`: Set to "production"

**Getting Database URL:**
1. Go to Railway dashboard
2. Click on your PostgreSQL service
3. Copy the connection string
4. Set as DATABASE_URL variable

### 📊 Testing Your Deployment

#### Health Check
```bash
curl https://your-app-name.railway.app/health
# Expected: {"status": "healthy", "timestamp": "..."}
```

#### Picks Endpoint
```bash
curl https://your-app-name.railway.app/immediate/picks
# Expected: 10 picks with 2-4% EV
```

#### Track Record
```bash
curl https://your-app-name.railway.app/track-record/track-record
# Expected: Transparent performance data
```

### 🚀 Railway Dashboard Setup

1. **Health Check Configuration**
   - Path: `/health`
   - Expected: `{"status": "healthy"}`
   - Interval: 30 seconds

2. **Domain Configuration**
   - Your app will be available at: `https://your-app-name.railway.app`
   - You can add a custom domain in Railway settings

3. **Monitoring**
   - Railway provides built-in monitoring
   - Check logs with `railway logs`
   - Monitor response times and uptime

### 💰 Production Checklist

#### Before Going Live:
- [ ] All API keys configured
- [ ] Database connection working
- [ ] Health check passing
- [ ] Track record building
- [ ] Customer pricing set

#### After Deployment:
- [ ] Monitor error logs
- [ ] Check response times
- [ ] Verify track record accuracy
- [ ] Test customer integrations

### 🎯 Success Metrics

**Technical:**
- 99%+ uptime
- <100ms response times
- All endpoints returning 200 OK

**Business:**
- 100+ graded picks
- Positive CLV demonstrated
- Customer sign-ups working

### 🚨 Troubleshooting

**Common Issues:**
1. **Build Failures**: Check requirements.txt and dependencies
2. **Database Errors**: Verify DATABASE_URL format
3. **API Failures**: Check API keys are valid
4. **CORS Issues**: Update allowed origins

**Debug Commands:**
```bash
railway logs --tail
railway status
railway restart
```

### 🎉 Launch Your Platform!

Once deployed, your sports betting platform will be:
- ✅ Live on Railway
- ✅ Serving real picks with 2-4% EV
- ✅ Building transparent track record
- ✅ Ready for paying customers

**Your sports betting platform is production-ready! 🚀**

Deploy now and start your journey to building a successful sports betting business!
