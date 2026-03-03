"use client";

import { UserNav } from "./UserNav";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense } from "react";

import { SPORTS } from '@/utils/sportUtils';

const SPORTS_LIST = SPORTS.filter(s => s.inSeason).map(s => ({
    id: s.id,
    name: s.name,
    emoji: s.id.includes('basketball') ? '🏀' : s.id.includes('hockey') ? '🏒' : s.id.includes('football') ? '🏈' : s.id.includes('soccer') ? '⚽' : s.id.includes('tennis') ? '🎾' : s.id.includes('mma') || s.id.includes('boxing') ? '🥊' : '🏆',
    short: s.name.replace(' (ATP/WTA)', '').replace(' (EPL)', '')
}));

// Added "All" tab at the beginning
const DISPLAY_SPORTS = [
    { id: 'all', name: 'All', emoji: '🏆', short: 'All' },
    ...SPORTS_LIST
];

function TopNavContent() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const active = searchParams.get('sport') || 'basketball_nba';

    const handleSort = (id: string) => {
        const params = new URLSearchParams(searchParams.toString());
        params.set('sport', id);
        router.push(`?${params.toString()}`, { scroll: false });
    };

    return (
        <nav className="sticky top-0 z-50 bg-[#080810]/90 
                    backdrop-blur-xl border-b border-[#1E1E35]
                    px-4 h-14 flex items-center justify-between">
            {/* Logo */}
            <div className="flex items-center gap-2 flex-shrink-0">
                <span className="text-[#F5C518] font-bold text-xl tracking-tight">
                    LUCRIX
                </span>
                <span className="hidden xs:inline-block text-[10px] text-[#6B7280] font-mono 
                         bg-[#1E1E35] px-2 py-0.5 rounded-full">
                    BETA
                </span>
            </div>

            {/* Sport Pills */}
            <div className="flex gap-1 overflow-x-auto scrollbar-none mx-4 items-center h-full">
                {DISPLAY_SPORTS.map(sport => (
                    <button key={sport.id}
                        onClick={() => handleSort(sport.id)}
                        className={`px-3 py-1 rounded-full text-xs font-semibold 
                        transition-all whitespace-nowrap
                        ${active === sport.id
                                ? 'bg-[#F5C518] text-black'
                                : 'bg-[#1E1E35] text-[#6B7280] hover:text-white'
                            }`}>
                        {sport.emoji} {sport.short}
                    </button>
                ))}
            </div>

            {/* User */}
            <div className="flex-shrink-0">
                <UserNav />
            </div>
        </nav>
    )
}

export function TopNav() {
    return (
        <Suspense fallback={<div className="h-14 bg-[#080810]/90 border-b border-[#1E1E35]" />}>
            <TopNavContent />
        </Suspense>
    )
}
