# Infrastructure Setup

## Railway Deployment

### Prerequisites

1. [Railway CLI](https://docs.railway.app/develop/cli) installed
2. Railway account and project created

### Setup Steps

#### 1. Create Railway Project

```bash
# Login to Railway
railway login

# Create new project
railway init
```

#### 2. Add PostgreSQL Database

In the Railway dashboard:
1. Click "New" -> "Database" -> "PostgreSQL"
2. The DATABASE_URL will be automatically injected

#### 3. Deploy Backend

```bash
cd backend

# Link to Railway service
railway link

# Set environment variables
railway variables set ENVIRONMENT=production
railway variables set ODDS_API_KEY=your_api_key_here
railway variables set FRONTEND_URL=https://your-frontend.railway.app

# Deploy
railway up
```

#### 4. Deploy Frontend

```bash
cd frontend

# Link to a new Railway service
railway link

# Set environment variables (API URL)
railway variables set VITE_API_URL=https://your-backend.railway.app

# Deploy
railway up
```

### Environment Variables

#### Backend
| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes (auto-injected) |
| `ENVIRONMENT` | `development` or `production` | Yes |
| `ODDS_API_KEY` | The Odds API key | Yes |
| `FRONTEND_URL` | Frontend URL for CORS | Yes |

#### Frontend
| Variable | Description | Required |
|----------|-------------|----------|
| `VITE_API_URL` | Backend API URL | Yes |

### Run Migrations

After deploying the backend:

```bash
cd backend
railway run alembic upgrade head
```

### Monitoring

- Railway provides automatic logging
- Access logs via: `railway logs`
- View metrics in the Railway dashboard

## Local Development with Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Architecture

```
┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │
│    Frontend     │────▶│    Backend      │
│  (React/Vite)   │     │   (FastAPI)     │
│                 │     │                 │
└─────────────────┘     └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │                 │
                        │   PostgreSQL    │
                        │   (Railway)     │
                        │                 │
                        └─────────────────┘
```
