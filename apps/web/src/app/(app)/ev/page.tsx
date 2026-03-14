// apps/web/src/app/(app)/ev/page.tsx
"use client";
import React, { useState, useCallback } from "react";
import { TrendingUp, Calculator, Info, Zap } from "lucide-react";
import { useLiveData } from "@/hooks/useLiveData";
import { api, isApiError } from "@/lib/api";
import LiveStatusBar from "@/components/LiveStatusBar";
import PageStates from "@/components/PageStates";
import GateLock from "@/components/GateLock";

import { useLucrixStore } from "@/store";
import { useFreshness } from "@/hooks/useFreshness";
import { FreshnessBadge } from "@/components/dashboard/FreshnessBadge";

export default function EVPage() {
    const sport = useLucrixStore((state: any) => state.activeSport);
    const freshness = useFreshness(sport);

    const fetcher = useCallback(
        async () => {
            const data = await api.get(`/api/ev?sport=${sport}`);
            if (isApiError(data)) return [];
            return Array.isArray(data) ? data : (data.items || []);
        },
        [sport]
    );

    const { data: picks, loading, error, lastUpdated, isStale, refresh } = useLiveData<any[]>(
        fetcher,
        [sport],
        { refreshInterval: 180000 }
    );

    return (
        <GateLock feature="edges" reason="The EV+ Live Scanner is reserved for Premium athletes.">
            <div className="p-4 sm:p-6 max-w-7xl mx-auto space-y-6 text-white pb-24">
                <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                    <div>
                        <div className="flex items-center gap-3 mb-2">
                            <div className="bg-emerald-500/20 p-2 rounded-lg border border-emerald-500/30">
                                <TrendingUp size={24} className="text-emerald-500" />
                            </div>
                            <h1 className="text-3xl font-black italic tracking-tighter uppercase text-white">EV+ Live Scanner</h1>
                        </div>
                        <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mb-2">High-Edge Market Opportunities</p>
                        <FreshnessBadge 
                            oddsTs={freshness?.odds_last_updated || null} 
                            evTs={freshness?.ev_last_updated || null} 
                        />
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
                    loading={loading && !picks}
                    error={error}
                    empty={!loading && (!picks || picks.length === 0)}
                    emptyMessage="No high-EV edges found right now. Markets are stable."
                >
                    <div className="bg-[#0D0D14] border border-white/5 rounded-2xl overflow-x-auto shadow-2xl">
                        <table className="w-full text-left min-w-[800px]">
                            <thead>
                                <tr className="bg-white/5 border-b border-white/5 text-[10px] font-black uppercase tracking-widest text-slate-500">
                                    <th className="px-6 py-4">Market Pick</th>
                                    <th className="px-6 py-4 text-center">Market Odds</th>
                                    <th className="px-6 py-4 text-center">Model Fair</th>
                                    <th className="px-6 py-4 text-center">Edge (EV%)</th>
                                    <th className="px-6 py-4 text-center">Kelly (%)</th>
                                    <th className="px-6 py-4 text-right">Action</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                    {(Array.isArray(picks) ? picks : picks?.items || []).map((pick: any, i: number) => (
                                    <tr key={`${pick.id || pick.event_id || i}-${i}`} className="group hover:bg-white/[0.02] transition-colors">
                                        <td className="px-6 py-6 font-sans">
                                            <div className="flex items-center gap-4">
                                                <div className="bg-white/5 px-2 py-1 rounded text-[10px] font-black border border-white/10 text-[#F5C518]">
                                                    {pick.sport}
                                                </div>
                                                <div>
                                                    <div className="font-bold text-lg group-hover:text-primary transition-colors text-white">{pick.player_name}</div>
                                                    <div className="text-[10px] font-black text-slate-500 uppercase tracking-tight">{pick.stat_type} — {pick.line}</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-6 text-center">
                                            <span className="bg-white/5 px-4 py-2 rounded-xl border border-white/10 font-black font-mono text-white text-sm">
                                                {pick.odds > 0 ? `+${pick.odds}` : pick.odds}
                                            </span>
                                            <div className="text-[9px] text-slate-500 mt-1 font-bold uppercase">{pick.book}</div>
                                        </td>
                                        <td className="px-6 py-6 text-center">
                                            <div className="text-sm font-black text-slate-400 font-mono">
                                                {pick.fair_odds > 0 ? `+${pick.fair_odds}` : pick.fair_odds}
                                            </div>
                                        </td>
                                        <td className="px-6 py-6 text-center">
                                            <div className="flex flex-col items-center">
                                                <span className="text-xl font-black text-emerald-500">+{pick.ev_percentage}%</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-6 text-center">
                                            <div className="bg-[#F5C51810] text-[#F5C518] px-3 py-1 rounded-lg border border-[#F5C51820] inline-flex items-center gap-1.5">
                                                <Calculator size={12} />
                                                <span className="font-black text-sm">{pick.kelly_percentage || 0}%</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-6 text-right">
                                            <button className="bg-white hover:bg-[#F5C518] hover:text-black text-black px-6 py-2.5 rounded-xl font-black uppercase tracking-widest text-[10px] transition-all">
                                                Bet
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </PageStates>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="bg-[#0F0F1A] border border-white/5 p-6 rounded-2xl flex items-center gap-4">
                        <div className="bg-[#F5C51820] p-3 rounded-2xl">
                            <Info className="text-[#F5C518]" size={24} />
                        </div>
                        <div>
                            <h4 className="font-bold text-sm text-white">What is EV+?</h4>
                            <p className="text-xs text-slate-500 mt-1">Expected Value indicates a bet where the probability is in your favor vs the book odds.</p>
                        </div>
                    </div>
                    {/* Kelly/institutional speed info cards */}
                </div>
            </div>
        </GateLock>
    );
}
