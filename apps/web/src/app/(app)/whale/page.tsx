"use client";

import React, { useState, useEffect, Suspense } from "react";
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

  const { data: rawAlerts, isLoading, error, refetch } = useQuery({
    queryKey: ['whale', sport, minUnits],
    queryFn: async () => {
      const res = await API.whale(sport, minUnits);
      if (isApiError(res)) throw res;
      // Robust unwrapping as requested in Commit 4
      return Array.isArray(res) ? res : (res.data || res.alerts || res.props || []);
    },
    refetchInterval: 20_000,
    staleTime: 10_000,
  });

  const alerts = rawAlerts || [];

  const [forceShow, setForceShow] = useState(false);
  useEffect(() => {
    const timeout = setTimeout(() => {
      setForceShow(true);
    }, 5000);
    return () => clearTimeout(timeout);
  }, [isLoading]);

  const isLocked = false;
  const isAuthLoading = false;

  if ((isLoading || isAuthLoading) && !forceShow) {
    return (
      <div className="space-y-6 pt-6 px-4">
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


        {alerts.map((alert: any, i: number) => (
          <div 
            key={i} 
            className={clsx(
              "bg-lucrix-surface border rounded-2xl p-6 transition-all relative overflow-hidden flex flex-col md:flex-row md:items-center justify-between gap-6",
              "bg-lucrix-surface border rounded-2xl p-6 transition-all relative overflow-hidden flex flex-col md:flex-row md:items-center justify-between gap-6 border-brand-warning/20 hover:border-brand-warning/40 shadow-card"
            )}
          >
            <div className="flex items-center gap-6">
              <div className="bg-lucrix-dark p-3 rounded-xl border border-lucrix-border">
                <div className={clsx(
                  "p-1.5 rounded-lg border",
                  (alert.units || 0) > 50 ? "bg-red-500/10 border-red-500/20 text-red-500" : "bg-brand-warning/10 border-brand-warning/20 text-brand-warning"
                )}>
                  <Zap size={20} fill="currentColor" />
                </div>
              </div>
              <div>
                <div className="text-lg font-black text-white font-display italic uppercase tracking-tight">
                  {alert.player_name || alert.team || alert.selection || "Institutional Move"}
                </div>
                <div className="flex items-center gap-3 mt-1">
                  <div className="text-[10px] font-bold text-textSecondary uppercase tracking-widest">
                    {alert.market || alert.market_key} — {alert.line}
                  </div>
                  <div className={clsx(
                    "px-2 py-0.5 rounded text-[8px] font-black uppercase tracking-tighter",
                    alert.side?.toLowerCase().includes('over') ? "bg-green-500/10 text-green-500 border border-green-500/20" : "bg-red-500/10 text-red-500 border border-red-500/20"
                  )}>
                    {alert.side || alert.sharp_side || 'OPEN'}
                  </div>
                </div>
              </div>
            </div>
            
            <div className="flex items-center justify-between md:justify-end gap-8 md:gap-12 w-full md:w-auto pt-4 md:pt-0 border-t md:border-0 border-lucrix-border/50">
              <div className="text-center">
                <div className="text-[9px] font-black text-textMuted uppercase tracking-widest mb-1 italic">Source/Book</div>
                <div className="text-xs font-black text-white italic uppercase">{alert.book || alert.source || 'INSTITUTIONAL'}</div>
              </div>
              <div className="text-center">
                <div className="text-[9px] font-black text-textMuted uppercase tracking-widest mb-1 italic">Bet Size</div>
                <div className="text-xl font-black text-brand-warning font-display italic leading-none">{alert.units || alert.severity || 0}U</div>
              </div>
              <div className="text-right min-w-[80px]">
                <div className="text-[9px] font-black text-textMuted uppercase tracking-widest mb-1 italic">Confidence</div>
                <div className={clsx(
                  "text-[10px] font-black uppercase tracking-widest",
                  (alert.confidence || 0) > 80 ? "text-brand-success" : "text-brand-warning"
                )}>
                  {alert.confidence ? `${alert.confidence}%` : 'HIGH'}
                </div>
              </div>
            </div>

            {/* Whale Insight Overlay (on hover or just visible) */}
            <div className="absolute top-0 right-0 w-32 h-32 bg-brand-warning/5 blur-3xl rounded-full -mr-16 -mt-16 pointer-events-none" />
          </div>
        ))}

        {alerts.length === 0 && (
          <div className="text-center py-24 text-textMuted font-black uppercase italic tracking-widest">
            No whale activity detected
          </div>
        )}
      </div>
    </div>
  );
}
