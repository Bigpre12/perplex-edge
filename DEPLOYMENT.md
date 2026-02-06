# Production Deployment Guide

## Overview
This guide covers deploying Perplex Edge to production environments including Railway, Docker, and custom hosting.

## Prerequisites

### Required API Keys
- **The Odds API** (Required): https://the-odds-api.com/
- **Database**: PostgreSQL (Railway provides this automatically)
- **Optional APIs**: OddsPapi, Stats API, Injury API, Roster API

### Infrastructure
- Docker & Docker Compose
- Node.js 18+ (for frontend build)
- Python 3.11+ (for local testing)

## Quick Deploy to Railway

### 1. Fork and Connect Repository
```bash
# Fork this repository on GitHub
# Connect your fork to Railway
```

### 2. Configure Environment Variables
In Railway dashboard, add these environment variables:

#### Required Variables
```bash
ENVIRONMENT=production
DATABASE_URL=postgresql+psycopg://username:password@host:port/database
ODDS_API_KEY=your_production_odds_api_key
FRONTEND_URL=https://your-app-name.up.railway.app
CORS_ORIGINS=https://your-app-name.up.railway.app
```

#### Optional Variables
```bash
AI_ENABLED=false
AI_API_KEY=your_groq_api_key
SENTRY_DSN=your_sentry_dsn
REDIS_URL=your_redis_url
SCHEDULER_ENABLED=true
SCHEDULER_USE_STUBS=false
```

### 3. Deploy
```bash
# Railway will automatically detect and deploy
# Frontend will be built and served
# Backend will start with PostgreSQL
```

## Docker Deployment

### 1. Environment Setup
```bash
# Copy production template
cp backend/.env.production backend/.env

# Edit with your actual values
nano backend/.env
```

### 2. Build and Run
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Run database migrations
docker-compose exec backend alembic upgrade head
```

### 3. Production Docker Compose
```yaml
version: "3.8"

services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - ODDS_API_KEY=${ODDS_API_KEY}
      - ENVIRONMENT=production
    depends_on:
      - db
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      - VITE_API_BASE_URL=${BACKEND_URL}
    restart: unless-stopped

volumes:
  postgres_data:
```

## Manual Deployment

### Backend Setup
```bash
# 1. Install dependencies
cd backend
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 2. Configure environment
cp .env.production .env
# Edit .env with your values

# 3. Database setup
alembic upgrade head

# 4. Start service
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
# 1. Install dependencies
cd frontend
npm install

# 2. Build for production
npm run build

# 3. Serve with nginx or similar
npm run preview
```

## Environment Variables Reference

### Core Configuration
| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `ENVIRONMENT` | Yes | deployment environment | `production` |
| `DATABASE_URL` | Yes | PostgreSQL connection | `postgresql+psycopg://...` |
| `ODDS_API_KEY` | Yes | The Odds API key | `abc123...` |
| `FRONTEND_URL` | Yes | Frontend URL for CORS | `https://app.example.com` |
| `CORS_ORIGINS` | Yes | Additional CORS origins | `https://admin.example.com` |

### Optional Features
| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `AI_ENABLED` | No | Enable AI features | `false` |
| `AI_API_KEY` | No | Groq API key | - |
| `SENTRY_DSN` | No | Error monitoring | - |
| `REDIS_URL` | No | Caching backend | In-memory |
| `SCHEDULER_ENABLED` | No | Background tasks | `true` |
| `SCHEDULER_USE_STUBS` | No | Use stub data | `false` |

### API Integration
| Variable | Required | Provider | Description |
|----------|----------|---------|-------------|
| `ODDSPAPI_API_KEY` | No | OddsPapi | Historical data |
| `STATS_API_KEY` | No | Sports Stats | Advanced stats |
| `INJURY_API_KEY` | No | Injury Tracker | Injury data |
| `ROSTER_API_KEY` | No | balldontlie.io | NBA rosters |

## Health Checks

### Backend Health
```bash
curl https://your-domain.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T12:00:00Z",
  "version": "0.1.0"
}
```

### Database Health
```bash
curl https://your-domain.com/health/database
```

## Monitoring

### Sentry Integration
1. Create Sentry project
2. Set `SENTRY_DSN` environment variable
3. Errors will be automatically tracked

### Application Metrics
- **API Response Time**: Monitor `/metrics` endpoint
- **Database Connections**: Check connection pool status
- **Scheduler Status**: Monitor background task health

## Security Considerations

### API Keys
- Never commit API keys to version control
- Use environment variables in production
- Rotate keys regularly
- Monitor API usage for anomalies

### Database Security
- Use strong passwords
- Enable SSL connections
- Regular backups
- Limit database user permissions

### CORS Configuration
- Set specific allowed origins
- Disable wildcard CORS in production
- Monitor for unauthorized access

## Troubleshooting

### Common Issues

#### CORS Errors
```bash
# Check CORS origins
curl -H "Origin: https://your-domain.com" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     https://your-api.com/endpoint
```

#### Database Connection
```bash
# Test database connection
docker-compose exec backend python -c "
from app.core.config import get_settings
settings = get_settings()
print(f'Database URL: {settings.database_url}')
"
```

#### API Key Issues
```bash
# Test API key
curl -H "Authorization: Bearer $ODDS_API_KEY" \
     https://api.the-odds-api.com/v4/sports
```

### Performance Optimization

#### Database Indexes
```sql
-- Add indexes for common queries
CREATE INDEX idx_model_picks_created_at ON model_picks(created_at);
CREATE INDEX idx_games_sport_key ON games(sport_key);
CREATE INDEX idx_odds_game_id ON odds(game_id);
```

#### Caching
- Enable Redis for distributed caching
- Cache API responses from external providers
- Use CDN for static assets

## Scaling

### Horizontal Scaling
- Load balance multiple backend instances
- Use read replicas for database
- Implement queue system for background jobs

### Vertical Scaling
- Increase database memory
- Optimize application memory usage
- Monitor resource utilization

## Backup and Recovery

### Database Backups
```bash
# Daily backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump $DATABASE_URL > $BACKUP_DIR/backup_$DATE.sql
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
```

### Disaster Recovery
1. Restore database from backup
2. Redeploy application
3. Verify all services are running
4. Test key functionality

## Support

### Monitoring Dashboards
- Set up Grafana for metrics visualization
- Configure alerts for critical issues
- Monitor API rate limits

### Logging
- Centralized logging with ELK stack
- Structured logging for easy parsing
- Log retention policies

### Contact
- Technical support: support@perplex-edge.com
- Documentation: https://docs.perplex-edge.com
- Status page: https://status.perplex-edge.com
