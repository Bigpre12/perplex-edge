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
};

function edgeToSignal(edge: number): ScannerRow["signal"] {
  if (edge >= 8) return "SHARP";
  if (edge >= 5) return "CLV";
  if (edge >= 2) return "EV+";
  return "FADE";
}

export function useScannerFeed(sport: string) {
  const normalizedSport = normalizeSportKey(sport);
  const query = useBackendData<any>("/api/props", {
    params: { sport: normalizedSport },
    pollMs: 30_000,
  });

  const rows = useMemo<ScannerRow[]>(() => {
    const data = unwrapList<any>(query.data);
    const mapped = data.map((r: any, idx: number) => {
      const edge = Number(r?.ev_value ?? r?.ev_percentage ?? 0) || 0;
      return {
        id: String(r?.id ?? `${r?.player_name ?? "row"}-${idx}`),
        player: r?.player_name ?? "—",
        market: r?.market_label ?? r?.market_key ?? "—",
        line: r?.line != null ? String(r.line) : "—",
        bookOdds: r?.book_odds != null ? String(r.book_odds) : "—",
        fairValue: r?.fair_value != null ? String(r.fair_value) : "—",
        edgePct: Math.abs(edge),
        signal: edgeToSignal(edge),
      };
    });
    mapped.sort((a, b) => Math.abs(b.edgePct) - Math.abs(a.edgePct));
    return mapped;
  }, [query.data]);

  return { ...query, rows };
}

