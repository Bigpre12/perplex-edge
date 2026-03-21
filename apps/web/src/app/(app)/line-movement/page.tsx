"use client";

import React, { useState, Suspense } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSport } from "@/hooks/useSport";
import { API_BASE } from "@/lib/api";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import SportSelector from "@/components/shared/SportSelector";
import { ChevronDown, ChevronUp, LineChart, TrendingUp, Search } from "lucide-react";
import { Sparklines, SparklinesLine, SparklinesSpots } from "react-sparklines";
import { clsx } from "clsx";

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

  const { data: slate, isLoading: slateLoading, error: slateError, refetch: refetchSlate } = useQuery({
    queryKey: ['slate', sport],
    queryFn: () => fetch(`${API_BASE}/api/slate/today?sport=${sport}`).then(r => r.json()),
    refetchInterval: 300_000,
  });

  if (slateLoading) {
    return (
      <div className="space-y-6 pt-6 px-4">
        <div className="flex justify-between items-center mb-8">
          <Skeleton className="h-10 w-48" />
          <Skeleton className="h-10 w-32" />
        </div>
        <div className="space-y-4">
          {[...Array(6)].map((_, i) => (
            <Skeleton key={i} className="h-20 w-full rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  if (slateError) {
    return <div className="p-6"><ErrorBanner message="Slate Engine Offline." onRetry={refetchSlate} /></div>;
  }

  const filteredSlate = (slate?.games || []).filter((g: any) => 
    g.away_team?.toLowerCase().includes(searchQuery.toLowerCase()) || 
    g.home_team?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="pb-24 space-y-8 pt-6 px-4">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-brand-cyan/10 p-2 rounded-lg border border-brand-cyan/20">
              <LineChart size={24} className="text-brand-cyan shadow-glow shadow-brand-cyan/40" />
            </div>
            <h1 className="text-3xl font-black italic tracking-tighter uppercase text-white font-display">Line Movement</h1>
          </div>
          <p className="text-[10px] text-textMuted font-black uppercase tracking-widest mb-4 italic">Sharp vs Public Market Flux</p>
          <SportSelector />
        </div>
        <div className="relative max-w-xs w-full">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-textMuted" size={14} />
          <input
            type="text"
            placeholder="Filter events..."
            className="w-full bg-lucrix-surface border border-lucrix-border rounded-lg py-2 pl-9 pr-4 text-xs font-bold text-white focus:border-brand-cyan/50 outline-none"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      <div className="space-y-4">
        {filteredSlate.map((game: any) => (
          <EventRow key={game.id} game={game} sport={sport} />
        ))}
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

  return (
    <div className="bg-lucrix-surface border border-lucrix-border rounded-xl overflow-hidden transition-all hover:border-brand-cyan/20">
      <div 
        className="p-5 flex items-center justify-between cursor-pointer group"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-6">
          <div className="text-sm font-black text-white font-display uppercase italic tracking-tight">
            {game.away_team} @ {game.home_team}
          </div>
          <div className="text-[10px] font-bold text-textSecondary uppercase tracking-widest">
            {new Date(game.commence_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5 text-brand-success">
            <TrendingUp size={14} />
            <span className="text-[10px] font-black italic">+0.5 Sharp Move</span>
          </div>
          {isExpanded ? <ChevronUp size={18} className="text-textMuted" /> : <ChevronDown size={18} className="text-textMuted group-hover:text-brand-cyan" />}
        </div>
      </div>

      {isExpanded && (
        <div className="p-6 bg-lucrix-dark/50 border-t border-lucrix-border animate-in slide-in-from-top-2 duration-200">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="w-6 h-6 border-2 border-brand-cyan border-t-transparent rounded-full animate-spin" />
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {movement?.books?.map((book: any, i: number) => (
                <div key={i} className="space-y-3">
                  <div className="flex justify-between items-center">
                    <div className="text-[10px] font-black text-white uppercase tracking-widest">{book.name}</div>
                    <div className="text-[10px] font-mono font-bold text-brand-cyan">{book.current_line}</div>
                  </div>
                  <div className="h-12 w-full">
                    <Sparklines data={book.history} width={100} height={30}>
                      <SparklinesLine color="#00f2ff" style={{ strokeWidth: 2 }} />
                      <SparklinesSpots size={2} />
                    </Sparklines>
                  </div>
                </div>
              ))}
              {!movement?.books?.length && (
                <div className="col-span-full text-center text-textMuted text-[10px] font-black uppercase italic py-4">
                  No movement data for this event yet.
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
