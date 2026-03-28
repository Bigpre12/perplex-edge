"use client";

import React, { useState, Suspense } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSport } from "@/hooks/useSport";
import { useAuth } from "@/hooks/useAuth";
import { API, isApiError } from "@/lib/api";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import SportSelector from "@/components/shared/SportSelector";
import { ShieldAlert, Zap, Star, Clock, Filter, AlertCircle } from "lucide-react";
import { clsx } from "clsx";

export default function WhaleAlertsPage() {
  return (
    <Suspense fallback={<div className="p-6 text-white font-black italic uppercase tracking-widest animate-pulse font-display text-center py-24">BOOTING WHALE TRACKER...</div>}>
      <WhaleAlertsContent />
    </Suspense>
  );
}

function WhaleAlertsContent() {
  const { sport } = useSport();
  const [minUnits, setMinUnits] = useState(10);

  const { data: alerts, isLoading, error, refetch } = useQuery({
    queryKey: ['whale', sport, minUnits],
    queryFn: async () => {
      const res = await API.whale(sport, minUnits);
      if (isApiError(res)) throw res;
      return res.data || [];
    },
    refetchInterval: 20_000,
    staleTime: 10_000,
  });

  const { checkAccess, loading: isAuthLoading } = useAuth();
  const isLocked = !isAuthLoading && !checkAccess("whaleIntel");

  if (isLoading || isAuthLoading) {
    return (
      <div className="space-y-6 pt-6 px-4">
        {/* ... existing skeleton ... */}
        <Skeleton className="h-10 w-48 mb-6" />
        <Skeleton className="h-20 w-full mb-4" />
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
            <Skeleton key={i} className="h-24 w-full rounded-2xl" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="pb-24 space-y-8 pt-6 px-4">
      {/* ... header code ... */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-brand-warning/10 p-2 rounded-lg border border-brand-warning/20">
              <ShieldAlert size={24} className="text-brand-warning shadow-glow shadow-brand-warning/40" />
            </div>
            <h1 className="text-3xl font-black italic tracking-tighter uppercase text-white font-display">Whale Tracker</h1>
          </div>
          <p className="text-[10px] text-textMuted font-black uppercase tracking-widest mb-4 italic">High-Stakes institutional Order Flow</p>
          <SportSelector />
        </div>
        <div className="flex flex-col items-end gap-3">
          <div className="flex items-center gap-2 bg-lucrix-surface border border-lucrix-border rounded-lg px-4 py-2">
            <Filter size={14} className="text-textMuted" />
            <span className="text-[10px] font-black text-textMuted uppercase">Min Units:</span>
            <input 
              type="number" 
              title="Minimum Units Threshold"
              aria-label="Minimum Units Threshold"
              className="bg-transparent text-white font-mono font-black text-sm w-12 outline-none" 
              value={minUnits} 
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setMinUnits(parseInt(e.target.value) || 0)}
            />
          </div>
          <div className="text-[9px] font-black text-textMuted uppercase tracking-widest flex items-center gap-1.5">
            <Clock size={11} className="text-brand-warning" />
            Live Sync: 20s
          </div>
        </div>
      </div>

      <div className="space-y-4 relative">
        {isLocked && (
          <div className="absolute inset-x-0 top-0 z-20 flex flex-col items-center justify-center pt-24 pb-12 bg-gradient-to-t from-lucrix-bg via-lucrix-bg/95 to-transparent min-h-[500px]">
             <div className="bg-lucrix-surface/90 backdrop-blur-xl border border-brand-warning/20 p-10 rounded-3xl text-center max-w-lg shadow-[0_0_50px_rgba(234,179,8,0.15)] scale-105">
              <Star size={48} className="mx-auto text-brand-warning mb-6 shadow-glow shadow-brand-warning/40" />
              <h2 className="text-3xl font-black italic uppercase tracking-tighter mb-4 text-white font-display">Elite Access Required</h2>
              <p className="text-textSecondary text-base font-bold mb-8 italic leading-relaxed">
                Whale movements represent institutional-grade order flow. <br/> Reveal the high-stakes positions moving the markets today.
              </p>
              <button 
                onClick={() => window.location.href = "/pricing"}
                className="w-full bg-brand-warning hover:bg-white text-black px-12 py-4 rounded-xl font-black uppercase tracking-widest text-sm transition-all shadow-[0_0_30px_rgba(234,179,8,0.3)] hover:scale-[1.02] active:scale-[0.98]"
              >
                Unlock Whale Flow →
              </button>
            </div>
          </div>
        )}

        {(isLocked ? (alerts?.slice(0, 3) || []) : alerts || []).map((alert: { player_name?: string; team?: string; market: string; line: string; odds: string; book?: string; units: number; timestamp?: string }, i: number) => (
          <div 
            key={i} 
            className={clsx(
              "bg-lucrix-surface border rounded-2xl p-6 transition-all relative overflow-hidden flex items-center justify-between",
              isLocked ? "blur-sm opacity-40 border-lucrix-border" : "border-brand-warning/20 hover:border-brand-warning/40 shadow-card"
            )}
          >
            <div className="flex items-center gap-6">
              <div className="bg-lucrix-dark p-3 rounded-xl border border-lucrix-border">
                <AlertCircle className={isLocked ? "text-textMuted" : "text-brand-warning"} />
              </div>
              <div>
                <div className="text-lg font-black text-white font-display italic uppercase tracking-tight">{alert.player_name || alert.team}</div>
                <div className="text-[10px] font-bold text-textSecondary uppercase tracking-widest mt-1">
                  {alert.market} — {alert.line} @ {alert.odds}
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-12">
              <div className="text-center">
                <div className="text-[9px] font-black text-textMuted uppercase tracking-widest mb-1">Book</div>
                <div className="text-xs font-black text-white italic">{alert.book || 'PINN'}</div>
              </div>
              <div className="text-center">
                <div className="text-[9px] font-black text-textMuted uppercase tracking-widest mb-1">Units</div>
                <div className="text-xl font-black text-brand-warning font-display italic">{alert.units}U</div>
              </div>
              <div className="text-right">
                <div className="text-[9px] font-black text-textMuted uppercase tracking-widest mb-1">Detected</div>
                <div className="text-xs font-bold text-textSecondary">{alert.timestamp ? new Date(alert.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "N/A"}</div>
              </div>
            </div>
          </div>
        ))}

        {!isLocked && (!alerts || alerts.length === 0) && (
          <div className="text-center py-24 text-textMuted font-black uppercase italic tracking-widest">
            Scanning for high-stakes positions...
          </div>
        )}
      </div>
    </div>
  );
}
