"use client";

import { useState } from "react";

export function FilterBar({ onChange }: { onChange?: (filters: any) => void }) {
    const [activeStats, setActiveStats] = useState<string[]>([]);

    const toggleStat = (stat: string) => {
        setActiveStats(prev =>
            prev.includes(stat) ? prev.filter(s => s !== stat) : [...prev, stat]
        );
    };

    return (
        <div className="flex gap-2 px-4 py-3 overflow-x-auto scrollbar-none items-center">
            {/* EV Filter */}
            <select className="bg-[#1E1E35] text-white text-xs rounded-full 
                         px-3 py-1.5 border border-[#2A2A45] outline-none
                         cursor-pointer hover:border-[#6B7280] transition-colors">
                <option>All EV</option>
                <option>+3% EV</option>
                <option>+5% EV</option>
                <option>+10% EV</option>
            </select>

            {/* Sharp Only Toggle */}
            <button className="flex items-center gap-1.5 bg-[#F5C518]/10 
                         text-[#F5C518] text-xs font-bold rounded-full 
                         px-3 py-1.5 border border-[#F5C518]/20
                         hover:bg-[#F5C518]/20 transition-colors whitespace-nowrap">
                ⚡ Sharp Only
            </button>

            {/* Steam Toggle */}
            <button className="flex items-center gap-1.5 bg-[#FF6B35]/10 
                         text-[#FF6B35] text-xs font-bold rounded-full 
                         px-3 py-1.5 border border-[#FF6B35]/20
                         hover:bg-[#FF6B35]/20 transition-colors whitespace-nowrap">
                🔥 Steam
            </button>

            <div className="w-[1px] h-4 bg-[#1E1E35] mx-1" />

            {/* Stat Type */}
            {['PTS', 'REB', 'AST', 'PRA', '3PM'].map(stat => (
                <button key={stat}
                    onClick={() => toggleStat(stat)}
                    className={`text-xs font-semibold rounded-full px-3 py-1.5 transition-all
                     ${activeStats.includes(stat)
                            ? 'bg-[#F5C518] text-black shadow-[0_0_15px_rgba(245,197,24,0.3)]'
                            : 'bg-[#1E1E35] text-[#6B7280] hover:text-white border border-transparent'
                        }`}>
                    {stat}
                </button>
            ))}
        </div>
    )
}
