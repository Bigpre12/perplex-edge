# Perplex Edge: Repository Audit & Competitive Analysis

This document summarizes the current technical state of Perplex Edge and identifies gaps where industry leaders (Outlier, OddsJam, Props.Cash, AVO) currently hold an advantage.

## 🚀 Current Technical Strengths

| Feature | Implementation Path | Competitive Advantage |
| :--- | :--- | :--- |
| **Unified Ingestion** | [unified_ingestion.py](file:///c:/Users/preio/OneDrive/Documents/Untitled/perplex_engine/perplex-edge/apps/api/src/services/unified_ingestion.py) | High-concurrency normalization of odds across sports. |
| **Multi-Brain Intel** | [workers/ev_engine.py](file:///c:/Users/preio/OneDrive/Documents/Untitled/perplex_engine/perplex-edge/apps/api/src/workers/ev_engine.py) | Combines EV, Whale/Steam, CLV, and Injury Impact in one dashboard. |
| **Dual Data Streams** | [models/unified.py](file:///c:/Users/preio/OneDrive/Documents/Untitled/perplex_engine/perplex-edge/apps/api/src/models/unified.py) | Native support for `props_live` and `props_history` for trend analysis. |
| **Premium UI Vibe** | [app/(app)/player-props](file:///c:/Users/preio/OneDrive/Documents/Untitled/perplex_engine/perplex-edge/apps/web/src/app/(app)/player-props) | Modern, glassmorphism-inspired design with real-time feedback. |

## ⚠️ Competitive Gaps & Weaknesses

Based on reviews of **Outlier**, **OddsJam**, and **Props.Cash**:

1. **Edge Discovery Speed**: Competitors like Outlier provide "Trending Edges" with a single click. Perplex Edge requires manual filtering.
2. **Hero Views**: Props.Cash excels at displaying "Hit Rate" charts (Last 5/10/20) against current lines. Our `props_history` wiring needs to power a similar specialized view.
3. **UX Consistency**: Some tabs (Whale, Injury) lack the deep drill-down "Hero" views found in the Props tab.
4. **API Standardization**: Several routes use dicts/mappings instead of strict Pydantic models, leading to potential frontend mismatch.
5. **Real-time Push**: While `ws_ev.py` exists, its integration with the frontend for "New Edge Found" notifications is less polished than OddsJam's real-time feed.

## 🗺️ Feature Map

- **Authentication**: `apps/api/src/routers/auth.py`
- **Player Props**: `apps/api/src/routers/props.py` -> `apps/web/src/app/(app)/player-props`
- **EV Intelligence**: `apps/api/src/routers/intel.py` -> `apps/web/src/app/(app)/ev`
- **Whale Tracker**: `apps/api/src/routers/whale.py` -> `apps/web/src/app/(app)/whale`
- **Injury Impact**: `apps/api/src/routers/injuries.py` -> `apps/web/src/app/(app)/injuries`
- **CLV Tracker**: `apps/api/src/routers/clv.py` -> `apps/web/src/app/(app)/clv`
- **Data Persistence**: `apps/api/src/db/session.py` (Supabase/Postgres)

---
*Drafted: March 20, 2026*
