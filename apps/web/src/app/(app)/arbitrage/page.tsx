// apps/web/src/app/(app)/arbitrage/page.tsx
"use client";
import { ArrowRightLeft, Calculator, Info, Zap } from "lucide-react";
import { useLiveData } from "@/hooks/useLiveData";
import { api } from "@/lib/api";
import LiveStatusBar from "@/components/LiveStatusBar";
import PageStates from "@/components/PageStates";
import GateLock from "@/components/GateLock";
import { useLucrixStore } from "@/store";
import { useFreshness } from "@/hooks/useFreshness";
import { FreshnessBadge } from "@/components/dashboard/FreshnessBadge";

export default function ArbitragePage() {
    const sport = useLucrixStore((state: any) => state.activeSport);
    const freshness = useFreshness(sport);
    const { data: opps, loading, error, lastUpdated, isStale, refresh } = useLiveData<any>(
        () => api.arbitrage(),
        [],
        { refreshInterval: 120000 }
    );

    const opportunities = opps?.opportunities || [];

    return (
        <div className="p-4 sm:p-6 max-w-7xl mx-auto space-y-6 text-white pb-24">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <div className="bg-emerald-500/20 p-2 rounded-lg border border-emerald-500/30">
                            <ArrowRightLeft size={24} className="text-emerald-500" />
                        </div>
                        <h1 className="text-3xl font-black italic tracking-tighter uppercase text-white">Arbitrage Scanner</h1>
                    </div>
                    <p className="text-[#6B7280] text-sm mb-2">Risk-free profit opportunities across books</p>
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

            <GateLock feature="edges" reason="The Arbitrage Scanner is reserved for Premium athletes.">
                <PageStates
                    loading={loading && !opps}
                    error={error}
                    empty={!loading && opportunities.length === 0}
                    emptyMessage="No risk-free arbs found. Markets are currently efficient."
                >
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {opportunities.map((opp: any, i: number) => (
                            <div key={i} className="bg-[#0D0D14] border border-emerald-500/30 rounded-2xl p-6 shadow-2xl transition hover:border-emerald-500/50">
                                <div className="flex justify-between items-start mb-6">
                                    <div>
                                        <div className="text-lg font-black text-white italic uppercase tracking-tight">{opp.player_name}</div>
                                        <div className="text-[10px] font-black text-[#6B7280] uppercase tracking-widest mt-1">
                                            {opp.sport} · {opp.stat_type} {opp.line}
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <div className="text-2xl font-black text-emerald-500 italic">+{opp.profit_percentage}% Profit</div>
                                        <div className="text-[9px] font-black text-[#6B7280] uppercase tracking-widest">Guaranteed Return</div>
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div className="bg-white/[0.02] p-4 rounded-xl border border-white/5">
                                        <div className="text-[10px] font-black text-[#6B7280] uppercase tracking-widest mb-2">OVER @ {opp.over_book}</div>
                                        <div className="flex justify-between items-end">
                                            <div className="text-xl font-black text-white font-mono">{opp.over_odds > 0 ? `+${opp.over_odds}` : opp.over_odds}</div>
                                            <div className="text-xs font-black text-emerald-500 font-mono">${opp.over_stake}</div>
                                        </div>
                                    </div>
                                    <div className="bg-white/[0.02] p-4 rounded-xl border border-white/5">
                                        <div className="text-[10px] font-black text-[#6B7280] uppercase tracking-widest mb-2">UNDER @ {opp.under_book}</div>
                                        <div className="flex justify-between items-end">
                                            <div className="text-xl font-black text-white font-mono">{opp.under_odds > 0 ? `+${opp.under_odds}` : opp.under_odds}</div>
                                            <div className="text-xs font-black text-blue-400 font-mono">${opp.under_stake}</div>
                                        </div>
                                    </div>
                                </div>

                                <div className="mt-4 text-[9px] text-[#6B7280] italic text-center">
                                    Example for $100 total stake. Bet on both sides to lock in profit regardless of outcome.
                                </div>
                            </div>
                        ))}
                    </div>
                </PageStates>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
                    <div className="bg-[#0F0F1A] border border-white/5 p-6 rounded-2xl flex items-center gap-4">
                        <div className="bg-emerald-500/20 p-3 rounded-2xl">
                            <Calculator className="text-emerald-500" size={24} />
                        </div>
                        <div>
                            <h4 className="font-bold text-sm text-white">Guaranteed P&L</h4>
                            <p className="text-xs text-[#6B7280] mt-1">Arbitrage bets leverage house discrepancy. Profit is locked in regardless of game result.</p>
                        </div>
                    </div>
                </div>
            </GateLock>
        </div>
    );
}
