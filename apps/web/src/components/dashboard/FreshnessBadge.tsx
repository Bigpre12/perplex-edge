// apps/web/src/components/FreshnessBadge.tsx
"use client";

import React from "react";

function timeAgo(ts: string | null): string {
  if (!ts) return "Not yet synced";
  const then = new Date(ts).getTime();
  const diffSec = Math.floor((Date.now() - then) / 1000);
  
  if (diffSec < 30) return "just now";
  if (diffSec < 60) return `${diffSec}s ago`;
  
  const min = Math.floor(diffSec / 60);
  if (min < 60) return `${min}m ago`;
  
  const hours = Math.floor(min / 60);
  if (hours < 24) return `${hours}h ago`;
  
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

function ageMs(ts: string | null): number {
  if (!ts) return Infinity;
  return Math.max(0, Date.now() - new Date(ts).getTime());
}

const SIX_HOURS = 6 * 60 * 60 * 1000;
const TWENTY_FOUR_HOURS = 24 * 60 * 60 * 1000;

export function FreshnessBadge({ 
  oddsTs, 
  evTs, 
  isLoading 
}: { 
  oddsTs: string | null; 
  evTs: string | null;
  isLoading?: boolean;
}) {
  if (isLoading) {
    return (
      <div className="flex gap-4 text-[10px] items-center font-medium opacity-80 mt-1 animate-pulse">
        <div className="flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-brand-cyan shadow-[0_0_8px_rgba(34,211,238,0.5)]" />
          <span className="text-brand-cyan uppercase tracking-widest font-black italic">
            Connecting to Intel Stream...
          </span>
        </div>
      </div>
    );
  }

  const oddsAge = ageMs(oddsTs);
  const evAge = ageMs(evTs);

  // Tiered odds status
  const oddsCritical = oddsAge >= TWENTY_FOUR_HOURS;
  const oddsStale = oddsAge >= SIX_HOURS;
  const oddsFresh = !oddsStale;

  // EV status: if no EV timestamp but odds are fresh, show idle, not stale
  const evStale = evTs ? evAge >= SIX_HOURS : oddsStale;
  const evIdleNoTimestamp = !evTs && !oddsStale;

  return (
    <>
      {/* Critical banner: shown on every page when odds are > 24h stale */}
      {oddsCritical && (
        <div className="w-full bg-red-500/15 border border-red-500/30 rounded-xl px-4 py-3 mb-2 animate-pulse">
          <p className="text-red-400 text-xs font-black uppercase tracking-widest text-center">
            ⚠ MARKET DATA OFFLINE — All signals reflect stale odds. Do not use for live betting decisions.
          </p>
        </div>
      )}

      <div className="flex gap-4 text-[10px] items-center font-medium opacity-80 mt-1">
        {/* Odds badge */}
        <div className="flex items-center gap-1.5">
          <span className={`w-1.5 h-1.5 rounded-full ${
            oddsCritical
              ? "bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)] animate-pulse"
              : oddsStale
                ? "bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]"
                : "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"
          }`} />
          <span className={
            oddsCritical
              ? "text-red-400 animate-pulse font-black"
              : oddsStale
                ? "text-red-400"
                : "text-emerald-400"
          }>
            {oddsCritical
              ? `ODDS CRITICAL · ${timeAgo(oddsTs)}`
              : oddsStale
                ? `ODDS STALE · ${timeAgo(oddsTs)}`
                : `ODDS · LIVE`}
          </span>
        </div>

        {/* EV badge */}
        <div className="flex items-center gap-1.5">
          <span className={`w-1.5 h-1.5 rounded-full ${evStale ? "bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]" : "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"}`} />
          <span className={evStale ? "text-red-400" : "text-emerald-400"}>
            EV {evStale ? "STALE" : "LIVE"} ·{" "}
            {evIdleNoTimestamp
              ? "idle (no edges)"
              : timeAgo(evTs)}
          </span>
        </div>
      </div>
    </>
  );
}
