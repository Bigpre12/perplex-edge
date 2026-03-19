"use client";
import { useHealthMonitor } from "@/hooks/useHealthMonitor";
import { useLucrixStore } from "@/store";

export default function HealthCheck() {
    const { check } = useHealthMonitor();
    const { backendOnline } = useLucrixStore();

    if (backendOnline) return null;

    return (
        <div className="fixed top-0 left-0 right-0 z-[9999] bg-red-950/95 text-red-400 px-5 py-3 text-center text-[13px] font-bold border-b border-red-400/20 backdrop-blur-md flex items-center justify-center gap-[15px]">
            <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 bg-red-400 rounded-full inline-block animate-pulse"></span>
                🔴 Backend offline — Critical connection lost. Retrying...
            </span>
            <button
                onClick={() => check()}
                className="bg-red-400 text-red-950 border-none rounded-md px-3 py-1 text-[11px] font-extrabold cursor-pointer uppercase tracking-wider transition-all duration-200 hover:opacity-80 active:scale-95"
            >
                Retry Request
            </button>
        </div>
    );
}
