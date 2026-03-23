"use client";

import React, { useState, Suspense, useMemo } from "react";
import { useSearchParams } from "next/navigation";
import { useSport } from "@/hooks/useSport";
import { usePropsBoard, CanonicalProp } from "@/hooks/usePropsBoard";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import SportSelector from "@/components/shared/SportSelector";
import { Trophy, Search, Clock, ShieldAlert, BarChart3, Info } from "lucide-react";
import { clsx } from "clsx";

export default function PropsPage() {
  return (
    <Suspense fallback={<div className="p-6 text-white text-center py-24 animate-pulse uppercase tracking-widest font-black italic">BOOTING INTEL...</div>}>
      <PropsPageContent />
    </Suspense>
  );
}

function PropsPageContent() {
  const { sport } = useSport();
  const searchParams = useSearchParams();
  
  // Custom states for filters
  const [search, setSearch] = useState("");
  const [minEv, setMinEv] = useState<number>(-5);
  const [statType, setStatType] = useState<string>("All");
  const [quickChip, setQuickChip] = useState<string>("All");

  const { data, isLoading, error, refetch } = usePropsBoard(sport, minEv > 0 ? minEv : undefined);

  const propsList = data?.props || [];

  // Derive unique stat types for the dropdown
  const statTypes = useMemo(() => {
    const types = new Set<string>();
    propsList.forEach(p => types.add(p.stat_type));
    return ["All", ...Array.from(types).sort()];
  }, [propsList]);

  // Filter and Sort logic
  const filteredProps = useMemo(() => {
    let result = [...propsList];

    // Filter out team markets (H2H, Spreads, Totals)
    result = result.filter(p => {
      const sType = (p.stat_type || "").toLowerCase();
      const isTeamMarket = sType === 'h2h' || sType === 'spreads' || sType === 'totals' || !p.player_name;
      return !isTeamMarket;
    });

    // Source data EV slider filter (handled locally if minEv < 0, else API did it)
    if (minEv > -5) {
      result = result.filter(p => p.ev_percentage >= minEv);
    }

    // Stat Type filter
    if (statType !== "All") {
      result = result.filter(p => p.stat_type === statType);
    }

    // Search filter
    if (search) {
      const s = search.toLowerCase();
      result = result.filter(p => 
        p.player_name.toLowerCase().includes(s) || 
        p.team.toLowerCase().includes(s) || 
        p.opponent.toLowerCase().includes(s)
      );
    }

    // Quick Chips filtering and sorting
    if (quickChip === "+EV only") {
      result = result.filter(p => p.ev_percentage > 0);
      result.sort((a, b) => b.ev_percentage - a.ev_percentage);
    } else if (quickChip === "High confidence") {
      result = result.filter(p => p.confidence >= 70);
      result.sort((a, b) => b.confidence - a.confidence);
    } else if (quickChip === "Soonest start") {
      result = result.filter(p => p.start_time);
      result.sort((a, b) => new Date(a.start_time!).getTime() - new Date(b.start_time!).getTime());
    } else {
      // Default: sort by EV desc
      result.sort((a, b) => b.ev_percentage - a.ev_percentage);
    }

    return result;
  }, [propsList, minEv, statType, search, quickChip]);

  if (isLoading) {
    return (
      <div className="space-y-6 pt-6 px-4">
        <div className="flex justify-between items-center mb-8">
          <Skeleton className="h-10 w-48" />
          <Skeleton className="h-10 w-32" />
        </div>
        <div className="space-y-4">
          {[...Array(8)].map((_, i) => (
            <Skeleton key={i} className="h-16 w-full rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return <div className="p-6"><ErrorBanner message={error.message} onRetry={refetch} /></div>;
  }

  return (
    <div className="pb-24 pt-6 px-4 max-w-7xl mx-auto space-y-8">
      {/* Header section */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-brand-cyan/10 p-2 rounded-lg border border-brand-cyan/20">
              <Trophy size={24} className="text-brand-cyan shadow-glow shadow-brand-cyan" />
            </div>
            <h1 className="text-3xl font-black italic tracking-tighter uppercase font-display text-white">Props Dashboard</h1>
          </div>
          <p className="text-[10px] text-textMuted font-black uppercase tracking-widest mb-4 italic">Institutional Edge Discovery · Live Updates</p>
          <SportSelector />
        </div>
      </div>

      {/* Fallback Notice */}
      {data?.fallback === "team_markets" && (
        <div className="bg-brand-primary/10 border border-brand-primary/20 rounded-xl px-4 py-3 flex items-center gap-3">
          <Info size={16} className="text-brand-primary flex-shrink-0" />
          <p className="text-xs font-bold text-brand-primary">
            Player props data is currently syncing. Showing team spreads &amp; totals in the meantime.
          </p>
        </div>
      )}

      {/* Control Panel: Filters, Search, Chips */}
      <div className="bg-lucrix-surface border border-lucrix-border rounded-2xl p-4 md:p-6 space-y-6 shadow-card">
        <div className="flex flex-col md:flex-row gap-6 md:items-end">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-textMuted" size={16} />
            <input 
              type="text" 
              placeholder="Search player or team..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-lucrix-dark border border-lucrix-border rounded-xl pl-10 pr-4 py-3 text-sm font-bold text-white focus:outline-none focus:border-brand-cyan transition-colors"
            />
          </div>

          {/* Stat Type */}
          <div className="w-full md:w-48">
            <label className="text-[10px] font-black uppercase tracking-widest text-textMuted mb-2 block">Stat Type</label>
            <select 
              title="Stat Type"
              aria-label="Stat Type"
              value={statType}
              onChange={(e) => setStatType(e.target.value)}
              className="w-full bg-lucrix-dark border border-lucrix-border rounded-xl px-4 py-3 text-sm font-bold text-white focus:outline-none focus:border-brand-cyan transition-colors appearance-none"
            >
              {statTypes.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>

          {/* Slider */}
          <div className="w-full md:w-64">
            <div className="flex justify-between items-center mb-2">
              <label className="text-[10px] font-black uppercase tracking-widest text-textMuted">Min EV Threshold</label>
              <span className={clsx("text-xs font-mono font-black", minEv > 0 ? "text-brand-success" : "text-textMuted")}>{minEv}%</span>
            </div>
            <input 
              type="range" 
              title="Min EV Threshold"
              aria-label="Min EV Threshold"
              min="-5" max="20" step="0.5"
              value={minEv}
              onChange={(e) => setMinEv(parseFloat(e.target.value))}
              className="w-full accent-brand-cyan"
            />
          </div>
        </div>

        {/* Quick Chips */}
        <div className="flex flex-wrap gap-2">
          {["All", "+EV only", "High confidence", "Soonest start"].map(chip => (
            <button 
              key={chip}
              onClick={() => setQuickChip(chip)}
              className={clsx(
                "px-4 py-1.5 rounded-full text-xs font-black uppercase tracking-widest transition-all",
                quickChip === chip 
                  ? "bg-brand-cyan text-black shadow-glow shadow-brand-cyan/30" 
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
        <div className="flex items-center justify-between text-[10px] font-black uppercase tracking-widest text-textMuted px-2">
          <div>
            <span className="text-white">{filteredProps.length}</span> Props Found
            {filteredProps.length > 0 && ` · Max EV: `}
            {filteredProps.length > 0 && <span className="text-brand-success">{Math.max(...filteredProps.map(p => p.ev_percentage)).toFixed(1)}%</span>}
          </div>
          <div className="flex items-center gap-1.5">
            <Clock size={10} />
            Updated {data.updated ? new Date(data.updated).toLocaleTimeString() : 'Just Now'}
          </div>
        </div>
      )}

      {/* Main Table View */}
      <div className="bg-lucrix-surface border border-lucrix-border rounded-2xl overflow-x-auto shadow-card">
        {filteredProps.length === 0 ? (
          <div className="p-12 text-center text-textMuted font-bold text-sm">
            No props available matching your criteria. Try adjusting filters or EV threshold.
          </div>
        ) : (
          <table className="w-full text-left border-collapse min-w-[800px]">
            <thead>
              <tr className="border-b border-lucrix-border">
                <th className="p-4 text-[10px] font-black uppercase tracking-widest text-textMuted whitespace-nowrap">Player & Matchup</th>
                <th className="p-4 text-[10px] font-black uppercase tracking-widest text-textMuted">Stat & Line</th>
                <th className="p-4 text-[10px] font-black uppercase tracking-widest text-textMuted">Best Odds</th>
                <th className="p-4 text-[10px] font-black uppercase tracking-widest text-textMuted">EV%</th>
                <th className="p-4 text-[10px] font-black uppercase tracking-widest text-textMuted">Confidence</th>
                <th className="p-4 text-[10px] font-black uppercase tracking-widest text-textMuted text-right">Intel</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-lucrix-border/50">
              {filteredProps.map(prop => (
                <PropRow key={prop.id} prop={prop} />
              ))}
            </tbody>
          </table>
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

function PropRow({ prop }: { prop: CanonicalProp }) {
  const isPositiveEv = prop.ev_percentage > 0;
  
  return (
    <tr className="group hover:bg-lucrix-dark/50 transition-colors">
      <td className="p-4 py-5 align-middle">
        <div className="flex flex-col">
          <span className="text-sm font-black italic uppercase tracking-tighter text-white font-display">{prop.player_name}</span>
          <span className="text-[10px] font-bold text-textSecondary">{prop.team} vs {prop.opponent}</span>
        </div>
      </td>
      <td className="p-4 align-middle">
        <div className="flex flex-col">
          <span className="text-[10px] font-black uppercase tracking-widest text-brand-cyan">{prop.stat_type}</span>
          <span className="text-lg font-black font-display text-white leading-none mt-1">{prop.line}</span>
        </div>
      </td>
      <td className="p-4 align-middle">
        <div className="flex gap-2">
          <div className="flex flex-col items-center bg-lucrix-dark border border-lucrix-border p-1.5 rounded-lg px-2">
            <span className="text-[8px] font-black text-textMuted uppercase mb-0.5">Ovr</span>
            <span className={clsx("text-xs font-mono font-black", prop.over_odds > 0 ? "text-brand-success" : "text-white")}>
              {prop.over_odds > 0 ? `+${prop.over_odds}` : prop.over_odds}
            </span>
          </div>
          <div className="flex flex-col items-center bg-lucrix-dark border border-lucrix-border p-1.5 rounded-lg px-2">
            <span className="text-[8px] font-black text-textMuted uppercase mb-0.5">Und</span>
            <span className={clsx("text-xs font-mono font-black", prop.under_odds > 0 ? "text-brand-success" : "text-white")}>
              {prop.under_odds > 0 ? `+${prop.under_odds}` : prop.under_odds}
            </span>
          </div>
        </div>
      </td>
      <td className="p-4 align-middle relative">
        <div className="group/tooltip inline-block relative cursor-help">
          <div className={clsx(
            "px-3 py-1 rounded-full text-xs font-black tracking-widest whitespace-nowrap border",
            isPositiveEv ? "bg-brand-success/10 text-brand-success border-brand-success/20" : "bg-brand-danger/10 text-brand-danger border-brand-danger/20 text-opacity-80"
          )}>
            {prop.ev_percentage > 0 ? "+" : ""}{prop.ev_percentage.toFixed(1)}%
          </div>
          {/* Tooltip */}
          <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 bg-lucrix-background border border-lucrix-border p-3 rounded-lg shadow-xl w-48 text-[10px] text-textSecondary opacity-0 group-hover/tooltip:opacity-100 pointer-events-none transition-opacity z-50">
            <div className="font-bold text-white mb-1 uppercase tracking-widest">Edge Explanation</div>
            <div>Model Fair Prob: {(prop.model_probability * 100).toFixed(1)}%</div>
            <div>Implied Prob: {(prop.implied_probability * 100).toFixed(1)}%</div>
            <div className="mt-1 text-brand-cyan text-[8px] italic">{prop.steam_signal ? 'Steam action detected.' : ''}</div>
          </div>
        </div>
      </td>
      <td className="p-4 align-middle">
        <div className="flex items-center gap-2">
          <BarChart3 size={14} className={prop.confidence > 75 ? "text-brand-cyan" : "text-textMuted"} />
          <span className="text-xs font-mono font-black text-white">{prop.confidence.toFixed(1)}</span>
        </div>
      </td>
      <td className="p-4 align-middle text-right">
        <div className="flex justify-end gap-1.5">
          {prop.steam_signal && (
            <span className="bg-lucrix-dark border border-brand-primary text-brand-primary text-[8px] font-black uppercase tracking-widest px-1.5 py-0.5 rounded">Steam</span>
          )}
          {prop.whale_signal && (
            <span className="bg-lucrix-dark border border-purple-400 text-purple-400 text-[8px] font-black uppercase tracking-widest px-1.5 py-0.5 rounded">Whale</span>
          )}
          {isPositiveEv && (
            <span className="bg-lucrix-dark border border-brand-cyan text-brand-cyan text-[8px] font-black uppercase tracking-widest px-1.5 py-0.5 rounded flex items-center gap-1">
              <ShieldAlert size={8} /> EDGE
            </span>
          )}
          {(!prop.steam_signal && !prop.whale_signal && !isPositiveEv) && <span className="text-textMuted text-xs">—</span>}
        </div>
      </td>
    </tr>
  );
}
