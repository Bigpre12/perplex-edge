# Perplex Edge

A full-stack sports betting analytics platform with odds comparison, prop analysis, injury tracking, and AI-powered predictions.

## 🚀 Quick Start

### Option 1: One-Click Deploy (Recommended)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https%3A%2F%2Fgithub.com%2Fyour-org%2Fperplex-edge)

### Option 2: Manual Setup
See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## 📋 Prerequisites

- **The Odds API** key (required): https://the-odds-api.com/
- Hosting platform (Railway recommended)
- Optional: Groq AI key for AI features

## ⚡ Features

- **Real-time Odds**: Live odds from multiple sportsbooks
- **AI Insights**: Machine learning-powered betting recommendations  
- **Prop Analysis**: Advanced player prop analytics
- **Injury Tracking**: Up-to-date injury reports and impact analysis
- **Historical Data**: Performance tracking and trend analysis
- **Automated Alerts**: Custom notifications for betting opportunities

## 🏗️ Tech Stack

- **Backend**: FastAPI + SQLAlchemy 2.x (async) + Alembic
- **Frontend**: React + Vite + TypeScript + TailwindCSS
- **Database**: PostgreSQL
- **Deployment**: Docker + Railway
- **Monitoring**: Sentry + structured logging
- **AI**: Groq Llama 3.3 70B (optional)

## 📁 Project Structure

```
perplex_engine/
├── backend/              # FastAPI application
│   ├── app/              # Application code
│   ├── alembic/          # Database migrations
│   ├── .env.example      # Development environment template
│   ├── .env.production   # Production environment template
│   └── requirements.txt
├── frontend/             # React application
│   ├── src/
│   ├── .env.example      # Frontend environment template
│   └── package.json
├── DEPLOYMENT.md         # Production deployment guide
├── CUSTOMER_SETUP.md     # Customer setup instructions
├── docker-compose.yml    # Local development
└── README.md
```

## 🛠️ Local Development

### Quick Start

1. **Clone and setup environment**:

   ```bash
   git clone https://github.com/your-org/perplex-edge.git
   cd perplex-edge
   cp backend/.env.example backend/.env
   # Edit backend/.env with your API keys
   ```

2. **Start services with Docker Compose**:

   ```bash
   docker-compose up -d
   ```

3. **Run database migrations**:

   ```bash
   docker-compose exec backend alembic upgrade head
   ```

4. **Start the frontend**:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   Frontend runs on http://localhost:5173

### Manual Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 📚 Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)**: Production deployment guide
- **[CUSTOMER_SETUP.md](CUSTOMER_SETUP.md)**: Customer setup instructions
- **API Documentation**: Available at `/docs` when running

## 🔧 Environment Variables

### Required Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection | `postgresql+psycopg://...` |
| `ODDS_API_KEY` | The Odds API key | `abc123...` |
| `FRONTEND_URL` | Frontend URL for CORS | `https://app.example.com` |
| `CORS_ORIGINS` | Additional CORS origins | `https://admin.example.com` |

### Optional Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `AI_ENABLED` | Enable AI features | `false` |
| `AI_API_KEY` | Groq API key | - |
| `SENTRY_DSN` | Error monitoring | - |
| `REDIS_URL` | Caching backend | In-memory |
| `SCHEDULER_ENABLED` | Background tasks | `true` |

## 🏃‍♂️ API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Auto-Generate TypeScript Types

```bash
cd frontend
npm run types:generate
```

This outputs `src/api/generated.ts` with all request/response types.

## 🔍 Monitoring & Health

### Health Checks
- **Backend**: `/health` - Overall service health
- **Database**: `/health/database` - Database connectivity
- **Metrics**: `/metrics` - Application metrics

### Error Tracking
Sentry integration for production error monitoring.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: https://docs.perplex-edge.com
- **Issues**: https://github.com/your-org/perplex-edge/issues
- **Email**: support@perplex-edge.com
- **Discord**: https://discord.gg/perplex-edge

## 🎯 Production Ready

✅ **Security**: Environment-based configuration, no hardcoded secrets  
✅ **Scalability**: Docker containerization, async database operations  
✅ **Monitoring**: Health checks, error tracking, structured logging  
✅ **Documentation**: Complete deployment and setup guides  
✅ **Testing**: Comprehensive test coverage  
✅ **Performance**: Optimized queries, caching, CDN-ready frontend  

---

**Built with ❤️ for sports betting analytics**
