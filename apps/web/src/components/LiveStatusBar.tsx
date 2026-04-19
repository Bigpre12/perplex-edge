"use client";

import React, { useEffect, useState } from 'react';
import { useLucrixStore } from '@/store';
import API, { isApiError } from '@/lib/api';

interface LiveStatusBarProps {
    lastUpdated?: Date | null;
    isStale?: boolean;
    loading?: boolean;
    error?: string | null;
    onRefresh?: () => void;
    refreshInterval?: number;
}

export default function LiveStatusBar({
    lastUpdated,
    isStale,
    loading,
    error,
    onRefresh,
    refreshInterval
}: LiveStatusBarProps) {
    const { backendOnline, setBackendOnline } = useLucrixStore();
    const [latency, setLatency] = useState<number | null>(null);
    const [lastCheck, setLastCheck] = useState<Date | null>(null);
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
        const check = async () => {
            const start = Date.now();
            try {
                const res = await API.livePing();
                const reachable =
                    !isApiError(res) &&
                    (res?.status === "ok" || res?.status === "healthy");
                if (reachable) {
                    setLatency(Date.now() - start);
                    setBackendOnline(true);
                } else {
                    setBackendOnline(false);
                }
            } catch {
                setBackendOnline(false);
            }
            setLastCheck(new Date());
        };

        check();
        const interval = setInterval(check, 10000); // 10s health check
        return () => clearInterval(interval);
    }, [setBackendOnline]);

    return (
        <div className="fixed bottom-4 right-4 z-50 flex items-center gap-3 bg-[#0a0a0f]/90 backdrop-blur-md border border-[#2a2a3a] px-3 py-1.5 rounded-full shadow-2xl">
            <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${backendOnline ? 'bg-[#00ff88] shadow-[0_0_8px_#00ff88]' : 'bg-[#ff4466] shadow-[0_0_8px_#ff4466]'} transition-all`} />
                <span className="text-[10px] font-black uppercase tracking-widest text-[#f0f0ff]">
                    {backendOnline ? 'System Live' : 'System Offline'}
                </span>
            </div>

            {loading && (
                <>
                    <div className="w-[1px] h-3 bg-[#2a2a3a]" />
                    <span className="text-[9px] text-blue-400 font-bold uppercase animate-pulse">Syncing...</span>
                </>
            )}

            {lastUpdated && !loading && (
                <>
                    <div className="w-[1px] h-3 bg-[#2a2a3a]" />
                    <div className="flex items-center gap-1">
                        <span className="text-[9px] text-[#70708a] font-bold uppercase">Updated</span>
                        <span className={`text-[10px] font-mono ${isStale ? 'text-orange-400' : 'text-[#00ff88]'}`}>
                            {mounted ? lastUpdated.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '--:--'}
                        </span>
                    </div>
                </>
            )}

            {backendOnline && !loading && !lastUpdated && (
                <>
                    <div className="w-[1px] h-3 bg-[#2a2a3a]" />
                    <div className="flex items-center gap-1">
                        <span className="text-[9px] text-[#70708a] font-bold uppercase">Latency</span>
                        <span className="text-[10px] font-mono text-[#00ff88]">{latency}ms</span>
                    </div>
                </>
            )}

            <div className="w-[1px] h-3 bg-[#2a2a3a]" />
            <button
                onClick={onRefresh}
                className="text-[9px] text-[#55556a] font-bold uppercase hover:text-white transition-colors"
                title={`Last check: ${mounted && lastCheck ? lastCheck.toLocaleTimeString() : '--:--:--'}`}
            >
                {mounted && lastCheck ? lastCheck.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '--:--'}
            </button>
        </div>
    );
}
