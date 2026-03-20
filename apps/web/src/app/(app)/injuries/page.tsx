"use client";

import { useState, useCallback } from "react";
import { AlertCircle, Calendar, Activity, Search, Siren } from "lucide-react";
import { useLiveData } from "@/hooks/useLiveData";
import { api, API, isApiError } from "@/lib/api";
import LiveStatusBar from "@/components/LiveStatusBar";
import PageStates from "@/components/PageStates";
import { LiveHistoricalToggle } from "@/components/dashboard/LiveHistoricalToggle";
import { Clock, TrendingUp } from "lucide-react";

export default function InjuriesPage() {
    const [sport, setSport] = useState("NBA");
    const [query, setQuery] = useState("");
    const [isHistorical, setIsHistorical] = useState(false);

    const { data: injuries, loading, error, lastUpdated, isStale, refresh } = useLiveData<any[]>(
        () => api.injuries(sport.toLowerCase() as any, isHistorical),
        [sport, isHistorical],
        { refreshInterval: isHistorical ? 600000 : 300000 }
    );

    const filtered = (injuries || []).filter((i: any) =>
        i.player?.toLowerCase().includes(query.toLowerCase()) ||
        i.team?.toLowerCase().includes(query.toLowerCase())
    );

    return (
        <div className="p-4 sm:p-6 max-w-7xl mx-auto space-y-8 pb-24 text-white">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <div className="bg-red-500/20 p-2 rounded-lg border border-red-500/30">
                            <Siren size={24} className="text-red-500" />
                        </div>
                        <h1 className="text-3xl font-black italic tracking-tighter uppercase text-white">Live Injury Wire</h1>
                    </div>
                    <p className="text-[#6B7280] text-sm font-medium">Real-time reports via ESPN & SportsDataIO</p>
                </div>

                <div className="flex items-center gap-4">
                    <LiveHistoricalToggle isHistorical={isHistorical} onChange={setIsHistorical} />
                    <div className="relative group">
                        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#6B7280] group-focus-within:text-white transition-colors" />
                        <input
                            type="text"
                            placeholder="Filter roster..."
                            className="bg-[#0D0D14] border border-white/5 rounded-xl pl-10 pr-4 py-2 text-xs font-black text-white focus:outline-none focus:border-blue-500/50 transition-all w-48 shadow-2xl"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                        />
                    </div>
                </div>
            </div>

            <div className="flex gap-2 p-1 bg-[#0D0D14] border border-white/5 rounded-2xl w-fit shadow-2xl overflow-x-auto no-scrollbar">
                {["NBA", "NFL", "MLB", "NHL"].map(s => (
                    <button
                        key={s}
                        onClick={() => setSport(s)}
                        className={`px-6 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${sport === s ? "bg-white text-black shadow-xl" : "text-[#6B7280] hover:text-white"
                            }`}
                    >
                        {s}
                    </button>
                ))}
            </div>

            <PageStates
                loading={loading && !injuries}
                error={error}
                empty={!loading && filtered.length === 0}
                emptyMessage={`No active injuries reported for ${sport}.`}
            >
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    {filtered.map((item: any, i: number) => (
                        <div key={i} className={`bg-[#0D0D14] border border-white/5 rounded-2xl p-6 transition-all shadow-2xl group relative overflow-hidden ${isHistorical ? 'hover:border-blue-500/30' : 'hover:border-red-500/30'}`}>
                            <div className="flex justify-between items-start mb-6">
                                <div>
                                    <div className="text-sm font-black text-white italic truncate max-w-[120px] uppercase font-display">{item.player || item.player_name}</div>
                                    <div className="text-[10px] font-black text-textMuted uppercase mt-0.5">{item.team || 'Global Intel'}</div>
                                </div>
                                <span className={`px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-widest border ${(item.status === 'OUT' || item.status_after === 'OUT') ? 'bg-red-500/10 text-red-500 border-red-500/20 shadow-[0_0_10px_rgba(239,68,68,0.1)]' :
                                    (item.status === 'GTD' || item.status_after === 'GTD') ? 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20' :
                                        'bg-blue-500/10 text-blue-400 border-blue-500/20'
                                    }`}>
                                    {item.status || item.status_after}
                                </span>
                            </div>

                            {isHistorical ? (
                                <div className="bg-blue-500/[0.03] border border-blue-500/10 rounded-xl p-4 mb-4">
                                    <div className="flex justify-between items-center mb-2">
                                        <p className="text-[9px] font-black text-blue-400 uppercase tracking-widest flex items-center gap-1">
                                            <TrendingUp size={10} /> Impact Score
                                        </p>
                                        <span className="text-sm font-black text-white">{(item.impact_value * 10).toFixed(1)}</span>
                                    </div>
                                    <p className="text-[11px] font-bold text-textSecondary italic leading-tight">
                                        Market adjustment: {item.status_before} → {item.status_after} detected.
                                    </p>
                                </div>
                            ) : (
                                <div className="bg-white/[0.02] border border-white/5 rounded-xl p-4 mb-4">
                                    <p className="text-[9px] font-black text-textMuted uppercase tracking-widest mb-1">Diagnosis</p>
                                    <p className="text-[11px] font-bold text-textSecondary italic leading-relaxed line-clamp-2">{item.detail || item.note || 'No additional details.'}</p>
                                </div>
                            )}

                            <div className="flex items-center justify-between opacity-50">
                                <div className="flex items-center gap-1.5 text-[9px] font-black text-textMuted uppercase tracking-widest">
                                    <Clock size={12} /> {item.created_at ? new Date(item.created_at).toLocaleDateString() : 'Today'}
                                </div>
                                <div className="flex items-center gap-1.5 text-[9px] font-black text-textMuted uppercase tracking-widest">
                                    <Activity size={12} /> VERIFIED
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </PageStates>
        </div>
    );
}
