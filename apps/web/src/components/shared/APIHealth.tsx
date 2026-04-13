'use client';
import { useLucrixStore } from '@/store';
import { clsx } from 'clsx';

export default function APIHealth() {
  const { backendOnline } = useLucrixStore();

  return (
    <div className="flex items-center gap-2 px-2 py-1 bg-white/5 rounded-full border border-white/5">
      <div
        className={clsx(
          "w-1.5 h-1.5 rounded-full animate-pulse-slow",
          backendOnline 
            ? "bg-brand-success shadow-glow shadow-brand-success/50" 
            : "bg-brand-danger shadow-glow shadow-brand-danger/50"
        )}
      />
      <span className={clsx(
        "text-[10px] font-black uppercase tracking-widest leading-none",
        backendOnline ? "text-brand-success" : "text-brand-danger"
      )}>
        API: {backendOnline ? 'Sync' : 'ERR'}
      </span>
    </div>
  );
}
