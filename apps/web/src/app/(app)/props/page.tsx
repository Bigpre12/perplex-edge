"use client";

import React, { useState, Suspense } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSearchParams } from "next/navigation";
import { useSport } from "@/hooks/useSport";
import { useTierGate } from "@/hooks/useTierGate";
import { API_BASE } from "@/lib/apiConfig";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import SportSelector from "@/components/shared/SportSelector";
import { Trophy, Star, Zap, Clock } from "lucide-react";
import { clsx } from "clsx";

export default function PropsPage() {
  return (
    <Suspense fallback={<div className="p-6 text-white font-black italic uppercase tracking-widest animate-pulse font-display text-center py-24">BOOTING INTEL...</div>}>
      <PropsPageContent />
    </Suspense>
  );
}

function PropsPageContent() {
  const { sport } = useSport();
  const searchParams = useSearchParams();
  
  const market = searchParams.get("market") || "";
  const date = searchParams.get("date") || new Date().toISOString().split('T')[0];

  const { data: propsData, isLoading, error, refetch } = useQuery({
    queryKey: ['props', sport, market, date],
    queryFn: () => fetch(`${API_BASE}/api/props?sport=${sport}&market=${market}&date=${date}`).then(async (r) => {
      if (!r.ok) {
        if (r.status === 403) throw new Error("403");
        throw new Error(`API Error: ${r.statusText}`);
      }
      return r.json();
    }),
    refetchInterval: 60_000,
    staleTime: 30_000
  });

  const { data: limitedData, isLocked, isLoading: isGateLoading } = useTierGate(
    { data: propsData, isLoading, error },
    { requiredTier: "pro" }
  );

  // If free tier, we only show top 10 if not locked by API
  const displayData = isLocked ? [] : (limitedData?.slice(0, 50) || propsData?.slice(0, 10) || []);

  if (isLoading || isGateLoading) {
    return (
      <div className="space-y-6 pt-6 px-4">
        <div className="flex justify-between items-center mb-8">
          <Skeleton className="h-10 w-48" />
          <Skeleton className="h-10 w-32" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {[...Array(8)].map((_, i) => (
            <Skeleton key={i} className="h-64 w-full rounded-2xl" />
          ))}
        </div>
      </div>
    );
  }

  if (error && !isLocked) {
    return <div className="p-6"><ErrorBanner message={error?.message} onRetry={refetch} /></div>;
  }

  return (
    <div className="pb-24 space-y-8 pt-6 px-4">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-brand-cyan/10 p-2 rounded-lg border border-brand-cyan/20">
              <Trophy size={24} className="text-brand-cyan shadow-glow shadow-brand-cyan" />
            </div>
            <h1 className="text-3xl font-black italic tracking-tighter uppercase font-display text-white">Props Board</h1>
          </div>
          <p className="text-[10px] text-textMuted font-black uppercase tracking-widest mb-4 italic">Institutional Player Prop Decisioning</p>
          <SportSelector />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {displayData.map((prop: any, i: number) => (
          <PropCard key={i} prop={prop} />
        ))}
      </div>

      {isLocked && (
        <div className="mt-12 p-12 text-center bg-gradient-to-b from-brand-cyan/10 to-transparent border border-brand-cyan/20 rounded-2xl relative overflow-hidden group cursor-pointer" onClick={() => window.location.href = "/subscription"}>
          <div className="relative z-10">
            <Star size={40} className="mx-auto text-brand-cyan mb-4 animate-pulse shadow-glow shadow-brand-cyan" />
            <h3 className="text-2xl font-black italic uppercase tracking-tighter mb-2 text-white font-display">
              Advanced Intel Locked
            </h3>
            <p className="text-textSecondary text-sm max-w-md mx-auto mb-8 font-bold">
              Upgrade to Pro or Elite to Reveal All sharp edges and model predictions for player props.
            </p>
            <button className="bg-brand-cyan hover:bg-brand-cyan/90 text-black px-10 py-4 rounded-xl font-black uppercase tracking-widest text-sm transition-all shadow-glow shadow-brand-cyan/50">
              Unlock All Intel →
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function PropCard({ prop }: { prop: any }) {
  return (
    <div className="bg-lucrix-surface border border-lucrix-border rounded-2xl p-6 transition-all group shadow-card hover:border-brand-cyan/30 flex flex-col justify-between">
      <div>
        <div className="flex justify-between items-start mb-6">
          <div>
            <div className="text-lg font-black tracking-tight text-white font-display italic uppercase">{prop.player_name}</div>
            <div className="text-[10px] font-black uppercase text-brand-cyan tracking-widest mt-1">
              {prop.market || prop.stat_type?.replace('_', ' ') || "POINTS"}
            </div>
          </div>
          <div className="text-right">
            <div className="text-[8px] font-black text-textMuted uppercase tracking-widest">Slate</div>
            <div className="text-xs font-bold text-textSecondary">{prop.sport?.toUpperCase()}</div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <PriceBox side="OVER" line={prop.line} odds={prop.over_odds} book={prop.best_over_book} />
          <PriceBox side="UNDER" line={prop.line} odds={prop.under_odds} book={prop.best_under_book} />
        </div>
      </div>

      <div className="mt-6 pt-4 border-t border-lucrix-border flex items-center justify-between">
        <div className="flex items-center gap-1.5 text-[9px] font-black text-textMuted uppercase tracking-widest">
          <Clock size={10} />
          {prop.last_updated ? new Date(prop.last_updated).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'LIVE'}
        </div>
        <button className="text-[9px] font-black uppercase tracking-widest text-brand-cyan border border-brand-cyan/20 bg-brand-cyan/10 px-2 py-1 rounded-sm">
          Edge: {prop.edge || '0.0%'}
        </button>
      </div>
    </div>
  );
}

function PriceBox({ side, line, odds, book }: any) {
  return (
    <div className="bg-lucrix-dark border border-lucrix-border/50 rounded-xl p-3">
      <div className="text-[9px] font-black text-textMuted uppercase tracking-widest mb-1">{side}</div>
      <div className="text-xl font-black text-white font-display leading-none mb-1">{line || '—'}</div>
      <div className="flex items-center justify-between">
        <span className={clsx("font-mono font-black text-xs", odds > 0 ? "text-brand-success" : "text-brand-danger")}>
          {odds > 0 ? `+${odds}` : odds || '—'}
        </span>
        <span className="text-[8px] font-black uppercase text-textMuted tracking-tighter truncate max-w-[40px]">{book || 'PINN'}</span>
      </div>
    </div>
  );
}
