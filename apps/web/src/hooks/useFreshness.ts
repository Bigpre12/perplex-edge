"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type Freshness = {
  last_odds_update: string | null;
  last_ev_update: string | null;
  server_time: string;
};

export function useFreshness(sport: string) {
  const [data, setData] = useState<Freshness | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        // Normalize sport key for backend consistency
        let normalizedSport = (sport || '').toLowerCase();
        if (normalizedSport === 'nba') normalizedSport = 'basketball_nba';
        if (normalizedSport === 'nfl') normalizedSport = 'americanfootball_nfl';
        if (normalizedSport === 'mlb') normalizedSport = 'baseball_mlb';
        if (normalizedSport === 'nhl') normalizedSport = 'icehockey_nhl';

        const result = await api.get(`/api/signals/freshness?sport=${normalizedSport}`);
        if (!cancelled && result?.data) {
          setData(result.data);
          setIsLoading(false);
        }
      } catch (err) {
        // silently ignore freshness poll errors
        if (!cancelled) setIsLoading(false);
      }
    }

    load();
    const id = setInterval(load, 30_000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [sport]);

  return { data, isLoading };
}
