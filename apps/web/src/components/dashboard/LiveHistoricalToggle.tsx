"use client";

import React from "react";
import { Activity, Clock } from "lucide-react";
import { cn } from "@/lib/utils";

interface LiveHistoricalToggleProps {
  isHistorical: boolean;
  onChange: (val: boolean) => void;
  className?: string;
}

export const LiveHistoricalToggle: React.FC<LiveHistoricalToggleProps> = ({
  isHistorical,
  onChange,
  className,
}) => {
  return (
    <div className={cn("flex p-1 bg-zinc-950/50 backdrop-blur-md border border-zinc-800/50 rounded-xl", className)}>
      <button
        onClick={() => onChange(false)}
        className={cn(
          "flex items-center gap-2 px-4 py-2 text-[13px] font-bold tracking-tight transition-all rounded-lg",
          !isHistorical 
            ? "bg-zinc-800 text-white shadow-[0_0_20px_rgba(0,0,0,0.5)] border border-zinc-700/50" 
            : "text-zinc-500 hover:text-zinc-300"
        )}
      >
        <div className={cn("w-1.5 h-1.5 rounded-full", !isHistorical ? "bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.8)] animate-pulse" : "bg-zinc-600")} />
        LIVE
      </button>
      <button
        onClick={() => onChange(true)}
        className={cn(
          "flex items-center gap-2 px-4 py-2 text-[13px] font-bold tracking-tight transition-all rounded-lg",
          isHistorical 
            ? "bg-zinc-800 text-white shadow-[0_0_20px_rgba(0,0,0,0.5)] border border-zinc-700/50" 
            : "text-zinc-500 hover:text-zinc-300"
        )}
      >
        <Clock className={cn("w-3.5 h-3.5", isHistorical ? "text-blue-400" : "text-zinc-500")} />
        TRENDS
      </button>
    </div>
  );
};
