"use client";

import React, { Suspense } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSport } from "@/hooks/useSport";
import { API_BASE } from "@/lib/api";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import SportSelector from "@/components/shared/SportSelector";
import { Calendar, Clock, Tv, Users, TrendingUp } from "lucide-react";
import { clsx } from "clsx";

export default function SlatePage() {
  return (
    <Suspense fallback={<div className="p-6 text-white font-black italic uppercase tracking-widest animate-pulse font-display text-center py-24">LOADING DAILY SLATE...</div>}>
      <SlateContent />
    </Suspense>
  );
}

function SlateContent() {
  const { sport } = useSport();

  const { data: slateData, isLoading, error, refetch } = useQuery({
    queryKey: ['slate', sport],
    queryFn: () => fetch(`${API_BASE}/api/slate/today?sport=${sport}`).then(r => r.json()),
    refetchInterval: 300_000,
  });

  if (isLoading) {
    return (
      <div className="space-y-6 pt-6 px-4">
        <Skeleton className="h-10 w-48 mb-8" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <Skeleton key={i} className="h-48 w-full rounded-2xl" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return <div className="p-6"><ErrorBanner message="Slate Engine Offline." onRetry={refetch} /></div>;
  }

  const games = slateData?.games || [];

  return (
    <div className="pb-24 space-y-8 pt-6 px-4">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-brand-cyan/10 p-2 rounded-lg border border-brand-cyan/20">
              <Calendar size={24} className="text-brand-cyan shadow-glow shadow-brand-cyan/40" />
            </div>
            <h1 className="text-3xl font-black italic tracking-tighter uppercase text-white font-display">Daily Slate</h1>
          </div>
          <p className="text-[10px] text-textMuted font-black uppercase tracking-widest mb-4 italic">Full Schedule & Market Consensus</p>
          <SportSelector />
        </div>
        <div className="text-right">
          <div className="text-[9px] font-black text-textMuted uppercase tracking-widest flex items-center justify-end gap-1.5">
            <Clock size={12} className="text-brand-cyan" />
            Update Frequency: 5m
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {games.map((game: any, i: number) => (
          <div key={i} className="bg-lucrix-surface border border-lucrix-border rounded-2xl overflow-hidden hover:border-brand-cyan/30 transition-all group shadow-card">
            <div className="bg-lucrix-dark/50 p-4 border-b border-lucrix-border flex justify-between items-center">
              <div className="flex items-center gap-2 text-brand-cyan">
                <Clock size={14} />
                <span className="text-[10px] font-black uppercase tracking-widest">
                  {new Date(game.commence_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
              {game.broadcaster && (
                <div className="flex items-center gap-2 text-textMuted">
                  <Tv size={14} />
                  <span className="text-[10px] font-black uppercase tracking-widest">{game.broadcaster}</span>
                </div>
              )}
            </div>

            <div className="p-6 space-y-6">
              <div className="space-y-4">
                <TeamRow name={game.away_team} logo={game.away_logo} price={game.away_price} />
                <div className="flex items-center justify-center gap-4">
                  <div className="h-px bg-lucrix-border flex-1" />
                  <span className="text-[9px] font-black text-textMuted uppercase italic">VS</span>
                  <div className="h-px bg-lucrix-border flex-1" />
                </div>
                <TeamRow name={game.home_team} logo={game.home_logo} price={game.home_price} />
              </div>

              <div className="pt-4 border-t border-lucrix-border space-y-3">
                <div className="flex justify-between items-center text-[9px] font-black text-textMuted uppercase tracking-widest">
                  <span>Market Consensus</span>
                  <TrendingUp size={12} className="text-brand-success" />
                </div>
                <div className="flex gap-2">
                  <div className="flex-1 bg-lucrix-dark rounded-lg p-2 text-center border border-lucrix-border/50">
                    <div className="text-[8px] text-textMuted uppercase mb-1">Spread</div>
                    <div className="text-xs font-black text-white">{game.consensus_spread || "N/A"}</div>
                  </div>
                  <div className="flex-1 bg-lucrix-dark rounded-lg p-2 text-center border border-lucrix-border/50">
                    <div className="text-[8px] text-textMuted uppercase mb-1">Total</div>
                    <div className="text-xs font-black text-white">{game.consensus_total || "N/A"}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}

        {games.length === 0 && (
          <div className="col-span-full text-center py-24 text-textMuted font-black uppercase italic tracking-widest">
            No games scheduled for the current selection.
          </div>
        )}
      </div>
    </div>
  );
}

function TeamRow({ name, logo, price }: any) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-3">
        {logo ? (
          <img src={logo} alt={name} className="w-8 h-8 object-contain" />
        ) : (
          <div className="w-8 h-8 bg-lucrix-dark rounded-full border border-lucrix-border flex items-center justify-center text-[10px] font-black text-textMuted uppercase">
            {name?.[0]}
          </div>
        )}
        <span className="text-sm font-black text-white font-display italic uppercase tracking-tight">{name}</span>
      </div>
      <div className="font-mono font-black text-xs text-brand-cyan">
        {price > 0 ? `+${price}` : price}
      </div>
    </div>
  );
}
