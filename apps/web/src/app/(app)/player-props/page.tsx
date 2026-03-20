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
import { useSearchParams } from "next/navigation";
import SportSelector from "@/components/shared/SportSelector";
import { useFreshness } from "@/hooks/useFreshness";
import { FreshnessBadge } from "@/components/dashboard/FreshnessBadge";

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

    const { data: propsData, loading, error, refresh, lastUpdated, isStale, status } = useLiveData(
        () => api.props(sport, market || undefined, minEv),
        [sport, market, minEv],
        { refreshInterval: 60000 }
    );

    const fullData = unwrap(propsData);
    const { tier: activeTier, propsLimit } = useGate();
    
    // In dev, show everything regardless of tier slicing
    const isDev = typeof window !== 'undefined' && 
      (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');

    const limitedData = isDev ? fullData : fullData.slice(0, propsLimit);

    const filtered = limitedData.filter((p: any) =>
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

                    <div className="mb-6">
                        <FreshnessBadge 
                            oddsTs={freshness?.odds_last_updated || null} 
                            evTs={freshness?.ev_last_updated || null} 
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

            <PageStates
                loading={loading && !propsData}
                error={error}
                empty={!loading && filtered.length === 0}
                status={status}
            >
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    {filtered.map((prop: any, i: number) => (
                        <PropCard key={i} prop={prop} />
                    ))}
                </div>

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
                            {prop.stat_type.replace('_', ' ')}
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
                <button
                    onClick={addToBuilder}
                    className="text-[9px] font-black uppercase tracking-widest text-brand-cyan hover:text-white transition-colors border border-brand-cyan/20 bg-brand-cyan/10 px-2 py-1 rounded-sm"
                >
                    Add Leg +
                </button>
            </div>
        </div>
    );
}
