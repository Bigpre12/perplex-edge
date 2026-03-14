"use client";

import React from "react";
interface Props {
    loading: boolean;
    error: string | null;
    empty: boolean;
    emptyMessage?: string;
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

    if (empty) return (
        <div className="text-center py-24 space-y-4 border border-white/5 bg-white/2 rounded-3xl">
            <div className="text-4xl opacity-20">📭</div>
            <div className="space-y-1">
                <p className="text-white font-black uppercase">{emptyMessage || "No data available right now"}</p>
                <p className="text-slate-500 text-xs max-w-xs mx-auto font-medium">Check back closer to game time or verify API connection</p>
            </div>
            <a href="http://localhost:8000/api/health" target="_blank" rel="noopener noreferrer" className="text-primary text-xs font-black uppercase underline block mt-4">
                Run API diagnostics →
            </a>
        </div>
    );

    return <>{children}</>;
}
