"use client";

import React, { Suspense } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSport } from "@/hooks/useSport";
import { API_BASE } from "@/lib/api";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import SportSelector from "@/components/shared/SportSelector";
import { Zap, Flame, Clock, TrendingUp, BarChart3 } from "lucide-react";
import { clsx } from "clsx";

export default function StreaksPage() {
  return (
    <Suspense fallback={<div className="p-6 text-white font-black italic uppercase tracking-widest animate-pulse font-display text-center py-24">TRACKING MOMENTUM...</div>}>
      <StreaksContent />
    </Suspense>
  );
}

function StreaksContent() {
  const { sport } = useSport();

  const { data: streaks, isLoading, error, refetch } = useQuery({
    queryKey: ['streaks', sport],
    queryFn: () => fetch(`${API_BASE}/api/streaks?sport=${sport}`).then(r => r.json()),
    refetchInterval: 120_000,
  });

  if (isLoading) {
    return (
      <div className="space-y-6 pt-6 px-4">
        <Skeleton className="h-10 w-48 mb-8" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <Skeleton key={i} className="h-44 w-full rounded-2xl" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return <div className="p-6"><ErrorBanner message="Streak Engine Offline." onRetry={refetch} /></div>;
  }

  const streakList = Array.isArray(streaks) ? streaks : streaks?.results || [];

  return (
    <div className="pb-24 space-y-8 pt-6 px-4">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-brand-warning/10 p-2 rounded-lg border border-brand-warning/20">
              <Flame size={24} className="text-brand-warning shadow-glow shadow-brand-warning/40 animate-pulse" />
            </div>
            <h1 className="text-3xl font-black italic tracking-tighter uppercase text-white font-display">Player Streaks</h1>
          </div>
          <p className="text-[10px] text-textMuted font-black uppercase tracking-widest mb-4 italic">Recent Momentum & Consistency Tracking</p>
          <SportSelector />
        </div>
        <div className="text-right">
          <div className="text-[9px] font-black text-textMuted uppercase tracking-widest flex items-center justify-end gap-1.5">
            <Clock size={12} className="text-brand-warning" />
            Scan: 120s
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {streakList.map((streak: any, i: number) => (
          <div key={i} className="bg-lucrix-surface border border-lucrix-border rounded-2xl p-6 hover:border-brand-warning/30 transition-all group relative overflow-hidden flex flex-col shadow-card">
            <div className="flex justify-between items-start mb-6">
              <div>
                <div className="text-lg font-black text-white font-display italic uppercase tracking-tight group-hover:text-brand-warning transition-colors">{streak.player}</div>
                <div className="text-[10px] font-bold text-textSecondary uppercase tracking-widest mt-1">
                  {streak.market} — Over {streak.line}
                </div>
              </div>
              <div className="bg-lucrix-dark p-2 rounded-lg border border-lucrix-border group-hover:bg-brand-warning/10 transition-colors">
                <BarChart3 size={18} className="text-brand-warning" />
              </div>
            </div>

            <div className="flex items-end justify-between mt-auto">
              <div className="space-y-1">
                <div className="text-[9px] font-black text-textMuted uppercase tracking-widest">Active Streak</div>
                <div className="flex items-center gap-2">
                  <span className="text-3xl font-black text-white font-display italic">{streak.count} Games</span>
                  <Zap size={20} className="text-brand-warning fill-brand-warning animate-bounce" />
                </div>
              </div>
              <div className="text-right">
                <div className="text-[9px] font-black text-textMuted uppercase tracking-widest mb-1">Upcoming</div>
                <div className="text-xs font-bold text-white flex items-center gap-1.5 justify-end">
                  vs {streak.opponent} <Clock size={10} className="text-brand-warning" />
                </div>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-lucrix-border flex gap-1">
              {[...Array(5)].map((_, j) => (
                <div 
                  key={j} 
                  className={clsx(
                    "flex-1 h-1.5 rounded-full",
                    j < streak.count ? "bg-brand-warning shadow-glow shadow-brand-warning/40" : "bg-lucrix-dark"
                  )} 
                />
              ))}
            </div>
          </div>
        ))}
        {streakList.length === 0 && (
          <div className="col-span-full text-center py-24 text-textMuted font-black uppercase italic tracking-widest">
            Scanning for consecutive performance outliers...
          </div>
        )}
      </div>
    </div>
  );
}
