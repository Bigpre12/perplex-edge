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

  const isStale = (ts: string | null, thresholdSec: number) => {
    if (!ts) return true;
    const diffSec = (Date.now() - new Date(ts).getTime()) / 1000;
    return diffSec > thresholdSec;
  };

  const oddsStale = isStale(oddsTs, 14400); // 4 hours
  const evStale = isStale(evTs, 14400);

  return (
    <div className="flex gap-4 text-[10px] items-center font-medium opacity-80 mt-1">
      <div className="flex items-center gap-1.5">
        <span className={`w-1.5 h-1.5 rounded-full ${oddsStale ? "bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]" : "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"}`} />
        <span className={oddsStale ? "text-red-400" : "text-emerald-400"}>
          ODDS {oddsStale ? "STALE" : "LIVE"} · {timeAgo(oddsTs)}
        </span>
      </div>
      <div className="flex items-center gap-1.5">
        <span className={`w-1.5 h-1.5 rounded-full ${evStale ? "bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]" : "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"}`} />
        <span className={evStale ? "text-red-400" : "text-emerald-400"}>
          EV {evStale ? "STALE" : "LIVE"} · {timeAgo(evTs)}
        </span>
      </div>
    </div>
  );
}
