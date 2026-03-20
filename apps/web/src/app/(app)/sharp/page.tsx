// apps/web/src/app/(app)/sharp/page.tsx
"use client";
import { Zap, AlertTriangle, ShieldCheck, ArrowRightLeft } from "lucide-react";
import { clsx } from "clsx";
import GateLock from "@/components/GateLock";
import { useLiveData } from "@/hooks/useLiveData";
import { api, unwrap } from "@/lib/api";
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
        () => api.steamAlerts(sport),
        [sport],
        { refreshInterval: 60000 }
    );

    const signals = unwrap(data);
    const steamAlerts = steamData || [];

    return (
        <div className="p-4 sm:p-6 max-w-7xl mx-auto space-y-8 text-white pb-24">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <div className="bg-brand-cyan/10 p-2 rounded-lg border border-brand-cyan/20">
                            <Zap size={24} className="text-brand-cyan shadow-glow shadow-brand-cyan/40" />
                        </div>
                        <h1 className="text-3xl font-black italic tracking-tighter uppercase font-display">Sharp Money Signals</h1>
                    </div>
                    <p className="text-textSecondary text-xs mt-3 max-w-lg font-bold leading-relaxed">
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
                <div className="bg-brand-danger/10 border border-brand-danger/30 rounded-xl p-4 flex flex-col md:flex-row items-center justify-between gap-4 animate-in fade-in slide-in-from-top-4 shadow-glow shadow-brand-danger/10">
                    <div className="flex items-center gap-3">
                        <AlertTriangle className="text-brand-danger animate-pulse" />
                        <div>
                            <h3 className="font-black text-brand-danger text-sm tracking-widest uppercase font-display italic">Live Steam Detected</h3>
                            <p className="text-[11px] font-bold text-textSecondary mt-1">Institutional money moving lines in real-time.</p>
                        </div>
                    </div>
                    <div className="flex gap-2 overflow-x-auto pb-2 md:pb-0 w-full md:w-auto mt-2 md:mt-0">
                        {steamAlerts.map((alert: any) => (
                            <div key={alert.id} className="bg-lucrix-dark/80 border border-brand-danger/20 px-4 py-2 rounded-lg text-[11px] whitespace-nowrap shadow-card">
                                <span className="font-black text-white uppercase tracking-wider">{alert.player} {alert.stat_type}</span>
                                <span className="mx-2 text-brand-danger font-black tracking-widest">{alert.move_direction === 'UP' ? '▲' : '▼'} {alert.line}</span>
                                <span className="text-textMuted uppercase font-bold tracking-widest">({alert.book})</span>
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
                            <div key={`${signal.game}-${idx}`} className="bg-lucrix-surface border border-lucrix-border rounded-xl p-6 hover:border-brand-cyan/30 transition-all duration-300 group overflow-hidden relative shadow-card hover:shadow-brand-cyan/10">
                                <div className="absolute top-0 right-0 py-8 px-12 opacity-[0.03] pointer-events-none group-hover:opacity-10 transition-opacity translate-x-4">
                                    <ShieldCheck size={120} className="text-brand-cyan" />
                                </div>

                                <div className="flex flex-col md:flex-row items-center justify-between gap-8 relative z-10">
                                    <div className="flex items-center gap-6 w-full md:w-auto">
                                        <div className="bg-brand-cyan/10 p-4 rounded-xl border border-brand-cyan/20 group-hover:bg-brand-cyan/20 transition-colors">
                                            <ShieldCheck className="text-brand-cyan" size={32} />
                                        </div>
                                        <div>
                                            <div className="text-xl font-black text-white uppercase italic tracking-tighter font-display">{signal.game}</div>
                                            <div className="flex items-center gap-2 mt-2">
                                                <span className="text-[10px] font-black uppercase tracking-widest text-textMuted bg-lucrix-dark px-2 py-1 rounded-sm border border-lucrix-border/50 shadow-inner">{signal.signal}</span>
                                                <span className="text-[11px] font-black tracking-widest text-brand-cyan uppercase bg-brand-cyan/10 px-2 py-1 rounded-sm border border-brand-cyan/20">{signal.team} {signal.market}</span>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="flex-1 max-w-md w-full mt-4 md:mt-0">
                                        <div className="flex justify-between text-[10px] font-black uppercase tracking-widest text-textMuted mb-2">
                                            <span>Square Avg ({signal.square_avg_odds})</span>
                                            <span className="text-brand-cyan drop-shadow-[0_0_8px_rgba(0,255,255,0.4)]">Sharp Consensus ({signal.sharp_avg_odds})</span>
                                        </div>
                                        <div className="relative h-2.5 bg-lucrix-dark rounded-full overflow-hidden border border-lucrix-border/50">
                                            <div className="absolute inset-y-0 left-0 bg-lucrix-border w-1/2" />
                                            <div className="absolute inset-y-0 right-0 bg-brand-warning w-1/2 shadow-glow shadow-brand-warning/50" />
                                            <div className="absolute inset-y-0 left-1/2 w-[2px] bg-white/40 z-10" />
                                        </div>
                                    </div>

                                    <div className="bg-brand-cyan/10 px-8 py-4 rounded-xl border border-brand-cyan/20 text-center min-w-[140px] mt-6 md:mt-0 group-hover:bg-brand-cyan/20 transition-colors">
                                        <div className="text-[10px] font-black uppercase tracking-widest text-brand-cyan/70 mb-1">Delta</div>
                                        <div className="text-3xl font-black text-brand-cyan font-display drop-shadow-[0_0_12px_rgba(0,255,255,0.5)] leading-none">{Math.abs(signal.delta)}¢</div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </PageStates>

                <div className="bg-lucrix-surface border border-dashed border-lucrix-border rounded-2xl p-10 text-center mt-8 shadow-card mx-auto max-w-3xl">
                    <AlertTriangle size={32} className="mx-auto text-textSecondary mb-4 opacity-50" />
                    <h4 className="text-lg font-black text-textSecondary uppercase tracking-widest font-display italic">Advanced Steam Scanning</h4>
                    <p className="text-textMuted text-[11px] max-w-md mx-auto mt-3 font-bold leading-relaxed">
                        These signals indicate where institutional money is moving. Retail books are usually slow to React, providing a window to beat the "CLV" (Closing Line Value).
                    </p>
                </div>
            </GateLock>
        </div>
    );
}
