'use client';

import React, { useEffect, useState } from 'react';
import { API, apiFetch, isApiError } from '@/lib/api';
import { SportKey } from '@/lib/sports.config';

import { useLiveData } from '@/hooks/useLiveData';

export function SteamAlerts({ sport }: { sport: SportKey }) {
    const { data: alertsData, loading } = useLiveData(
        () => apiFetch<any>(API.alerts(sport)),
        [sport],
        { refreshInterval: 15000 }
    );

    const alerts = Array.isArray(alertsData) ? alertsData : (alertsData as any)?.alerts || [];

    if (loading && alerts.length === 0) return <div className="space-y-2 animate-pulse">{[...Array(3)].map((_, i) => <div key={i} className="h-16 bg-[#161625] rounded-lg" />)}</div>;

    return (
        <div className="bg-[#12121e] border border-[#2a2a3a] rounded-xl overflow-hidden shadow-xl">
            <div className="bg-[#1a1c2e] p-4 border-b border-[#2a2a3a] flex items-center gap-2">
                <span className="text-xl">🔥</span>
                <h3 className="font-bold text-[#f0f0ff] uppercase tracking-tighter text-sm">Steam Alerts</h3>
                <span className="ml-auto flex h-2 w-2 rounded-full bg-[#ff4466] animate-pulse"></span>
            </div>

            <div className="p-0 overflow-y-auto max-h-[400px]">
                {alerts.length === 0 ? (
                    <div className="p-8 text-center text-[#55556a] text-xs font-bold uppercase tracking-widest leading-relaxed">
                        Scanning Markets...<br />No Heavy Pressure Detected
                    </div>
                ) : (
                    <div className="divide-y divide-[#1e1e2d]">
                        {alerts.map((alert: any, idx: number) => (
                            <div key={alert.id || idx} className="p-3 border-l-2 border-orange-500 bg-orange-500/[0.03] hover:bg-orange-500/[0.06] transition-colors">
                                <div className="flex justify-between items-start mb-1">
                                    <span className="text-[10px] text-orange-400 font-black uppercase tracking-widest">
                                        {alert.severity || 'Market Steam'}
                                    </span>
                                    <span className="text-[10px] text-[#55556a] font-mono">{alert.time_ago || 'Just now'}</span>
                                </div>
                                <div className="text-xs font-bold text-[#f0f0ff] mb-1">
                                    {alert.message || `${alert.player_name}: ${alert.stat_type} line moved ${alert.line_start} → ${alert.line_current}`}
                                </div>
                                <div className="flex items-center gap-2">
                                    <div className="text-[10px] text-[#70708a] font-bold">
                                        {alert.books_count || 12} Books In Sync
                                    </div>
                                    <div className="h-1 w-1 rounded-full bg-[#44445a]"></div>
                                    <div className="text-[10px] text-orange-400 font-bold">
                                        Heavy Momentum
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            <div className="p-3 bg-[#0a0a0f] border-t border-[#1e1e2d] flex justify-between items-center">
                <p className="text-[10px] text-[#55556a] uppercase font-black">Market Pressure</p>
                <div className="flex gap-1">
                    {[1, 2, 3, 4, 5].map(i => <div key={i} className={`h-1 w-3 rounded-full ${i <= 3 ? 'bg-orange-500' : 'bg-[#1e1e2d]'}`}></div>)}
                </div>
            </div>
        </div>
    );
}
