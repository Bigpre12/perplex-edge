"use client";
import { useState, useEffect } from "react";
import { Ship, Info, AlertTriangle } from "lucide-react";
import api from "@/lib/api";

import { useLucrixStore } from "@/store";
import { useLiveData } from "@/hooks/useLiveData";
import PageStates from "@/components/PageStates";

export default function WhaleTrackerPage() {
    const sport = useLucrixStore((state: any) => state.activeSport);
    const { data: res, loading, error, refresh } = useLiveData(
        () => api.whaleSignals(sport),
        [sport],
        { refreshInterval: 30000 }
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
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-bold flex items-center gap-3">
                        <Ship className="w-8 h-8 text-[#F5C518]" />
                        Whale Tracker
                    </h1>
                    <p className="text-slate-400 mt-1">Real-time detection of high-limit market movements and sharp money.</p>
                </div>
                <div className="bg-[#F5C518]/10 border border-[#F5C518]/20 px-4 py-2 rounded-lg flex items-center gap-2 text-[#F5C518] text-sm">
                    <AlertTriangle className="w-4 h-4" />
                    <span>Live Auto-Refresh (30s)</span>
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
                                    <td className="px-6 py-4 font-medium">
                                        <div className="flex flex-col">
                                            <span>{move.player || move.player_name}</span>
                                            <span className="text-[10px] text-slate-500 uppercase tracking-tight">{move.game || 'Live Market'}</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-slate-400 capitalize">{move.stat || move.stat_type}</td>
                                    <td className="px-6 py-4 text-center">
                                        <div className="flex flex-col items-center gap-1">
                                            <span className="bg-emerald-500/10 text-emerald-500 px-2 py-1 rounded text-xs font-bold">
                                                {move.line}
                                            </span>
                                            <span className="text-[10px] text-slate-500">{move.pick || move.side || 'SHARP'}</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-slate-300">
                                        <div className="flex flex-col">
                                            <span className="text-xs text-[#F5C518] font-bold">{move.whale_label || move.type}</span>
                                            <span className="text-[10px] text-slate-500">Confidence: {move.confidence}%</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-right text-slate-500 text-sm">
                                        {move.alert_time ? new Date(move.alert_time).toLocaleTimeString() : 
                                         move.generated_at ? new Date(move.generated_at).toLocaleTimeString() : 'RECENT'}
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
