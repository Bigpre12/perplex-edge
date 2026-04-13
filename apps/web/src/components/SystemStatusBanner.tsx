"use client";
import React, { useState } from "react";
import { useLucrixStore } from "@/store";
import { useHealthMonitor } from "@/hooks/useHealthMonitor";

export default function SystemStatusBanner() {
  const { backendOnline, isConnecting } = useLucrixStore();
  const { checkNow } = useHealthMonitor();
  const [retrying, setRetrying] = useState(false);

  const handleRetry = async () => {
    setRetrying(true);
    await checkNow();
    setRetrying(false);
  };

  if (backendOnline) return null;

  if (isConnecting) {
    return (
      <div className="w-full bg-amber-500/10 border-b border-amber-500/20 px-4 py-1.5 text-xs text-amber-400 flex items-center gap-2">
        <span className="animate-pulse">●</span>
        BACKEND RECONNECTING... Data from last sync shown below.
      </div>
    );
  }

  return (
    <div className="w-full bg-amber-500/10 border-b border-amber-500/30 px-4 py-2 flex items-center justify-between text-xs">
      <div className="flex items-center gap-2 text-amber-500 font-bold">
        <span className="animate-pulse">●</span>
        <span>BACKEND RECONNECTING... Data from last sync shown below.</span>
      </div>
      <button
        onClick={handleRetry}
        disabled={retrying}
        className="ml-4 px-3 py-1 bg-amber-500/20 hover:bg-amber-500/30 
                   border border-amber-500/40 rounded text-amber-300 
                   disabled:opacity-50 transition-colors whitespace-nowrap font-black uppercase"
      >
        {retrying ? "Checking..." : "Force Sync"}
      </button>
    </div>
  );
}
