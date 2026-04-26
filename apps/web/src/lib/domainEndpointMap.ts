export const DOMAIN_ENDPOINT_MAP: Record<string, string[]> = {
  clv: ["/api/clv", "/api/clv/summary"],
  hitRate: ["/api/hit-rate", "/api/hit-rate/summary"],
  signals: ["/api/signals", "/api/signals/freshness"],
  pickIntel: ["/api/pick-intel"],
  lineMovement: ["/api/line-movement"],
  betTracker: ["/api/bets/my", "/api/bets/stats"],
  brain: ["/api/brain", "/api/brain/status", "/api/brain/metrics"],
  parlays: ["/api/parlays", "/api/parlays/simulate"],
  sharp: ["/api/sharp"],
  arbitrage: ["/api/arbitrage"],
  whale: ["/api/whale"],
  propsHistory: ["/api/props/history"],
  kalshi: ["/api/kalshi", "/api/kalshi_ws"],
  settings: ["/api/auth/me", "/api/auth/keys"],
};

