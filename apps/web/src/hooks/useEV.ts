import { useEffect } from "react";
import { useBackendData } from "@/hooks/useBackendData";
import { normalizeSportKey } from "@/constants/sports";

export interface EVRecord {
  id: string;
  player_name: string;
  market_key: string;
  ev_pct: number;
  edge_percent?: number;
  ev_score?: number;
  bookmaker: string;
  line?: number;
  recommendation: string;
  sport: string;
}

export const useEV = (sport = "all") => {
  const normalizedSport = normalizeSportKey(sport);

  const evTop = useBackendData<any>("/api/ev/top", {
    params: { sport: normalizedSport, limit: 50 },
    pollMs: 15_000,
  });

  useEffect(() => {
    fetch(`/backend/api/ev/compute?sport=${normalizedSport}`, { method: "POST" })
      .catch(() => fetch(`/backend/api/compute?sport=${normalizedSport}`, { method: "POST" }))
      .catch(() => undefined);
  }, [normalizedSport]);

  const rowsRaw = evTop.data;
  const rows = Array.isArray(rowsRaw)
    ? rowsRaw
    : (rowsRaw?.data || rowsRaw?.results || rowsRaw?.edges || []) as EVRecord[];

  return {
    data: rows as EVRecord[],
    isLoading: evTop.isLoading,
    isError: evTop.isError,
    error: evTop.error,
    refetch: evTop.refetch,
    isFetching: evTop.isLoading,
    lastUpdated: evTop.lastUpdated,
  };
};
