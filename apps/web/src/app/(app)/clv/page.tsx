import { History, TrendingUp, ShieldCheck, Target, Zap, Info } from "lucide-react";
import { useLiveData } from "@/hooks/useLiveData";
import { api } from "@/lib/api";
import { useLucrixStore } from "@/store";
import PageStates from "@/components/PageStates";
import LiveStatusBar from "@/components/LiveStatusBar";
import GateLock from "@/components/GateLock";
import SportSelector from "@/components/shared/SportSelector";
import { clsx } from "clsx";

export default function CLVTrackerPage() {
    const activeSport = useLucrixStore((state: any) => state.activeSport);
    
    // 1. Summary Stats
    const { data: summaryData, loading: summaryLoading } = useLiveData<any>(
        () => api.get(`/api/clv/summary?sport=${activeSport}`),
        [activeSport]
    );

    // 2. Track List
    const { data: trackData, loading: trackLoading, error, lastUpdated, isStale, refresh } = useLiveData<any>(
        () => api.get(`/api/clv?sport=${activeSport}`),
        [activeSport],
        { refreshInterval: 300000 }
    );

    const metrics = summaryData?.metrics || { total_tracked: 0, beat_rate_pct: 0, avg_clv_pct: 0, edge_proven: false };
    const clvList = trackData?.data || [];

    return (
        <div className="p-4 sm:p-6 max-w-7xl mx-auto space-y-8 text-white pb-24 font-display">
            {/* Header Section */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div className="flex flex-col gap-1">
                    <div className="flex items-center gap-3">
                        <div className="bg-amber-500/20 p-2 rounded-lg border border-amber-500/30 shadow-glow shadow-amber-500/20">
                            <History size={24} className="text-amber-500" />
                        </div>
                        <h1 className="text-3xl font-black italic tracking-tighter uppercase text-white">Institutional CLV</h1>
                    </div>
                    <p className="text-[#6B7280] text-[10px] font-black uppercase tracking-[0.2em] mt-1 pl-1">
                        Closing Line Value · Proof of Market Mastery
                    </p>
                </div>

                <div className="flex flex-col space-y-2">
                    <SportSelector />
                    <div className="flex justify-end">
                        <LiveStatusBar
                            lastUpdated={lastUpdated}
                            isStale={isStale}
                            loading={trackLoading}
                            error={error}
                            onRefresh={refresh}
                            refreshInterval={300}
                        />
                    </div>
                </div>
            </div>

            {/* Performance Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-lucrix-surface border border-white/5 p-5 rounded-3xl relative overflow-hidden group">
                    <div className="absolute -right-4 -top-4 text-white/5 group-hover:text-amber-500/10 transition-colors">
                        <Target size={80} />
                    </div>
                    <p className="text-[9px] font-black text-textMuted uppercase tracking-widest mb-1">Beat Rate</p>
                    <div className="text-3xl font-black italic text-emerald-500">{metrics.beat_rate_pct}%</div>
                    <p className="text-[10px] font-bold text-textMuted mt-1">Institutional Benchmark: 62%</p>
                </div>

                <div className="bg-lucrix-surface border border-white/5 p-5 rounded-3xl relative overflow-hidden group">
                    <div className="absolute -right-4 -top-4 text-white/5 group-hover:text-blue-500/10 transition-colors">
                        <TrendingUp size={80} />
                    </div>
                    <p className="text-[9px] font-black text-textMuted uppercase tracking-widest mb-1">Avg CLV Edge</p>
                    <div className="text-3xl font-black italic text-blue-400">+{metrics.avg_clv_pct}%</div>
                    <p className="text-[10px] font-bold text-textMuted mt-1">Yield Alpha vs Open</p>
                </div>

                <div className="bg-lucrix-surface border border-white/5 p-5 rounded-3xl relative overflow-hidden group">
                    <div className="absolute -right-4 -top-4 text-white/5 group-hover:text-purple-500/10 transition-colors">
                        <ShieldCheck size={80} />
                    </div>
                    <p className="text-[9px] font-black text-textMuted uppercase tracking-widest mb-1">Proven Edge</p>
                    <div className={clsx("text-2xl font-black italic mt-1", metrics.edge_proven ? "text-emerald-500" : "text-amber-500")}>
                        {metrics.edge_proven ? "CONFIRMED" : "IDENTIFIED"}
                    </div>
                    <p className="text-[10px] font-bold text-textMuted mt-1">Verified Audit Trail</p>
                </div>

                <div className="bg-lucrix-surface border border-amber-500/20 p-5 rounded-3xl bg-amber-500/5 ring-1 ring-amber-500/10">
                    <p className="text-[9px] font-black text-amber-500 uppercase tracking-widest mb-1">Sample Set</p>
                    <div className="text-3xl font-black italic text-white">{metrics.total_tracked}</div>
                    <p className="text-[10px] font-bold text-amber-500/70 mt-1">Full Cycle Analytics</p>
                </div>
            </div>

            <GateLock feature="clv" reason="CLV Analytics and Audit are reserved for Elite members.">
                <PageStates
                    loading={trackLoading && clvList.length === 0}
                    error={error}
                    empty={!trackLoading && clvList.length === 0}
                    emptyMessage="Awaiting game completions for CLV settlement."
                >
                    <div className="bg-[#0A0A0F] border border-white/5 rounded-3xl overflow-hidden shadow-2xl">
                        <div className="overflow-x-auto">
                            <table className="w-full text-left">
                                <thead className="bg-white/5 border-b border-white/5">
                                    <tr>
                                        <th className="px-6 py-5 text-[10px] font-black text-textMuted uppercase tracking-widest">Selection</th>
                                        <th className="px-6 py-5 text-[10px] font-black text-textMuted uppercase tracking-widest">Market</th>
                                        <th className="px-6 py-5 text-[10px] font-black text-textMuted uppercase tracking-widest">Open</th>
                                        <th className="px-6 py-5 text-[10px] font-black text-textMuted uppercase tracking-widest">Close</th>
                                        <th className="px-6 py-5 text-[10px] font-black text-textMuted uppercase tracking-widest">Performance</th>
                                        <th className="px-6 py-5 text-[10px] font-black text-textMuted uppercase tracking-widest text-right">Audit</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-white/5">
                                    {clvList.map((item: any) => (
                                        <tr key={item.id} className="hover:bg-white/[0.02] transition-colors group">
                                            <td className="px-6 py-5">
                                                <div className="font-black italic text-white uppercase tracking-tight text-lg group-hover:text-amber-500 transition-colors">
                                                    {item.player || "Team Move"}
                                                </div>
                                                <div className="text-[9px] font-black text-textMuted uppercase tracking-widest mt-1">
                                                    {item.sport.toUpperCase()}
                                                </div>
                                            </td>
                                            <td className="px-6 py-5">
                                                <div className="text-xs font-black uppercase text-white/70">{item.market}</div>
                                            </td>
                                            <td className="px-6 py-5">
                                                <div className="text-sm font-mono font-black text-slate-400 bg-white/5 px-2 py-1 rounded-lg inline-block">{item.open_line}</div>
                                            </td>
                                            <td className="px-6 py-5">
                                                <div className="text-sm font-mono font-black text-white bg-white/10 px-2 py-1 rounded-lg inline-block border border-white/10">
                                                    {item.close_line?.toFixed(1) || "—"}
                                                </div>
                                            </td>
                                            <td className="px-6 py-5">
                                                <div className={clsx(
                                                    "flex items-center gap-2 font-black italic text-lg",
                                                    item.beat ? "text-emerald-500" : "text-red-500"
                                                )}>
                                                    {item.beat ? <Zap size={14} className="fill-current" /> : null}
                                                    {item.clv_value > 0 ? `+${item.clv_value.toFixed(2)}%` : `${item.clv_value.toFixed(2)}%`}
                                                </div>
                                            </td>
                                            <td className="px-6 py-5 text-right">
                                                <div className="text-[10px] font-mono font-black text-textMuted uppercase">
                                                    {new Date(item.timestamp).toLocaleDateString()}
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </PageStates>
            </GateLock>
        </div>
    );
}
