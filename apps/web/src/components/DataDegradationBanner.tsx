"use client";

import React, { useEffect, useState } from "react";
import API, { isApiError } from "@/lib/api";
import { useLucrixStore } from "@/store";
import { AlertTriangle } from "lucide-react";

type Degradation = {
  level?: string;
  reasons?: string[];
  user_message?: string;
};

/**
 * Shows when /api/health/deps reports partial or severe degradation.
 * Complements SystemStatusBanner (backend reachability) with data-truth state.
 */
export default function DataDegradationBanner() {
  const backendOnline = useLucrixStore((s: any) => s.backendOnline);
  const [deg, setDeg] = useState<Degradation | null>(null);
  const [level, setLevel] = useState<string>("none");

  useEffect(() => {
    if (!backendOnline) {
      setDeg(null);
      setLevel("none");
      return;
    }

    const load = async () => {
      const res = await API.healthDeps();
      if (isApiError(res)) return;
      const d = (res as any)?.degradation;
      if (!d) return;
      setDeg(d);
      setLevel(String(d.level || "none"));
    };

    load();
    const id = setInterval(load, 30_000);
    return () => clearInterval(id);
  }, [backendOnline]);

  if (!backendOnline || level === "none") return null;

  const msg =
    deg?.user_message ||
    (level === "severe"
      ? "Market data may be stale or incomplete."
      : "Market data is partially delayed.");

  const bar =
    level === "severe"
      ? "bg-amber-500/15 border-amber-500/35 text-amber-200"
      : "bg-brand-cyan/10 border-brand-cyan/25 text-brand-cyan/90";

  return (
    <div
      className={`w-full border-b px-4 py-2 text-[11px] font-semibold flex items-center gap-2 ${bar}`}
      role="status"
    >
      <AlertTriangle className="shrink-0 size-4 opacity-90" />
      <span className="uppercase tracking-wide font-black text-[10px]">{level}</span>
      <span className="font-medium normal-case tracking-normal">{msg}</span>
    </div>
  );
}
