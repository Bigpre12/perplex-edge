# Perplex Edge

A full-stack sports betting analytics platform with odds comparison, prop analysis, injury tracking, and model predictions.

## Tech Stack

- **Backend**: FastAPI + SQLAlchemy 2.x (async) + Alembic
- **Frontend**: React + Vite + TypeScript
- **Database**: PostgreSQL
- **Data Sources**: The Odds API

## Project Structure

```
perplex_engine/
├── backend/          # FastAPI application
│   ├── app/          # Application code
│   ├── alembic/      # Database migrations
│   └── requirements.txt
├── frontend/         # React application
│   └── src/
├── docker-compose.yml
└── README.md
```

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose

### Quick Start

1. **Clone and setup environment variables**:

   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your API keys
   ```

2. **Start services with Docker Compose**:

   ```bash
   docker-compose up -d
   ```

   This starts:
   - PostgreSQL on port 5432
   - FastAPI backend on port 8000

3. **Run database migrations**:

   ```bash
   cd backend
   alembic upgrade head
   ```

4. **Start the frontend**:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   Frontend runs on http://localhost:5173

### Manual Backend Setup (without Docker)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Auto-Generate TypeScript Types

With the backend running locally, generate TS types from the OpenAPI schema:

```bash
cd frontend
npm run types:generate
```

This outputs `src/api/generated.ts` with all request/response types.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://postgres:postgres@localhost:5432/perplex` |
| `ODDS_API_KEY` | The Odds API key | - |
| `ENVIRONMENT` | `development` or `production` | `development` |

## License

MIT
