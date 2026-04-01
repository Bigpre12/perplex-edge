"use client";

import React, { Suspense, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSport } from "@/hooks/useSport";
import { API, isApiError } from "@/lib/api";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import SportSelector from "@/components/shared/SportSelector";
import { BrainCircuit, Zap, ShieldCheck, Activity, Target, TrendingUp } from "lucide-react";
import { Progress } from "@/components/ui/Progress";
import { clsx } from "clsx";
import type { LucideIcon } from "lucide-react";

import { UpgradeGate } from "@/components/UpgradeGate";

export default function BrainPage() {
  return (
    <Suspense fallback={<div className="p-6 text-white font-black italic uppercase tracking-widest animate-pulse font-display text-center py-24">BOOTING NEURAL ENGINE...</div>}>
      <UpgradeGate feature="neuralBrain">
        <BrainContent />
      </UpgradeGate>
    </Suspense>
  );
}

function BrainContent() {
  const { sport } = useSport();

  const { data: brainData, isLoading: brainLoading, error: brainError, refetch: refetchBrain, dataUpdatedAt: brainUpdatedAt } = useQuery({
    queryKey: ['brain', sport],
    queryFn: async () => {
      const res = await API.brain.status();
      if (isApiError(res)) throw res;
      return res;
    },
    refetchInterval: 30_000,
  });

  const { data: smartMoney, isLoading: smartLoading, dataUpdatedAt: smartUpdatedAt } = useQuery({
    queryKey: ['smart-money', sport],
    queryFn: async () => {
      const res = await API.recentIntel(sport);
      if (isApiError(res)) return { aligned_props: [] };
      return res.data || res;
    },
    refetchInterval: 30_000,
  });

  const lastSync = brainUpdatedAt ? new Date(brainUpdatedAt).toLocaleTimeString() : 'N/A';

  if (brainLoading || smartLoading) {
    return (
      <div className="space-y-6 pt-6 px-4">
        <Skeleton className="h-10 w-48 mb-8" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <Skeleton key={i} className="h-56 w-full rounded-2xl" />
          ))}
        </div>
      </div>
    );
  }

  if (brainError) {
    return <div className="p-6"><ErrorBanner message="Neural Core Overload." onRetry={refetchBrain} /></div>;
  }

  const props = brainData?.props || [];

  return (
    <div className="pb-24 space-y-8 pt-6 px-4">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-brand-purple/10 p-2 rounded-lg border border-brand-purple/20">
              <BrainCircuit size={24} className="text-brand-purple shadow-glow shadow-brand-purple/40" />
            </div>
            <h1 className="text-3xl font-black italic tracking-tighter uppercase text-white font-display">Neural Engine</h1>
          </div>
          <p className="text-[10px] text-textMuted font-black uppercase tracking-widest mb-4 italic">Quantitative Model Aggregation</p>
          <SportSelector />
        </div>
        <div className="flex gap-4">
          <StatBadge 
            label={"Neural Sync: " + lastSync}
            value={brainData?.status?.overall_status === "ACTIVE" ? "ACTIVE" : "OFFLINE"} 
            icon={<BrainCircuit size={12} />} 
            color={brainData?.status?.overall_status === "ACTIVE" ? "text-brand-success" : "text-brand-danger"}
          />
          <StatBadge 
            label="Live Data Volume" 
            value={brainData?.status?.metrics?.live_volume ? `${(brainData.status.metrics.live_volume / 100).toFixed(1)}k` : "0"} 
            icon={<Zap size={12} />} 
            color="text-brand-warning" 
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {props.map((prop: { id: string; player: string; market: string; line: string; score: number; reasoning: string; projection: string; recommendation: string }, i: number) => {
          const isSmartAligned = (smartMoney as any)?.aligned_props?.includes(prop.id);
          
          return (
            <div key={i} className="bg-lucrix-surface border border-lucrix-border rounded-2xl p-6 hover:border-brand-purple/30 transition-all group relative overflow-hidden shadow-card">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <div className="text-lg font-black text-white font-display italic uppercase tracking-tight group-hover:text-brand-purple transition-colors">{prop.player}</div>
                  <div className="text-[10px] font-bold text-textSecondary uppercase tracking-widest mt-1">
                    {prop.market} — {prop.line}
                  </div>
                </div>
                {isSmartAligned && (
                  <div className="bg-brand-cyan/10 px-2 py-1 rounded border border-brand-cyan/20 flex items-center gap-1.5 animate-pulse">
                    <ShieldCheck size={12} className="text-brand-cyan" />
                    <span className="text-[8px] font-black text-brand-cyan uppercase tracking-widest">Sharp Aligned</span>
                  </div>
                )}
              </div>

              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-[9px] font-black uppercase tracking-widest mb-2">
                    <span className="text-textMuted">Model Confidence</span>
                    <span className={clsx(
                      prop.score >= 75 ? "text-brand-success" : prop.score >= 50 ? "text-brand-warning" : "text-brand-danger"
                    )}>{prop.score}%</span>
                  </div>
                  <div className="h-1.5 bg-lucrix-dark rounded-full overflow-hidden border border-lucrix-border/50">
                    <Progress 
                      value={prop.score} 
                      color={prop.score >= 75 ? "success" : prop.score >= 50 ? "warning" : "danger"} 
                    />
                  </div>
                </div>

                <div className="bg-lucrix-dark/50 rounded-xl p-3 border border-lucrix-border/50">
                  <p className="text-[11px] text-textSecondary font-bold italic leading-relaxed">
                    "{prop.reasoning || "Neural models detect high-volume correlation between opening markets and historical player performance."}"
                  </p>
                </div>
              </div>

              <div className="mt-6 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 bg-lucrix-dark rounded-lg border border-lucrix-border">
                    <Target size={12} className="text-textMuted" />
                  </div>
                  <span className="text-[9px] font-black text-textMuted uppercase tracking-widest">Projection: {prop.projection}</span>
                </div>
                <button className={clsx(
                  "px-4 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all",
                  prop.recommendation === "OVER" ? "bg-brand-success/10 text-brand-success border border-brand-success/20" : "bg-brand-danger/10 text-brand-danger border border-brand-danger/20"
                )}>
                  {prop.recommendation}
                </button>
              </div>
            </div>
          );
        })}

        {props.length === 0 && (
          <div className="col-span-full text-center py-24 text-textMuted font-black uppercase italic tracking-widest">
            Neural Engine is calculating the next wave of edges...
          </div>
        )}
      </div>
    </div>
  );
}

function StatBadge({ label, value, icon, color = "text-brand-purple" }: { label: string; value: string; icon: React.ReactNode; color?: string }) {
  return (
    <div className="bg-lucrix-surface border border-lucrix-border rounded-xl px-4 py-2 flex items-center gap-3">
      <div className={clsx("p-1.5 bg-lucrix-dark rounded border border-lucrix-border", color)}>
        {icon}
      </div>
      <div>
        <div className="text-[8px] font-black text-textMuted uppercase tracking-widest">{label}</div>
        <div className="text-sm font-black text-white italic">{value}</div>
      </div>
    </div>
  );
}
