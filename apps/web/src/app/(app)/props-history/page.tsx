"use client";

import React, { useState, Suspense } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSport } from "@/hooks/useSport";
import { API_BASE } from "@/lib/api";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import SportSelector from "@/components/shared/SportSelector";
import { History, Search, LineChart, BarChart2, Clock, Calendar, TrendingUp } from "lucide-react";
import { clsx } from "clsx";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell } from "recharts";

export default function PropsHistoryPage() {
  return (
    <Suspense fallback={<div className="p-6 text-white font-black italic uppercase tracking-widest animate-pulse font-display text-center py-24">RETRIEVING HISTORICAL DATA...</div>}>
      <PropsHistoryContent />
    </Suspense>
  );
}

function PropsHistoryContent() {
  const { sport } = useSport();
  const [playerQuery, setPlayerQuery] = useState("");
  const [selectedPlayer, setSelectedPlayer] = useState<string | null>(null);

  const { data: history, isLoading, error, refetch } = useQuery({
    queryKey: ['props-history', sport, selectedPlayer],
    queryFn: () => {
      if (!selectedPlayer) return null;
      return fetch(`${API_BASE}/api/props-history?sport=${sport}&player=${selectedPlayer}`).then(r => r.json());
    },
    enabled: !!selectedPlayer,
    staleTime: 300_000,
  });

  return (
    <div className="pb-24 space-y-8 pt-6 px-4">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-brand-cyan/10 p-2 rounded-lg border border-brand-cyan/20">
              <History size={24} className="text-brand-cyan shadow-glow shadow-brand-cyan/40" />
            </div>
            <h1 className="text-3xl font-black italic tracking-tighter uppercase text-white font-display">Props History</h1>
          </div>
          <p className="text-[10px] text-textMuted font-black uppercase tracking-widest mb-4 italic">Deep-Dive Player Performance Metrics</p>
          <SportSelector />
        </div>
        <div className="relative w-full max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-textMuted" size={14} />
          <input 
            type="text" 
            placeholder="Search player name (e.g. LeBron James)..." 
            className="w-full bg-lucrix-surface border border-lucrix-border rounded-xl py-3 pl-10 pr-4 text-xs font-bold text-white focus:border-brand-cyan/50 outline-none transition-all shadow-card"
            value={playerQuery}
            onChange={(e) => setPlayerQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && setSelectedPlayer(playerQuery)}
          />
          {playerQuery && !selectedPlayer && (
            <button 
              onClick={() => setSelectedPlayer(playerQuery)}
              className="absolute right-2 top-1/2 -translate-y-1/2 bg-brand-cyan text-black px-3 py-1 rounded-lg text-[10px] font-black uppercase tracking-widest"
            >
              Search
            </button>
          )}
        </div>
      </div>

      {!selectedPlayer ? (
        <div className="text-center py-32 space-y-6 bg-lucrix-surface/30 border border-dashed border-lucrix-border rounded-3xl">
          <BarChart2 size={48} className="mx-auto text-textMuted opacity-20" />
          <p className="text-textSecondary font-bold italic">Search for a player to analyze their market history.</p>
        </div>
      ) : isLoading ? (
        <div className="space-y-6">
          <Skeleton className="h-64 w-full rounded-3xl" />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[...Array(3)].map((_, i) => <Skeleton key={i} className="h-32 w-full rounded-2xl" />)}
          </div>
        </div>
      ) : error ? (
        <ErrorBanner message="History Query Failed." onRetry={refetch} />
      ) : (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <div className="bg-lucrix-surface border border-lucrix-border rounded-3xl p-8 shadow-card">
            <div className="flex justify-between items-center mb-8">
              <div>
                <h2 className="text-xl font-black text-white font-display italic uppercase tracking-tight">Performance Log</h2>
                <p className="text-[9px] font-black text-textMuted uppercase tracking-widest mt-1">Last {history?.games?.length || 0} Game Entries</p>
              </div>
              <div className="flex gap-4">
                <MiniStat label="Avg Value" value={history?.meta?.avg_value || '0.0'} />
                <MiniStat label="Hit %" value={`${history?.meta?.hit_pct || '0'}%`} />
              </div>
            </div>

            <div className="h-80 w-full mt-8 min-w-0">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={history?.games || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} opacity={0.3} />
                  <XAxis dataKey="date" stroke="#4b5563" fontSize={9} tickLine={false} axisLine={false} />
                  <YAxis stroke="#4b5563" fontSize={9} tickLine={false} axisLine={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0D0D14', border: '1px solid #1e293b', borderRadius: '12px', fontSize: '10px' }}
                    cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                  />
                  <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                    {(history?.games || []).map((entry: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={entry.hit ? '#10b981' : '#ef4444'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-lucrix-surface border border-lucrix-border rounded-2xl p-6">
              <h3 className="text-xs font-black text-white uppercase tracking-widest mb-6 flex items-center gap-2">
                <Calendar size={14} className="text-brand-cyan" /> Recent Log
              </h3>
              <div className="space-y-4">
                {history?.games?.slice(0, 5).map((game: any, idx: number) => (
                  <div key={idx} className="flex justify-between items-center p-3 bg-lucrix-dark/50 rounded-xl border border-lucrix-border">
                    <div>
                      <div className="text-[10px] font-black text-white uppercase italic">{game.opponent}</div>
                      <div className="text-[8px] font-bold text-textMuted uppercase">{game.date}</div>
                    </div>
                    <div className="flex items-center gap-4">
                       <span className="text-sm font-black text-white font-mono">{game.value}</span>
                       <span className={clsx(
                         "text-[9px] font-black px-2 py-0.5 rounded uppercase tracking-widest",
                         game.hit ? "bg-brand-success/10 text-brand-success" : "bg-brand-danger/10 text-brand-danger"
                       )}>
                         {game.hit ? "HIT" : "MISS"}
                       </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-lucrix-surface border border-lucrix-border rounded-2xl p-6">
              <h3 className="text-xs font-black text-white uppercase tracking-widest mb-6 flex items-center gap-2">
                <TrendingUp size={14} className="text-brand-cyan" /> Market Sensitivity
              </h3>
              <div className="p-8 text-center bg-lucrix-dark/30 rounded-2xl border border-dashed border-lucrix-border">
                <p className="text-[10px] font-bold text-textMuted italic mb-4">Correlation analysis against opening lines...</p>
                <div className="flex justify-center gap-12">
                   <div>
                     <div className="text-2xl font-black text-brand-cyan font-display italic">0.82</div>
                     <div className="text-[8px] font-black text-textMuted uppercase mt-1">Sharp Beta</div>
                   </div>
                   <div>
                     <div className="text-2xl font-black text-brand-cyan font-display italic">+4.2%</div>
                     <div className="text-[8px] font-black text-textMuted uppercase mt-1">Closing Edge</div>
                   </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function MiniStat({ label, value }: { label: string, value: string }) {
  return (
    <div className="text-right">
      <div className="text-[8px] font-black text-textMuted uppercase tracking-widest">{label}</div>
      <div className="text-xl font-black text-white italic font-display">{value}</div>
    </div>
  );
}
