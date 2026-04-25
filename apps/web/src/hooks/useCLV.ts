"use client";

import { useBackendData } from "@/hooks/useBackendData";
import { normalizeSportKey } from "@/constants/sports";

export function useCLV(sport: string, date: string) {
  return useBackendData<any>("/api/clv/summary", {
    params: { sport: normalizeSportKey(sport), date },
    pollMs: 60_000,
  });
}
