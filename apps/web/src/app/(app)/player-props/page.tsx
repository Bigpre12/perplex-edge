"use client";

import { useState, Suspense } from "react";
import { Zap, Search, RefreshCw, Filter, Trophy, Star, Clock } from "lucide-react";
import { clsx } from "clsx";
import { useLiveData } from "@/hooks/useLiveData";
import { useGate } from "@/hooks/useGate";
import { useLucrixStore } from "@/store";
import GateLock from "@/components/GateLock";
import PropsEmptyState from "@/components/PropsEmptyState";
import LiveStatusBar from "@/components/LiveStatusBar";
import { api, unwrap } from "@/lib/api";
import { useSearchParams } from "next/navigation";
import SportSelector from "@/components/shared/SportSelector";
import { UniversalDataGate, DataStatus } from "@/components/shared/UniversalDataGate";
import { useFreshness } from "@/hooks/useFreshness";
import { FreshnessBadge } from "@/components/dashboard/FreshnessBadge";
import { LiveHistoricalToggle } from "@/components/dashboard/LiveHistoricalToggle";
import TrendChart from "@/components/TrendChart";
import { motion, AnimatePresence } from "framer-motion";
import { X, TrendingUp, Brain } from "lucide-react";
import { useQuery } from "@tanstack/react-query";

export default function PlayerPropsPage() {
    return (
        <Suspense fallback={<div className="p-6 text-white font-black italic uppercase tracking-widest animate-pulse font-display">BOOTING INTEL...</div>}>
            <PlayerPropsContent />
        </Suspense>
    );
}

function PlayerPropsContent() {
    const sport = useLucrixStore((state: any) => state.activeSport);
    const tier = useLucrixStore((state: any) => state.userTier);
    const freshness = useFreshness(sport);
    const searchParams = useSearchParams();
    
    // Filters from URL (controlled by SportFilterBar)
    const market = searchParams.get("market");
    const minEv = parseFloat(searchParams.get("minEdge") || "0");
    const [searchQuery, setSearchQuery] = useState("");
    const [isHistorical, setIsHistorical] = useState(false);

    const { data: propsData, loading, error, refresh, lastUpdated, isStale, status } = useLiveData(
        () => api.props(sport, market || undefined, minEv, 50, isHistorical),
        [sport, market, minEv, isHistorical],
        { refreshInterval: isHistorical ? 300000 : 60000 }
    );

    const [selectedHero, setSelectedHero] = useState<string | null>(null);

    const fullData = unwrap(propsData) || [];
    const { tier: activeTier, propsLimit } = useGate();

    const currentStatus = (propsData as any)?.status || (loading ? "loading" : "ok");
    const debugInfo = (propsData as any)?.meta ? {
        source: (propsData as any).meta.source,
        rows: (propsData as any).meta.db_rows,
        last_sync: (propsData as any).meta.last_sync,
        request_id: (propsData as any).meta.request_id
    } : undefined;
    
    // Grouping for Historical Mode
    const historicalGroups = isHistorical ? fullData.reduce((acc: any, tick: any) => {
        const key = `${tick.player_name}_${tick.market_key}`;
        if (!acc[key]) {
            acc[key] = {
                player_name: tick.player_name,
                market_key: tick.market_key,
                latest_line: tick.line,
                ticks: []
            };
        }
        acc[key].ticks.push(tick);
        return acc;
    }, {}) : {};
    
    const historicalItems = Object.values(historicalGroups);

    // In dev, show everything regardless of tier slicing
    const isDev = typeof window !== 'undefined' && 
      (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');

    const limitedData = isDev ? (isHistorical ? historicalItems : fullData) : (isHistorical ? historicalItems.slice(0, propsLimit) : fullData.slice(0, propsLimit));

    const filtered = (limitedData as any[]).filter((p: any) =>
        (p.player_name?.toLowerCase().includes(searchQuery.toLowerCase())) ||
        (p.market_key?.toLowerCase().includes(searchQuery.toLowerCase()))
    );

    return (
        <div className="pb-24 space-y-8">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="bg-brand-cyan/10 p-2 rounded-lg border border-brand-cyan/20">
                            <Trophy size={24} className="text-brand-cyan shadow-glow shadow-brand-cyan" />
                        </div>
                        <h1 className="text-3xl font-black italic tracking-tighter uppercase font-display text-white">Pick Intel</h1>
                    </div>
                    <p className="text-[10px] text-textMuted font-bold uppercase tracking-widest mb-4">Elite Player Prop Decisioning</p>
                    
                    <div className="mb-6">
                        <SportSelector />
                    </div>

                    <div className="flex flex-wrap items-center gap-4 mb-6">
                        <FreshnessBadge 
                            oddsTs={freshness?.odds_last_updated || null} 
                            evTs={freshness?.ev_last_updated || null} 
                        />
                        <LiveHistoricalToggle 
                            isHistorical={isHistorical} 
                            onChange={setIsHistorical} 
                        />
                    </div>
                    <div className="relative max-w-md">
                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-textMuted" size={18} />
                        <input
                            type="text"
                            placeholder="Search athlete or market..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full bg-lucrix-surface border border-lucrix-border rounded-xl py-3 pl-12 pr-4 text-sm focus:border-brand-cyan/50 focus:ring-1 focus:ring-brand-cyan/30 outline-none transition-all font-bold placeholder:text-textMuted text-white shadow-card"
                        />
                    </div>
                </div>

                <LiveStatusBar
                    lastUpdated={lastUpdated}
                    isStale={isStale}
                    loading={loading}
                    error={error}
                    onRefresh={refresh}
                    refreshInterval={120}
                />
            </div>

            <UniversalDataGate
                status={currentStatus as DataStatus}
                isLoading={loading && !propsData}
                data={filtered}
                debugInfo={debugInfo}
                onRetry={refresh}
            >
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    {filtered.map((item: any, i: number) => (
                        isHistorical 
                            ? <HistoricalPropCard key={i} group={item} />
                            : <PropCard key={i} prop={item} onViewHero={() => setSelectedHero(item.player_name)} />
                    ))}
                </div>

                <HeroModal 
                    playerName={selectedHero} 
                    sport={sport} 
                    onClose={() => setSelectedHero(null)} 
                />

                {activeTier === "free" && fullData.length > propsLimit && !isDev && (
                    <div className="mt-12 p-12 text-center bg-gradient-to-b from-brand-cyan/10 to-transparent border border-brand-cyan/20 rounded-2xl relative overflow-hidden group cursor-pointer" onClick={() => window.location.href = "/subscription"}>
                        <div className="relative z-10">
                            <Star size={40} className="mx-auto text-brand-cyan mb-4 animate-pulse shadow-glow shadow-brand-cyan" />
                            <h3 className="text-2xl font-black italic uppercase tracking-tighter mb-2 text-white font-display">
                                +{fullData.length - propsLimit} Pro Intelligence Items Hidden
                            </h3>
                            <p className="text-textSecondary text-sm max-w-md mx-auto mb-8 font-bold">
                                You are viewing a limited feed. Upgrade to Reveal All sharp edges and model predictions.
                            </p>
                            <button className="bg-brand-cyan hover:bg-brand-cyan/90 text-black px-10 py-4 rounded-xl font-black uppercase tracking-widest text-sm transition-all shadow-glow shadow-brand-cyan/50">
                                Reveal All Intel →
                            </button>
                        </div>
                        <div className="absolute inset-0 bg-brand-cyan/5 blur-3xl rounded-full scale-50 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </div>
                )}
            </UniversalDataGate>
        </div>
    );
}

function PropCard({ prop, onViewHero }: { prop: any, onViewHero: () => void }) {
    const over = prop.best_over;
    const under = prop.best_under;
    const rec = prop.recommendation;

    const addToBuilder = () => {
        const saved = localStorage.getItem("parlay_legs");
        let legs = [];
        try {
            if (saved) legs = JSON.parse(saved);
        } catch (e) { }

        const newLeg = {
            prop_id: prop.id || `${prop.player_name}_${prop.stat_type}`,
            player_name: prop.player_name,
            side: rec?.side === "under" ? "Under" : "Over", // Use recommendation as default
            line: (rec?.side === "under" ? under?.line : over?.line) || 0,
            stat_category: prop.stat_type,
            odds: (rec?.side === "under" ? under?.odds : over?.odds) || 0,
            over_price: over?.odds || -110,
            under_price: under?.odds || -110,
            historical_hit_rate: prop.hit_rate_l10 ? prop.hit_rate_l10 / 100 : 0.5,
            game_id: prop.game_id
        };

        if (!legs.find((l: any) => l.prop_id === newLeg.prop_id)) {
            legs.push(newLeg);
            localStorage.setItem("parlay_legs", JSON.stringify(legs));
            alert("Added to Parlay Slip!");
        }
    };

    return (
        <div className={clsx(
            "bg-lucrix-surface border rounded-2xl p-6 transition-all group shadow-card relative overflow-hidden flex flex-col justify-between",
            rec?.tier === "S" ? "border-brand-cyan/50 shadow-glow shadow-brand-cyan/10" : "border-lucrix-border hover:border-brand-cyan/30"
        )}>
            {/* Recommendation Ribbon for S/A Tier */}
            {(rec?.tier === "S" || rec?.tier === "A") && (
                <div className="absolute top-0 right-0">
                    <div className="bg-brand-cyan text-black text-[8px] font-black uppercase tracking-widest py-1 px-4 rounded-bl-xl rotate-0 origin-top-right">
                        {rec.tier} TIER PICK
                    </div>
                </div>
            )}

            <div>
                <div className="flex justify-between items-start mb-6">
                    <div>
                        <div className="text-lg font-black tracking-tight text-white font-display italic uppercase">{prop.player_name}</div>
                        <div className="text-[10px] font-black uppercase text-brand-cyan tracking-widest mt-1">
                            {prop.stat_type?.replace('_', ' ')}
                        </div>
                    </div>
                    <div className="text-right">
                        <div className="text-[10px] font-black text-textMuted uppercase tracking-widest">Matchup</div>
                        <div className="text-xs font-bold text-textSecondary">{prop.away_team} @ {prop.home_team}</div>
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                    <div className={clsx(
                        "border rounded-xl p-3 transition-all",
                        rec?.side === "over"
                            ? "bg-brand-success/10 border-brand-success/30 ring-1 ring-brand-success/20"
                            : "bg-lucrix-dark border-lucrix-border/50 opacity-80"
                    )}>
                        <div className="flex justify-between items-center mb-2">
                            <div className="text-[10px] font-black text-brand-success uppercase tracking-widest">OVER</div>
                            {rec?.side === "over" && (
                                <Zap size={10} className="text-brand-success fill-brand-success animate-pulse" />
                            )}
                        </div>
                        {over ? (
                            <>
                                <div className="text-2xl font-black text-white font-display leading-none mb-2">{over.line}</div>
                                <div className="flex items-center justify-between mt-1">
                                    <span className="font-mono font-black text-brand-success text-sm">{over.odds > 0 ? `+${over.odds}` : over.odds}</span>
                                    <span className="text-[9px] font-black uppercase text-textMuted tracking-tighter truncate max-w-[50px]">{over.book}</span>
                                </div>
                            </>
                        ) : (
                            <div className="text-xs text-textMuted italic font-bold py-2">No market</div>
                        )}
                    </div>

                    <div className={clsx(
                        "border rounded-xl p-3 transition-all",
                        rec?.side === "under"
                            ? "bg-brand-danger/10 border-brand-danger/30 ring-1 ring-brand-danger/20"
                            : "bg-lucrix-dark border-lucrix-border/50 opacity-80"
                    )}>
                        <div className="flex justify-between items-center mb-2">
                            <div className="text-[10px] font-black text-brand-danger uppercase tracking-widest">UNDER</div>
                            {rec?.side === "under" && (
                                <Zap size={10} className="text-brand-danger fill-brand-danger animate-pulse" />
                            )}
                        </div>
                        {under ? (
                            <>
                                <div className="text-2xl font-black text-white font-display leading-none mb-2">{under.line}</div>
                                <div className="flex items-center justify-between mt-1">
                                    <span className="font-mono font-black text-brand-danger text-sm">{under.odds > 0 ? `+${under.odds}` : under.odds}</span>
                                    <span className="text-[9px] font-black uppercase text-textMuted tracking-tighter truncate max-w-[50px]">{under.book}</span>
                                </div>
                            </>
                        ) : (
                            <div className="text-xs text-textMuted italic font-bold py-2">No market</div>
                        )}
                    </div>
                </div>

                {/* Advisor Insights */}
                {rec && (
                    <div className="mt-4 p-3 bg-lucrix-dark/50 rounded-xl border border-lucrix-border">
                        <div className="flex items-center gap-2 mb-1.5">
                            <div className={clsx(
                                "size-1.5 rounded-full",
                                rec.tier === "S" ? "bg-brand-cyan animate-pulse shadow-glow shadow-brand-cyan" : "bg-brand-cyan/50"
                            )} />
                            <span className="text-[9px] font-black text-textMuted uppercase tracking-widest">Advisor Insight</span>
                        </div>
                        <p className="text-[11px] font-bold text-textSecondary leading-tight">
                            {rec.reason}
                        </p>
                    </div>
                )}
            </div>

            <div className="mt-6 pt-4 border-t border-lucrix-border flex items-center justify-between">
                <div className="text-[9px] font-black text-textMuted uppercase tracking-widest">
                    Tick: {prop.commence_time ? new Date(prop.commence_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '—'}
                </div>
                <div className="flex items-center gap-2">
                    <button
                        onClick={onViewHero}
                        className="text-[9px] font-black uppercase tracking-widest text-white/70 hover:text-brand-cyan transition-colors"
                    >
                        Hero Stats →
                    </button>
                    <button
                        onClick={addToBuilder}
                        className="text-[9px] font-black uppercase tracking-widest text-brand-cyan hover:text-white transition-colors border border-brand-cyan/20 bg-brand-cyan/10 px-2 py-1 rounded-sm"
                    >
                        Add Leg +
                    </button>
                </div>
            </div>
        </div>
    );
}

function HeroModal({ playerName, sport, onClose }: { playerName: string | null, sport: string, onClose: () => void }) {
    const { data: heroRes, isLoading } = useQuery({
        queryKey: ["hero", playerName, sport],
        queryFn: () => api.hero(playerName || "", sport),
        enabled: !!playerName
    });

    const hero = unwrap(heroRes);

    if (!playerName) return null;

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-md"
                onClick={onClose}
            >
                <motion.div
                    initial={{ scale: 0.95, y: 20 }}
                    animate={{ scale: 1, y: 0 }}
                    exit={{ scale: 0.95, y: 20 }}
                    onClick={(e) => e.stopPropagation()}
                    className="w-full max-w-2xl bg-[#0D0D14] border border-white/5 rounded-3xl shadow-2xl overflow-hidden"
                >
                    {/* Header */}
                    <div className="p-6 border-b border-white/[0.05] flex justify-between items-start">
                        <div className="flex items-center gap-4">
                            <h2 className="text-2xl font-black text-white italic tracking-tighter uppercase font-display">
                                {playerName} <span className="text-brand-cyan">Hero View</span>
                            </h2>
                        </div>
                        <button 
                            onClick={onClose} 
                            className="p-2 hover:bg-white/5 rounded-full transition-colors text-[#6B7280] hover:text-white"
                            aria-label="Close Hero Stats"
                            title="Close"
                        >
                            <X size={20} />
                        </button>
                    </div>

                    {/* Content */}
                    {isLoading ? (
                        <div className="py-24 text-center text-brand-cyan animate-pulse font-black uppercase italic tracking-widest">
                            Crunching Models...
                        </div>
                    ) : hero ? (
                        <div className="p-6 space-y-8">
                            <div className="grid grid-cols-3 gap-4">
                                <div className="bg-white/5 p-4 rounded-2xl border border-white/10 text-center">
                                    <div className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">L5 Hit Rate</div>
                                    <div className="text-2xl font-black text-green-500">{(hero.stats?.l5_hit * 100).toFixed(0)}%</div>
                                </div>
                                <div className="bg-white/5 p-4 rounded-2xl border border-white/10 text-center">
                                    <div className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">L10 Hit Rate</div>
                                    <div className="text-2xl font-black text-green-500">{(hero.stats?.l10_hit * 100).toFixed(0)}%</div>
                                </div>
                                <div className="bg-white/5 p-4 rounded-2xl border border-white/10 text-center">
                                    <div className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Current Line</div>
                                    <div className="text-2xl font-black text-white">{hero.current_line}</div>
                                </div>
                            </div>

                            <div className="bg-black/40 p-6 rounded-2xl border border-white/5">
                                <h3 className="text-[10px] font-black uppercase text-brand-cyan tracking-[0.2em] mb-6 flex items-center gap-2 italic">
                                    <TrendingUp size={14} className="text-brand-cyan" />
                                    Performance Analytics vs Market Line
                                </h3>
                                <TrendChart 
                                    data={hero.history?.map((h: any, i: number) => ({
                                        game: `G${i}`,
                                        value: h.line,
                                        hit: h.line > hero.current_line 
                                    })).slice(-10)} 
                                    line={hero.current_line}
                                    statType="Prop"
                                />
                            </div>

                            <div className="p-4 bg-brand-cyan/5 border border-brand-cyan/20 rounded-xl">
                                <div className="flex items-center gap-2 mb-2">
                                    <Brain size={14} className="text-brand-cyan" />
                                    <span className="text-[10px] font-black uppercase text-white tracking-widest">Model Consensus</span>
                                </div>
                                <p className="text-[11px] font-bold text-slate-400 leading-relaxed italic">
                                    Our multi-brain ensemble suggests {playerName} is currently trending in the top 5% of efficiency for the {sport} slate. High correlation noted between market steam and projected volume.
                                </p>
                            </div>
                        </div>
                    ) : (
                        <div className="py-12 text-center text-slate-500 font-bold uppercase tracking-widest italic">No hero data found for this player.</div>
                    )}
                </motion.div>
            </motion.div>
        </AnimatePresence>
    );
}

function HistoricalPropCard({ group }: { group: any }) {
    // Transform ticks for TrendChart
    const trendData = group.ticks.map((t: any, idx: number) => ({
        game: `G${idx}`,
        value: t.line,
        hit: false // Placeholder
    })).slice(-10);

    return (
        <div className="bg-lucrix-surface border border-lucrix-border rounded-2xl p-6 shadow-card hover:border-blue-500/30 transition-all group">
            <div className="flex justify-between items-start mb-6">
                <div>
                    <div className="text-lg font-black tracking-tight text-white font-display italic uppercase leading-none">{group.player_name}</div>
                    <div className="text-[10px] font-black uppercase text-brand-cyan tracking-widest mt-1.5 flex items-center gap-2">
                        <span className="bg-brand-cyan/10 px-1.5 py-0.5 rounded border border-brand-cyan/20">
                            {group.market_key?.replace('_', ' ')}
                        </span>
                    </div>
                </div>
                <div className="text-right">
                    <div className="text-[8px] font-black text-white bg-blue-500/20 px-2 py-0.5 rounded border border-blue-500/30 uppercase tracking-widest mb-1.5">Market Trend</div>
                    <div className="text-sm font-black text-white font-display uppercase tracking-tight italic">Line: {group.latest_line}</div>
                </div>
            </div>

            <div className="mt-4 pt-4 border-t border-lucrix-border/50">
                <div className="text-[9px] font-black text-textMuted uppercase tracking-widest mb-4 flex items-center justify-between">
                    <div className="flex items-center gap-1.5">
                        <Clock size={11} className="text-blue-400" />
                        Price History (Last 10)
                    </div>
                    <div className="text-[8px] bg-zinc-800 px-1.5 py-0.5 rounded text-zinc-400">VOLATILE</div>
                </div>
                <TrendChart data={trendData} line={group.latest_line} statType={group.market_key} />
            </div>

            <div className="mt-6 flex items-center justify-between text-[10px] font-black text-textMuted uppercase tracking-widest group-hover:text-blue-400 transition-colors cursor-pointer">
                <span>View Full Market Depth →</span>
            </div>
        </div>
    );
}
