"use client";

import { useCallback } from "react";
import { Radio, Activity, Trophy, Clock, BrainCircuit } from "lucide-react";
import { useLiveData } from "@/hooks/useLiveData";
import { api } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";
import LiveStatusBar from "@/components/LiveStatusBar";
import PageStates from "@/components/PageStates";

import { useSport } from "@/context/SportContext";
import { isApiError } from "@/lib/api";

export default function LivePage() {
    const { selectedSport: sport } = useSport();

    const { data: liveData, loading, error, lastUpdated, isStale, refresh, status } = useLiveData<any>(
        () => api.liveGames(sport),
        [sport],
        { refreshInterval: 30000 } // 30 seconds
    );

    const games = isApiError(liveData) ? [] : liveData?.games || [];
    const filtered = games; // Assuming 'filtered' is meant to be 'games' or a derived value from 'games'

    return (
        <div className="p-4 sm:p-6 max-w-7xl mx-auto space-y-8 pb-24 text-white">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <div className="bg-red-500/20 p-2 rounded-lg border border-red-500/30 animate-pulse">
                            <Radio size={24} className="text-red-500" />
                        </div>
                        <h1 className="text-3xl font-black italic tracking-tighter uppercase text-white">Live Odds Console</h1>
                    </div>
                    <p className="text-[#6B7280] text-sm font-medium">Real-time market pressure and live game state</p>
                </div>

                <LiveStatusBar
                    lastUpdated={lastUpdated}
                    isStale={isStale}
                    loading={loading}
                    error={error}
                    onRefresh={refresh}
                    refreshInterval={30}
                />
            </div>

            {/* Brain Alerts Panel */}
            <div className="bg-emerald-900/10 border border-emerald-500/20 rounded-2xl p-4 md:p-6 mb-8 flex flex-col md:flex-row gap-4 items-center justify-between">
                <div className="flex items-center gap-4">
                    <div className="relative">
                        <BrainCircuit className="w-8 h-8 text-emerald-500 relative z-10" />
                        <div className="absolute inset-x-0 bottom-0 h-4 bg-emerald-500/30 blur z-0" />
                        <div className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-400 rounded-full animate-ping" />
                        <div className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-500 rounded-full" />
                    </div>
                    <div>
                        <h2 className="text-lg font-black uppercase tracking-widest text-emerald-500">Brain Alerts Active</h2>
                        <p className="text-sm font-mono text-emerald-600/70">Scanning live game flows for neural edges.</p>
                    </div>
                </div>
                <div className="text-xs font-mono text-emerald-500/50 bg-emerald-950 px-3 py-1.5 rounded-full border border-emerald-900">
                    Live Analysis Subsystem: ONLINE
                </div>
            </div>

            <PageStates
                loading={loading && !liveData}
                error={error}
                empty={!loading && filtered.length === 0}
                emptyMessage="No games are currently in-play."
                status={status}
            >
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {games.map((game: any) => (
                        <div key={game.id} className="bg-[#0D0D14] border border-white/5 rounded-2xl overflow-hidden shadow-2xl">
                            {/* Scoreboard Header */}
                            <div className="p-6 bg-gradient-to-r from-red-500/10 to-transparent border-b border-white/5">
                                <div className="flex justify-between items-center mb-6">
                                    <div className="flex items-center gap-2 text-[10px] font-black text-red-500 uppercase tracking-[0.2em]">
                                        <Activity size={14} /> {game.status} · {game.clock}
                                    </div>
                                    <div className="flex items-center gap-2 text-[10px] font-black text-[#6B7280] uppercase tracking-widest">
                                        <Clock size={14} /> {game.time_remaining}
                                    </div>
                                </div>

                                <div className="flex justify-between items-center px-4">
                                    <div className="text-center flex-1">
                                        <div className="text-sm font-black text-white italic truncate max-w-[120px] mx-auto">{game.away_team}</div>
                                        <div className="text-4xl font-black text-white mt-1 font-mono tracking-tighter">{game.away_score}</div>
                                    </div>
                                    <div className="text-xs font-black text-white/20 italic px-4 uppercase">VS</div>
                                    <div className="text-center flex-1">
                                        <div className="text-sm font-black text-white italic truncate max-w-[120px] mx-auto">{game.home_team}</div>
                                        <div className="text-4xl font-black text-white mt-1 font-mono tracking-tighter">{game.home_score}</div>
                                    </div>
                                </div>
                            </div>

                            {/* Live Props Feed */}
                            <div className="p-6 space-y-4 bg-white/[0.01]">
                                <h4 className="text-[10px] font-black text-[#6B7280] uppercase tracking-[0.2em] flex items-center gap-2">
                                    <Trophy size={14} /> Market Pressure Edges
                                </h4>
                                <div className="space-y-3">
                                    {game.props?.map((prop: any, i: number) => (
                                        <div key={i} className="bg-white/[0.02] border border-white/5 rounded-xl p-4 flex justify-between items-center transition hover:bg-white/[0.04]">
                                            <div>
                                                <div className="text-sm font-black text-white italic uppercase tracking-tight">{prop.player_name}</div>
                                                <div className="text-[10px] font-bold text-[#6B7280] uppercase mt-0.5">{prop.stat_type} · Line: {prop.line}</div>
                                            </div>
                                            <div className="text-center">
                                                <div className="text-xs font-black text-emerald-500 font-mono italic">{prop.current_value} ACTUAL</div>
                                                <div className="text-[9px] font-black text-[#6B7280] uppercase tracking-widest mt-0.5">PACE: {prop.pace}</div>
                                            </div>
                                            <div className="text-right">
                                                <div className="text-xs font-black text-primary font-mono">{prop.over_odds > 0 ? `+${prop.over_odds}` : prop.over_odds}</div>
                                                <div className="text-[9px] font-black text-[#6B7280] uppercase tracking-widest mt-0.5">{prop.book}</div>
                                            </div>
                                        </div>
                                    ))}
                                    {(!game.props || game.props.length === 0) && (
                                        <p className="text-xs text-[#6B7280] italic text-center py-4">No live market discrepancies detected yet.</p>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </PageStates>
        </div>
    );
}
