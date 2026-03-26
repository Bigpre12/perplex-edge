// apps/web/src/components/FreshnessBadge.tsx
"use client";

import React from "react";

function timeAgo(ts: string | null): string {
  if (!ts) return "Never";
  const then = new Date(ts).getTime();
  const diffSec = Math.floor((Date.now() - then) / 1000);
  if (diffSec < 30) return "just now";
  if (diffSec < 60) return `${diffSec}s ago`;
  const min = Math.floor(diffSec / 60);
  return `${min}m ago`;
}

export function FreshnessBadge({ oddsTs, evTs }: { oddsTs: string | null; evTs: string | null }) {
  console.log('freshness data:', { oddsTs, evTs });
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
