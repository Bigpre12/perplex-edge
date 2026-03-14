// apps/web/src/app/(app)/sharp/page.tsx
"use client";
import { Zap, AlertTriangle, ShieldCheck, ArrowRightLeft } from "lucide-react";
import { clsx } from "clsx";
import GateLock from "@/components/GateLock";
import { useLiveData } from "@/hooks/useLiveData";
import { api } from "@/lib/api";
import LiveStatusBar from "@/components/LiveStatusBar";
import PageStates from "@/components/PageStates";

import { useSport } from "@/context/SportContext";

export default function SharpMoneyPage() {
    const { selectedSport: sport } = useSport();
    const { data, loading, error, lastUpdated, isStale, refresh } = useLiveData<any>(
        () => api.sharpMoves(sport),
        [sport],
        { refreshInterval: 300000 }
    );

    const { data: steamData } = useLiveData<any>(
        () => api.brain.steamAlerts(sport),
        [sport],
        { refreshInterval: 60000 }
    );

    const signals = data?.signals || [];
    const steamAlerts = steamData || [];

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-8 text-white pb-24">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <div className="bg-primary/20 p-2 rounded-lg border border-primary/30">
                            <Zap size={24} className="text-primary" />
                        </div>
                        <h1 className="text-3xl font-black italic tracking-tighter uppercase">Sharp Money Signals</h1>
                    </div>
                    <p className="text-slate-400 text-sm max-w-lg">
                        Track "Smart Money" by monitoring odds discrepancies between sharp books (Pinnacle, Circa) and retail books (DraftKings, FanDuel).
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

            {steamAlerts.length > 0 && (
                <div className="bg-rose-500/10 border border-rose-500/30 rounded-2xl p-4 flex flex-col md:flex-row items-center justify-between gap-4 animate-in fade-in slide-in-from-top-4">
                    <div className="flex items-center gap-3">
                        <AlertTriangle className="text-rose-500 animate-pulse" />
                        <div>
                            <h3 className="font-bold text-rose-500 text-sm tracking-widest uppercase">Live Steam Detected</h3>
                            <p className="text-xs text-rose-200/70">Institutional money moving lines in real-time.</p>
                        </div>
                    </div>
                    <div className="flex gap-2 overflow-x-auto pb-2 md:pb-0 w-full md:w-auto">
                        {steamAlerts.map((alert: any) => (
                            <div key={alert.id} className="bg-rose-950/50 border border-rose-500/20 px-4 py-2 rounded-xl text-xs whitespace-nowrap">
                                <span className="font-bold text-white">{alert.player} {alert.stat_type}</span>
                                <span className="mx-2 text-rose-500 font-black tracking-widest">{alert.move_direction === 'UP' ? '▲' : '▼'} {alert.line}</span>
                                <span className="text-slate-400">({alert.book})</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            <GateLock feature="sharpMoney" reason="Sharp money signals require Premium access.">
                <PageStates
                    loading={loading && !data}
                    error={error}
                    empty={!loading && signals.length === 0}
                    emptyMessage="No sharp money discrepancies detected in current market."
                >
                    <div className="grid grid-cols-1 gap-6">
                        {signals.map((signal: any, idx: number) => (
                            <div key={`${signal.game}-${idx}`} className="bg-[#0D0D14] border border-white/5 rounded-3xl p-6 hover:border-primary/30 transition-all group overflow-hidden relative shadow-2xl">
                                <div className="absolute top-0 right-0 py-8 px-12 opacity-5 pointer-events-none group-hover:opacity-10 transition-opacity translate-x-4">
                                    <ShieldCheck size={120} className="text-primary" />
                                </div>

                                <div className="flex flex-col md:flex-row items-center justify-between gap-8 relative z-10">
                                    <div className="flex items-center gap-6 w-full md:w-auto">
                                        <div className="bg-primary/10 p-4 rounded-2xl border border-primary/20">
                                            <ShieldCheck className="text-primary" size={32} />
                                        </div>
                                        <div>
                                            <div className="text-xl font-bold">{signal.game}</div>
                                            <div className="flex items-center gap-2 mt-1">
                                                <span className="text-xs font-black uppercase text-slate-500 bg-white/5 px-2 py-0.5 rounded border border-white/10">{signal.signal}</span>
                                                <span className="text-sm font-bold text-primary">{signal.team} {signal.market}</span>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="flex-1 max-w-md w-full">
                                        <div className="flex justify-between text-[10px] font-black uppercase tracking-widest text-slate-500 mb-2">
                                            <span>Square Avg ({signal.square_avg_odds})</span>
                                            <span className="text-primary">Sharp Consensus ({signal.sharp_avg_odds})</span>
                                        </div>
                                        <div className="relative h-3 bg-white/5 rounded-full overflow-hidden border border-white/10">
                                            <div className="absolute inset-y-0 left-0 bg-slate-700 w-1/2" />
                                            <div className="absolute inset-y-0 right-0 bg-[#F5C518] w-1/2" />
                                            <div className="absolute inset-y-0 left-1/2 w-1 bg-white/20 z-10" />
                                        </div>
                                    </div>

                                    <div className="bg-primary/20 px-8 py-4 rounded-3xl border border-primary/30 text-center min-w-[140px]">
                                        <div className="text-[10px] font-black uppercase tracking-widest text-primary/60 mb-1">Delta</div>
                                        <div className="text-3xl font-black text-primary">{Math.abs(signal.delta)}¢</div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </PageStates>

                <div className="bg-[#11111F] border border-dashed border-white/10 rounded-3xl p-12 text-center">
                    <AlertTriangle size={32} className="mx-auto text-slate-600 mb-4" />
                    <h4 className="text-xl font-bold text-slate-300">Advanced Steam Scanning</h4>
                    <p className="text-slate-500 text-sm max-w-md mx-auto mt-2">
                        These signals indicate where institutional money is moving. Retail books are usually slow to React, providing a window to beat the "CLV" (Closing Line Value).
                    </p>
                </div>
            </GateLock>
        </div>
    );
}
