import React from "react";
import { Info, AlertTriangle, RefreshCw, Database } from "lucide-react";

export type DataStatus = "ok" | "no_data" | "upstream_error" | "pipeline_error" | "loading";

interface Props {
    status: DataStatus;
    isLoading?: boolean;
    data?: any[];
    emptyMessage?: string;
    debugInfo?: {
        source?: string;
        rows?: number;
        last_sync?: string;
        request_id?: string;
    };
    onRetry?: () => void;
    children: React.ReactNode;
}

export const UniversalDataGate: React.FC<Props> = ({
    status,
    isLoading,
    data,
    emptyMessage = "No data available in this window.",
    debugInfo,
    onRetry,
    children
}) => {
    if (isLoading || status === "loading") {
        return (
            <div className="flex flex-col items-center justify-center py-24 space-y-4 animate-pulse">
                <div className="w-10 h-10 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                <p className="text-slate-500 text-[10px] font-black uppercase tracking-[0.2em]">Syncing Intelligence...</p>
            </div>
        );
    }

    if (status === "no_data" || (status === "ok" && (!data || data.length === 0))) {
        return (
            <div className="text-center py-24 space-y-4 border border-white/5 bg-white/2 rounded-3xl backdrop-blur-sm">
                <div className="text-4xl opacity-40">📡</div>
                <div className="space-y-1 px-4">
                    <p className="text-white font-black uppercase tracking-tighter text-xl">{emptyMessage}</p>
                    <p className="text-slate-500 text-xs max-w-xs mx-auto font-bold uppercase tracking-widest leading-relaxed">
                        The engine is active but no results matched your current filters.
                    </p>
                </div>
                {onRetry && (
                    <button onClick={onRetry} className="mt-4 bg-white/5 hover:bg-white/10 border border-white/10 px-6 py-2 rounded-full text-white text-[10px] font-black uppercase tracking-widest transition-all inline-flex items-center gap-2">
                        <RefreshCw size={12} /> Sync Engine Now
                    </button>
                )}
            </div>
        );
    }

    if (status === "upstream_error") {
        return (
            <div className="text-center py-24 space-y-4 border border-amber-500/20 bg-amber-500/5 rounded-3xl">
                <AlertTriangle className="mx-auto text-amber-500" size={40} />
                <div className="space-y-1">
                    <p className="text-white font-black uppercase">Provider Latency</p>
                    <p className="text-slate-500 text-xs max-w-xs mx-auto">Upstream odds feed is experiencing delays. Re-attempting connection...</p>
                </div>
                {onRetry && (
                    <button onClick={onRetry} className="text-amber-500 text-xs font-black uppercase underline decoration-2 underline-offset-4">Retry Provider Link</button>
                )}
            </div>
        );
    }

    if (status === "pipeline_error") {
        return (
            <div className="text-center py-24 space-y-4 border border-red-500/20 bg-red-500/5 rounded-3xl">
                <Database className="mx-auto text-red-500" size={40} />
                <div className="space-y-1">
                    <p className="text-white font-black uppercase">Core Engine Error</p>
                    <p className="text-slate-500 text-xs max-w-xs mx-auto">The internal sync pipeline encountered an issue. Engineers have been notified.</p>
                </div>
                {debugInfo?.request_id && (
                    <p className="text-[9px] text-slate-700 font-mono">Trace ID: {debugInfo.request_id}</p>
                )}
            </div>
        );
    }

    return <>{children}</>;
};
