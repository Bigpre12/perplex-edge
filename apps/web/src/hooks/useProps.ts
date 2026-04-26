import { useMemo } from "react";
import { useBackendData } from "@/hooks/useBackendData";
import { normalizeSportKey } from "@/constants/sports";
import { unwrapList } from "@/lib/contracts";

export interface PropRecord {
  id: string;
  player_name: string;
  market_key: string;
  line: number;
  odds_over: number;
  odds_under: number;
  confidence: number;
  grade: string;
  sport: string;
  book: string;
  commence_time: string;
  updated_at?: string;
}

export const useProps = (sport = "basketball_nba", limit = 50) => {
  const normalizedSport = normalizeSportKey(sport);
  const req = useBackendData<any>("/api/props", {
    params: { sport: normalizedSport, limit },
    pollMs: 30_000,
  });
  const rows = useMemo(() => {
    return unwrapList<PropRecord>(req.data);
  }, [req.data]);
  const freshness = useMemo(() => {
    const newest = rows.find((row: any) => row?.updated_at)?.updated_at;
    return newest || req.lastUpdated;
  }, [rows, req.lastUpdated]);

  return { ...req, data: rows, updated_at: freshness };
};
