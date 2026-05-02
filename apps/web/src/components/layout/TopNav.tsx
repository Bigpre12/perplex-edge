"use client";

import { UserNav } from "./UserNav";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState, useEffect } from "react";
import { NotificationBell } from "@/components/NotificationBell";
import { GlobalSearch } from "@/components/GlobalSearch";
import { useLucrixStore } from "@/store";
import { openBillingPortal } from "@/lib/stripe";
import APIHealth from "@/components/shared/APIHealth";
import { useDataFreshness } from "@/context/DataFreshnessContext";

import { SPORTS_CONFIG, DISPLAY_SPORTS as SPORT_KEYS } from "@/lib/sports.config";

const DISPLAY_SPORTS = [
    { id: 'all', name: 'All', emoji: '⚡' },
    ...SPORT_KEYS.map(key => ({
        id: key,
        name: (SPORTS_CONFIG as any)[key]?.label || key,
        emoji: (SPORTS_CONFIG as any)[key]?.icon || '⚡'
    }))
];

function NavUpgradeButton() {
    const tier = useLucrixStore((state: any) => state.userTier);

    if (tier === "elite") return null;

    if (tier === "pro") return (
        <a href="/pricing" className="ml-2 hidden sm:flex items-center justify-center h-8 px-4 rounded-btn text-white text-xs font-bold leading-none bg-gradient-to-br from-brand-purple to-brand-cyan hover:opacity-90 transition-opacity">
            Upgrade
        </a>
    );

    return (
        <a href="/pricing" className="ml-2 hidden sm:flex items-center justify-center h-8 px-4 rounded-btn text-white text-xs font-bold leading-none bg-gradient-to-br from-brand-purple to-brand-cyan hover:opacity-90 transition-opacity">
            Upgrade
        </a>
    );
}

function TopNavContent() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const activeSport = useLucrixStore((state: any) => state.activeSport);
    const setActiveSport = useLucrixStore((state: any) => state.setActiveSport);
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    const handleSort = (id: string) => {
        setActiveSport(id);
        const params = new URLSearchParams(searchParams.toString());
        params.set('sport', id);
        router.push(`?${params.toString()}`, { scroll: false });
    };

    const active = mounted ? activeSport : "all";
    const { isStale, stalenessLabel } = useDataFreshness();

    return (
        <nav className="fixed top-0 left-0 right-0 z-50 bg-lucrix-dark h-14 border-b border-lucrix-border flex items-center justify-between px-4 sm:px-6">
            
            {/* Left section: Wordmark + Health */}
            <div className="flex items-center gap-4 flex-shrink-0 min-w-[11rem] max-w-[14rem]">
                <Link href="/desk" className="flex flex-col hover:opacity-80 transition-opacity min-w-0">
                    <span className="text-white font-display font-bold text-[20px] tracking-tight leading-none">
                        PERPLEX-EDGE
                    </span>
                    <div className="flex items-center gap-1.5 mt-1 flex-wrap">
                        <APIHealth />
                        {isStale ? (
                            <span
                                title={stalenessLabel || "Market data may be stale"}
                                className="text-[9px] font-black uppercase tracking-wider px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/35"
                            >
                                Stale
                            </span>
                        ) : null}
                    </div>
                </Link>
            </div>

            {/* Center section: Sport Pills */}
            <div className="flex-1 overflow-x-auto scrollbar-hide flex items-center mx-4 max-w-3xl">
                <div className="flex items-center gap-2 px-4 whitespace-nowrap">
                    {DISPLAY_SPORTS.map(sport => (
                        <button key={sport.id}
                            onClick={() => handleSort(sport.id)}
                            className={`h-8 px-4 rounded-full text-sm font-medium transition-all whitespace-nowrap flex items-center gap-1.5 shrink-0
                            ${active === sport.id
                                    ? 'bg-brand-purple text-white shadow-glow'
                                    : 'bg-transparent text-textSecondary hover:bg-lucrix-elevated hover:text-white'
                                }`}>
                            <span>{sport.emoji}</span> {sport.name}
                        </button>
                    ))}
                </div>
            </div>

            {/* Right section: Search + Actions */}
            <div className="flex-shrink-0 flex items-center gap-3 w-48 justify-end">
                <div className="hidden md:block">
                    <GlobalSearch />
                </div>
                <NotificationBell />
                <NavUpgradeButton />
                <div className="pl-1">
                    <UserNav />
                </div>
            </div>
            
        </nav>
    )
}

export function TopNav() {
    return (
        <Suspense fallback={<div className="fixed top-0 left-0 right-0 z-50 h-14 bg-lucrix-dark border-b border-lucrix-border" />}>
            <TopNavContent />
        </Suspense>
    )
}
