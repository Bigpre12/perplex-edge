"use client";

import { useState, Suspense } from "react";
import { Zap, Search, RefreshCw, Filter, Trophy, Star } from "lucide-react";
import { clsx } from "clsx";
import { useLiveData } from "@/hooks/useLiveData";
import { useGate } from "@/hooks/useGate";
import { useLucrixStore } from "@/store";
import GateLock from "@/components/GateLock";
import PropsEmptyState from "@/components/PropsEmptyState";
import LiveStatusBar from "@/components/LiveStatusBar";
import PageStates from "@/components/PageStates";
import { api, unwrap } from "@/lib/api";
import { useFreshness } from "@/hooks/useFreshness";
import { FreshnessBadge } from "@/components/dashboard/FreshnessBadge";

export default function PlayerPropsPage() {
    return (
        <Suspense fallback={<div className="p-6 text-white font-black italic animate-pulse">BOOTING INTEL...</div>}>
            <PlayerPropsContent />
        </Suspense>
    );
}

function PlayerPropsContent() {
    const sport = useLucrixStore((state: any) => state.activeSport);
    const tier = useLucrixStore((state: any) => state.userTier);
    const freshness = useFreshness(sport);
    const [searchQuery, setSearchQuery] = useState("");
    const [evOnly, setEvOnly] = useState(false);

    const { data: propsData, loading, error, refresh, lastUpdated, isStale } = useLiveData(
        () => api.props(sport),
        [sport],
        { refreshInterval: 120000 }
    );

    const fullData = (propsData as any)?.items || [];
    const { tier: activeTier, propsLimit } = useGate();
    
    // In dev, show everything regardless of tier slicing
    const isDev = typeof window !== 'undefined' && 
      (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');

    const limitedData = isDev ? fullData : fullData.slice(0, propsLimit);

    const filtered = limitedData.filter((p: any) =>
        p.player_name?.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-8 text-white pb-24">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="bg-primary/20 p-2 rounded-lg border border-primary/30">
                            <Trophy size={24} className="text-primary" />
                        </div>
                        <h1 className="text-3xl font-black italic tracking-tighter uppercase">Pick Intel</h1>
                    </div>
                    <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mb-4">Elite Player Prop Decisioning</p>
                    <div className="mb-6">
                        <FreshnessBadge 
                            oddsTs={freshness?.odds_last_updated || null} 
                            evTs={freshness?.ev_last_updated || null} 
                        />
                    </div>
                    <div className="relative max-w-md">
                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                        <input
                            type="text"
                            placeholder="Search athlete or market..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full bg-[#1A1D2E] border border-white/5 rounded-2xl py-3 pl-12 pr-4 text-sm focus:border-primary/50 outline-none transition-all font-bold placeholder:text-slate-600"
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

            <PageStates
                loading={loading && !propsData}
                error={error}
                empty={!loading && filtered.length === 0}
            >
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {filtered.map((prop: any, i: number) => (
                        <PropCard key={i} prop={prop} />
                    ))}
                </div>

                {activeTier === "free" && fullData.length > propsLimit && !isDev && (
                    <div className="mt-12 p-12 text-center bg-gradient-to-b from-primary/5 to-transparent border border-primary/20 rounded-3xl relative overflow-hidden group cursor-pointer" onClick={() => window.location.href = "/subscription"}>
                        <div className="relative z-10">
                            <Star size={40} className="mx-auto text-primary mb-4 animate-pulse" />
                            <h3 className="text-2xl font-black italic uppercase tracking-tighter mb-2">
                                +{fullData.length - propsLimit} Pro Intelligence Items Hidden
                            </h3>
                            <p className="text-slate-400 text-sm max-w-md mx-auto mb-8 font-bold">
                                You are viewing a limited feed. Upgrade to Reveal All sharp edges and model predictions.
                            </p>
                            <button className="bg-primary hover:bg-primary/90 text-white px-10 py-4 rounded-2xl font-black uppercase tracking-widest text-sm transition-all shadow-xl shadow-primary/20">
                                Reveal All Intel →
                            </button>
                        </div>
                        <div className="absolute inset-0 bg-primary/5 blur-3xl rounded-full scale-50 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </div>
                )}
            </PageStates>
        </div>
    );
}

function PropCard({ prop }: { prop: any }) {
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
            "bg-[#0D0D14] border rounded-3xl p-6 transition-all group shadow-2xl relative overflow-hidden",
            rec?.tier === "S" ? "border-primary/50 shadow-primary/10" : "border-white/5 hover:border-primary/30"
        )}>
            {/* Recommendation Ribbon for S/A Tier */}
            {(rec?.tier === "S" || rec?.tier === "A") && (
                <div className="absolute top-0 right-0">
                    <div className="bg-primary text-white text-[8px] font-black uppercase tracking-widest py-1 px-4 rounded-bl-xl rotate-0 origin-top-right">
                        {rec.tier} TIER PICK
                    </div>
                </div>
            )}

            <div className="flex justify-between items-start mb-6">
                <div>
                    <div className="text-xl font-black tracking-tight">{prop.player_name}</div>
                    <div className="text-[10px] font-black uppercase text-primary tracking-widest mt-1">
                        {prop.stat_type.replace('_', ' ')}
                    </div>
                </div>
                <div className="text-right">
                    <div className="text-[10px] font-black text-slate-600 uppercase tracking-widest">Matchup</div>
                    <div className="text-xs font-bold text-slate-400">{prop.away_team} @ {prop.home_team}</div>
                </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
                <div className={clsx(
                    "border rounded-2xl p-4 transition-all",
                    rec?.side === "over"
                        ? "bg-emerald-500/10 border-emerald-500/30 ring-1 ring-emerald-500/20"
                        : "bg-emerald-500/5 border-emerald-500/10"
                )}>
                    <div className="flex justify-between items-center mb-2">
                        <div className="text-[10px] font-black text-emerald-500 uppercase tracking-widest">OVER</div>
                        {rec?.side === "over" && (
                            <Zap size={10} className="text-emerald-500 fill-emerald-500 animate-pulse" />
                        )}
                    </div>
                    {over ? (
                        <>
                            <div className="text-2xl font-black">{over.line}</div>
                            <div className="flex items-center justify-between mt-1">
                                <span className="font-mono font-black text-emerald-500 text-sm">{over.odds > 0 ? `+${over.odds}` : over.odds}</span>
                                <span className="text-[9px] font-black uppercase text-slate-600 tracking-tighter">{over.book}</span>
                            </div>
                        </>
                    ) : (
                        <div className="text-xs text-slate-600 italic">No market</div>
                    )}
                </div>

                <div className={clsx(
                    "border rounded-2xl p-4 transition-all",
                    rec?.side === "under"
                        ? "bg-red-500/10 border-red-500/30 ring-1 ring-red-500/20"
                        : "bg-red-500/5 border-red-500/10"
                )}>
                    <div className="flex justify-between items-center mb-2">
                        <div className="text-[10px] font-black text-red-500 uppercase tracking-widest">UNDER</div>
                        {rec?.side === "under" && (
                            <Zap size={10} className="text-red-500 fill-red-500 animate-pulse" />
                        )}
                    </div>
                    {under ? (
                        <>
                            <div className="text-2xl font-black">{under.line}</div>
                            <div className="flex items-center justify-between mt-1">
                                <span className="font-mono font-black text-red-500 text-sm">{under.odds > 0 ? `+${under.odds}` : under.odds}</span>
                                <span className="text-[9px] font-black uppercase text-slate-600 tracking-tighter">{under.book}</span>
                            </div>
                        </>
                    ) : (
                        <div className="text-xs text-slate-600 italic">No market</div>
                    )}
                </div>
            </div>

            {/* Advisor Insights */}
            {rec && (
                <div className="mt-4 p-3 bg-white/5 rounded-xl border border-white/5">
                    <div className="flex items-center gap-2 mb-1">
                        <div className={clsx(
                            "w-2 h-2 rounded-full",
                            rec.tier === "S" ? "bg-primary animate-ping" : "bg-primary/50"
                        )} />
                        <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest">Advisor Insight</span>
                    </div>
                    <p className="text-[11px] font-bold text-slate-200 leading-tight">
                        {rec.reason}
                    </p>
                </div>
            )}

            <div className="mt-6 pt-4 border-t border-white/5 flex items-center justify-between">
                <div className="text-[10px] font-black text-slate-600 uppercase tracking-widest">
                    Last Tick: {new Date(prop.commence_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
                <button
                    onClick={addToBuilder}
                    className="text-[10px] font-black uppercase tracking-widest text-primary hover:text-primary/80 transition-colors"
                >
                    Add to Builder +
                </button>
            </div>
        </div>
    );
}
