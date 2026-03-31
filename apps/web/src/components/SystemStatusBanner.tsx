"use client";
import React, { useState, useEffect, useCallback } from "react";
import API from "@/lib/api";

export default function SystemStatusBanner() {
  const [status, setStatus] = useState<"checking" | "online" | "offline">("checking");
  const [retrying, setRetrying] = useState(false);

  const check = useCallback(async () => {
    try {
      // Use the centralized API health check
      const data = await API.health();
      const isOnline = data?.status === "ok" || data?.status === "healthy";
      setStatus(isOnline ? "online" : "offline");
    } catch (err) {
      console.error("SystemStatusBanner: Health check failed", err);
      setStatus("offline");
    }
  }, []);

  // Auto-check every 60s to reduce noise
  useEffect(() => {
    check();
    const id = setInterval(check, 60_000);
    return () => clearInterval(id);
  }, [check]);

  const handleRetry = async () => {
    setRetrying(true);
    await check();
    setRetrying(false);
  };

  if (status === "online") return null;

  if (status === "checking") return (
    <div className="w-full bg-yellow-500/10 border-b border-yellow-500/20 px-4 py-1.5 text-xs text-yellow-400 flex items-center gap-2">
      <span className="animate-pulse">●</span>
      Connecting to backend services...
    </div>
  );

  return (
    <div className="w-full bg-red-500/10 border-b border-red-500/30 px-4 py-2 flex items-center justify-between text-xs">
      <div className="flex items-center gap-2 text-red-400">
        <span className="animate-pulse">●</span>
        <span>Backend offline — Critical connection lost.</span>
      </div>
      <button
        onClick={handleRetry}
        disabled={retrying}
        className="ml-4 px-3 py-1 bg-red-500/20 hover:bg-red-500/30 
                   border border-red-500/40 rounded text-red-300 
                   disabled:opacity-50 transition-colors whitespace-nowrap"
      >
        {retrying ? "Checking..." : "RETRY CONNECTION"}
      </button>
    </div>
  );
}
