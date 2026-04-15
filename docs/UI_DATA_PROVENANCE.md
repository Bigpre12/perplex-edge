# UI data provenance

Rules for surfacing **where data came from**, **how fresh it is**, and **how confidence should adjust** when the backend used a fallback provider or stale cache. Aligns with `source_provider` tagging in `WaterfallRouter` and future API fields such as `meta.fallback_used`.

**Spec:** [WATERFALL_PROVIDER_MATRIX.md](./WATERFALL_PROVIDER_MATRIX.md).

---

## 1. Source badges (`source_provider`)

| `source_provider` value | Badge text (short) | Tooltip (long) |
|-------------------------|-------------------|----------------|
| `the_odds_api` | Odds API | Multi-book odds from The Odds API. |
| `betstack` | BetStack | Consensus-style lines from BetStack free API — not a full sportsbook board. |
| `therundown` | TheRundown | Backup schedule / limited books via TheRundown. |
| `sportsgameodds` | SGO | SportsGameOdds — quota-sensitive; strong for MMA / alt lines where configured. |
| `isports` | iSports | iSports schedule or odds hook — verify fixture mapping. |
| `api_sports` | API-Sports | API-Sports feed (fixtures / stats / odds by endpoint). |
| `sportmonks` | SportMonks | SportMonks — often soccer depth. |
| `balldontlie` | BallDontLie | BallDontLie — US schedule/stats oriented. |
| `thesportsdb` | TheSportsDB | TheSportsDB metadata or schedule fallback. |
| `espn` | ESPN | ESPN unofficial scoreboard — good for scores, treat metadata as best-effort. |
| `kalshi` | Kalshi | Kalshi contract — binary market; not equivalent to sportsbook American odds. |
| `unknown` / missing | Source unknown | Backend did not stamp a provider; treat confidence as lower. |

Use **sentence case** in tooltips; badges stay **2 words max** on dense tables.

---

## 2. Stale banner copy

| Condition | Banner title | Body |
|-----------|--------------|------|
| Odds older than freshness SLA (e.g. more than 15 min pregame) | Data may be stale | Last successful odds sync is older than expected. Lines can drift from market. |
| Live scores delayed | Live scores delayed | Scoreboard source is behind real time. Do not use for in-play betting decisions alone. |
| Signals / EV not updated 24h+ | Intelligence feed paused | No new EV signals in the last 24 hours. Check `/api/meta/inspect` and ingestion heartbeats. |
| Fallback provider active (`meta.fallback_used` future) | Backup data source | Primary feed was unavailable. Edge quality may be reduced — see tooltip on confidence. |

---

## 3. Confidence penalties (conceptual)

When **`meta.fallback_used`** is true or `source_provider` is not tier-A for that surface:

- **EV / edge displays:** show a subtle down-arrow or “adjusted” glyph; tooltip: *“Confidence reduced: data came from a backup provider or cached snapshot.”*
- **CLV / closing:** if close tick source was secondary, tooltip: *“CLV used alternate close source.”*
- **Kalshi vs books:** never silently equate contract mid to sportsbook fair; show separate confidence stream.

Constants can live in frontend config later; this doc defines **copy and behavior**, not pixel values.

---

## 4. Future API shape (forward compatible)

```json
{
  "meta": {
    "fallback_used": false,
    "source_provider": "the_odds_api",
    "data_freshness_seconds": 120
  }
}
```

Clients should **not** break if fields are omitted; treat omission as unknown / neutral confidence.
