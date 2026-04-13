'use client';
import { SPORTS_CONFIG, ACTIVE_SPORTS } from '@/lib/sports.config';
import { useLucrixStore } from '@/store';
import { clsx } from "clsx";

export default function SportSelector() {
    const { activeSport, setActiveSport } = useLucrixStore();

    return (
        <div className="relative group">
            <div className="flex items-center gap-2 overflow-x-auto scrollbar-none py-2 px-1 snap-x">
                {ACTIVE_SPORTS.map(key => {
                    const sport = (SPORTS_CONFIG as any)[key];
                    if (!sport) return null;
                    const isActive = key === activeSport;
                    return (
                        <button
                            key={key}
                            onClick={() => setActiveSport(key)}
                            className={clsx(
                                "flex items-center gap-2 px-4 py-2.5 rounded-xl border transition-all duration-200 snap-start whitespace-nowrap",
                                "font-bold text-xs uppercase tracking-widest",
                                isActive 
                                    ? "bg-brand-cyan/20 border-brand-cyan text-white shadow-glow shadow-brand-cyan/20 scale-105 z-10" 
                                    : "bg-lucrix-surface border-lucrix-border text-textMuted hover:border-brand-cyan/40 hover:text-white"
                            )}
                        >
                            <span className={clsx(
                                "text-base transition-transform duration-200",
                                isActive ? "scale-110 rotate-12" : "group-hover:rotate-6"
                            )}>
                                {sport.icon}
                            </span>
                            <span>{sport.label}</span>
                        </button>
                    );
                })}
            </div>
            {/* Subtle Gradient Fades for Scroll */}
            <div className="absolute inset-y-0 left-0 w-8 bg-gradient-to-r from-lucrix-dark to-transparent pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="absolute inset-y-0 right-0 w-8 bg-gradient-to-l from-lucrix-dark to-transparent pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity" />
        </div>
    );
}
