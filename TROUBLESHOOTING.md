# 🔧 Troubleshooting Guide

Common issues and solutions for Perplex Edge deployment and operation.

## 🚨 Quick Fixes

### Most Common Issues

#### 1. "No API Key" Error
**Problem**: Missing or invalid The Odds API key
```bash
# Error message
"ODDS_API_KEY is required but not set"
```

**Solution**:
```bash
# 1. Get API key from https://the-odds-api.com/
# 2. Set environment variable
export ODDS_API_KEY=your_actual_api_key_here

# 3. Restart service
docker-compose restart backend
# or redeploy on Railway
```

#### 2. CORS Errors
**Problem**: Frontend can't connect to backend
```bash
# Error message
"Access-Control-Allow-Origin" header missing
```

**Solution**:
```bash
# Set correct frontend URL
export FRONTEND_URL=https://your-app-name.up.railway.app
export CORS_ORIGINS=https://your-app-name.up.railway.app

# Restart backend
docker-compose restart backend
```

#### 3. Database Connection Failed
**Problem**: Can't connect to PostgreSQL
```bash
# Error message
"Could not connect to database"
```

**Solution**:
```bash
# Check database URL format
export DATABASE_URL=postgresql+psycopg://user:password@host:5432/database

# Verify database is running
docker-compose ps db

# Check database logs
docker-compose logs db
```

#### 4. Frontend Loading Issues
**Problem**: Frontend shows blank page or errors
```bash
# Error message
"Cannot connect to API"
```

**Solution**:
```bash
# Check frontend API URL
export VITE_API_BASE_URL=https://your-backend-name.up.railway.app

# Rebuild frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

## 🔍 Diagnostic Commands

### Health Checks
```bash
# Backend health
curl https://your-app-url.up.railway.app/health

# Database health
curl https://your-app-url.up.railway.app/health/database

# Full system status
curl https://your-app-url.up.railway.app/health
```

### Log Analysis
```bash
# Railway: Check service logs in dashboard

# Docker: View all logs
docker-compose logs -f

# Specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Database Diagnostics
```bash
# Connect to database
docker-compose exec db psql -U postgres -d perplex

# Check tables
\dt

# Check recent data
SELECT COUNT(*) FROM games;
SELECT COUNT(*) FROM odds;
SELECT created_at FROM model_picks ORDER BY created_at DESC LIMIT 5;
```

## 🏗️ Environment Issues

### Development vs Production

#### Mixed Environment Configuration
**Problem**: Development settings in production
```bash
# Symptoms
- Localhost URLs in production
- Debug endpoints exposed
- Development database URLs
```

**Solution**:
```bash
# Ensure production environment
export ENVIRONMENT=production

# Remove development origins
unset ALLOW_DEV_ORIGINS_IN_PROD

# Validate configuration
curl https://your-app-url.up.railway.app/health | jq .environment
```

#### Environment Variable Validation
**Problem**: Missing required variables
```bash
# Check all required variables
echo "DATABASE_URL: $DATABASE_URL"
echo "ODDS_API_KEY: $ODDS_API_KEY"
echo "FRONTEND_URL: $FRONTEND_URL"
echo "CORS_ORIGINS: $CORS_ORIGINS"
```

**Solution**: Use production template
```bash
# Copy template
cp .env.production.template .env

# Fill in all required values
nano .env
```

## 🚀 Deployment Issues

### Railway Deployment

#### Build Failures
**Problem**: Docker build fails on Railway
```bash
# Symptoms
- Build timeout
- Dependency installation failed
- Compilation errors
```

**Solution**:
```bash
# 1. Check Dockerfile syntax
docker build -t test ./backend

# 2. Verify requirements.txt
pip install -r requirements.txt --dry-run

# 3. Check for large files
du -sh . | grep -E "^[0-9]+M|[0-9]+G"

# 4. Optimize .dockerignore
echo "*.pyc" >> .dockerignore
echo "__pycache__" >> .dockerignore
echo ".git" >> .dockerignore
```

#### Runtime Errors
**Problem**: Application crashes on startup
```bash
# Symptoms
- 502 Bad Gateway
- Service restarts repeatedly
- Health checks failing
```

**Solution**:
```bash
# 1. Check environment variables
railway variables list

# 2. View build logs
railway logs

# 3. Check database connectivity
railway run bash
curl http://localhost:8000/health
```

### Docker Deployment

#### Container Issues
**Problem**: Containers won't start or crash
```bash
# Symptoms
- Exit code 1
- Port conflicts
- Volume mounting issues
```

**Solution**:
```bash
# 1. Check container status
docker-compose ps

# 2. Inspect failed container
docker-compose logs backend

# 3. Check port conflicts
netstat -tulpn | grep :8000

# 4. Verify volumes
docker volume ls
```

#### Network Issues
**Problem**: Services can't communicate
```bash
# Symptoms
- Connection refused errors
- DNS resolution failures
- Network timeout
```

**Solution**:
```bash
# 1. Check network configuration
docker network ls
docker network inspect perplex_network_prod

# 2. Test connectivity
docker-compose exec backend ping db
docker-compose exec frontend ping backend

# 3. Rebuild network
docker-compose down
docker network prune
docker-compose up -d
```

## 📊 Performance Issues

### Slow Response Times
**Problem**: API requests taking too long
```bash
# Symptoms
- Requests > 5 seconds
- Database timeouts
- Memory usage high
```

**Solution**:
```bash
# 1. Check database performance
docker-compose exec db psql -U postgres -d perplex -c "
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC LIMIT 10;
"

# 2. Enable caching
export REDIS_URL=redis://redis:6379/0
docker-compose restart backend

# 3. Monitor resources
docker stats
```

### Memory Issues
**Problem**: Out of memory errors
```bash
# Symptoms
- OOM killer events
- Container crashes
- Swap usage high
```

**Solution**:
```bash
# 1. Check memory usage
docker stats --no-stream

# 2. Limit container memory
# Update docker-compose.yml
services:
  backend:
    mem_limit: 1g
    memswap_limit: 1g

# 3. Optimize application
# Check for memory leaks in Python code
```

## 🔌 API Integration Issues

### The Odds API
**Problem**: API rate limiting or errors
```bash
# Symptoms
- 429 Too Many Requests
- Invalid API key errors
- Data not updating
```

**Solution**:
```bash
# 1. Check API key validity
curl -H "Authorization: Bearer $ODDS_API_KEY" \
     https://api.the-odds-api.com/v4/sports

# 2. Monitor usage
# Check Railway logs for API calls

# 3. Adjust rate limiting
export SCHED_ODDS_INTERVAL_MIN=120  # Increase interval
```

### Groq AI API
**Problem**: AI features not working
```bash
# Symptoms
- AI insights missing
- Model errors
- Timeout issues
```

**Solution**:
```bash
# 1. Test API key
curl -H "Authorization: Bearer $AI_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": "Hello"}]}' \
     https://api.groq.com/openai/v1/chat/completions

# 2. Check configuration
export AI_ENABLED=true
export AI_API_KEY=your_valid_key
export AI_TIMEOUT_SECONDS=60

# 3. Restart service
docker-compose restart backend
```

## 🗄️ Database Issues

### Migration Problems
**Problem**: Database schema out of sync
```bash
# Symptoms
- Table doesn't exist errors
- Column missing errors
- Data type mismatches
```

**Solution**:
```bash
# 1. Check migration status
docker-compose exec backend alembic current

# 2. Run missing migrations
docker-compose exec backend alembic upgrade head

# 3. Reset if needed (WARNING: destroys data)
docker-compose exec backend alembic downgrade base
docker-compose exec backend alembic upgrade head
```

### Data Corruption
**Problem**: Bad data in database
```bash
# Symptoms
- Impossible odds values
- Invalid dates
- Duplicate records
```

**Solution**:
```bash
# 1. Identify bad data
docker-compose exec db psql -U postgres -d perplex -c "
SELECT COUNT(*) FROM model_picks WHERE odds < -10000 OR odds > 10000;
"

# 2. Clean bad data
docker-compose exec db psql -U postgres -d perplex -c "
DELETE FROM model_picks WHERE odds < -10000 OR odds > 10000;
"

# 3. Add validation
# Update application code to validate inputs
```

## 🔒 Security Issues

### API Key Exposure
**Problem**: API keys in logs or code
```bash
# Symptoms
- API keys visible in logs
- Keys committed to git
- Keys in frontend code
```

**Solution**:
```bash
# 1. Check for exposed keys
grep -r "sk_" . --exclude-dir=node_modules
grep -r "gsk_" . --exclude-dir=node_modules

# 2. Rotate exposed keys
# Get new keys from API providers

# 3. Update environment variables
export ODDS_API_KEY=new_key_here
export AI_API_KEY=new_ai_key_here

# 4. Restart services
docker-compose restart
```

### CORS Misconfiguration
**Problem**: Too permissive CORS settings
```bash
# Symptoms
- Wildcard CORS in production
- Development origins in production
- Security warnings
```

**Solution**:
```bash
# 1. Check current CORS settings
curl -H "Origin: https://evil.com" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     https://your-app-url.up.railway.app/endpoint

# 2. Fix CORS configuration
export CORS_ORIGINS=https://your-domain.com
unset ALLOW_DEV_ORIGINS_IN_PROD

# 3. Restart backend
docker-compose restart backend
```

## 📱 Frontend Issues

### Build Failures
**Problem**: Frontend won't compile
```bash
# Symptoms
- TypeScript errors
- Missing dependencies
- Build timeout
```

**Solution**:
```bash
# 1. Check TypeScript errors
cd frontend
npm run build

# 2. Install missing dependencies
npm install

# 3. Clear cache
rm -rf node_modules package-lock.json
npm install
```

### Runtime Errors
**Problem**: Frontend crashes or shows errors
```bash
# Symptoms
- White screen
- Console errors
- API call failures
```

**Solution**:
```bash
# 1. Check browser console
# Open developer tools and look for errors

# 2. Verify API connectivity
curl https://your-backend-url.up.railway.app/health

# 3. Check environment variables
echo "VITE_API_BASE_URL: $VITE_API_BASE_URL"
```

## 🆘 Getting Help

### Self-Service Resources
```bash
# Documentation
https://docs.perplex-edge.com

# Status page
https://status.perplex-edge.com

# Community Discord
https://discord.gg/perplex-edge
```

### Support Channels
```bash
# Email support
support@perplex-edge.com

# GitHub issues
https://github.com/your-org/perplex-edge/issues

# Priority support (enterprise)
enterprise@perplex-edge.com
```

### When to Contact Support
- **Critical**: Production downtime, data loss, security issues
- **High**: Feature not working, performance problems
- **Medium**: Configuration questions, minor bugs
- **Low**: Documentation requests, feature suggestions

### Information to Include
```bash
# When reporting issues, include:
1. Environment (Railway/Docker/Local)
2. Error messages (full stack traces)
3. Steps to reproduce
4. Expected vs actual behavior
5. Recent changes or deployments
```

---

**🔧 Most issues are resolved by:**
1. **Checking environment variables**
2. **Verifying API keys**
3. **Restarting services**
4. **Checking logs**

**Still stuck?** We're here to help at support@perplex-edge.com 🚀
