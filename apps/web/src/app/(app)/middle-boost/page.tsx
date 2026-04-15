// apps/web/src/app/(app)/middle-boost/page.tsx
"use client";
import React from "react";
import { Zap, Calculator, TrendingUp, Info } from "lucide-react";
import { useLiveData } from "@/hooks/useLiveData";
import API from "@/lib/api";
import LiveStatusBar from "@/components/LiveStatusBar";
import PageStates from "@/components/PageStates";
import GateLock from "@/components/GateLock";

export default function MiddleBoostPage() {
    const { data, loading, error, lastUpdated, isStale, refresh } = useLiveData<any>(
        () => API.middleBoost(),
        [],
        { refreshInterval: 300000 }
    );

    const middles = data?.items || [];

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-8 text-white pb-24">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <div className="bg-[#F5C51820] p-2 rounded-lg border border-[#F5C51830]">
                            <Zap size={24} className="text-[#F5C518]" />
                        </div>
                        <h1 className="text-3xl font-black italic tracking-tighter uppercase">Middle & Boost Analysis</h1>
                    </div>
                    <p className="text-slate-400 text-sm max-w-lg">
                        Identify windows where you can win both sides of a bet or capitalize on sportsbook boosted odds.
                    </p>
                </div>

                <LiveStatusBar
                    lastUpdated={lastUpdated}
                    isStale={isStale}
                    loading={loading}
                    error={error}
                    onRefresh={refresh}
                    refreshInterval={300}
                />
            </div>

            <GateLock feature="edges" reason="Middle and Boost Analysis is reserved for Premium athletes.">
                <PageStates
                    loading={loading && !data}
                    error={error}
                    empty={!loading && middles.length === 0}
                    emptyMessage="No middle opportunities or high-EV boosts found right now."
                >
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {middles.map((mid: any) => (
                            <div key={mid.id} className="bg-[#0D0D14] border border-white/5 rounded-3xl p-6 hover:border-[#F5C51830] transition-all shadow-2xl relative overflow-hidden group">
                                <div className="absolute -right-4 -bottom-4 opacity-5 group-hover:opacity-10 transition-opacity">
                                    <Calculator size={100} className="text-[#F5C518]" />
                                </div>

                                <div className="flex justify-between items-start mb-6">
                                    <div>
                                        <div className="text-xs font-black text-[#F5C518] uppercase tracking-widest bg-[#F5C51810] px-2 py-0.5 rounded border border-[#F5C51820] inline-block mb-2">
                                            {mid.status}
                                        </div>
                                        <div className="text-xl font-bold">{mid.match}</div>
                                    </div>
                                    <div className="text-right">
                                        <div className="text-2xl font-black text-emerald-500">+{mid.ev_percent}%</div>
                                        <div className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Expected Value</div>
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-3 mb-6">
                                    <div className="bg-white/5 p-3 rounded-xl border border-white/5">
                                        <div className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">{mid.book_a.name}</div>
                                        <div className="text-sm font-bold text-white">{mid.book_a.line}</div>
                                        <div className="text-xs font-mono text-emerald-500 font-black">{mid.book_a.odds}</div>
                                    </div>
                                    <div className="bg-white/5 p-3 rounded-xl border border-white/5">
                                        <div className="text-[10px] font-black uppercase text-slate-500 tracking-widest mb-1">{mid.book_b.name}</div>
                                        <div className="text-sm font-bold text-white">{mid.book_b.line}</div>
                                        <div className="text-xs font-mono text-emerald-500 font-black">{mid.book_b.odds}</div>
                                    </div>
                                </div>

                                <div className="flex items-center gap-3 text-xs text-slate-400 bg-white/5 p-3 rounded-xl">
                                    <Info size={14} className="text-blue-400" />
                                    <span>Middle width: <b className="text-white">{mid.middle_width}</b> points</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </PageStates>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
                    <div className="bg-[#0F0F1A] border border-white/5 p-6 rounded-3xl flex items-center gap-6">
                        <div className="bg-emerald-500/10 p-4 rounded-2xl">
                            <TrendingUp className="text-emerald-500" size={32} />
                        </div>
                        <div>
                            <h4 className="text-lg font-bold">What is a Middle?</h4>
                            <p className="text-slate-500 text-sm mt-1">
                                A middle occurs when you bet the Over on one line and the Under on a higher line. If the final score lands between them, you win both bets.
                            </p>
                        </div>
                    </div>
                </div>
            </GateLock>
        </div>
    );
}
