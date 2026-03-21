"use client";

import React, { Suspense } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSport } from "@/hooks/useSport";
import { API_BASE } from "@/lib/api";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import SportSelector from "@/components/shared/SportSelector";
import { Target, Clock, TrendingUp, BarChart, Percent } from "lucide-react";
import { clsx } from "clsx";

export default function HitRatePage() {
  return (
    <Suspense fallback={<div className="p-6 text-white font-black italic uppercase tracking-widest animate-pulse font-display text-center py-24">CALCULATING HIT RATES...</div>}>
      <HitRateContent />
    </Suspense>
  );
}

function HitRateContent() {
  const { sport } = useSport();

  const { data: hitRateData, isLoading, error, refetch } = useQuery({
    queryKey: ['hit-rate', sport],
    queryFn: () => fetch(`${API_BASE}/api/hit-rate?sport=${sport}`).then(r => r.json()),
    refetchInterval: 300_000, // 5 minutes
  });

  if (isLoading) {
    return (
      <div className="space-y-6 pt-6 px-4">
        <Skeleton className="h-10 w-48 mb-8" />
        <div className="space-y-4">
          {[...Array(8)].map((_, i) => (
            <Skeleton key={i} className="h-20 w-full rounded-2xl" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return <div className="p-6"><ErrorBanner message="Hit Rate Engine Offline." onRetry={refetch} /></div>;
  }

  const results = hitRateData?.results || [];

  return (
    <div className="pb-24 space-y-8 pt-6 px-4">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-brand-success/10 p-2 rounded-lg border border-brand-success/20">
              <Target size={24} className="text-brand-success shadow-glow shadow-brand-success/40" />
            </div>
            <h1 className="text-3xl font-black italic tracking-tighter uppercase text-white font-display">Hit Rate analysis</h1>
          </div>
          <p className="text-[10px] text-textMuted font-black uppercase tracking-widest mb-4 italic">Historical Frequency & Regression</p>
          <SportSelector />
        </div>
        <div className="text-right">
          <div className="text-[9px] font-black text-textMuted uppercase tracking-widest flex items-center justify-end gap-1.5">
            <Clock size={12} className="text-brand-success" />
            Refresh: 5m
          </div>
        </div>
      </div>

      <div className="bg-lucrix-surface border border-lucrix-border rounded-2xl overflow-hidden shadow-card">
        <table className="w-full text-left">
          <thead>
            <tr className="bg-lucrix-dark/80 border-b border-lucrix-border text-[9px] font-black uppercase tracking-widest text-textMuted">
              <th className="px-6 py-4">Player / Team</th>
              <th className="px-6 py-4 text-center">Market</th>
              <th className="px-6 py-4 text-center">L5 Hit</th>
              <th className="px-6 py-4 text-center">L10 Hit</th>
              <th className="px-6 py-4 text-center">Season Hit</th>
              <th className="px-6 py-4 text-right">Trend</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-lucrix-border/50">
            {results.map((row: any, i: number) => (
              <tr key={i} className="group hover:bg-lucrix-dark/50 transition-colors">
                <td className="px-6 py-5">
                  <div className="font-black text-white font-display italic uppercase tracking-tight">{row.player}</div>
                  <div className="text-[10px] font-bold text-textSecondary uppercase tracking-widest mt-0.5">{row.team}</div>
                </td>
                <td className="px-6 py-5 text-center font-mono font-black text-white text-xs">
                  {row.market} {row.line}
                </td>
                <td className="px-6 py-5 text-center">
                  <HitCircle value={row.l5} total={5} />
                </td>
                <td className="px-6 py-5 text-center">
                  <HitBadge value={row.l10_pct} />
                </td>
                <td className="px-6 py-5 text-center">
                  <HitBadge value={row.season_pct} />
                </td>
                <td className="px-6 py-5 text-right">
                  <div className={clsx(
                    "inline-flex items-center gap-1 text-[10px] font-black italic uppercase tracking-widest",
                    row.trend === "UP" ? "text-brand-success" : "text-brand-danger"
                  )}>
                    {row.trend === "UP" ? <TrendingUp size={12} /> : <BarChart size={12} className="rotate-180" />}
                    {row.trend}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function HitBadge({ value }: { value: number }) {
  return (
    <span className={clsx(
      "font-mono font-black text-sm",
      value >= 70 ? "text-brand-success" : value >= 50 ? "text-brand-warning" : "text-brand-danger"
    )}>
      {value}%
    </span>
  );
}

function HitCircle({ value, total }: { value: number, total: number }) {
  return (
    <div className="flex items-center justify-center gap-1">
      {[...Array(total)].map((_, i) => (
        <div 
          key={i} 
          className={clsx(
            "w-1.5 h-1.5 rounded-full border",
            i < value ? "bg-brand-success border-brand-success shadow-glow shadow-brand-success/40" : "bg-lucrix-dark border-lucrix-border"
          )} 
        />
      ))}
      <span className="text-[10px] font-black text-textMuted ml-1">{value}/{total}</span>
    </div>
  );
}
