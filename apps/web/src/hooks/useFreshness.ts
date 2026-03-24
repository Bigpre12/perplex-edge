"use client";
// apps/web/src/hooks/useFreshness.ts
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type Freshness = {
  odds_last_updated: string | null;
  ev_last_updated: string | null;
  server_time: string;
};

export function useFreshness(sport: string) {
  const [data, setData] = useState<Freshness | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const result = await api.freshness(sport);
        if (!cancelled) {
          setData(result?.data ?? result);
        }
      } catch (err) {
        // silently ignore freshness poll errors
      }
    }

    load();
    const id = setInterval(load, 30_000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [sport]);

  return data;
}
