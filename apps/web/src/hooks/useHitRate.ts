import { useBackendData } from "@/hooks/useBackendData";
import { normalizeSportKey } from "@/constants/sports";

export interface HitRateStats {
  overall_hit_rate: number;
  roi: number;
  graded_picks: number;
  streak?: number;
}

function sanitize(raw: any): HitRateStats {
  const safe = (v: any) => {
    const n = Number(v);
    return Number.isFinite(n) ? n : 0;
  };
  return {
    overall_hit_rate: safe(raw?.overall_hit_rate),
    roi: safe(raw?.roi),
    graded_picks: safe(raw?.graded_picks),
    streak: safe(raw?.streak),
  };
}

export const useHitRate = (sport = "basketball_nba") => {
  const req = useBackendData<any>("/api/hit-rate/summary", { params: { sport: normalizeSportKey(sport) }, pollMs: 60_000 });
  return { ...req, data: sanitize(req.data || {}) };
};

export const useHitRatePlayers = (sport = "basketball_nba") => {
  const req = useBackendData<any>("/api/hit-rate/leaderboard", { params: { sport: normalizeSportKey(sport) }, pollMs: 60_000 });
  const rowsRaw = req.data;
  const rows = (Array.isArray(rowsRaw) ? rowsRaw : (rowsRaw?.data || rowsRaw?.results || [])) as any[];
  return {
    ...req,
    data: rows.map((r, i) => ({ ...r, id: r?.id ?? r?.player_id ?? `hrp-${i}` })),
  };
};
