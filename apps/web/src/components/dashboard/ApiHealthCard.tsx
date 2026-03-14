"use client";
import { useEffect, useState } from "react";

type HealthStatus = "Healthy" | "Degraded" | "Offline" | "Checking";

interface HealthData {
  status: string;
  version?: string;
  timestamp?: string;
}

import { api, isApiError } from "@/lib/api";

export default function ApiHealthCard() {
  const [health, setHealth]   = useState<HealthStatus>("Checking");
  const [detail, setDetail]   = useState<HealthData | null>(null);

  useEffect(() => {
    const check = async () => {
      try {
        const data = await api.health();
        if (!isApiError(data)) {
          setDetail(data);
          const s = data.status?.toLowerCase();
          if (s === "healthy") setHealth("Healthy");
          else if (s === "degraded") setHealth("Degraded");
          else setHealth("Healthy");
        } else {
          setHealth(data.status && data.status >= 500 ? "Offline" : "Degraded");
        }
      } catch {
        setHealth("Offline");
      }
    };
    check();
    const id = setInterval(check, 30_000);
    return () => clearInterval(id);
  }, []);

  const colors: Record<HealthStatus, string> = {
    Healthy:  "text-green-400",
    Degraded: "text-yellow-400",
    Offline:  "text-red-400",
    Checking: "text-gray-400 animate-pulse",
  };

  return (
    <div className="bg-[#0d1117] border border-white/10 rounded-xl p-5">
      <p className="text-xs text-gray-500 uppercase tracking-widest mb-2">API Health</p>
      <p className={`text-2xl font-bold italic ${colors[health]}`}>{health}</p>
      {detail?.version && (
        <p className="text-xs text-gray-600 mt-1">v{detail.version}</p>
      )}
    </div>
  );
}
