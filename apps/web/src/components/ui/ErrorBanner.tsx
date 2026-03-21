"use client";

import React from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";

interface ErrorBannerProps {
  message?: string;
  onRetry?: () => void;
}

export function ErrorBanner({ message, onRetry }: ErrorBannerProps) {
  return (
    <div className="flex flex-col items-center justify-center p-8 bg-red-500/10 border border-red-500/20 rounded-2xl text-center space-y-4">
      <div className="bg-red-500/20 p-3 rounded-full">
        <AlertTriangle className="text-red-500" size={32} />
      </div>
      <div className="space-y-1">
        <h3 className="text-white font-black uppercase tracking-tighter text-xl">Data Fetch Error</h3>
        <p className="text-slate-400 text-sm font-bold max-w-md mx-auto">
          {message || "We encountered an issue while fetching the latest data from the engine."}
        </p>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="flex items-center gap-2 bg-red-500 hover:bg-red-600 text-white px-6 py-2 rounded-xl font-black uppercase tracking-widest text-xs transition-all shadow-glow shadow-red-500/20"
        >
          <RefreshCw size={14} />
          Retry Connection
        </button>
      )}
    </div>
  );
}
