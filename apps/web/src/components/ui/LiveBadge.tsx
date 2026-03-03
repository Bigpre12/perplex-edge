"use client";

import React from 'react';

interface LiveBadgeProps {
    connected: boolean;
    pulse?: boolean;
}

export function LiveBadge({ connected, pulse = true }: LiveBadgeProps) {
    if (!connected) {
        return (
            <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-[#EF4444]/10 border border-[#EF4444]/20 text-[10px] font-black uppercase tracking-tighter text-[#EF4444]">
                <span className="size-1.5 rounded-full bg-[#EF4444]" />
                Offline
            </span>
        );
    }

    return (
        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-[#22C55E]/10 border border-[#22C55E]/20 text-[10px] font-black uppercase tracking-tighter text-[#22C55E]">
            <span className={`size-1.5 rounded-full bg-[#22C55E] ${pulse ? 'animate-pulse' : ''}`} />
            Live
        </span>
    );
}
