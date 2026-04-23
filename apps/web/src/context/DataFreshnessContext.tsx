"use client";

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { formatDistanceToNow } from "date-fns";
import API, { isApiError } from "@/lib/api";
import { useLucrixStore } from "@/store";

export type OddsQuotaPayload = {
  month?: string;
  used?: number;
  remaining?: number | null;
  limit?: number;
  percent_used?: number;
  is_exhausted?: boolean;
  is_warning?: boolean;
  ingest_blocked?: boolean;
  ingest_block_reason?: string | null;
};

export type HealthDepsPayload = {
  degradation?: { level?: string; reasons?: string[]; user_message?: string };
  freshness?: { odds?: string | null; ev?: string | null };
  sync?: { last_odds_sync?: string | null; last_ev_sync?: string | null };
  components?: { odds_stream?: string | null; odds_quota?: OddsQuotaPayload | null };
};

export type DataFreshnessValue = {
  lastSyncedAt: Date | null;
  isStale: boolean;
  stalenessLabel: string;
  oddsStream: string | null;
  degradationLevel: string;
  degradation: HealthDepsPayload["degradation"] | null;
  raw: HealthDepsPayload | null;
  refetch: () => void;
};

const defaultValue: DataFreshnessValue = {
  lastSyncedAt: null,
  isStale: false,
  stalenessLabel: "",
  oddsStream: null,
  degradationLevel: "none",
  degradation: null,
  raw: null,
  refetch: () => {},
};

const DataFreshnessContext = createContext<DataFreshnessValue>(defaultValue);

export function DataFreshnessProvider({ children }: { children: React.ReactNode }) {
  const backendOnline = useLucrixStore((s: { backendOnline: boolean }) => s.backendOnline);
  const [raw, setRaw] = useState<HealthDepsPayload | null>(null);

  const load = useCallback(async () => {
    if (!backendOnline) {
      setRaw(null);
      return;
    }
    const res = await API.healthDeps();
    if (isApiError(res)) return;
    setRaw(res as HealthDepsPayload);
  }, [backendOnline]);

  useEffect(() => {
    void load();
    const id = window.setInterval(() => void load(), 30_000);
    return () => window.clearInterval(id);
  }, [load]);

  const value = useMemo((): DataFreshnessValue => {
    const level = String(raw?.degradation?.level ?? "none");
    const oss = String(raw?.components?.odds_stream ?? "").toUpperCase();
    const iso =
      raw?.freshness?.odds ||
      raw?.sync?.last_odds_sync ||
      null;
    let lastSyncedAt: Date | null = null;
    if (iso) {
      const d = new Date(iso);
      lastSyncedAt = Number.isFinite(d.getTime()) ? d : null;
    }

    const streamBad = ["STALE", "EMPTY", "ERROR"].includes(oss);
    const isStale = level !== "none" || streamBad;

    let stalenessLabel = "";
    if (lastSyncedAt) {
      try {
        const rel = formatDistanceToNow(lastSyncedAt, { addSuffix: true });
        const abs = lastSyncedAt.toLocaleString(undefined, {
          month: "short",
          day: "numeric",
          year: "numeric",
          hour: "numeric",
          minute: "2-digit",
        });
        stalenessLabel = `${rel} (${abs})`;
      } catch {
        stalenessLabel = "";
      }
    }

    return {
      lastSyncedAt,
      isStale,
      stalenessLabel,
      oddsStream: raw?.components?.odds_stream ?? null,
      degradationLevel: level,
      degradation: raw?.degradation ?? null,
      raw,
      refetch: load,
    };
  }, [raw, load]);

  return (
    <DataFreshnessContext.Provider value={value}>{children}</DataFreshnessContext.Provider>
  );
}

export function useDataFreshness() {
  return useContext(DataFreshnessContext);
}
