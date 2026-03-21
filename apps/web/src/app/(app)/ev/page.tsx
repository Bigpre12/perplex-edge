"use client";

import React, { useState, Suspense, useMemo } from "react";
import { useSearchParams } from "next/navigation";
import { useSport } from "@/hooks/useSport";
import { useEVBoard } from "@/hooks/useEVBoard";
import { CanonicalProp } from "@/hooks/usePropsBoard";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import SportSelector from "@/components/shared/SportSelector";
import { Zap, Clock, ShieldAlert, TrendingUp, Info } from "lucide-react";
import { clsx } from "clsx";

export default function EVPage() {
  return (
    <Suspense fallback={<div className="p-6 text-white text-center py-24 animate-pulse uppercase tracking-widest font-black italic">BOOTING EV ENGINE...</div>}>
      <EVPageContent />
    </Suspense>
  );
}

function EVPageContent() {
  const { sport } = useSport();
  const searchParams = useSearchParams();
  
  // Custom states for filters
  const [minEv, setMinEv] = useState<number>(3);
  const [timeWindow, setTimeWindow] = useState<string>("All"); // All, Next 2h, Tonight
  const [signalToggle, setSignalToggle] = useState<string>("All"); // All, Steam only, Whale only, Model only

  const { data, isLoading, error, refetch } = useEVBoard(sport, minEv);

  const evList = data?.props || [];

  // Filter and Sort logic
  const filteredEVs = useMemo(() => {
    let result = [...evList];

    // Source data EV slider filter
    if (minEv > 0) {
      result = result.filter(p => p.ev_percentage >= minEv);
    }

    // Time window filter
    if (timeWindow === "Next 2h") {
      const now = new Date();
      const limit = new Date(now.getTime() + 2 * 60 * 60 * 1000);
      result = result.filter(p => p.start_time && new Date(p.start_time) <= limit && new Date(p.start_time) >= now);
    } else if (timeWindow === "Tonight") {
      const today = new Date();
      today.setHours(23, 59, 59, 999);
      result = result.filter(p => p.start_time && new Date(p.start_time) <= today);
    }

    // Signal toggles
    if (signalToggle === "Steam only") {
      result = result.filter(p => p.steam_signal);
    } else if (signalToggle === "Whale only") {
      result = result.filter(p => p.whale_signal);
    } else if (signalToggle === "Model only") {
      result = result.filter(p => !p.steam_signal && !p.whale_signal && p.ev_percentage > 0);
    }

    // Default sort: EV% desc, then Start Time asc
    result.sort((a, b) => {
      const evDiff = b.ev_percentage - a.ev_percentage;
      if (Math.abs(evDiff) > 0.1) return evDiff;
      if (a.start_time && b.start_time) {
        return new Date(a.start_time).getTime() - new Date(b.start_time).getTime();
      }
      return 0;
    });

    return result;
  }, [evList, minEv, timeWindow, signalToggle]);

  const maxEV = filteredEVs.length > 0 ? Math.max(...filteredEVs.map(p => p.ev_percentage)) : 0;
  
  // Calculate median
  const medianEV = useMemo(() => {
    if (filteredEVs.length === 0) return 0;
    const sorted = [...filteredEVs].sort((a, b) => a.ev_percentage - b.ev_percentage);
    const mid = Math.floor(sorted.length / 2);
    return sorted.length % 2 !== 0 ? sorted[mid].ev_percentage : (sorted[mid - 1].ev_percentage + sorted[mid].ev_percentage) / 2;
  }, [filteredEVs]);

  if (isLoading) {
    return (
      <div className="space-y-6 pt-6 px-4">
        <div className="flex justify-between items-center mb-8">
          <Skeleton className="h-10 w-48" />
          <Skeleton className="h-10 w-32" />
        </div>
        <div className="space-y-4">
          {[...Array(8)].map((_, i) => (
            <Skeleton key={i} className="h-24 w-full rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return <div className="p-6"><ErrorBanner message={error.message} onRetry={refetch} /></div>;
  }

  return (
    <div className="pb-24 pt-6 px-4 max-w-5xl mx-auto space-y-8">
      {/* Header section */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-brand-success/10 p-2 rounded-lg border border-brand-success/20">
              <Zap size={24} className="text-brand-success shadow-glow shadow-brand-success" />
            </div>
            <h1 className="text-3xl font-black italic tracking-tighter uppercase font-display text-white">EV Cheat Sheet</h1>
          </div>
          <p className="text-[10px] text-textMuted font-black uppercase tracking-widest mb-4 italic">The Best Edges Right Now</p>
          <SportSelector />
        </div>
      </div>

      {/* Control Panel: Filters, Search, Chips */}
      <div className="bg-lucrix-surface border border-lucrix-border rounded-2xl p-4 md:p-6 space-y-6 shadow-card">
        <div className="flex flex-col md:flex-row gap-6 md:items-end">
          
          {/* Slider */}
          <div className="w-full md:w-64">
            <div className="flex justify-between items-center mb-2">
              <label className="text-[10px] font-black uppercase tracking-widest text-textMuted">Minimum EV</label>
              <span className="text-xs font-mono font-black text-brand-success">{minEv}%</span>
            </div>
            <input 
              type="range" 
              title="Minimum EV"
              aria-label="Minimum EV"
              min="1" max="20" step="0.5"
              value={minEv}
              onChange={(e) => setMinEv(parseFloat(e.target.value))}
              className="w-full accent-brand-success"
            />
          </div>

          {/* Time Window */}
          <div className="w-full md:w-48">
            <label className="text-[10px] font-black uppercase tracking-widest text-textMuted mb-2 block">Time Window</label>
            <select 
              title="Time Window"
              aria-label="Time Window"
              value={timeWindow}
              onChange={(e) => setTimeWindow(e.target.value)}
              className="w-full bg-lucrix-dark border border-lucrix-border rounded-xl px-4 py-3 text-sm font-bold text-white focus:outline-none focus:border-brand-success transition-colors appearance-none"
            >
              <option value="All">All Games</option>
              <option value="Next 2h">Next 2 Hours</option>
              <option value="Tonight">Tonight</option>
            </select>
          </div>

        </div>

        {/* Signal Toggles */}
        <div className="flex flex-wrap gap-2">
          {["All", "Steam only", "Whale only", "Model only"].map(chip => (
            <button 
              key={chip}
              onClick={() => setSignalToggle(chip)}
              className={clsx(
                "px-4 py-1.5 rounded-full text-xs font-black uppercase tracking-widest transition-all",
                signalToggle === chip 
                  ? "bg-brand-success text-black shadow-glow shadow-brand-success/30" 
                  : "bg-lucrix-dark text-textMuted border border-lucrix-border hover:border-textMuted"
              )}
            >
              {chip}
            </button>
          ))}
        </div>
      </div>

      {/* Top Summary Strip */}
      {data && (
        <div className="flex items-center justify-between bg-lucrix-dark border border-lucrix-border/50 rounded-xl p-3 px-5 text-[10px] font-black uppercase tracking-widest text-textMuted">
          <div className="flex items-center gap-3 md:gap-6 flex-wrap">
            <span><span className="text-white text-sm">{filteredEVs.length}</span> +EV PROPS FOUND</span>
            {filteredEVs.length > 0 && (
              <>
                <span className="hidden md:inline">·</span>
                <span>MEDIAN EV <span className="text-brand-success text-sm">{medianEV.toFixed(1)}%</span></span>
                <span className="hidden md:inline">·</span>
                <span>MAX EV <span className="text-brand-success text-sm">{maxEV.toFixed(1)}%</span></span>
              </>
            )}
          </div>
          <div className="flex items-center gap-1.5 whitespace-nowrap">
            <Clock size={10} />
            UPDATED {new Date(data.updated).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        </div>
      )}

      {/* Focus View List */}
      <div className="space-y-4">
        {filteredEVs.length === 0 ? (
          <div className="p-12 text-center text-textMuted font-bold text-sm bg-lucrix-surface border border-lucrix-border rounded-2xl shadow-card">
            No edges found matching your criteria. Try lowering your EV threshold.
          </div>
        ) : (
          filteredEVs.map(prop => (
            <EVCheatRow key={prop.id} prop={prop} />
          ))
        )}
      </div>

      {/* Disclaimer */}
      <div className="text-center text-[10px] font-bold text-textMuted/50 max-w-2xl mx-auto flex items-center justify-center gap-2">
        <Info size={12} />
        EV% and Confidence are model-based estimations and not guaranteed outcomes. <a href="#" className="underline">View Track Record</a>
      </div>
    </div>
  );
}

function EVCheatRow({ prop }: { prop: CanonicalProp }) {
  // Use best bet side based on best odds
  const betSide = prop.implied_probability > 0 || prop.ev_percentage > 0 ? (prop.best_book ? (prop.over_odds && prop.over_odds > 0 && String(prop.over_odds).includes(String(prop.best_book)) ? "OVER" : "UNDER") : "OVER") : "OVER";
  const displayOdds = prop.best_book && prop.over_odds ? prop.over_odds : prop.under_odds || -110;
  
  return (
    <div className="group relative bg-lucrix-surface border border-lucrix-border hover:border-brand-success/50 transition-colors rounded-2xl p-4 md:p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-card hover:shadow-glow hover:shadow-brand-success/10 cursor-pointer overflow-hidden">
      {/* Background Pulse for very high EV */}
      {prop.ev_percentage > 10 && (
        <div className="absolute top-0 right-0 w-32 h-32 bg-brand-success/5 blur-3xl rounded-full" />
      )}
      
      {/* Left side: Big EV + Details */}
      <div className="flex items-center gap-5 md:gap-8 w-full md:w-auto relative z-10">
        
        {/* BIG EV% */}
        <div className="flex flex-col items-center justify-center bg-brand-success/10 border border-brand-success/20 p-3 px-4 rounded-xl min-w-[90px]">
          <span className="text-[10px] font-black uppercase tracking-widest text-brand-success mb-1">EDGE</span>
          <span className="text-2xl font-black font-display text-brand-success leading-none">+{prop.ev_percentage.toFixed(1)}%</span>
        </div>

        {/* Player Details */}
        <div className="flex flex-col">
          <h3 className="text-xl md:text-2xl font-black italic uppercase tracking-tighter text-white font-display leading-tight">{prop.player_name}</h3>
          
          <div className="flex items-center gap-2 mt-1 flex-wrap">
            <span className="text-sm font-black text-brand-cyan uppercase tracking-widest">{prop.stat_type}</span>
            <span className="text-lg font-black font-display text-white">{prop.line}</span>
          </div>

          {/* Mini Tag Row */}
          <div className="flex items-center gap-3 mt-2 text-[10px] font-black uppercase tracking-widest text-textMuted">
            <span className="text-textSecondary">{prop.sport.replace(/_/g, " ")}</span>
            <span>·</span>
            <span className="flex items-center gap-1">
              <Clock size={10} /> 
              {prop.start_time ? new Date(prop.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'LIVE'}
            </span>
            {(prop.steam_signal || prop.whale_signal) && <span>·</span>}
            {prop.steam_signal && <span className="text-brand-primary">STEAM</span>}
            {prop.whale_signal && <span className="text-purple-400">WHALE</span>}
          </div>
        </div>
      </div>

      {/* Right side: Book & Odds */}
      <div className="flex items-stretch md:items-end flex-row md:flex-col gap-3 md:gap-2 w-full md:w-auto relative z-10 border-t md:border-t-0 border-lucrix-border/50 pt-4 md:pt-0">
        <div className="flex-1 md:flex-none flex flex-col items-center md:items-end justify-center bg-lucrix-dark md:bg-transparent rounded-xl border md:border-transparent border-lucrix-border p-3 md:p-0">
          <span className="text-[10px] font-black uppercase tracking-widest text-textMuted mb-1">Top Book</span>
          <span className="font-bold text-sm text-white">{prop.best_book}</span>
        </div>
        
        <div className="flex-1 md:flex-none flex items-center justify-center md:justify-end gap-2 bg-lucrix-dark md:bg-brand-success/10 border border-lucrix-border md:border-brand-success/20 p-3 md:py-2 md:px-4 rounded-xl">
          <span className="text-[10px] font-black uppercase tracking-widest text-textMuted md:text-brand-success/80">
            {betSide}
          </span>
          <span className="text-lg font-mono font-black text-brand-success">
            {displayOdds > 0 ? `+${displayOdds}` : displayOdds}
          </span>
        </div>
      </div>
    </div>
  );
}
