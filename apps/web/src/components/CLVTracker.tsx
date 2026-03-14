'use client';

import React, { useEffect, useState } from 'react';
import { api, isApiError } from '@/lib/api';
import { SportKey } from '@/lib/sports.config';

export function CLVTracker({ sport }: { sport: SportKey }) {
    const [entries, setEntries] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const load = async () => {
            const res = await api.get<any>(`/api/clv?sport=${sport}`);
            if (!isApiError(res)) {
                setEntries(res.clv || []);
            }
            setLoading(false);
        };
        load();
    }, [sport]);

    if (loading) return <div className="animate-pulse bg-[#161625] h-64 rounded-xl border border-[#2a2a3a]" />;

    // Calculate aggregate CLV
    const avgClv = entries.length > 0
        ? (entries.reduce((acc, curr) => acc + (curr.clv || 0), 0) / entries.length).toFixed(2)
        : "0.00";

    const beadColor = (clv: number) => clv > 0 ? '#00ff88' : clv < 0 ? '#ff4466' : '#9090aa';

    return (
        <div className="bg-[#12121e] border border-[#2a2a3a] rounded-xl overflow-hidden shadow-xl">
            <div className="bg-[#1a1c2e] p-4 border-b border-[#2a2a3a] flex justify-between items-center">
                <div className="flex items-center gap-2">
                    <span className="text-xl">📊</span>
                    <h3 className="font-bold text-[#f0f0ff] uppercase tracking-tighter text-sm">Closing Line Value (CLV)</h3>
                </div>
                <div className="flex flex-col items-end">
                    <span className="text-[10px] text-[#9090aa] uppercase font-bold">Avg Edge</span>
                    <span className={`text-sm font-black ${Number(avgClv) > 0 ? 'text-[#00ff88]' : 'text-[#ff4466]'}`}>{avgClv}%</span>
                </div>
            </div>

            <div className="p-0 overflow-y-auto max-h-[300px]">
                {entries.length === 0 ? (
                    <div className="p-8 text-center text-[#55556a] text-xs font-bold uppercase tracking-widest">
                        No Recent CLV Data
                    </div>
                ) : (
                    <div className="divide-y divide-[#1e1e2d]">
                        {entries.map((entry, idx) => (
                            <div key={entry.id || idx} className="p-3 hover:bg-[#161625] transition-colors flex justify-between items-center">
                                <div className="flex flex-col">
                                    <span className="text-xs font-bold text-[#f0f0ff]">{entry.player_name}</span>
                                    <span className="text-[10px] text-[#70708a] uppercase">{entry.stat_type}</span>
                                </div>
                                <div className="flex items-center gap-4">
                                    <div className="text-right">
                                        <div className="text-[10px] text-[#55556a] font-bold">L: {entry.line}</div>
                                        <div className="text-[11px] font-mono text-[#9090aa]">Open: {entry.open_odds}</div>
                                    </div>
                                    <div
                                        className="w-12 py-1 rounded text-center text-[11px] font-black"
                                        style={{ background: `${beadColor(entry.clv)}15`, color: beadColor(entry.clv), border: `1px solid ${beadColor(entry.clv)}30` }}
                                    >
                                        {entry.clv > 0 ? '+' : ''}{entry.clv}%
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            <div className="p-3 bg-[#0a0a0f] border-t border-[#1e1e2d]">
                <p className="text-[10px] text-[#55556a] leading-tight italic">
                    CLV measures your ability to beat the final market price. Consistent positive CLV is the #1 predictor of long-term profitability.
                </p>
            </div>
        </div>
    );
}
