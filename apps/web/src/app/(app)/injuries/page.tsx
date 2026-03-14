"use client";

import { useState, useCallback } from "react";
import { AlertCircle, Calendar, Activity, Search, Siren } from "lucide-react";
import { useLiveData } from "@/hooks/useLiveData";
import { api, API, isApiError } from "@/lib/api";
import LiveStatusBar from "@/components/LiveStatusBar";
import PageStates from "@/components/PageStates";

export default function InjuriesPage() {
    const [sport, setSport] = useState("NBA");
    const [query, setQuery] = useState("");

    const { data: injuries, loading, error, lastUpdated, isStale, refresh } = useLiveData<any[]>(
        async () => {
            const res = await api.get<any[]>(API.injuries(sport.toLowerCase() as any));
            if (isApiError(res)) throw new Error(res.message);
            return res;
        },
        [sport],
        { refreshInterval: 600000 } // 10 minutes
    );

    const filtered = (injuries || []).filter(i =>
        i.player.toLowerCase().includes(query.toLowerCase()) ||
        i.team.toLowerCase().includes(query.toLowerCase())
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
                    <div className="relative group">
                        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#6B7280] group-focus-within:text-primary transition-colors" />
                        <input
                            type="text"
                            placeholder="Filter roster..."
                            className="bg-[#0D0D14] border border-white/5 rounded-xl pl-10 pr-4 py-2 text-xs font-bold text-white focus:outline-none focus:border-primary/50 transition-all w-48 shadow-2xl"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                        />
                    </div>
                    <LiveStatusBar
                        lastUpdated={lastUpdated}
                        isStale={isStale}
                        loading={loading}
                        error={error}
                        onRefresh={refresh}
                        refreshInterval={600}
                    />
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
                    {filtered.map((injury: any, i: number) => (
                        <div key={i} className="bg-[#0D0D14] border border-white/5 rounded-2xl p-6 hover:border-red-500/30 transition-all shadow-2xl group relative overflow-hidden">
                            <div className="flex justify-between items-start mb-6">
                                <div>
                                    <div className="text-sm font-black text-white italic truncate max-w-[120px]">{injury.player}</div>
                                    <div className="text-[10px] font-black text-[#6B7280] uppercase mt-0.5">{injury.team}</div>
                                </div>
                                <span className={`px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-widest border ${injury.status === 'OUT' ? 'bg-red-500/10 text-red-500 border-red-500/20' :
                                    injury.status === 'GTD' ? 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20' :
                                        'bg-white/5 text-[#6B7280] border-white/10'
                                    }`}>
                                    {injury.status}
                                </span>
                            </div>

                            <div className="bg-white/[0.02] border border-white/5 rounded-xl p-4 mb-4">
                                <p className="text-[10px] font-black text-[#6B7280] uppercase tracking-widest mb-1">Diagnosis</p>
                                <p className="text-xs font-bold text-white italic leading-relaxed line-clamp-2">{injury.detail}</p>
                            </div>

                            <div className="flex items-center justify-between opacity-50">
                                <div className="flex items-center gap-1.5 text-[9px] font-black text-[#6B7280] uppercase tracking-widest">
                                    <Calendar size={12} /> {injury.date || 'Today'}
                                </div>
                                <div className="flex items-center gap-1.5 text-[9px] font-black text-[#6B7280] uppercase tracking-widest">
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
