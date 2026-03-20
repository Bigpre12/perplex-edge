"use client";

import { Activity, Shield, Zap, Info, TrendingUp, TrendingDown, Clock, Search } from "lucide-react";
import { useLiveData } from "@/hooks/useLiveData";
import { api } from "@/lib/api";
import LiveStatusBar from "@/components/LiveStatusBar";
import PageStates from "@/components/PageStates";
import GateLock from "@/components/GateLock";
import { useLucrixStore } from "@/store";
import { useFreshness } from "@/hooks/useFreshness";
import { FreshnessBadge } from "@/components/dashboard/FreshnessBadge";
import SportSelector from "@/components/shared/SportSelector";
import { clsx } from "clsx";

export default function LineMovementPage() {
    const activeSport = useLucrixStore((state: any) => state.activeSport);
    const freshness = useFreshness(activeSport);
    const { data: moveResponse, loading, error, lastUpdated, isStale, refresh } = useLiveData<any>(
        () => api.lineMovement(activeSport),
        [activeSport],
        { refreshInterval: 60000 }
    );

    const moves = moveResponse?.data || [];

    return (
        <div className="p-4 sm:p-6 max-w-7xl mx-auto space-y-6 text-white pb-24">
            {/* Header Area */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div className="flex flex-col gap-1">
                    <div className="flex items-center gap-3">
                        <div className="bg-blue-500/20 p-2 rounded-lg border border-blue-500/30 shadow-glow shadow-blue-500/20">
                            <Activity size={24} className="text-blue-500" />
                        </div>
                        <h1 className="text-3xl font-black italic tracking-tighter uppercase text-white font-display">Market Velocity</h1>
                    </div>
                    <p className="text-[#6B7280] text-[10px] font-black uppercase tracking-[0.2em] mt-1 pl-1">
                        Institutional Order Flow · Steam & Whale Scanner
                    </p>
                </div>

                <div className="flex flex-col space-y-2">
                    <SportSelector />
                    <div className="flex justify-end">
                        <LiveStatusBar
                            lastUpdated={lastUpdated}
                            isStale={isStale}
                            loading={loading}
                            error={error}
                            onRefresh={refresh}
                            refreshInterval={60}
                        />
                    </div>
                </div>
            </div>

            {/* Stats Dashboard */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-lucrix-surface border border-white/5 p-4 rounded-2xl">
                    <p className="text-[9px] font-black text-textMuted uppercase tracking-widest mb-1">Active Signals</p>
                    <div className="text-xl font-black italic">{moves.length}</div>
                </div>
                <div className="bg-lucrix-surface border border-white/5 p-4 rounded-2xl">
                    <p className="text-[9px] font-black text-textMuted uppercase tracking-widest mb-1">Steam Alerts</p>
                    <div className="text-xl font-black italic text-emerald-500">
                        {moves.filter((m:any) => m.type === "STEAM").length}
                    </div>
                </div>
                <div className="bg-lucrix-surface border border-white/5 p-4 rounded-2xl">
                    <p className="text-[9px] font-black text-textMuted uppercase tracking-widest mb-1">Whale Activity</p>
                    <div className="text-xl font-black italic text-blue-400">
                        {moves.filter((m:any) => m.type === "WHALE").length}
                    </div>
                </div>
                <div className="bg-lucrix-surface border border-blue-500/20 p-4 rounded-2xl bg-blue-500/5">
                    <p className="text-[9px] font-black text-blue-400 uppercase tracking-widest mb-1">Market Sentiment</p>
                    <div className="text-xl font-black italic">BULLISH</div>
                </div>
            </div>

            <GateLock feature="edges" reason="The Market Velocity scanner is reserved for Elite members.">
                <PageStates
                    loading={loading && !moveResponse}
                    error={error}
                    empty={!loading && moves.length === 0}
                    emptyMessage="No significant market moves detected. Volatility is low."
                >
                    <div className="grid grid-cols-1 gap-3">
                        {moves.map((move: any) => (
                            <div key={move.id} className="bg-[#0A0A0F] border border-white/5 rounded-2xl p-5 hover:border-blue-500/40 transition-all group relative overflow-hidden">
                                {move.type === "STEAM" && (
                                    <div className="absolute top-0 left-0 w-1 h-full bg-emerald-500/50 shadow-glow shadow-emerald-500/40" />
                                )}
                                {move.type === "WHALE" && (
                                    <div className="absolute top-0 left-0 w-1 h-full bg-blue-500/50 shadow-glow shadow-blue-500/40" />
                                )}

                                <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                                    <div className="flex items-center gap-5">
                                        <div className={clsx(
                                            "size-12 rounded-xl flex items-center justify-center border",
                                            move.direction === "UP" ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-500" : "bg-red-500/10 border-red-500/20 text-red-500"
                                        )}>
                                            {move.direction === "UP" ? <TrendingUp size={24} /> : <TrendingDown size={24} />}
                                        </div>
                                        <div>
                                            <div className="flex items-center gap-2 mb-1">
                                                <span className={clsx(
                                                    "text-[8px] font-black uppercase px-1.5 py-0.5 rounded-sm border shadow-sm",
                                                    move.type === "STEAM" ? "bg-emerald-500/20 text-emerald-500 border-emerald-500/30" : 
                                                    move.type === "WHALE" ? "bg-blue-500/20 text-blue-500 border-blue-500/30" : 
                                                    "bg-white/10 text-white border-white/10"
                                                )}>
                                                    {move.type}
                                                </span>
                                                <span className="text-[8px] font-black text-textMuted uppercase tracking-widest">
                                                    Intensity {move.intensity}%
                                                </span>
                                            </div>
                                            <h3 className="text-lg font-black italic text-white uppercase tracking-tight group-hover:text-blue-400 transition-colors">
                                                {move.player || "Team Move"}
                                            </h3>
                                            <div className="text-[10px] font-black text-[#6B7280] uppercase tracking-widest mt-1">
                                                {move.market} · {move.outcome} {move.line > 0 ? `@ ${move.line}` : ""}
                                            </div>
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-8 pr-4">
                                        <div className="text-right">
                                            <div className="text-[9px] font-black text-textMuted uppercase mb-1">Velocity</div>
                                            <div className="flex items-center gap-2">
                                                <div className="w-24 h-1 bg-white/5 rounded-full overflow-hidden">
                                                    <div className={clsx("h-full bg-blue-500 shadow-glow shadow-blue-500/50", `w-dp-${Math.round((move.intensity || 0) / 10) * 10}`)} />
                                                </div>
                                            </div>
                                        </div>
                                        <div className="text-right">
                                            <div className="text-[9px] font-black text-textMuted uppercase mb-1">Books Moving</div>
                                            <div className="text-xl font-mono font-black text-white italic">{move.books_count}</div>
                                        </div>
                                        <div className="text-right min-w-[60px]">
                                            <div className="text-[9px] font-black text-textMuted uppercase mb-1">Age</div>
                                            <div className="text-[10px] font-mono font-black text-white uppercase">
                                                {new Date(move.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </PageStates>
            </GateLock>
        </div>
    );
}
