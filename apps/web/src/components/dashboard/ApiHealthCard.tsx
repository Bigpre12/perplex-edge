"use client";
import { useEffect, useState } from "react";
import API, { isApiError } from "@/lib/api";

type HealthStatus = "Healthy" | "Degraded" | "Offline" | "Checking";

interface HealthData {
  status: string;
  version?: string;
  timestamp?: string;
  database?: string;
}

export default function ApiHealthCard() {
  const [health, setHealth]   = useState<HealthStatus>("Checking");
  const [detail, setDetail]   = useState<HealthData | null>(null);

  useEffect(() => {
    const check = async () => {
      try {
        const data = await API.health();
        const st = typeof data?.status === "string" ? data.status.toLowerCase() : "";
        const isHealthy =
          st === "healthy" ||
          st === "ok" ||
          st === "alive" ||
          st === "live" ||
          st === "computed_live" ||
          data?.database === "connected" ||
          data?.system_status === "ONLINE";
        
        if (isHealthy) {
          setDetail(data);
          setHealth("Healthy");
        } else if (data?.status === "degraded") {
          setDetail(data);
          setHealth("Degraded");
        } else if (isApiError(data)) {
          setHealth(data.status && data.status >= 500 ? "Offline" : "Degraded");
        } else {
          setHealth("Healthy");
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
