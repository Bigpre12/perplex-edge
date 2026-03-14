// apps/web/src/hooks/useFreshness.ts
import { useEffect, useState } from "react";

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
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const res = await fetch(`${baseUrl}/api/meta/freshness?sport=${sport}`);
      if (!res.ok) return;
      const json = await res.json();
      if (!cancelled) setData(json);
    }

    load();
    const id = setInterval(load, 30_000); // Poll every 30s
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [sport]);

  return data;
}
