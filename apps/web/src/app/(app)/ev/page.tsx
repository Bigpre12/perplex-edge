"use client";

import React, { useState, Suspense } from "react";
import { TrendingUp, Zap, Filter, Search, BookOpen, Clock, AlertTriangle, Star } from "lucide-react";
import { Sparklines, SparklinesLine, SparklinesSpots } from "react-sparklines";
import { useWSFallback } from "@/hooks/useWSFallback";
import { useSport } from "@/hooks/useSport";
import { useTierGate } from "@/hooks/useTierGate";
import { API_BASE, API } from "@/lib/api";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import SportSelector from "@/components/shared/SportSelector";
import { clsx } from "clsx";

export default function EVPage() {
  return (
    <Suspense fallback={<div className="p-6 text-white font-black italic uppercase tracking-widest animate-pulse font-display text-center py-24">BOOTING EV ENGINE...</div>}>
      <EVPageContent />
    </Suspense>
  );
}

function EVPageContent() {
  const { sport } = useSport();
  const [minEv, setMinEv] = useState(2);
  const [searchQuery, setSearchQuery] = useState("");

  const { data: evData, isLoading, isError, isWSOpen } = useWSFallback({
    wsEndpoint: "/api/ws_ev",
    queryKey: ["ev", sport, minEv],
    queryFn: () => fetch(`${API_BASE}/api/ev?sport=${sport}&min_ev=${minEv}`).then(r => r.json()),
    refetchInterval: 15_000,
  });

  const { data: limitedData, isLocked, isLoading: isGateLoading } = useTierGate(
    { data: evData, isLoading, error: isError ? new Error("Fetch failed") : null },
    { requiredTier: "pro" }
  );

  const displayData = isLocked ? [] : (limitedData || []);

  if (isLoading || isGateLoading) {
    return (
      <div className="space-y-6 pt-6 px-4">
        <div className="flex justify-between items-center mb-8">
          <Skeleton className="h-10 w-48" />
          <Skeleton className="h-10 w-32" />
        </div>
        <Skeleton className="h-96 w-full rounded-2xl" />
      </div>
    );
  }

  if (isError && !isLocked) {
    return <div className="p-6"><ErrorBanner message="Failed to connect to EV engine." /></div>;
  }

  return (
    <div className="pb-24 space-y-8 pt-6 px-4">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className={clsx(
              "p-2 rounded-lg border transition-all",
              isWSOpen ? "bg-brand-success/10 border-brand-success/20" : "bg-brand-warning/10 border-brand-warning/20"
            )}>
              <TrendingUp size={24} className={isWSOpen ? "text-brand-success shadow-glow shadow-brand-success/40" : "text-brand-warning"} />
            </div>
            <h1 className="text-3xl font-black italic tracking-tighter uppercase text-white font-display">EV+ Live Scanner</h1>
          </div>
          <p className="text-[10px] text-textMuted font-black uppercase tracking-widest mb-4 italic">
            {isWSOpen ? "Live Stream Active" : "Polling Mode (WS Down)"}
          </p>
          <SportSelector />
        </div>
      </div>

      <div className="bg-lucrix-surface/50 border border-lucrix-border rounded-xl p-4 flex flex-wrap items-center gap-6 shadow-sm">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-textMuted" size={14} />
          <input 
            type="text" 
            placeholder="Search Player or Market..." 
            className="w-full bg-lucrix-dark/50 border border-lucrix-border rounded-lg py-2 pl-10 pr-4 text-xs font-bold text-white focus:border-brand-success/50 outline-none transition-all"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-lucrix-dark/50 border border-lucrix-border rounded-lg px-3 py-1.5">
            <span className="text-[10px] font-black text-textMuted uppercase tracking-widest">Min EV:</span>
            <input 
              type="range" min="0" max="15" step="0.5" 
              className="w-24 accent-brand-success cursor-pointer" 
              value={minEv}
              onChange={(e) => setMinEv(parseFloat(e.target.value))}
            />
            <span className="text-xs font-black text-brand-success w-8 font-mono">{minEv}%</span>
          </div>
        </div>
      </div>

      <div className="bg-lucrix-surface border border-lucrix-border rounded-xl overflow-hidden shadow-card">
        <table className="w-full text-left">
          <thead>
            <tr className="bg-lucrix-dark/80 border-b border-lucrix-border text-[9px] font-black uppercase tracking-widest text-textMuted">
              <th className="px-6 py-4">Market Pick</th>
              <th className="px-6 py-4 text-center">Market Odds</th>
              <th className="px-6 py-4 text-center">Edge (EV%)</th>
              <th className="px-6 py-4 text-right">Last Update</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-lucrix-border/50">
            {displayData.filter((p: any) => p.player_name?.toLowerCase().includes(searchQuery.toLowerCase())).map((pick: any, i: number) => (
              <tr key={i} className="group hover:bg-lucrix-dark/50 transition-colors">
                <td className="px-6 py-5">
                  <div className="flex items-center gap-4">
                    <div className="bg-brand-warning/10 px-2 py-1 rounded-sm text-[10px] font-black border border-brand-warning/20 text-brand-warning uppercase tracking-widest">
                      {pick.sport}
                    </div>
                    <div>
                      <div className="font-black text-lg text-white font-display italic uppercase tracking-tight">{pick.player_name}</div>
                      <div className="text-[10px] font-bold text-textSecondary uppercase tracking-widest mt-0.5">{pick.market} — {pick.line}</div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-5 text-center">
                  <div className="flex flex-col items-center">
                    <span className="bg-lucrix-dark px-4 py-2 rounded-lg border border-lucrix-border font-black font-mono text-white text-sm">
                      {pick.odds > 0 ? `+${pick.odds}` : pick.odds}
                    </span>
                    <div className="text-[8px] text-textMuted mt-1.5 font-black uppercase tracking-widest">{pick.book}</div>
                  </div>
                </td>
                <td className="px-6 py-5 text-center">
                  <div className="flex flex-col items-center">
                    <div className="flex items-center gap-1.5">
                      <span className={clsx(
                        "text-xl font-black font-display",
                        pick.ev >= 3 ? "text-brand-success" : pick.ev >= 0 ? "text-brand-warning" : "text-brand-danger"
                      )}>
                        +{pick.ev}%
                      </span>
                      {pick.ev >= 5 && <Zap size={14} className="text-brand-success fill-brand-success animate-pulse" />}
                    </div>
                  </div>
                </td>
                <td className="px-6 py-5 text-right">
                  <div className="text-[10px] font-black text-textMuted uppercase tracking-widest flex items-center justify-end gap-1.5">
                    <Clock size={12} className="text-brand-cyan" />
                    {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {isLocked && (
        <div className="mt-12 p-12 text-center bg-gradient-to-b from-brand-success/10 to-transparent border border-brand-success/20 rounded-2xl relative overflow-hidden group cursor-pointer" onClick={() => window.location.href = "/subscription"}>
          <div className="relative z-10">
            <Star size={40} className="mx-auto text-brand-success mb-4 animate-pulse shadow-glow shadow-brand-success" />
            <h3 className="text-2xl font-black italic uppercase tracking-tighter mb-2 text-white font-display">
              Pro EV Scanner Locked
            </h3>
            <p className="text-textSecondary text-sm max-w-md mx-auto mb-8 font-bold">
              Upgrade to Pro+ to access the real-time EV scanner and live streaming picks.
            </p>
            <button className="bg-brand-success hover:bg-brand-success/90 text-black px-10 py-4 rounded-xl font-black uppercase tracking-widest text-sm transition-all shadow-glow shadow-brand-success/50">
              Unlock EV Intel →
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
