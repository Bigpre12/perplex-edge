# Multi-provider waterfall — provider matrix

Authoritative reference for **which external layer serves which data type**, how failover is ordered, and how internal engines should treat **fallback / stale** upstream data. Implementation source: `apps/api/src/core/waterfall_config.py` plus `services/waterfall_router.py`. Toggle legacy chains with `WATERFALL_CONFIG_VERSION=1` (not recommended except for rollback).

**Related:** [UI_DATA_PROVENANCE.md](./UI_DATA_PROVENANCE.md) (badges, stale copy, confidence), [PRODUCT_BLUEPRINT.md](./PRODUCT_BLUEPRINT.md) (product context), [PERPLEX_EDGE_MASTER_BLUEPRINT_V2.md](./PERPLEX_EDGE_MASTER_BLUEPRINT_V2.md) (V2 narrative + IA), [BRAINS_AUDIT_AND_REBUILD_SPEC.md](./BRAINS_AUDIT_AND_REBUILD_SPEC.md) (brains health).

---

## 1. Provider inventory

| Provider | Role | Sports / markets | Freshness / SLA (typical) | Quota / cost | Trust tier | Weaknesses | Normalization target |
|----------|------|------------------|---------------------------|--------------|------------|------------|----------------------|
| **The Odds API** | Primary odds / props | Major US + intl; h2h, spreads, totals, player props | ~1–5 min cache in client | Credit-metered; key rotation | **A** | Monthly caps; prop depth varies by sport | `event_id`, Odds API `market_key`, book keys |
| **BetStack** (`api.betstack.dev`) | Supplemental consensus | Leagues in `LUCRIX_TO_BETSTACK_LEAGUE` | Event list + embedded lines | Free tier rate limits | **B+** | Not a full multi-book board; mapping to internal props | Internal `game_id`, consensus lines object |
| **Kalshi** | Primary (contracts) / cross-signal | Binary event contracts per CFTC rules | WS + REST polling | Fee + tier gates | **A** (price) / **B** (vs books semantics) | Binary ≠ American odds; correlation to books manual | `ticker`, `event_ticker`, contract side |
| **BallDontLie** | Primary schedule/stats (US) | NBA, NFL, MLB, NHL, NCAA (per API) | ~1 min cached games | Free tier w/ key | **B+** | Not odds | BDL `game_id` → canonical `event_id` |
| **ESPN** (unofficial site API) | Fallback scores / news / metadata | Broad coverage | Scoreboard near-live | No key | **B** | Undocumented; shape shifts | ESPN event ids → map to canonical |
| **TheSportsDB** | Fallback schedule / metadata | All sports incl. MMA | ~24h friendly cache paths | Free key | **C+** | Odds depth low | `idEvent` → metadata |
| **TheRundown** | Fallback odds-adjacent / schedule | NBA, NFL, MLB, NHL, NCAAB, NCAAF (mapped sport IDs) | 10 min client TTL | 20k datapoints/day | **B** | Few books | `event_id` → events row |
| **SportsGameOdds** | Fallback / MMA / alt lines | UFC + majors; alt lines sparingly | 30 min TTL (quota) | 1k objects/mo | **B** | Strict quota | SGO `eventID` |
| **API-Sports** | Secondary fixtures / stats / odds hooks | Multi-sport via subdomains | Varies | 100 req/day free | **B** | Odds endpoint per-fixture | `fixture.id` |
| **SportMonks** | Soccer depth / fixtures | Football v3 (+ other products) | API-dependent | Key tiered | **B+** | Cost at scale | Fixture / team ids |
| **iSports** | Schedule + odds hooks | Configured sports in account | Per-endpoint | Twin-key quota | **B** | Odds need `fixtureId` path | iSports fixture id |
| **StatsBomb** | Specialty soccer analytics | Event-level tactical data | Static / batch | License | **A** (analytics) | Not a live odds feed | Match id |
| **OddsPapi** | Roadmap / wire when client exists | TBD by contract | TBD | Key in `config` only today | **TBD** | No first-class client in repo v1 | TBD |
| **SportsDataIO** | **Roadmap** — not wired v1 | Enterprise sports data | N/A | Contract | **TBD** | Not implemented | `event_id` (vendor) |
| **Sportradar** | **Roadmap** — not wired v1 | Official feeds | N/A | Contract | **TBD** | Not implemented | Sportradar uuid |

**Unified ingestion** (see `unified_ingestion` module docstring): primary board build uses **The Odds API** (stage 1), **BetStack** consensus merge (stage 2), optional **Kalshi** cross-signal (stage 3), persistence to `props_live` / `unified_odds` / history (stage 4). **ESPN** may appear in auxiliary jobs (scores/news), not as the primary odds book source.

---

## 2. Matrix by data type

Rows are **logical data products**. Columns describe the **runtime waterfall** (first hit wins unless empty), not every batch job.

| Data type | Primary | Secondary | Tertiary | Cache (Redis / DB) | Degraded mode | Conflict rule | UI label (fallback / stale) |
|-----------|---------|-----------|----------|-------------------|---------------|----------------|------------------------------|
| Pregame odds | The Odds API | BetStack consensus | TheRundown → SGO → iSports → API-Sports | `wf:odds_pregame:*`, odds client cache | Older cached snapshot; widen book list | Prefer higher trust tier; newer `commence_time` wins tie | “Consensus / backup feed” |
| Live odds | The Odds API (same chain as pregame until live-specific client) | BetStack (if lines updating) | TheRundown / SGO | Same + short TTL | Show last known with **stale** banner | Do not mix in-play with pregame without flag | “Live data delayed” |
| Player props | The Odds API | OddsPapi (roadmap) | — | props tables | Hide thin markets | Same player + market: prefer primary book set | “Props from alternate source” |
| Alt lines | The Odds API | SportsGameOdds (quota) | — | SGO client cache | Strip alt markets | Primary book line wins for CLV base | “Alt line (low-volume source)” |
| Injuries | ESPN | API-Sports | TheSportsDB | DB `injuries` | Last successful ingest timestamp | Text fields: prefer official team feed wording | “Injury data may be delayed” |
| Player stats | API-Sports / BallDontLie (sport-dependent) | SportMonks | TheSportsDB | Redis per client | Reduce refresh frequency | Recency + minutes played | “Stats from secondary feed” |
| Game stats | ESPN | API-Sports | TheSportsDB | Scoreboard cache | Final-only if live fails | Box score completeness | “Scoreboard fallback” |
| Schedules | BallDontLie (US) / API-Sports (soccer) | TheSportsDB | ESPN | `wf:schedule:*` | Calendar day from tertiary | Start time: prefer official league if conflict | “Schedule source: …” |
| Metadata | TheSportsDB | ESPN | API-Sports | Long TTL | Static placeholder | Logo / name: single canonical table | “Metadata cached” |
| Live state | ESPN | API-Sports | — | Short TTL | Poll backoff | Period/clock: trust ESPN first for US | “Live state delayed” |
| Kalshi contracts | Kalshi REST/WS | — | — | Kalshi service cache | Read-only if auth fails | Do not infer sportsbook fair odds = Kalshi mid | “Exchange contract (not a sportsbook line)” |
| Closing lines | Internal `line_ticks` / history | The Odds API (historical if enabled) | — | Postgres | Last tick older than game start + buffer | CLV uses agreed close book order | “CLV uses last tick before close” |
| Historical odds | Postgres history | The Odds API historical endpoints (if enabled) | — | DB | Empty if never ingested | Single canonical close per market | “Historical sample limited” |
| Book availability | Derived from multi-book ingest | — | — | `unified_odds` | Single-book sport | Max book count cap in UI | “Limited books” |
| Steam inputs | `line_ticks` + volume proxies | — | — | Redis streams / DB | Noise if tick sparse | Deduplicate by event+market+window | “Low tick density” |
| Parlay inputs | Same as odds + correlation model | — | — | — | Strip legs missing prices | Warn on same-game correlation | “Leg removed (missing price)” |
| Hit-rate features | Graded bets + outcomes | — | — | `player_hit_rates` | Shrink toward prior if n small | Bucket definition frozen per release | “Small sample” |
| CLV inputs | Closing line + bet entry line | — | — | CLV tables | Skip if no close | One close source per config | “CLV unavailable (no close)” |

---

## 3. Internal engines (inputs + confidence)

| Engine | Upstream inputs | When upstream is fallback or stale |
|--------|-----------------|-----------------------------------|
| Projections | Odds (multi-book), props, injuries, minutes | Penalize confidence if props from tertiary odds or injury source is ESPN-only fallback |
| Fair odds | De-vig / consensus (Odds API + BetStack) | Penalize if BetStack-only or single-book |
| EV | Fair vs offered | Penalize if stale `last_odds_sync` or `meta.fallback_used` |
| CLV | Closing tick vs entry | Penalize if close from backup provider |
| Hit rate | Graded outcomes | Penalize if grading used delayed scores |
| Steam / sharp / whale | Ticks + flow proxies | Penalize if tick density below threshold |
| User bets | User entry + line at entry | No external penalty; flag if line source unknown |
| Cache / feature flags | Redis + env | Penalize if serving cached odds past freshness SLA |

---

## 4. Operational rules

1. **Provider health score (conceptual):** blend last success (heartbeat), error rate, latency p95, and quota headroom. Sport-level overrides may down-rank a provider without removing it (future YAML in `apps/api/src/core/`).
2. **Failover order:** `waterfall_config.get_provider_chain(sport, data_type)` — first non-empty response wins; `source_provider` is stamped per item in `WaterfallRouter`.
3. **Stale detection:** Align with `system_sync_state` / meta inspect: flag when `last_signal` or ingest heartbeat older than policy (e.g. 24h for signals, minutes for live odds).
4. **Dedupe on disagreement:** Prefer higher trust tier; if same tier, prefer newer timestamp; persist both for audit when divergence exceeds threshold (future rule engine).

---

## 5. `unified_ingestion` vs waterfall

| Stage | Providers (external) | Persistence / side effects |
|-------|----------------------|----------------------------|
| 1 | The Odds API (`get_live_odds`) | Raw events → mapper |
| 2 | BetStack (`betstack_client` consensus lines) | Merged into prop / unified shapes |
| 3 | Kalshi (optional cross-signal) | Feature flags / tier gates |
| 4 | Internal writers | `props_live`, `unified_odds`, history, heartbeats |

Waterfall router **odds** chain is used by REST `/api/waterfall/odds` and any code path calling `waterfall_router.get_data(..., "odds")`; ingestion **does not** replace stage 1–2 with the router today — it implements its own staged pipeline above. Every external in that pipeline appears in this matrix.

---

<a id="part-ii-v2-routing-spec"></a>

## Part II — V2 routing spec

V2 adds a **canonical five-column waterfall** (Primary / Secondary / Tertiary / Cached / Degraded) per **data domain**, **per-provider routing contracts** (prefer / skip / normalize / conflict / confidence / UI), **provider health scoring**, **override hooks**, **reprocessing rules**, and an **audit event schema** for router decisions. **Product role** vs **repo status** separates commercial intent from what is wired in this repository today.

### II.1 V2 domain matrix (Primary, Secondary, Tertiary, Cached, Degraded)

| Data domain | Primary | Secondary | Tertiary | Cached | Degraded |
|-------------|---------|-----------|----------|--------|----------|
| Pregame odds | The Odds API | BetStack, TheRundown, SGO, iSports, API-Sports | SportMonks (soccer-heavy) | Redis `wf:*`, odds client TTL, `unified_odds` | Last known board; widen books; stamp `source_provider` |
| Live odds | The Odds API | BetStack (if updating), TheRundown | SGO | Same + short TTL Redis | Stale banner; freeze in-play flag if clock unknown |
| Player props | The Odds API | OddsPapi (roadmap) | SGO (alt/player where licensed) | `props_live`, props history | Hide thin markets; reduce MC confidence |
| Alt lines | The Odds API | SGO (quota) | TheRundown | SGO client cache | Strip alts; show quota-sensitive label |
| Mainlines and derivatives | The Odds API | BetStack consensus | iSports / API-Sports fixture odds | DB unified rows | Single-book: inflate uncertainty on derivatives |
| Injuries | ESPN | API-Sports | TheSportsDB | `injuries` table | Timestamp-only delayed message |
| Player stats | API-Sports / BallDontLie | SportMonks | TheSportsDB | Redis client cache | Shrink projection weight |
| Game stats | ESPN | API-Sports | TheSportsDB | Scoreboard cache | Final-only snapshot |
| Schedules | BallDontLie (US) / API-Sports | TheSportsDB | ESPN | `wf:schedule:*` | Calendar-only tertiary |
| Team and player metadata | TheSportsDB | ESPN | API-Sports | Long TTL metadata cache | Static placeholder avatars |
| Play-by-play / live game state | ESPN | API-Sports | Sportradar (roadmap enterprise) | Short TTL | Poll backoff; PBP delayed banner |
| Kalshi sports contracts | Kalshi REST/WS | — | — | Kalshi service cache | Read-only if auth fails; illiquidity widen spread display |
| Kalshi life-event contracts | Kalshi REST/WS | — | — | Same | Isolated UI; no sportsbook EV column unless bridge toggled |
| Historical odds | Postgres `props_history` / tick store | The Odds API historical (if enabled) | — | DB | Empty if never ingested |
| Closing lines | Internal ticks / `line_ticks` | The Odds API historical | — | Postgres | Last tick with provisional close label |
| Book availability and regionalization | Derived from `unified_odds` book columns | Contracted regional feeds (abstract) | — | Per-user region cache (future) | Limited books in region |
| Steam detection inputs | `props_history`, `line_ticks`, Redis sharp tracker | The Odds API (context only) | — | Redis | Low density suppress steam alerts |
| Whale / sharp action inputs | `unified_odds` multi-book SQL (alert_writer) | Sharp book list config | — | DB | Outlier threshold raised if few books |
| Parlay pricing inputs | Same as odds + internal correlation | Monte Carlo leg priors | — | — | Strip legs; correlation unknown label |
| Hit-rate feature inputs | Graded `model_picks` / user bets | — | — | `player_hit_rates` | Shrink priors if low n |
| CLV grading inputs | Entry snapshot + closing tick | Internal CLV tables | — | Redis CLV openers | Skip row if no close |
| Monte Carlo simulation inputs | Ingested props/odds + correlation model id | BetStack as marginal fallback | Prior shrink | Cached scenario seeds (future) | Widen fan charts; degraded label |
| Portfolio exposure inputs | User bets + positions + contract holdings | Kalshi positions | — | DB | Cross-venue rollup partial if one venue offline |
| Settlement inputs | League official results (abstract) | Exchange settlement API (Kalshi) | Grading service | DB | Manual dispute queue (future) |

### II.2 Per-provider routing contract

**Legend:** `repo_status` = **wired** | **partial** | **roadmap** | **abstract** (pattern for future sportsbook/regional feeds). **Product role** = how GTM / architecture names the tier.

| Provider | Product role | repo_status | prefer_when | skip_when | Normalization | Conflict reconciliation | Confidence penalty on fallback | UI label |
|----------|----------------|-------------|-------------|-----------|---------------|---------------------------|-------------------------------|----------|
| The Odds API | Primary sportsbook board | wired | Keys healthy; in-season sport | Keys dead / 429 exhausted | `event_id`, `market_key`, book keys | Higher trust vs tertiary for same line | None when primary | Odds API |
| SportsDataIO | Enterprise depth (product primary when licensed) | roadmap | Contract active; sport in SDI catalog | No license / no client | Vendor `event_id` to canonical | Prefer SDI official time when conflict with free feeds | Low until client validates joins | Enterprise feed pending wire |
| Kalshi | Primary for contracts | wired | Auth OK; ticker liquid | Auth fail; halted market | `ticker`, `event_ticker`, side | Never auto-win vs sportsbook; dual-store | High if illiquid | Kalshi contract |
| BallDontLie | Primary US schedule/stats | wired | US league supported | Off-season or rate limited | `game_id` to canonical event | Schedule: prefer BDL over TSB for US when fresher | Mild if stale cache | BallDontLie |
| ESPN | Fallback live/scores/news | wired | No paid key; need scoreboard | Shape drift / parse errors | ESPN event id to map table | Prefer for live clock US over free DBs | Medium on undocumented API | ESPN |
| TheSportsDB | Fallback metadata/schedule | wired | Broad coverage cheap | Odds depth needed | `idEvent` | Metadata wins if only source | Medium | TheSportsDB |
| StatsBomb | Specialty soccer analytics | partial | Licensed match analytics | Live odds not a substitute | Match id | Analytics trump free xG estimates | Low when used for props context | StatsBomb |
| SportsGameOdds | Alt lines / MMA | wired | MMA or alt quota available | Quota exceeded | SGO `eventID` | SGO alt vs Odds API: prefer Odds API for CLV base | High (quota + thin) | SGO |
| OddsPapi | Supplemental odds | roadmap | Client shipped + keys | No client | TBD vendor map | TBD | TBD | OddsPapi roadmap |
| Sportradar | Enterprise official | roadmap | Enterprise contract | No feed | UUID map | Official over free when licensed | Low when primary paid | Sportradar roadmap |
| BetStack | Consensus lines | wired | League in LUCRIX map | 429 / URL misconfig | `game_id` + lines object | Consensus vs multi-book: use for fair not for CLV close | Medium if single consensus | BetStack |
| TheRundown | Backup odds-adjacent | wired | Key set; sport in SPORT_ID_MAP | Unknown sport id | TheRundown `event_id` | Few books: down-rank vs Odds API | Medium | TheRundown |
| API-Sports | Fixtures / stats / odds hooks | wired | Subdomain + key valid | Daily cap hit | `fixture.id` | Fixture time vs BDL: newer wins | Medium | API-Sports |
| SportMonks | Soccer depth | wired | Football endpoints | Non-soccer | Fixture id | Soccer depth over TSB for live fixture list | Medium | SportMonks |
| iSports | Schedule / odds hooks | wired | Twin-key creds | Auth failure | Fixture id | iSports vs API-Sports: trust tier + recency | Medium | iSports |
| Sportsbook_regional (abstract) | Book-specific or geo odds | abstract | Contract + compliance OK | Geo block | Book-native id to internal | Regional line vs global: policy engine | Varies by jurisdiction | Regional book feed |

### II.3 Provider health score (conceptual)

Define `health_score` in `[0,1]` per provider per sport (rolling window, e.g. 24h):

`health_score = w1 * success_rate + w2 * (1 - norm_p95_latency) + w3 * quota_headroom - w4 * error_burst - w5 * staleness_flag`

- **success_rate:** heartbeats ok / attempts (`HeartbeatService`, `/api/meta/waterfall`).
- **latency:** p95 from logs or APM (future).
- **quota_headroom:** credits remaining / caps (Odds API headers, BetStack 429 rate).
- **Weights** `w1..w5` configured per provider class in future `waterfall_overrides.yaml`.

**Router behavior:** sort chain by `health_score` without violating contractual order (only **reorder within same trust band** unless ops override).

### II.4 Overrides, failover, stale detection, reprocessing

| Mechanism | Spec |
|-----------|------|
| Sport-level override | Future file `apps/api/src/core/waterfall_overrides.yaml`: per `sport_key`, reorder or disable provider ids. |
| Market-type override | Same file: e.g. `player_props` may skip SGO first when quota low. |
| Auto-failover | `get_provider_chain` order; first non-empty response wins; stamp `source_provider`. |
| Stale detection | Compare `system_sync_state.last_odds_sync`, ingest heartbeats, and domain SLA tables (config). |
| Reprocessing / backfill | Idempotent re-run `unified_ingestion.run(sport)` for window; rebuild `unified_odds` + EV; never delete props below `MIN_RECORDS_FOR_DELETE` without ops flag. |
| Conflict reconciliation | Trust tier table (A greater than B+ greater than B greater than C); tie-breaker = newer `updated_at` / line tick; optionally persist **both** for audit if delta over threshold. |

### II.5 Audit logging schema (router selection)

Persist one row per routing decision (future table `waterfall_selection_audit` or append-only log):

| Field | Type | Description |
|-------|------|-------------|
| `selection_id` | uuid | Unique id for this decision |
| `sport_key` | string | e.g. `basketball_nba` |
| `data_domain` | string | e.g. `pregame_odds`, `kalshi_life_event_contracts` |
| `ordered_chain` | json array | Provider ids attempted in order |
| `winner_provider` | string | First that returned usable payload |
| `reject_reasons` | json array | Per skipped provider: provider and reason empty or 429 or timeout or health |
| `staleness_s` | int | Seconds since last successful ingest for that domain |
| `cache_hit` | bool | Whether Redis / DB cache served response |
| `config_version` | string | e.g. `WATERFALL_CONFIG_VERSION=2` |

Map to observability stack (logs, metrics, traces) and optional linkage to `brain_execution_runs` in [BRAINS_AUDIT_AND_REBUILD_SPEC.md](./BRAINS_AUDIT_AND_REBUILD_SPEC.md).

### II.6 Implementation alignment (repo honesty)

| Data domain | Current repo entrypoint | Gap vs V2 |
|-------------|-------------------------|-----------|
| Pregame / live odds (router) | `waterfall_config.get_provider_chain` + `WaterfallRouter` | Live-specific client not separate; document only |
| Ingest board | `unified_ingestion` + `odds_api_client` + BetStack | Does not yet emit Part II audit rows |
| Kalshi | `kalshi_service`, routers, optional ingest | Life-event classifier and separate UI tab spec-first |
| SportsDataIO / Sportradar | `waterfall_config.KNOWN_PROVIDER_IDS`; no client | roadmap until modules land |
| PBP deep | ESPN partial | Sportradar enterprise roadmap |
| Regionalization | Not implemented | abstract tier + policy future |
| Monte Carlo | `monte_carlo_service`, parlay routes | No persisted random_seed / audit yet |

---

*Part II satisfies Master Prompt V2 waterfall requirements; Part I remains the historical eight-column matrix for continuity.*
