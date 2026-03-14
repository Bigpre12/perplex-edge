"use client";
import { useState, useEffect, useCallback } from "react";
import { API } from "@/lib/api";

export default function SystemStatusBanner() {
  const [status, setStatus] = useState<"checking" | "online" | "offline">("checking");
  const [retrying, setRetrying] = useState(false);

  const check = useCallback(async () => {
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/health`,
        { signal: AbortSignal.timeout(4000) }
      );
      setStatus(res.ok ? "online" : "offline");
    } catch {
      setStatus("offline");
    }
  }, []);

  // Auto-check every 15s
  useEffect(() => {
    check();
    const id = setInterval(check, 15_000);
    return () => clearInterval(id);
  }, [check]);

  const handleRetry = async () => {
    setRetrying(true);
    await check();
    setRetrying(false);
  };

  // ONLINE — show nothing
  if (status === "online") return null;

  // CHECKING — subtle pulse, not blocking
  if (status === "checking") return (
    <div className="w-full bg-yellow-500/10 border-b border-yellow-500/20 px-4 py-1.5 text-xs text-yellow-400 flex items-center gap-2">
      <span className="animate-pulse">●</span>
      Connecting to backend...
    </div>
  );

  // OFFLINE — warning bar, NOT a full block
  return (
    <div className="w-full bg-red-500/10 border-b border-red-500/30 px-4 py-2 flex items-center justify-between text-xs">
      <div className="flex items-center gap-2 text-red-400">
        <span>●</span>
        <span>Backend offline —</span>
        <code className="font-mono bg-black/30 px-1.5 py-0.5 rounded text-red-300">
          cd backend && python -m uvicorn app.main:app --reload --port 8000
        </code>
      </div>
      <button
        onClick={handleRetry}
        disabled={retrying}
        className="ml-4 px-3 py-1 bg-red-500/20 hover:bg-red-500/30 
                   border border-red-500/40 rounded text-red-300 
                   disabled:opacity-50 transition-colors whitespace-nowrap"
      >
        {retrying ? "Checking..." : "RETRY"}
      </button>
    </div>
  );
}
