"use client";
import { useCallback, useState, useEffect } from "react";
import { Calendar, Clock, Trophy } from "lucide-react";
import { useLiveData } from "@/hooks/useLiveData";
import { api } from "@/lib/api";
import LiveStatusBar from "@/components/LiveStatusBar";
import PageStates from "@/components/PageStates";
import { useLucrixStore } from "@/store";

export default function TodaysSlate() {
    const sport = useLucrixStore((state: any) => state.activeSport);
    const { data, loading, error, lastUpdated, isStale, refresh } = useLiveData(
        () => api.slate(sport),
        [sport],
        { refreshInterval: 300000 } // 5 minutes
    );

    const [mounted, setMounted] = useState(false);
    useEffect(() => setMounted(true), []);

    return (
        <div className="space-y-6 p-4 sm:p-6 max-w-7xl mx-auto pb-24">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <div className="bg-blue-500/20 p-2 rounded-lg border border-blue-500/30">
                            <Calendar className="text-blue-400" size={24} />
                        </div>
                        <h1 className="text-3xl font-black italic tracking-tighter uppercase text-white">Today's Slate</h1>
                    </div>
                    <p className="text-[#6B7280] text-sm">
                        {mounted ? new Date().toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric' }) : "--"}
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

            <PageStates
                loading={loading && !data}
                error={error}
                empty={!loading && (!data?.sports || data.sports.length === 0)}
                emptyMessage="No active games scheduled for today."
            >
                <div className="space-y-12">
                    {data?.sports?.map((sportObj: any) => (
                        <div key={sportObj.sport} className="space-y-4">
                            <h2 className="text-xs font-black text-[#6B7280] uppercase tracking-[0.2em] border-b border-white/5 pb-2">
                                {sportObj.sport.replace(/_/g, " ")} — {sportObj.game_count} Games
                            </h2>

                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                {sportObj.games.map((g: any) => (
                                    <GameCard key={`${g.game_id}-${g.home}`} game={g} />
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            </PageStates>
        </div>
    );
}

function GameCard({ game }: { game: any }) {
    const [mounted, setMounted] = useState(false);
    useEffect(() => setMounted(true), []);

    const time = game.tip_time && mounted ? new Date(game.tip_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "TBD";

    return (
        <div className="bg-[#0D0D14] border border-white/5 rounded-2xl overflow-hidden shadow-xl transition hover:border-[#F5C51850]">
            <div className="p-4 border-b border-white/5 bg-white/[0.02] flex justify-between items-center text-sm font-black uppercase italic tracking-tighter">
                <div className="flex items-center gap-3">
                    <span className="text-[#6B7280]">{game.away}</span>
                    <span className="text-[10px] text-white/20">@</span>
                    <span className="text-white">{game.home}</span>
                </div>
                <div className="flex items-center gap-1.5 text-[#6B7280]">
                    <Clock size={12} /> {time}
                </div>
            </div>

            <div className="p-4 space-y-3">
                <p className="text-[10px] text-[#6B7280] uppercase font-black tracking-widest">Market Efficiency Edges</p>

                {game.top_props && game.top_props.length > 0 ? (
                    <div className="space-y-2">
                        {game.top_props.slice(0, 3).map((prop: any, j: number) => (
                            <div key={j} className="flex justify-between items-center bg-white/[0.03] p-2 rounded-lg text-sm border border-white/5">
                                <span className="text-white font-bold">{prop.player_name}</span>
                                <span className="text-[#F5C518] font-mono font-black text-xs">+{prop.edge_score || 0}%</span>
                            </div>
                        ))}
                    </div>
                ) : (
                    <p className="text-xs text-[#6B7280] italic">No high-confidence edges identified yet.</p>
                )}
            </div>
        </div>
    );
}
