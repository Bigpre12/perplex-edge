"use client";
import React, { useState, useEffect } from "react";
import { Bell } from "lucide-react";
import { API, isApiError } from "@/lib/api";

import { useLucrixStore } from "@/store";
import { useLiveData } from "@/hooks/useLiveData";

export function NotificationBell() {
    const activeSport = useLucrixStore((state: any) => state.activeSport);
    const { data, loading } = useLiveData(
        () => API.alerts(activeSport === 'all' ? 'basketball_nba' : activeSport),
        [activeSport],
        { refreshInterval: 30000 }
    );

    const [open, setOpen] = useState(false);
    const [archived, setArchived] = useState(false); // To handle "Archive All" locally if needed

    const alerts = Array.isArray(data) ? data : (data as any)?.alerts || [];
    const displayAlerts = archived ? [] : alerts.slice(0, 10);
    const unreadCount = displayAlerts.length;

    return (
        <div className="relative">
            <button
                onClick={() => setOpen(!open)}
                className="p-2 bg-[#161625] rounded-full hover:bg-[#1e1e2d] text-[#9090aa] hover:text-white transition-all relative border border-[#2a2a3a]"
            >
                <Bell size={18} />
                {unreadCount > 0 && (
                    <span className="absolute -top-1 -right-1 bg-[#ff4466] text-white text-[9px] w-4 h-4 rounded-full flex items-center justify-center font-black shadow-[0_0_8px_rgba(255,68,102,0.4)]">
                        {unreadCount}
                    </span>
                )}
            </button>

            {open && (
                <div className="absolute right-0 top-12 w-80 bg-[#12121e] border border-[#2a2a3a] shadow-2xl rounded-xl overflow-hidden z-[100]">
                    <div className="bg-[#1a1c2e] p-3 border-b border-[#2a2a3a] flex justify-between items-center">
                        <h3 className="text-[#f0f0ff] font-bold text-xs uppercase tracking-tight">Market Pulse</h3>
                        <button onClick={() => setArchived(true)} className="text-[10px] text-[#55556a] hover:text-[#9090aa] font-bold uppercase">Archive All</button>
                    </div>
                    <div className="max-h-96 overflow-y-auto custom-scrollbar">
                        {displayAlerts.length === 0 ? (
                            <div className="p-8 text-center text-[#55556a] text-xs font-bold uppercase tracking-widest">No New Alerts</div>
                        ) : (
                            displayAlerts.map((a: any, idx: number) => (
                                <div key={a.id || idx} className="p-3 border-b border-[#2a2a3a]/50 hover:bg-[#161625] transition-colors cursor-pointer">
                                    <div className="flex justify-between items-start mb-1">
                                        <span className="text-[11px] font-black text-white uppercase tracking-tighter italic">
                                            {a.severity || 'MARKET MOVE'}
                                        </span>
                                        <span className="text-[9px] text-[#55556a] font-mono">{a.time_ago || 'Now'}</span>
                                    </div>
                                    <p className="text-xs text-[#9090aa] leading-snug font-medium">
                                        {a.message || `${a.player_name} line shift detected.`}
                                    </p>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
