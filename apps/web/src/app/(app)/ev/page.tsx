// apps/web/src/app/(app)/ev/page.tsx
"use client";
import React, { useState, useCallback } from "react";
import { TrendingUp, Calculator, Info, Zap } from "lucide-react";
import { useLiveData } from "@/hooks/useLiveData";
import { api, isApiError, unwrap } from "@/lib/api";
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
            const data = await api.ev.top(sport);
            return unwrap(data);
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
                    <div className="bg-lucrix-surface border border-lucrix-border rounded-xl overflow-x-auto shadow-card">
                        <table className="w-full text-left min-w-[800px]">
                            <thead>
                                <tr className="bg-lucrix-dark/80 border-b border-lucrix-border text-[9px] font-black uppercase tracking-widest text-textMuted">
                                    <th className="px-6 py-4">Market Pick</th>
                                    <th className="px-6 py-4 text-center">Market Odds</th>
                                    <th className="px-6 py-4 text-center">Model Fair</th>
                                    <th className="px-6 py-4 text-center">Edge (EV%)</th>
                                    <th className="px-6 py-4 text-center">Kelly (%)</th>
                                    <th className="px-6 py-4 text-right">Action</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-lucrix-border/50">
                                    {(Array.isArray(picks) ? picks : picks?.items || []).map((pick: any, i: number) => (
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
                                        <td className="px-6 py-5 text-center">
                                            <span className="bg-lucrix-dark px-4 py-2 rounded-lg border border-lucrix-border font-black font-mono text-white text-sm">
                                                {pick.odds > 0 ? `+${pick.odds}` : pick.odds}
                                            </span>
                                            <div className="text-[9px] text-textMuted mt-2 font-bold uppercase tracking-widest">{pick.book}</div>
                                        </td>
                                        <td className="px-6 py-5 text-center">
                                            <div className="text-sm font-black text-textSecondary font-mono">
                                                {pick.fair_odds > 0 ? `+${pick.fair_odds}` : pick.fair_odds}
                                            </div>
                                        </td>
                                        <td className="px-6 py-5 text-center">
                                            <div className="flex flex-col items-center">
                                                <span className="text-xl font-black text-brand-success font-display">+{pick.ev_percentage}%</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-5 text-center">
                                            <div className="bg-brand-warning/10 text-brand-warning px-3 py-1.5 rounded-lg border border-brand-warning/20 inline-flex items-center gap-1.5 shadow-glow shadow-brand-warning/10">
                                                <Calculator size={12} />
                                                <span className="font-black text-sm font-mono">{pick.kelly_percentage || 0}%</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-5 text-right">
                                            <button className="bg-lucrix-dark border border-lucrix-border hover:bg-brand-success hover:border-brand-success hover:text-black text-white px-6 py-2.5 rounded-lg font-black uppercase tracking-widest text-[10px] transition-all shadow-glow hover:shadow-brand-success/20">
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
