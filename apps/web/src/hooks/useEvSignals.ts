"use client";
import { useMemo } from "react";
import { useBackendData } from "@/hooks/useBackendData";
import { useAuth } from "@/hooks/useAuth";
import { normalizeSportKey } from "@/constants/sports";

export type EVSignal = {
    event_id: string;
    sport_key: string;
    player_name: string;
    market_key: string;
    line: number;
    bookmaker: string;
    current_price: number;
    true_prob: number;
    implied_prob: number;
    edge_percent: number;
    confidence_score: number;
    updated_at: string;
    type?: string;
    timestamp?: string;
    event?: string;
    player?: string;
    confidence?: number;
};

export function useEvSignals(sport: string, minEv = 2.0) {
  const { isSignedIn, loading } = useAuth();
  const normalizedSport = normalizeSportKey(sport);
  const canQueryProtected = isSignedIn && !loading;
  const primary = useBackendData<any>("/api/signals/freshness", {
    params: { sport: normalizedSport },
    pollMs: 30_000,
  });
  const fallback = useBackendData<any>("/api/ev/top", {
    params: { sport: normalizedSport, limit: 50 },
    pollMs: 30_000,
    enabled: canQueryProtected,
    requireAuth: true,
  });

  const signals = useMemo(() => {
    const rawPrimary = primary.data?.results || primary.data?.signals || primary.data?.data || [];
    const chosen = Array.isArray(rawPrimary) && rawPrimary.length > 0 ? rawPrimary : (fallback.data?.results || fallback.data?.data || fallback.data || []);
    const arr = Array.isArray(chosen) ? chosen : [];
    return arr
      .map((s: any) => ({
        event_id: s.id || s.event_id,
        sport_key: s.sport || normalizedSport,
        player_name: s.player_name || s.player || "Unknown",
        market_key: s.market_key || s.stat_type || "market",
        line: Number(s.line || 0),
        bookmaker: s.bookmaker || s.book || "consensus",
        current_price: Number(s.current_price || s.price || s.odds || 0),
        true_prob: Number(s.true_prob || s.fair_prob || 0),
        implied_prob: Number(s.implied_prob || 0),
        edge_percent: Number(s.edge_percent || s.ev_pct || 0),
        confidence_score: Number(s.confidence_score || s.edge_percent || 0),
        updated_at: s.updated_at || new Date().toISOString(),
        type: String(s.type || s.signal_type || "signal").toLowerCase(),
        timestamp: s.timestamp || s.updated_at || new Date().toISOString(),
        event: s.event || s.player_name || s.player,
        player: s.player || s.player_name,
        confidence: Number(s.confidence || s.confidence_score || s.edge_percent || 0),
      }))
      .filter((s: EVSignal) => s.edge_percent >= minEv);
  }, [primary.data, fallback.data, minEv, normalizedSport]);

  return {
    signals,
    loading: primary.isLoading && fallback.isLoading,
    error: primary.error || fallback.error,
    lastUpdated: primary.lastUpdated || fallback.lastUpdated,
    refetch: async () => {
      if (!canQueryProtected) {
        await primary.refetch();
        return;
      }
      await Promise.all([primary.refetch(), fallback.refetch()]);
    },
  };
}
