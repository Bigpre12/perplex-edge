"use client";

import React, { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, RefreshCw } from "lucide-react";
import { useLucrixStore } from "@/store";
import { useDataFreshness } from "@/context/DataFreshnessContext";
import { useSport } from "@/context/SportContext";

/**
 * Shows when /api/health/deps reports partial or severe degradation.
 * Uses DataFreshnessContext for a single health poll shared with the rest of the app.
 */
export default function DataDegradationBanner() {
  const backendOnline = useLucrixStore((s: { backendOnline: boolean }) => s.backendOnline);
  const queryClient = useQueryClient();
  const { selectedSport } = useSport();
  const {
    degradationLevel,
    degradation,
    stalenessLabel,
    refetch: refetchFreshness,
    raw,
  } = useDataFreshness();
  const q = raw?.components?.odds_quota;
  const quotaExhausted = Boolean(q?.is_exhausted);
  const quotaIngestBlocked = Boolean(q?.ingest_blocked);
  const [syncing, setSyncing] = useState(false);

  const level = degradationLevel;
  if (!backendOnline || level === "none") return null;

  const msg =
    degradation?.user_message ||
    (level === "severe"
      ? "Market data may be stale or incomplete."
      : "Market data is partially delayed.");

  const bar =
    level === "severe"
      ? "bg-amber-500/15 border-amber-500/35 text-amber-200"
      : "bg-brand-cyan/10 border-brand-cyan/25 text-brand-cyan/90";

  const sport =
    !selectedSport || selectedSport === "all"
      ? "basketball_nba"
      : selectedSport;

  const forceSync = async () => {
    if (quotaExhausted || quotaIngestBlocked) return;
    setSyncing(true);
    try {
      await fetch(
        `/api/sync/odds?sport=${encodeURIComponent(sport)}`,
        { method: "POST" }
      );
      await queryClient.invalidateQueries();
      await refetchFreshness();
    } finally {
      setSyncing(false);
    }
  };

  return (
    <div
      className={`w-full border-b px-4 py-2 text-[11px] font-semibold flex flex-wrap items-center gap-x-3 gap-y-2 ${bar}`}
      role="status"
    >
      <div className="flex items-center gap-2 min-w-0 flex-1">
        <AlertTriangle className="shrink-0 size-4 opacity-90" />
        <span className="uppercase tracking-wide font-black text-[10px] shrink-0">
          {level}
        </span>
        <span className="font-medium normal-case tracking-normal min-w-0">
          {msg}
        </span>
      </div>
      {stalenessLabel ? (
        <span className="text-[10px] font-medium normal-case opacity-90 whitespace-nowrap">
          Last synced: {stalenessLabel}
        </span>
      ) : null}
      <button
        type="button"
        onClick={() => void forceSync()}
        disabled={syncing || quotaExhausted || quotaIngestBlocked}
        title={
          quotaExhausted
            ? "Quota exhausted — sync disabled until next billing cycle"
            : quotaIngestBlocked
              ? "Ingest paused (quota guard) — sync disabled"
              : undefined
        }
        className="shrink-0 flex items-center gap-1.5 px-3 py-1 rounded-lg bg-black/25 border border-current/20 text-[10px] font-black uppercase tracking-widest hover:bg-black/40 disabled:opacity-50"
      >
        <RefreshCw className={`size-3 ${syncing ? "animate-spin" : ""}`} />
        Force sync
      </button>
    </div>
  );
}
