"use client";

import React from "react";
import { RefreshCcw } from "lucide-react";

export interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: React.ReactNode;
  onRetry?: () => void;
  retryLabel?: string;
  className?: string;
}

export function EmptyState({
  title,
  description,
  icon,
  onRetry,
  retryLabel = "Retry",
  className = "",
}: EmptyStateProps) {
  return (
    <div
      className={`flex flex-col items-center justify-center p-12 rounded-2xl bg-white/[0.03] border border-white/10 text-center ${className}`}
      role="status"
    >
      {icon ? <div className="mb-4 text-white/40">{icon}</div> : null}
      <p className="text-white font-black uppercase tracking-widest text-xs mb-2">{title}</p>
      {description ? (
        <p className="text-textMuted text-sm font-medium max-w-md mb-6 leading-relaxed">{description}</p>
      ) : null}
      {onRetry ? (
        <button
          type="button"
          onClick={onRetry}
          className="flex items-center gap-2 px-6 py-2 bg-white/10 hover:bg-white/15 border border-white/15 text-white rounded-full text-[10px] font-black uppercase tracking-widest transition-all active:scale-95"
        >
          <RefreshCcw className="w-3.5 h-3.5" />
          {retryLabel}
        </button>
      ) : null}
    </div>
  );
}
