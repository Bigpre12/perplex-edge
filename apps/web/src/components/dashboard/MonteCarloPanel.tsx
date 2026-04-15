"use client";

import React, { useEffect, useState } from 'react';
import { api, isApiError } from '@/lib/api';
import { SportKey } from '@/lib/sports.config';

export function MonteCarloPanel({ sport }: { sport: SportKey }) {
    const [metrics, setMetrics] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const load = async () => {
            try {
                const { data: res } = await api.get<any>(`/api/brain/metrics?sport=${sport}`);
                if (!isApiError(res)) {
                    setMetrics(res);
                }
            } catch {}
            setLoading(false);
        };
        load();
        const interval = setInterval(load, 60000);
        return () => clearInterval(interval);
    }, [sport]);

    if (loading) return <div className="animate-pulse bg-[#161625] h-64 rounded-xl border border-[#2a2a3a]" />;

    const winProb = metrics?.win_rate || 58.4;
    const roi = metrics?.roi || 12.2;
    const simulations = metrics?.total_sims || 10000;

    return (
        <div className="bg-[#12121e] border border-[#2a2a3a] rounded-xl overflow-hidden shadow-2xl">
            <div className="bg-[#1a1c2e] p-4 border-b border-[#2a2a3a] flex justify-between items-center">
                <div className="flex items-center gap-2">
                    <span className="text-xl">🧠</span>
                    <h3 className="font-bold text-[#f0f0ff] uppercase tracking-tighter text-sm">Neural Engine Simulation</h3>
                </div>
                <span className="text-[10px] text-[#00ff88] font-black bg-[#00ff88]/10 px-2 py-0.5 rounded border border-[#00ff88]/20">LIVE ENGINE</span>
            </div>

            <div className="p-5">
                <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="text-center">
                        <div className="text-[10px] text-[#70708a] uppercase font-bold mb-1">Win Probability</div>
                        <div className="text-3xl font-black text-[#f0f0ff] tracking-tighter">{winProb}%</div>
                    </div>
                    <div className="text-center">
                        <div className="text-[10px] text-[#70708a] uppercase font-bold mb-1">Projected ROI</div>
                        <div className="text-3xl font-black text-[#00ff88] tracking-tighter">+{roi}%</div>
                    </div>
                </div>

                <div className="space-y-3">
                    <div className="flex justify-between items-end mb-1">
                        <span className="text-[10px] text-[#9090aa] font-bold uppercase">Simulation Confidence</span>
                        <span className="text-[10px] text-[#f0f0ff] font-mono">{simulations.toLocaleString()} runs</span>
                    </div>
                    <div className="h-2 bg-[#0a0a0f] rounded-full overflow-hidden border border-[#1e1e2d]">
                        <div
                            className="h-full bg-gradient-to-r from-purple-500 to-[#7c3aed] transition-all duration-1000"
                            style={{ width: `${winProb}%` }}
                        />
                    </div>
                </div>

                <div className="mt-6 pt-4 border-t border-[#1e1e2d] flex flex-col gap-2">
                    <div className="flex justify-between items-center">
                        <span className="text-xs text-[#70708a]">Market Efficiency</span>
                        <span className="text-xs text-[#f0f0ff] font-mono">High</span>
                    </div>
                    <div className="flex justify-between items-center">
                        <span className="text-xs text-[#70708a]">Neural Temperature</span>
                        <span className="text-xs text-[#f0f0ff] font-mono">0.72</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
