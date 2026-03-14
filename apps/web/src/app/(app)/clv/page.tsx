"use client";
import { useState, useEffect } from "react";
import { History, Info, TrendingUp } from "lucide-react";
import api from "@/lib/api";

import { useLucrixStore } from "@/store";
import { useLiveData } from "@/hooks/useLiveData";
import PageStates from "@/components/PageStates";

export default function CLVTrackerPage() {
    const sport = useLucrixStore((state: any) => state.activeSport);
    const { data, loading, error, refresh } = useLiveData(
        () => api.get(`/api/clv/track?sport=${sport}`),
        [sport],
        { refreshInterval: 300000 }
    );

    const clvData = (data as any[]) || [];

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-bold flex items-center gap-3">
                        <History className="w-8 h-8 text-[#F5C518]" />
                        CLV Tracker
                    </h1>
                    <p className="text-slate-400 mt-1">Closing Line Value: Measure how much you Beat the Book before tip-off.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-[#12121e] border border-white/5 p-6 rounded-2xl">
                    <p className="text-slate-400 text-sm uppercase tracking-wider font-medium">Avg Edge Beat</p>
                    <p className="text-3xl font-bold text-[#F5C518] mt-2">+4.2%</p>
                </div>
                <div className="bg-[#12121e] border border-white/5 p-6 rounded-2xl">
                    <p className="text-slate-400 text-sm uppercase tracking-wider font-medium">Beating the Market</p>
                    <p className="text-3xl font-bold text-green-500 mt-2">82%</p>
                </div>
                <div className="bg-[#12121e] border border-white/5 p-6 rounded-2xl">
                    <p className="text-slate-400 text-sm uppercase tracking-wider font-medium">Sample Size</p>
                    <p className="text-3xl font-bold text-slate-200 mt-2">{clvData.length} Picks</p>
                </div>
            </div>

            <PageStates
                loading={loading && clvData.length === 0}
                error={error}
                empty={!loading && clvData.length === 0}
            >
                <div className="bg-[#12121e] border border-white/5 rounded-2xl overflow-hidden">
                    <table className="w-full text-left">
                        <thead className="bg-white/5 text-slate-400 text-xs uppercase font-medium">
                            <tr>
                                <th className="px-6 py-4">Player</th>
                                <th className="px-6 py-4">Open</th>
                                <th className="px-6 py-4">Close (Current)</th>
                                <th className="px-6 py-4">CLV Beats</th>
                                <th className="px-6 py-4 text-right">Recorded At</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {clvData.map((item: any, i: number) => (
                                <tr key={i} className="hover:bg-white/5 transition-colors">
                                    <td className="px-6 py-4 font-medium">{item.player}</td>
                                    <td className="px-6 py-4 text-slate-400">{item.open_line}</td>
                                    <td className="px-6 py-4 text-slate-300">
                                        {item.close_line != null || item.current_line != null 
                                          ? parseFloat(String(item.close_line || item.current_line)).toFixed(1) 
                                          : '—'}
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className={`px-2 py-1 rounded text-xs ${parseFloat(item.clv_value) >= 0 ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'}`}>
                                            {item.clv_value}%
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-right text-slate-500 text-sm">
                                        {new Date(item.recorded_at).toLocaleDateString()}
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
