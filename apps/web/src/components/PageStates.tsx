"use client";

import React from "react";
interface Props {
    loading: boolean;
    error: string | null;
    empty: boolean;
    emptyMessage?: string;
    status?: string | null;
    children: React.ReactNode;
}

export default function PageStates({ loading, error, empty, emptyMessage, children }: Props) {
    if (loading) return (
        <div className="flex items-center justify-center py-24">
            <div className="text-center space-y-3">
                <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
                <p className="text-gray-400 text-sm font-bold uppercase tracking-widest">Loading live data...</p>
            </div>
        </div>
    );

    if (error) return (
        <div className="text-center py-24 space-y-4 border border-red-500/20 bg-red-500/5 rounded-3xl">
            <div className="text-4xl">⚠️</div>
            <div className="space-y-1">
                <p className="text-white font-black uppercase">{error?.includes("Failed to fetch") ? "Backend Offline" : "Data Error"}</p>
                <p className="text-slate-500 text-xs max-w-xs mx-auto">{error || "Ensure the backend is running on port 8000"}</p>
            </div>
            <button onClick={() => window.location.reload()} className="text-primary text-xs font-black uppercase underline">Retry Connection</button>
        </div>
    );

    if (empty || status === "awaiting_ingest") return (
        <div className="text-center py-24 space-y-4 border border-white/5 bg-white/2 rounded-3xl backdrop-blur-sm">
            <div className="text-4xl opacity-40 animate-pulse">📡</div>
            <div className="space-y-1 px-4">
                <p className="text-white font-black uppercase tracking-tighter text-xl">
                    {status === "awaiting_ingest" ? "Awaiting Data Ingest" : (emptyMessage || "No data available")}
                </p>
                <p className="text-slate-500 text-xs max-w-xs mx-auto font-bold uppercase tracking-widest leading-relaxed">
                    {status === "awaiting_ingest" 
                        ? "The brain is currently seeding new odds. This typically takes 2-3 minutes. Hang tight."
                        : "Check back closer to game time or verify API connection"}
                </p>
            </div>
            <div className="flex flex-col items-center gap-4 mt-6">
                <button onClick={() => window.location.reload()} className="bg-white/5 hover:bg-white/10 border border-white/10 px-6 py-2 rounded-full text-white text-[10px] font-black uppercase tracking-widest transition-all">
                    Sync Engine Now
                </button>
                <a href="http://localhost:8000/api/health" target="_blank" rel="noopener noreferrer" className="text-slate-600 hover:text-primary text-[9px] font-black uppercase tracking-widest underline transition-colors">
                    System Health Check →
                </a>
            </div>
        </div>
    );

    return <>{children}</>;
}
