# MVP surface checklist (LUCRIX)

Maps blueprint MVP to **existing routes** in `apps/web`. Use with [PRODUCT_BLUEPRINT.md](./PRODUCT_BLUEPRINT.md).

| Surface | Route | Primary API | Status |
|---------|-------|-------------|--------|
| Command / Desk | `/dashboard` | `/api/props/graded`, `/api/injuries`, `/api/health` | Shipped |
| Scanner | `/institutional/scanner` | Intel / scan endpoints as page implements | Shipped (institutional) |
| Props | `/player-props` | `/api/props/live`, `POST /api/compute` | Shipped |
| EV+ | `/ev` | `/api/ev`, `POST /api/compute` | Shipped |
| CLV | `/clv` | `/api/clv` | Shipped |
| Hit rate | `/hit-rate` | `/api/hit-rate`, `/api/hit-rate/players` | Shipped |
| Signals | `/signals` | `/api/signals` | Shipped |
| Live | `/live` | `/api/live` | Shipped |
| Line movement | `/line-movement` | `/api/slate/today`, `/api/props/live`, `/api/line-movement` | Shipped |
| Bet tracker | `/bet-tracker` | Bets / ledger as wired in page | Shipped |
| Player drill | `/player/[id]` | Hero / props APIs as wired | Shipped |
| Brain | `/brain` | `/api/brain/*`, intel | Shipped |
| Alerts (create) | `/api/alerts` (POST trigger) | From alerts UI where present | Partial |
| Settings | `/settings` | `/api/user/settings` | Shipped |
| Billing | `/pricing`, `/subscription`, `/checkout` | Stripe `/api/stripe`, `/api/billing` | Shipped |

**Meta / versioning:** `GET /api/meta/build` — `api_version`, `git_sha`, `environment`.

**Standard errors:** `{ "error": { "code", "message", "request_id", "details?" } }` for validation and unhandled paths (see FastAPI handlers in `main.py`).
