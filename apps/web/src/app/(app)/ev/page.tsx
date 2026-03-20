// apps/web/src/app/(app)/ev/page.tsx
"use client";
import React, { useState, useCallback } from "react";
import { TrendingUp, Calculator, Info, Zap, Filter, Search, BookOpen } from "lucide-react";
import { Sparklines, SparklinesLine, SparklinesSpots } from "react-sparklines";
import { useLiveData } from "@/hooks/useLiveData";
import { api, isApiError, unwrap } from "@/lib/api";
import LiveStatusBar from "@/components/LiveStatusBar";
import PageStates from "@/components/PageStates";
import GateLock from "@/components/GateLock";

import { useLucrixStore } from "@/store";
import { useFreshness } from "@/hooks/useFreshness";
import { FreshnessBadge } from "@/components/dashboard/FreshnessBadge";
import SportSelector from "@/components/shared/SportSelector";
import { LiveHistoricalToggle } from "@/components/dashboard/LiveHistoricalToggle";
import { Clock } from "lucide-react";

export default function EVPage() {
    const sport = useLucrixStore((state: any) => state.activeSport);
    const freshness = useFreshness(sport);
    const [isHistorical, setIsHistorical] = useState(false);

    const { data: picks, loading, error, lastUpdated, isStale, refresh } = useLiveData<any[]>(
        () => api.ev.top(sport, 50, isHistorical),
        [sport, isHistorical],
        { refreshInterval: isHistorical ? 600000 : 180000 }
    );

    const [minEv, setMinEv] = useState(2);
    const [searchQuery, setSearchQuery] = useState("");
    const [selectedBook, setSelectedBook] = useState("all");

    const fullPicks = unwrap(picks) || [];
    const filteredPicks = fullPicks.filter((p: any) => {
        const matchesSearch = p.player_name?.toLowerCase().includes(searchQuery.toLowerCase()) || 
                             p.market_key?.toLowerCase().includes(searchQuery.toLowerCase());
        const matchesEv = (p.ev_percentage || p.edge_pct || 0) >= minEv;
        const matchesBook = selectedBook === "all" || p.bookmaker === selectedBook || p.book === selectedBook;
        return matchesSearch && matchesEv && matchesBook;
    });

    const books = Array.from(new Set(fullPicks.map((p: any) => p.bookmaker || p.book))).filter(Boolean);

    return (
        <GateLock feature="edges" reason="The EV+ Live Scanner is reserved for Premium athletes.">
            <div className="pb-24 space-y-8">
                <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                    <div>
                        <div className="flex items-center gap-3 mb-2">
                            <div className="bg-brand-success/10 p-2 rounded-lg border border-brand-success/20">
                                <TrendingUp size={24} className="text-brand-success shadow-glow shadow-brand-success/40" />
                            </div>
                            <h1 className="text-3xl font-black italic tracking-tighter uppercase text-white font-display">EV+ Live Scanner</h1>
                        </div>
                        <p className="text-[10px] text-textMuted font-bold uppercase tracking-widest mb-4">High-Edge Market Opportunities</p>
                        
                        <div className="mb-6">
                            <SportSelector />
                        </div>

                        <FreshnessBadge 
                            oddsTs={freshness?.odds_last_updated || null} 
                            evTs={freshness?.ev_last_updated || null} 
                        />
                    </div>

                    <div className="flex items-center gap-4">
                        <LiveHistoricalToggle isHistorical={isHistorical} onChange={setIsHistorical} />
                        <LiveStatusBar
                            lastUpdated={lastUpdated}
                            isStale={isStale}
                            loading={loading}
                            error={error}
                            onRefresh={refresh}
                            refreshInterval={120}
                        />
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
                            <Filter size={14} className="text-textMuted" />
                            <span className="text-[10px] font-black text-textMuted uppercase tracking-widest">Min EV:</span>
                            <input 
                                type="range" min="0" max="15" step="0.5" 
                                aria-label="Minimum EV Percentage"
                                title="Minimum EV Percentage"
                                className="w-24 accent-brand-success cursor-pointer" 
                                value={minEv}
                                onChange={(e) => setMinEv(parseFloat(e.target.value))}
                            />
                            <span className="text-xs font-black text-brand-success w-8 font-mono">{minEv}%</span>
                        </div>

                        <div className="flex items-center gap-2 bg-lucrix-dark/50 border border-lucrix-border rounded-lg px-3 py-1.5 focus-within:border-brand-success/50 transition-all">
                            <BookOpen size={14} className="text-textMuted" />
                            <select 
                                aria-label="Select Sportsbook"
                                title="Select Sportsbook"
                                className="bg-transparent text-xs font-black uppercase text-white outline-none cursor-pointer"
                                value={selectedBook}
                                onChange={(e) => setSelectedBook(e.target.value)}
                            >
                                <option value="all" className="bg-lucrix-surface">All Books</option>
                                {books.map((b: any) => <option key={b} value={b} className="bg-lucrix-surface">{b}</option>)}
                            </select>
                        </div>
                    </div>
                </div>

                <PageStates
                    loading={loading && !picks}
                    error={error}
                    empty={!loading && (!picks || picks.length === 0)}
                    emptyMessage="No high-EV edges found right now. Markets are stable."
                >
                    <div className="bg-lucrix-surface border border-lucrix-border rounded-xl overflow-x-auto shadow-card">
                        <table className="w-full text-left min-w-[800px]">
                            <thead>
                                <tr className="bg-lucrix-dark/80 border-b border-lucrix-border text-[9px] font-black uppercase tracking-widest text-textMuted">
                                    <th className="px-6 py-4">Market Pick</th>
                                    <th className="px-6 py-4 text-center">Trend</th>
                                    <th className="px-6 py-4 text-center">Market Odds</th>
                                    <th className="px-6 py-4 text-center">Edge (EV%)</th>
                                    <th className="px-6 py-4 text-right">Action</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-lucrix-border/50">
                                    {(filteredPicks).map((pick: any, i: number) => (
                                    <tr key={`${pick.id || pick.event_id || i}-${i}`} className="group hover:bg-lucrix-dark/50 transition-colors">
                                        <td className="px-6 py-5">
                                            <div className="flex items-center gap-4">
                                                <div className="bg-brand-warning/10 px-2 py-1 rounded-sm text-[10px] font-black border border-brand-warning/20 text-brand-warning uppercase tracking-widest shadow-glow shadow-brand-warning/10">
                                                    {pick.sport}
                                                </div>
                                                <div>
                                                    <div className="font-black text-lg group-hover:text-brand-success transition-colors text-white font-display italic uppercase tracking-tight">{pick.player_name}</div>
                                                    <div className="text-[10px] font-bold text-textSecondary uppercase tracking-widest mt-0.5">{pick.stat_type} — {pick.line}</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-5">
                                            <div className="flex items-center gap-3 h-10 w-24 mx-auto">
                                                {pick.trend && pick.trend.length > 1 ? (
                                                    <Sparklines data={pick.trend} width={100} height={30}>
                                                        <SparklinesLine color="#0df233" style={{ strokeWidth: 3 }} />
                                                        <SparklinesSpots size={3} />
                                                    </Sparklines>
                                                ) : (
                                                    <div className="text-[8px] font-black text-textMuted uppercase italic mx-auto">Stable</div>
                                                )}
                                            </div>
                                        </td>
                                        <td className="px-6 py-5 text-center">
                                            <div className="flex flex-col items-center">
                                                <span className="bg-lucrix-dark px-4 py-2 rounded-lg border border-lucrix-border font-black font-mono text-white text-sm">
                                                    {pick.odds > 0 ? `+${pick.odds}` : pick.odds}
                                                </span>
                                                <div className="text-[8px] text-textMuted mt-1.5 font-black uppercase tracking-widest">{pick.bookmaker || pick.book}</div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-5 text-center">
                                            <div className="flex flex-col items-center">
                                                <div className="flex items-center gap-1.5">
                                                    <span className="text-xl font-black text-brand-success font-display">+{pick.ev_percentage || pick.edge_pct}%</span>
                                                    {(pick.ev_percentage || pick.edge_pct) > 5 && (
                                                        <Zap size={14} className="text-brand-success fill-brand-success animate-pulse" />
                                                    )}
                                                </div>
                                                <div className="text-[9px] font-black text-textMuted uppercase tracking-tighter mt-1">
                                                    Fair: {pick.fair_odds > 0 ? `+${pick.fair_odds}` : pick.fair_odds} | Kelly: {pick.kelly_percentage || 0}%
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-5 text-right">
                                            {isHistorical ? (
                                                <div className="text-[10px] font-black text-textMuted uppercase tracking-widest flex items-center justify-end gap-1.5">
                                                    <Clock size={12} className="text-blue-400" />
                                                    {new Date(pick.created_at).toLocaleDateString()}
                                                </div>
                                            ) : (
                                                <button className="bg-lucrix-dark border border-lucrix-border hover:bg-brand-success hover:border-brand-success hover:text-black text-white px-6 py-2.5 rounded-lg font-black uppercase tracking-widest text-[10px] transition-all shadow-glow hover:shadow-brand-success/20">
                                                    Bet
                                                </button>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </PageStates>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="bg-lucrix-surface border border-lucrix-border p-6 rounded-xl flex items-start gap-4 shadow-card">
                        <div className="bg-brand-warning/10 p-3 rounded-xl border border-brand-warning/20">
                            <Info className="text-brand-warning" size={24} />
                        </div>
                        <div>
                            <h4 className="font-black text-sm text-white uppercase tracking-tight font-display italic">What is EV+?</h4>
                            <p className="text-[11px] text-textSecondary mt-1.5 font-bold leading-relaxed">Expected Value indicates a bet where the probability is in your favor vs the book odds over the long term.</p>
                        </div>
                    </div>
                    {/* Kelly/institutional speed info cards */}
                </div>
            </div>
        </GateLock>
    );
}
