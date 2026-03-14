// apps/web/src/app/(app)/line-movement/page.tsx
"use client";
import { TrendingUp, Activity, ArrowUpRight, ArrowDownRight, Clock } from "lucide-react";
import { clsx } from "clsx";
import GateLock from "@/components/GateLock";
import { useLiveData } from "@/hooks/useLiveData";
import { api } from "@/lib/api";
import LiveStatusBar from "@/components/LiveStatusBar";
import PageStates from "@/components/PageStates";
import { useSport } from "@/context/SportContext";
import { useFreshness } from "@/hooks/useFreshness";
import { FreshnessBadge } from "@/components/dashboard/FreshnessBadge";

export default function LineMovementPage() {
    const { selectedSport: sport } = useSport();
    const freshness = useFreshness(sport);
    const { data, loading, error, lastUpdated, isStale, refresh } = useLiveData<any>(
        () => api.lineMovement(sport),
        [sport],
        { refreshInterval: 300000 }
    );

    const movementData = data?.data || [];

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-8 text-white pb-24">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <div className="bg-blue-500/20 p-2 rounded-lg border border-blue-500/30">
                            <Activity size={24} className="text-blue-500" />
                        </div>
                        <h1 className="text-3xl font-black italic tracking-tighter uppercase">Live Line Movement</h1>
                    </div>
                    <p className="text-slate-400 text-sm max-w-lg mb-2">
                        Monitor real-time market fluctuations. Rapid line moves (Steam) often indicate institutional or "sharp" betting groups entering the market.
                    </p>
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
                    refreshInterval={300}
                />
            </div>

            <GateLock feature="lineMovement" reason="Live line movement tracking is a Premium feature.">
                <PageStates
                    loading={loading && !data}
                    error={error}
                    empty={!loading && movementData.length === 0}
                    emptyMessage="No significant line movement detected in the last snapshot cycle."
                >
                    <div className="grid grid-cols-1 gap-4">
                        {movementData.map((event: any, idx: number) => (
                            <div key={`${event.event_id}-${idx}`} className="space-y-4">
                                <h3 className="text-xs font-black text-slate-500 uppercase tracking-widest border-b border-white/5 pb-2">
                                    {event.game} — {event.sport}
                                </h3>
                                {event.movements.map((move: any, midx: number) => (
                                    <div key={midx} className="bg-[#0D0D14] border border-white/5 rounded-3xl p-6 hover:border-blue-500/30 transition-all flex flex-col md:flex-row items-center justify-between gap-6 group">
                                        <div className="flex items-center gap-6 w-full md:w-auto">
                                            <div className="h-14 w-14 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center">
                                                <TrendingUp className={clsx(move.delta > 0 ? "text-emerald-500" : "text-red-500")} size={28} />
                                            </div>
                                            <div>
                                                <div className="text-[10px] font-black uppercase text-slate-500 tracking-widest mb-1">Live Update · {move.book.toUpperCase()}</div>
                                                <div className="text-lg font-bold">{move.team}</div>
                                                <div className="text-sm font-black text-primary uppercase">Market Odds</div>
                                            </div>
                                        </div>

                                        <div className="flex items-center gap-8 bg-white/5 px-8 py-4 rounded-2xl border border-white/5 w-full md:w-auto">
                                            <div className="text-center">
                                                <div className="text-[10px] font-black uppercase text-slate-600 mb-1">Movement</div>
                                                <div className="text-xl font-mono font-black">{move.from} → {move.to}</div>
                                            </div>
                                            <div className="h-8 w-[1px] bg-white/10" />
                                            <div className="text-center">
                                                <div className="text-[10px] font-black uppercase text-slate-600 mb-1">Delta</div>
                                                <div className={clsx("text-xl font-mono font-black", move.delta > 0 ? "text-emerald-500" : "text-red-500")}>
                                                    {move.delta > 0 ? `+${move.delta}` : move.delta}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ))}
                    </div>

                    <button className="bg-white/5 hover:bg-white/10 border border-white/10 px-6 py-3 rounded-xl font-black uppercase tracking-widest text-[10px] transition-all flex items-center gap-2">
                        View Chart <Clock size={12} />
                    </button>
                </PageStates>
            </GateLock>
        </div>
    );
}
