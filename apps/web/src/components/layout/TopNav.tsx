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

const DISPLAY_SPORTS = [
    { id: 'all', name: 'All', emoji: '🏆' },
    { id: 'basketball_nba', name: 'NBA', emoji: '🏀' },
    { id: 'basketball_wnba', name: 'WNBA', emoji: '🏀' },
    { id: 'icehockey_nhl', name: 'NHL', emoji: '🏒' },
    { id: 'tennis_atp', name: 'Tennis', emoji: '🎾' },
    { id: 'boxing_boxing', name: 'Boxing', emoji: '🥊' },
    { id: 'mma_mixed_martial_arts', name: 'MMA', emoji: '🥊' },
    { id: 'soccer_mls', name: 'Soccer', emoji: '⚽' },
];

function NavUpgradeButton() {
    const tier = useLucrixStore((state: any) => state.userTier);

    if (tier === "elite") return (
        <button onClick={() => openBillingPortal()} style={{
            background: "#f59e0b20", color: "#f59e0b",
            border: "1px solid #f59e0b40",
            borderRadius: "8px", padding: "6px 14px",
            fontSize: "12px", fontWeight: 800, cursor: "pointer",
        }}>
            👑 Elite
        </button>
    );

    if (tier === "pro") return (
        <a href="/pricing" style={{
            background: "#6366f120", color: "#818cf8",
            border: "1px solid #6366f140",
            borderRadius: "8px", padding: "6px 14px",
            fontSize: "12px", fontWeight: 800,
            textDecoration: "none",
        }}>
            ⚡ Upgrade to Elite
        </a>
    );

    return (
        <a href="/pricing" style={{
            background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
            color: "#fff", border: "none",
            borderRadius: "8px", padding: "6px 14px",
            fontSize: "12px", fontWeight: 800,
            textDecoration: "none",
        }}>
            Upgrade ⚡
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

    const handleSort = (id: any) => {
        setActiveSport(id);
        const params = new URLSearchParams(searchParams.toString());
        params.set('sport', id);
        router.push(`?${params.toString()}`, { scroll: false });
    };

    const active = mounted ? activeSport : "";

    return (
        <nav className="sticky top-0 z-50 bg-[#080810]/90 
                    backdrop-blur-xl border-b border-[#1E1E35]
                    px-4 h-14 flex items-center justify-between">
            {/* Logo */}
            <Link href="/" className="flex items-center gap-2 flex-shrink-0 hover:opacity-80 transition-opacity">
                <span className="text-[#F5C518] font-bold text-xl tracking-tight">
                    LUCRIX
                </span>
                <span className="hidden xs:inline-block text-[10px] text-[#6B7280] font-mono 
                         bg-[#1E1E35] px-2 py-0.5 rounded-full">
                    BETA
                </span>
                <div className="hidden sm:block ml-2">
                    <APIHealth />
                </div>
            </Link>

            {/* Navigation Tabs */}
            <div className="flex gap-4 mx-4 items-center h-full border-r border-white/10 pr-4 hidden lg:flex">
                <Link href="/whale" className="text-xs font-bold text-slate-400 hover:text-[#F5C518] transition-colors">WHALE</Link>
                <Link href="/clv" className="text-xs font-bold text-slate-400 hover:text-[#F5C518] transition-colors">CLV</Link>
                <Link href="/markets" className="text-xs font-bold text-slate-400 hover:text-[#F5C518] transition-colors">MARKETS</Link>
                <Link href="/books" className="text-xs font-bold text-slate-400 hover:text-[#F5C518] transition-colors">BOOKS</Link>
                <Link href="/kalshi" className="text-xs font-bold text-slate-400 hover:text-purple-400 transition-colors flex items-center gap-1">
                    KALSHI <span className="text-[8px] bg-purple-500/20 text-purple-400 px-1 rounded">ELITE</span>
                </Link>
            </div>

            {/* Sport Pills */}
            <div className="flex gap-1 overflow-x-auto scrollbar-none mx-4 items-center h-full flex-1">
                {DISPLAY_SPORTS.map(sport => (
                    <button key={sport.id}
                        onClick={() => handleSort(sport.id)}
                        className={`px-3 py-1 rounded-full text-xs font-semibold 
                        transition-all whitespace-nowrap
                        ${active === sport.id
                                ? 'bg-[#F5C518] text-black'
                                : 'bg-[#1E1E35] text-[#6B7280] hover:text-white'
                            }`}>
                        {sport.emoji} {sport.name}
                    </button>
                ))}
            </div>

            {/* User */}
            <div className="flex-shrink-0 flex items-center gap-2">
                <NavUpgradeButton />
                <GlobalSearch />
                <NotificationBell />
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
