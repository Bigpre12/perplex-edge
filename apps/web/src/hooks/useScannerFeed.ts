import { useMemo } from "react";
import { useBackendData } from "@/hooks/useBackendData";
import { unwrapList } from "@/lib/contracts";
import { normalizeSportKey } from "@/constants/sports";

export type ScannerRow = {
  id: string;
  player: string;
  market: string;
  line: string;
  bookOdds: string;
  fairValue: string;
  edgePct: number;
  signal: "SHARP" | "CLV" | "EV+" | "FADE";
  recommendation?: string;
  tier?: string;
};

export function useScannerFeed(sport: string) {
  const normalizedSport = normalizeSportKey(sport);
  const query = useBackendData<any>("/api/scanner", {
    params: { sport: normalizedSport, min_ev: 2.0 },
    pollMs: 30_000,
  });

  const rows = useMemo<ScannerRow[]>(() => {
    // Backend returns { status: "ok", data: [...] }
    const responseData = query.data;
    if (!responseData || responseData.status !== "ok") return [];
    
    const data = unwrapList<any>(responseData.data);
    return data.map((r: any) => ({
      id: r.id,
      player: r.player || "—",
      market: r.market || "—",
      line: r.line != null ? String(r.line) : "—",
      bookOdds: r.bookOdds || "—",
      fairValue: r.fairValue != null ? String(r.fairValue) : "—",
      edgePct: r.edgePct || 0,
      signal: (r.signal as any) || "EV+",
      recommendation: r.recommendation,
      tier: r.tier
    }));
  }, [query.data]);

  return { ...query, rows };
}
