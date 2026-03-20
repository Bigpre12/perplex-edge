"use client";
import { useState, useEffect } from "react";
import { Ship, Info, AlertTriangle } from "lucide-react";
import api from "@/lib/api";
import { LiveHistoricalToggle } from "@/components/dashboard/LiveHistoricalToggle";

import { useLucrixStore } from "@/store";
import { useLiveData } from "@/hooks/useLiveData";
import PageStates from "@/components/PageStates";

export default function WhaleTrackerPage() {
    const sport = useLucrixStore((state: any) => state.activeSport);
    const [isHistorical, setIsHistorical] = useState(false);
    const { data: res, loading, error, refresh } = useLiveData(
        () => api.whaleSignals(sport, isHistorical),
        [sport, isHistorical],
        { refreshInterval: isHistorical ? 300000 : 30000 }
    );

    const resObj = (res as any);
    const rawWhales = Array.isArray(res) ? res : (resObj?.data || resObj?.signals || []);
    
    // Deduplicate by id + player + stat + line
    const seen = new Set();
    const whaleMoves = rawWhales.filter((w: any) => {
        const pName = w.player || w.player_name || '';
        const sType = w.stat || w.stat_type || '';
        const key = `${w.id || ''}-${pName}-${sType}-${w.line || ''}`;
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
    });

    return (
        <div className="space-y-6">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
                <div>
                    <h1 className="text-3xl font-black italic uppercase tracking-tighter flex items-center gap-3 text-white font-display">
                        <Ship className="w-8 h-8 text-blue-400 shadow-glow shadow-blue-400/20" />
                        Whale Tracker
                    </h1>
                    <p className="text-[10px] text-textMuted font-bold uppercase tracking-widest mt-1">Institutional Market Movement Detection</p>
                </div>
                <div className="flex items-center gap-4">
                    <LiveHistoricalToggle isHistorical={isHistorical} onChange={setIsHistorical} />
                    {!isHistorical && (
                        <div className="bg-red-500/10 border border-red-500/20 px-4 py-2 rounded-lg flex items-center gap-2 text-red-500 text-[10px] font-black uppercase tracking-widest">
                            <div className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
                            <span>Live Refresh</span>
                        </div>
                    )}
                </div>
            </div>

            <PageStates
                loading={loading && whaleMoves.length === 0}
                error={error}
                empty={!loading && whaleMoves.length === 0}
                emptyMessage="No active whale moves detected."
            >
                <div className="bg-[#12121e] border border-white/5 rounded-2xl overflow-hidden">
                    <table className="w-full text-left">
                        <thead className="bg-white/5 text-slate-400 text-xs uppercase font-medium">
                            <tr>
                                <th className="px-6 py-4">Player / Event</th>
                                <th className="px-6 py-4">Stat</th>
                                <th className="px-6 py-4 text-center">Move</th>
                                <th className="px-6 py-4">Odds (Bf/Af)</th>
                                <th className="px-6 py-4 text-right">Detected</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {whaleMoves.map((move: any, i: number) => (
                                <tr key={i} className="hover:bg-white/5 transition-colors">
                                    <td className="px-6 py-4 font-black">
                                        <div className="flex flex-col">
                                            <span className="text-white font-display italic uppercase">{move.player || move.player_name}</span>
                                            <span className="text-[10px] text-textMuted uppercase tracking-tight">{move.game || 'Global Market'}</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-textSecondary font-bold text-xs uppercase tracking-tight">{move.stat || move.stat_type?.replace('_', ' ')}</td>
                                    <td className="px-6 py-4 text-center">
                                        <div className="flex flex-col items-center gap-1">
                                            <span className="bg-blue-500/10 text-blue-400 border border-blue-500/20 px-2 py-1 rounded text-xs font-black">
                                                {move.line || move.line_after}
                                            </span>
                                            <span className="text-[10px] text-textMuted font-bold uppercase tracking-tighter">
                                                {move.pick || move.side || (move.line_after > move.line_before ? 'OVER' : 'UNDER')}
                                            </span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-textSecondary">
                                        <div className="flex flex-col">
                                            <span className="text-xs text-white font-black">{move.whale_label || move.move_size || 'SHARP'}</span>
                                            <span className="text-[10px] text-textMuted font-bold uppercase tracking-widest">
                                                {move.odds_after ? `${move.odds_before} → ${move.odds_after}` : `Score: ${move.whale_rating || move.confidence || 0}`}
                                            </span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-right text-textMuted text-[10px] font-black uppercase tracking-widest">
                                        {move.time_detected ? new Date(move.time_detected).toLocaleTimeString() : 
                                         move.alert_time ? new Date(move.alert_time).toLocaleTimeString() : 
                                         move.created_at ? new Date(move.created_at).toLocaleTimeString() : 'RECENT'}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </PageStates>
        </div>
    );
}
