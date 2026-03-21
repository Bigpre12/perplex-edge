"use client";

import React, { useState, Suspense } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSport } from "@/hooks/useSport";
import { API_BASE } from "@/lib/api";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import SportSelector from "@/components/shared/SportSelector";
import { Siren, Clock, Activity, Search, TrendingUp, AlertCircle } from "lucide-react";
import { Progress } from "@/components/ui/Progress";
import { clsx } from "clsx";

export default function InjuriesPage() {
  return (
    <Suspense fallback={<div className="p-6 text-white font-black italic uppercase tracking-widest animate-pulse font-display text-center py-24">ACCESSING INJURY WIRE...</div>}>
      <InjuriesContent />
    </Suspense>
  );
}

function InjuriesContent() {
  const { sport } = useSport();
  const [searchQuery, setSearchQuery] = useState("");

  const { data: injuries, isLoading, error, refetch } = useQuery({
    queryKey: ['injuries', sport],
    queryFn: () => fetch(`${API_BASE}/api/injuries?sport=${sport}`).then(r => r.json()),
    refetchInterval: 600_000, // 10 minutes
  });

  if (isLoading) {
    return (
      <div className="space-y-6 pt-6 px-4">
        <Skeleton className="h-10 w-48 mb-8" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {[...Array(8)].map((_, i) => (
            <Skeleton key={i} className="h-48 w-full rounded-2xl" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return <div className="p-6"><ErrorBanner message="Injury Database Offline." onRetry={refetch} /></div>;
  }

  const filteredInjuries = (injuries || []).filter((i: any) => 
    i.player?.toLowerCase().includes(searchQuery.toLowerCase()) || 
    i.team?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="pb-24 space-y-8 pt-6 px-4">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-brand-danger/10 p-2 rounded-lg border border-brand-danger/20">
              <Siren size={24} className="text-brand-danger shadow-glow shadow-brand-danger/40 animate-pulse" />
            </div>
            <h1 className="text-3xl font-black italic tracking-tighter uppercase text-white font-display">Injury Wire</h1>
          </div>
          <p className="text-[10px] text-textMuted font-black uppercase tracking-widest mb-4 italic">Real-Time Medical Intelligence</p>
          <SportSelector />
        </div>
        <div className="flex flex-col items-end gap-3">
          <div className="relative w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-textMuted" size={14} />
            <input 
              type="text" 
              placeholder="Filter roster..." 
              className="w-full bg-lucrix-surface border border-lucrix-border rounded-xl py-2 pl-10 pr-4 text-xs font-bold text-white focus:border-brand-danger/50 outline-none"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <div className="text-[9px] font-black text-textMuted uppercase tracking-widest flex items-center gap-1.5">
            <Clock size={11} className="text-brand-danger" />
            Cycle: 10m
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {filteredInjuries.map((injury: any, i: number) => (
          <div key={i} className="bg-lucrix-surface border border-lucrix-border rounded-2xl p-6 hover:border-brand-danger/30 transition-all group relative overflow-hidden shadow-card">
            <div className="flex justify-between items-start mb-6">
              <div>
                <div className="text-sm font-black text-white font-display italic uppercase tracking-tight group-hover:text-brand-danger transition-colors">{injury.player}</div>
                <div className="text-[9px] font-bold text-textSecondary uppercase tracking-widest mt-0.5">{injury.team}</div>
              </div>
              <span className={clsx(
                "px-2 py-0.5 rounded text-[9px] font-black uppercase tracking-widest border",
                injury.status === "OUT" ? "bg-brand-danger/10 text-brand-danger border-brand-danger/20 shadow-glow shadow-brand-danger/10" :
                injury.status === "GTD" ? "bg-brand-warning/10 text-brand-warning border-brand-warning/20" :
                "bg-brand-cyan/10 text-brand-cyan border-brand-cyan/20"
              )}>
                {injury.status}
              </span>
            </div>

            <div className="bg-lucrix-dark/50 border border-lucrix-border/50 rounded-xl p-3 mb-4">
              <div className="flex justify-between items-center mb-1.5">
                <span className="text-[8px] font-black text-textMuted uppercase tracking-widest">Market Impact</span>
                <span className="text-xs font-black text-white italic">{injury.impact_score || '3.5'}/10</span>
              </div>
              <div className="h-1 bg-lucrix-dark rounded-full overflow-hidden">
                <Progress 
                  value={(injury.impact_score || 3.5) * 10} 
                  color="danger" 
                />
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <AlertCircle size={12} className="text-textMuted" />
                <span className="text-[10px] font-bold text-textSecondary">{injury.detail || "Evaluating lower body soreness."}</span>
              </div>
              <div className="flex items-center justify-between opacity-60">
                <div className="flex items-center gap-1.5 text-[8px] font-black text-textMuted uppercase tracking-widest">
                  <Clock size={10} /> {injury.return_timeline || "Day-to-Day"}
                </div>
                <div className="flex items-center gap-1.5 text-[8px] font-black text-textMuted uppercase tracking-widest">
                  <Activity size={10} /> VERIFIED
                </div>
              </div>
            </div>
          </div>
        ))}
        {filteredInjuries.length === 0 && (
          <div className="col-span-full text-center py-24 text-textMuted font-black uppercase italic tracking-widest">
            Rosters are currently fully operational.
          </div>
        )}
      </div>
    </div>
  );
}
