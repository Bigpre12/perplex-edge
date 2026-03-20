# Perplex Edge: Complete Stack Overview 🚀

This document provides a comprehensive map of the entire Perplex Edge platform after the Phase 10 "Top Dawg" upgrade.

---

## 🎨 1. Frontend: The Powerhouse UI
**Framework**: Next.js 14 (App Router) + Tailwind CSS + Shadcn UI
**Visual Identity**: Modern dark-mode aesthetic with vibrant accent colors and glassmorphism.

### Key Modules & Pages
- **`app/(app)/player-props/`**: High-velocity props dashboard with "Hero" hit-rate views (L5/L10/L20).
- **`app/(app)/ev/`**: Real-time +EV insights with integrated trending logic and volatility alerts.
- **`app/(app)/whale/`**: Steam and RLM (Reverse Line Movement) visualization.
- **`app/(app)/hit-rate/`**: Statistical breakdown of player consistency over time.
- **`components/Oracle/`**: AI-driven chat assistant with live market context injection.
- **`components/Common/LiveHistoricalToggle`**: Global switch between live markets and historical performance tracking.

---

## 🚀 2. Backend: Standardized FastAPI Engine
**Framework**: FastAPI (Python 3.14+)
**Core Design**: Domain-driven service layer with standardized persistence.

### Data Ingestion Layer (`UnifiedIngestion`)
- **Odds Mapping**: `OddsMapper.map_theodds_props_to_records` normalizes raw book data into Pydantic models.
- **Layered Persistence**: Parallel writes to `props_live` (current state) and `props_history` (time-series).
- **Zero-Mock Policy**: All production routes are strictly wired to the database.

### The Intelligence Layer (The "Brains")
- **`BrainOddsScout`**: High-frequency EV calculation engine writing to `edges_ev_history`.
- **`BrainCLVTracker`**: Institutional-grade closing-line-value tracking.
- **`SteamService`**: Multi-book line movement detection across 3+ sportsbooks.
- **`WhaleService`**: Significant price moves and sharp money identification.
- **`InjuryImpactBrain`**: Live player status quantification and edge adjustment.

---

## 💾 3. Database: Unified Model Layer
**Database**: PostgreSQL (Supabase) / SQLite (Local)
**ORM**: SQLAlchemy 2.0 (Consolidated in `models/brain.py`)

### Core Tables
- **`props_live`**: Realized, paired Over/Under lines with implied probabilities.
- **`props_history`**: 1-minute resolution snapshots for charting and steam analysis.
- **`edges_ev_history`**: Historical log of every +EV opportunity identified by the engine.
- **`whale_moves`**: Superset table for sharp money and large-scale line shifts.
- **`clv_tracking`**: Audit trail of every bet's performance against the closing line.
- **`steam_events`**: Consolidated log of rapid market movements.

---

## 🏗️ 4. Infrastructure & Reliability
- **Deployment**: Railway (Backend Container) + Vercel (Frontend).
- **AI Stack**: Groq (Llama-3.3-70B) for speed + OpenAI (GPT-4o) for high-reasoning fallback.
- **Verification**: `tests/test_api_reliability.py` ensures 100% schema compliance and removes all testing fixtures.
- **Health Monitoring**: Integrated `DataInspector` and `/api/health` endpoints for real-time infrastructure visibility.

---

**Perplex Edge is now standardized, hardened, and institution-ready. 🏆**
