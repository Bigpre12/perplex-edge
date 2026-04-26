"use client";

import React, { useState, Suspense } from "react";
import { useSport } from "@/hooks/useSport";
import { Skeleton } from "@/components/ui/Skeleton";
import SportSelector from "@/components/shared/SportSelector";
import { Radio, Zap, Users, Shield, Clock, Search } from "lucide-react";
import { clsx } from "clsx";
import { EmptyState } from "@/components/shared/EmptyState";
import { useEvSignals } from "@/hooks/useEvSignals";
import DataFreshnessBanner from "@/components/shared/DataFreshnessBanner";

export default function SignalsPage() {
  return (
    <Suspense fallback={<div className="p-6 text-white font-black italic uppercase tracking-widest animate-pulse font-display text-center py-24">BOOTING SIGNAL FEED...</div>}>
      <SignalsContent />
    </Suspense>
  );
}

function SignalsContent() {
  const { sport } = useSport();
  const [filterType, setFilterType] = useState<string>("all");

  const { signals, loading: isLoading, error, refetch, lastUpdated } = useEvSignals(sport, 0);
  const isError = Boolean(error);
  const isFetched = !isLoading;

  if (isLoading) {
    return (
      <div className="space-y-6 pt-6 px-4">
        <Skeleton className="h-10 w-48 mb-8" />
        <div className="space-y-4">
          {[...Array(6)].map((_, i) => (
            <Skeleton key={i} className="h-24 w-full rounded-2xl" />
          ))}
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="p-6 pt-10 max-w-lg mx-auto">
        <EmptyState
          title="No market anomalies detected for this slate."
          description="Unable to connect to backend. Data will populate once API is online."
          onRetry={() => refetch()}
        />
      </div>
    );
  }

  const signalList = (Array.isArray(signals) ? signals : []).filter((s: any) =>
    filterType === "all" ? true : String(s?.type || "").toLowerCase() === filterType
  );

  return (
    <div className="pb-24 space-y-8 pt-6 px-4">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-brand-cyan/10 p-2 rounded-lg border border-brand-cyan/20">
              <Radio size={24} className="text-brand-cyan shadow-glow shadow-brand-cyan/40" />
            </div>
            <h1 className="text-3xl font-black italic tracking-tighter uppercase text-white font-display">Market Signals</h1>
          </div>
          <p className="text-[10px] text-textMuted font-black uppercase tracking-widest mb-4 italic">Aggregated Institutional & Public Flow</p>
          <SportSelector />
        </div>
        <DataFreshnessBanner lastUpdated={lastUpdated} label="Signals feed" />
        <div className="flex bg-lucrix-surface border border-lucrix-border rounded-xl p-1 shadow-inner">
          {["all", "steam", "sharp", "public"].map((t) => (
            <button
              key={t}
              onClick={() => setFilterType(t)}
              className={clsx(
                "px-4 py-2 text-[10px] font-black uppercase tracking-widest rounded-lg transition-all",
                filterType === t ? "bg-brand-cyan text-black shadow-glow shadow-brand-cyan/20" : "text-textMuted hover:text-white"
              )}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-4">
        {signalList.map((signal: any, i: number) => (
          <SignalCard key={i} signal={signal} />
        ))}
        {isFetched && signalList.length === 0 && (
          <EmptyState
            title="No market anomalies detected for this slate."
            description="No data available. Waiting for market sync."
            onRetry={() => refetch()}
          />
        )}
      </div>
    </div>
  );
}

function SignalCard({ signal }: any) {
  const getIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case "steam": return <Zap size={18} className="text-brand-danger" />;
      case "sharp": return <Shield size={18} className="text-brand-cyan" />;
      case "public": return <Users size={18} className="text-brand-warning" />;
      default: return <Radio size={18} className="text-white" />;
    }
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 80) return "text-brand-success";
    if (score >= 50) return "text-brand-warning";
    return "text-brand-danger";
  };

  return (
    <div className="bg-lucrix-surface border border-lucrix-border rounded-2xl p-6 hover:border-brand-cyan/20 transition-all flex items-center justify-between group shadow-card">
      <div className="flex items-center gap-6">
        <div className={clsx(
          "p-4 rounded-xl border",
          signal.type === "steam" ? "bg-brand-danger/10 border-brand-danger/20" : 
          signal.type === "sharp" ? "bg-brand-cyan/10 border-brand-cyan/20" : 
          "bg-brand-warning/10 border-brand-warning/20"
        )}>
          {getIcon(signal.type)}
        </div>
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className={clsx(
              "text-[8px] font-black px-1.5 py-0.5 rounded border uppercase tracking-widest",
              signal.type === "steam" ? "text-brand-danger border-brand-danger/20" : 
              signal.type === "sharp" ? "text-brand-cyan border-brand-cyan/20" : 
              "text-brand-warning border-brand-warning/20"
            )}>
              {signal.type}
            </span>
            <div className="text-lg font-black text-white font-display italic uppercase tracking-tight">{signal.event || signal.player}</div>
          </div>
          <p className="text-[11px] font-bold text-textSecondary">{signal.description || "Unusual volume detected on current market line."}</p>
        </div>
      </div>

      <div className="flex items-center gap-10">
        <div className="text-center">
          <div className="text-[9px] font-black text-textMuted uppercase tracking-widest mb-1">Confidence</div>
          <div className={clsx("text-xl font-black font-display italic", getConfidenceColor(signal.confidence))}>
            {signal.confidence}%
          </div>
        </div>
        <div className="text-right flex flex-col items-end">
          <div className="text-[9px] font-black text-textMuted uppercase tracking-widest mb-1 flex items-center gap-1.5">
            <Clock size={10} /> {new Date(signal.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
          <button className="text-[9px] font-black uppercase tracking-widest text-brand-cyan border border-brand-cyan/20 bg-brand-cyan/10 px-2 py-1 rounded-sm">
            Insights →
          </button>
        </div>
      </div>
    </div>
  );
}
