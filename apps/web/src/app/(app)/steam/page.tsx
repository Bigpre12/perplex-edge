"use client";

import React, { Suspense } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSport } from "@/hooks/useSport";
import { useTierGate } from "@/hooks/useTierGate";
import { API_BASE } from "@/lib/api";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import SportSelector from "@/components/shared/SportSelector";
import { Zap, AlertTriangle, Clock, Star, TrendingUp } from "lucide-react";
import { clsx } from "clsx";

export default function SteamMovesPage() {
  return (
    <Suspense fallback={<div className="p-6 text-white font-black italic uppercase tracking-widest animate-pulse font-display text-center py-24">BOOTING STEAM SCANNER...</div>}>
      <SteamMovesContent />
    </Suspense>
  );
}

function SteamMovesContent() {
  const { sport } = useSport();

  const { data: steamData, isLoading, error, refetch } = useQuery({
    queryKey: ['steam', sport],
    queryFn: () => fetch(`${API_BASE}/api/steam?sport=${sport}`).then(r => {
      if (!r.ok) {
        if (r.status === 403) throw new Error("403");
        throw new Error("Failed to fetch steam moves");
      }
      return r.json();
    }),
    refetchInterval: 15_000,
    staleTime: 5_000,
  });

  const { data: limitedData, isLocked, isLoading: isGateLoading } = useTierGate(
    { data: steamData, isLoading, error },
    { requiredTier: "elite" }
  );

  if (isLoading || isGateLoading) {
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

  return (
    <div className="pb-24 space-y-8 pt-6 px-4">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-brand-danger/10 p-2 rounded-lg border border-brand-danger/20">
              <Zap size={24} className="text-brand-danger shadow-glow shadow-brand-danger/40 animate-pulse" />
            </div>
            <h1 className="text-3xl font-black italic tracking-tighter uppercase text-white font-display">Steam Moves</h1>
          </div>
          <p className="text-[10px] text-textMuted font-black uppercase tracking-widest mb-4 italic">Institutional Momentum Tracking</p>
          <SportSelector />
        </div>
        <div className="text-right">
          <div className="text-[9px] font-black text-textMuted uppercase tracking-widest flex items-center justify-end gap-1.5">
            <Clock size={12} className="text-brand-danger" />
            High-Frequency Scan: 15s
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 relative">
        {isLocked && (
          <div className="absolute inset-0 z-10 flex items-center justify-center pt-24">
            <div className="bg-lucrix-surface/80 backdrop-blur-md border border-brand-danger/30 p-10 rounded-3xl text-center max-w-lg shadow-2xl">
              <Star size={40} className="mx-auto text-brand-danger mb-6 animate-bounce shadow-glow shadow-brand-danger" />
              <h2 className="text-2xl font-black italic uppercase tracking-tighter mb-4 text-white font-display">Elite Steam Locked</h2>
              <p className="text-textSecondary text-sm font-bold mb-8 italic">
                Steam moves represent the most aggressive institutional money entry. <br/> Elite access provides a 0-sec delay on all market movement alerts.
              </p>
              <button 
                onClick={() => window.location.href = "/subscription"}
                className="bg-brand-danger hover:bg-brand-danger/90 text-white px-12 py-4 rounded-xl font-black uppercase tracking-widest text-sm transition-all shadow-glow shadow-brand-danger/50"
              >
                Unlock Instant Steam →
              </button>
            </div>
          </div>
        )}

        {(isLocked ? (steamData?.slice(0, 3) || []) : limitedData || []).map((move: any, i: number) => (
          <div 
            key={i} 
            className={clsx(
              "bg-lucrix-surface border rounded-2xl p-6 transition-all relative overflow-hidden",
              isLocked ? "blur-md opacity-30 border-lucrix-border" : "border-brand-danger/20 hover:border-brand-danger/40 shadow-card"
            )}
          >
            <div className="flex justify-between items-start mb-6">
              <div>
                <div className="text-lg font-black text-white font-display italic uppercase tracking-tight">{move.game || move.player}</div>
                <div className="text-[10px] font-bold text-textSecondary uppercase tracking-widest mt-1">
                  {move.market} — {move.line}
                </div>
              </div>
              <div className="bg-brand-danger/10 p-2 rounded-lg border border-brand-danger/20">
                <TrendingUp size={16} className="text-brand-danger" />
              </div>
            </div>

            <div className="flex items-center justify-between mt-auto">
              <div className="flex flex-col">
                <span className="text-[9px] font-black text-textMuted uppercase tracking-widest mb-1">Book Leak</span>
                <span className="text-xs font-black text-white italic">{move.book}</span>
              </div>
              <div className="flex flex-col text-right">
                <span className="text-[9px] font-black text-textMuted uppercase tracking-widest mb-1">Detected</span>
                <span className="text-xs font-bold text-textSecondary">{new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}</span>
              </div>
            </div>

            {move.reverse_movement && (
              <div className="mt-4 pt-3 border-t border-lucrix-border">
                <span className="bg-brand-warning/10 text-brand-warning text-[8px] font-black px-2 py-0.5 rounded border border-brand-warning/30 uppercase tracking-widest italic">
                  ⚠️ Reverse Line Movement Detected
                </span>
              </div>
            )}
          </div>
        ))}

        {!isLocked && (!limitedData || limitedData.length === 0) && (
          <div className="col-span-full text-center py-24 text-textMuted font-black uppercase italic tracking-widest">
            Scanning for rapid market shifts...
          </div>
        )}
      </div>
    </div>
  );
}
