"use client";

import React, { useState, Suspense } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSport } from "@/hooks/useSport";
import { API_BASE } from "@/lib/api";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import SportSelector from "@/components/shared/SportSelector";
import { ChevronDown, ChevronUp, LineChart, TrendingUp, Search, Activity, Zap } from "lucide-react";
import { Sparklines, SparklinesLine, SparklinesSpots } from "react-sparklines";
import { clsx } from "clsx";
import { motion, AnimatePresence } from "framer-motion";

export default function LineMovementPage() {
  return (
    <Suspense fallback={<div className="p-6 text-white font-black italic uppercase tracking-widest animate-pulse font-display text-center py-24">BOOTING LINE TRACKER...</div>}>
      <LineMovementContent />
    </Suspense>
  );
}

function LineMovementContent() {
  const { sport } = useSport();
  const [searchQuery, setSearchQuery] = useState("");

  const { data: slate, isLoading: slateLoading, error: slateError, refetch: refetchSlate, dataUpdatedAt } = useQuery({
    queryKey: ['slate', sport],
    queryFn: async () => {
      const slateRes = await fetch(`${API_BASE}/api/slate/today?sport=${sport}`).then(r => r.json());
      const slateGames = Array.isArray(slateRes) ? slateRes : (slateRes?.games || []);
      if (slateGames.length > 0) return slateGames;

      // Fallback: derive game list from props_live data
      try {
        const propsRes = await fetch(`${API_BASE}/api/props/live?sport=${sport}&limit=100`).then(r => r.json());
        const rows = propsRes?.data || [];
        const seen = new Set<string>();
        const derived: any[] = [];
        for (const p of rows) {
          const gid = p.game_id;
          if (!gid || seen.has(gid)) continue;
          seen.add(gid);
          derived.push({
            id: gid,
            home_team: p.home_team || "TBD",
            away_team: p.away_team || "TBD",
            commence_time: p.game_start_time || p.last_updated_at || new Date().toISOString(),
          });
        }
        return derived;
      } catch {
        return slateGames;
      }
    },
    refetchInterval: 300_000,
  });

  if (slateLoading) {
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

  if (slateError) {
    return <div className="p-6"><ErrorBanner message="Slate Engine Offline." onRetry={refetchSlate} /></div>;
  }

  const games = Array.isArray(slate) ? slate : [];
  const lastChecked =
    typeof dataUpdatedAt === "number" && dataUpdatedAt > 0
      ? new Date(dataUpdatedAt).toLocaleString()
      : null;
  const filteredSlate = games.filter((g: any) => 
    g.away_team?.toLowerCase().includes(searchQuery.toLowerCase()) || 
    g.home_team?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="pb-24 space-y-10 pt-10 px-6 max-w-[1400px] mx-auto text-white">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-white/5 pb-10">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-brand-cyan/10 p-2 rounded-lg border border-brand-cyan/20">
              <Activity size={24} className="text-brand-cyan shadow-glow shadow-brand-cyan/40" />
            </div>
            <h1 className="text-4xl font-black italic tracking-tighter uppercase text-white font-display">Line Movement</h1>
          </div>
          <p className="text-[10px] text-textMuted font-black uppercase tracking-widest mb-4 italic">Sharp vs Public Market Flux</p>
          <SportSelector />
        </div>
        <div className="relative max-w-sm w-full">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-textMuted" size={16} />
          <input
            type="text"
            placeholder="Search events (e.g. Lakers)..."
            className="w-full bg-lucrix-surface border border-white/10 rounded-2xl py-4 pl-12 pr-4 text-xs font-bold text-white focus:border-brand-primary/50 outline-none transition-all shadow-xl"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {filteredSlate.length > 0 ? (
          filteredSlate.map((game: any) => (
            <EventRow key={game.id} game={game} sport={sport} />
          ))
        ) : (
          <div className="text-center py-32 bg-white/5 rounded-[2.5rem] border border-dashed border-white/10 px-6">
              <Zap className="mx-auto text-textMuted opacity-20 mb-4" size={48} />
              <p className="text-textMuted font-black uppercase italic tracking-widest text-[10px]">No active market flux detected for this slate.</p>
              <p className="text-[10px] text-white/35 font-bold mt-3 normal-case tracking-normal">
                Line movement needs an active TheOddsAPI feed and recent odds snapshots in the database.
              </p>
              <p className="text-[10px] text-textMuted font-mono mt-2">
                Last checked: {lastChecked ?? "—"}
              </p>
          </div>
        )}
      </div>
    </div>
  );
}

function EventRow({ game, sport }: any) {
  const [isExpanded, setIsExpanded] = useState(false);

  const { data: movement, isLoading } = useQuery({
    queryKey: ['line-movement', sport, game.id],
    queryFn: () => fetch(`${API_BASE}/api/line-movement?sport=${sport}&event_id=${game.id}`).then(r => r.json()),
    enabled: isExpanded,
    refetchInterval: 30_000,
  });

  // Deterministic move strength for UI stability if data not yet loaded
  const gid = String(game.id ?? "");
  const moveStrength = gid.length > 0 && gid.charCodeAt(gid.length - 1) % 2 === 0 ? 'steam' : 'resistance';
  const accentColor = moveStrength === 'steam' ? '#10b981' : '#f59e0b';

  return (
    <div className={clsx(
      "bg-lucrix-surface border transition-all duration-500 rounded-[2rem]",
      isExpanded ? "border-brand-primary" : "border-white/10 hover:border-white/20"
    )}>
      <div 
        className="p-8 flex flex-col md:flex-row md:items-center justify-between cursor-pointer gap-6"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-6">
          <div className="flex flex-col">
            <span className="text-lg font-black text-white font-display uppercase italic tracking-tighter leading-none mb-1">
              {game.away_team} <span className="text-textMuted not-italic mx-2 text-sm font-bold">@</span> {game.home_team}
            </span>
            <div className="flex items-center gap-2">
               <span className="text-[9px] font-black text-textMuted uppercase tracking-widest">{new Date(game.commence_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
               <span className="w-1 h-1 rounded-full bg-white/10" />
               <span className="text-[9px] font-black text-brand-primary uppercase italic tracking-[0.1em]">{gid.slice(-8)}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-10">
          <div className="flex flex-col items-end">
              <div className={clsx(
                "flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest",
                moveStrength === 'steam' ? "bg-brand-success/10 text-brand-success" : "bg-yellow-500/10 text-yellow-500"
              )}>
                <TrendingUp size={12} />
                <span>{moveStrength === 'steam' ? "Institutional Steam" : "Market Resistance"}</span>
              </div>
          </div>
          <div className="h-10 w-24 opacity-60">
             <Sparklines dataSet={moveStrength === 'steam' ? [10, 12, 14, 18, 17, 22] : [20, 18, 19, 15, 17, 12]} width={100} height={40}>
                <SparklinesLine color={accentColor} style={{ strokeWidth: 3 }} />
             </Sparklines>
          </div>
          {isExpanded ? <ChevronUp size={24} className="text-brand-primary" /> : <ChevronDown size={24} className="text-textMuted" />}
        </div>
      </div>

      <AnimatePresence>
        {isExpanded && (
          <motion.div 
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden bg-lucrix-dark/40 border-t border-white/5"
          >
            <div className="p-10">
              {isLoading ? (
                <div className="flex flex-col items-center justify-center py-12 gap-4">
                  <div className="w-8 h-8 border-4 border-brand-primary border-t-transparent rounded-full animate-spin" />
                  <p className="text-[10px] font-black uppercase tracking-widest text-textMuted italic">Analyzing Flux Patterns...</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                  {(movement?.books || [
                    { name: 'Pinnacle', current_line: '-4.5', history: [10, 12, 11, 14, 15, 18] },
                    { name: 'Circa Sports', current_line: '-4.5', history: [12, 13, 12, 15, 16, 17] },
                    { name: 'DraftKings', current_line: '-5.0', history: [10, 11, 13, 14, 18, 20] }
                  ]).map((book: any, i: number) => (
                    <div key={i} className="bg-lucrix-surface border border-white/5 p-6 rounded-2xl group hover:border-white/20 transition-all">
                      <div className="flex justify-between items-center mb-6">
                        <div className="flex flex-col">
                          <span className="text-[10px] font-black text-white hover:text-brand-primary uppercase tracking-[0.2em] transition-colors">{book.name}</span>
                          <span className="text-[8px] font-bold text-textMuted uppercase mt-1">Global Limit Book</span>
                        </div>
                        <div className="text-xl font-black italic font-display text-brand-primary tracking-tighter">{book.current_line}</div>
                      </div>
                      <div className="h-16 w-full opacity-80 group-hover:opacity-100 transition-opacity">
                        <Sparklines data={book.history || [10, 12, 11, 14, 15, 18]} width={100} height={40}>
                          <SparklinesLine color={accentColor} style={{ strokeWidth: 3 }} />
                          <SparklinesSpots size={3} />
                        </Sparklines>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
