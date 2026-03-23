"use client";
import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { useSubscription } from '@/hooks/useSubscription';
import { useFreshness } from '@/hooks/useFreshness';
import { useSport } from '@/context/SportContext';
import { formatDistanceToNow } from 'date-fns';
import { 
    Home, 
    Target, 
    Zap, 
    BarChart2, 
    Link as LinkIcon, 
    Activity, 
    TrendingUp, 
    Diamond, 
    Settings,
    ArrowRightLeft,
    TrendingDown,
    History
} from 'lucide-react';

export default function Sidebar() {
    const { tier } = useSubscription();
    const pathname = usePathname();
    const [mounted, setMounted] = useState(false);
    const [activePath, setActivePath] = useState("");

    useEffect(() => {
        setMounted(true);
        setActivePath(pathname);
    }, [pathname]);

    const { selectedSport } = useSport();
    const freshness = useFreshness(selectedSport);

    // Navigation items based on spec
    const navItems = [
        { href: "/", icon: <Home size={20} />, label: "Home" },
        { href: "/player-props", icon: <Target size={20} />, label: "Props" },
        { href: "/ev", icon: <Zap size={20} />, label: "EV+" },
        { href: "/sharp", icon: <Zap size={20} />, label: "Sharp" },
        { href: "/hit-rate", icon: <BarChart2 size={20} />, label: "Hit Rate" },
        { href: "/parlays", icon: <LinkIcon size={20} />, label: "Parlay" },
        { href: "/live", icon: <Activity size={20} />, label: "Live", showLiveDot: true },
        { href: "/line-movement", icon: <TrendingUp size={20} />, label: "Move" },
        { href: "/arbitrage", icon: <ArrowRightLeft size={20} />, label: "Arb" },
        { href: "/whale", icon: <TrendingDown size={20} />, label: "Whale" },
        { href: "/props-history", icon: <History size={20} />, label: "History" },
        { href: "/kalshi", icon: <Diamond size={20} />, label: "Kalshi", badge: "ELITE" },
        { href: "/settings", icon: <Settings size={20} />, label: "Settings" },
    ];

    return (
        <aside className="fixed left-0 top-[100px] bottom-0 w-[240px] flex-shrink-0 border-r border-lucrix-border bg-lucrix-dark flex flex-col justify-between z-30 hidden md:flex">
            <div className="flex flex-col gap-1 p-3 flex-1 overflow-y-auto scrollbar-none">
                <nav className="flex flex-col gap-1">
                    {navItems.map((item) => {
                        const isActive = mounted && (activePath === item.href || (item.href !== "/" && activePath.startsWith(item.href)));
                        
                        return (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={cn(
                                    "flex items-center justify-between gap-3 px-3 py-2.5 rounded-lg transition-all group",
                                    isActive
                                        ? "bg-lucrix-elevated border-l-[3px] border-brand-purple text-white pl-[9px]" 
                                        : "text-textSecondary hover:bg-lucrix-elevated hover:text-white border-l-[3px] border-transparent pl-[9px]"
                                )}
                            >
                                <div className="flex items-center gap-3">
                                    <span className={cn(
                                        "transition-transform",
                                        isActive ? "text-brand-purple" : "text-textSecondary group-hover:text-textPrimary"
                                    )}>
                                        {item.icon}
                                    </span>
                                    <span className={cn("text-sm font-medium", isActive ? "text-white" : "text-textSecondary group-hover:text-white")}>
                                        {item.label}
                                    </span>
                                </div>
                                <div className="flex items-center gap-2">
                                    {item.showLiveDot && (
                                        <div className="w-2 h-2 rounded-full bg-brand-danger animate-pulse-slow"></div>
                                    )}
                                    {item.badge && (
                                        <span className="text-[10px] font-bold px-1.5 py-0.5 rounded badge-elite">
                                            {item.badge}
                                        </span>
                                    )}
                                </div>
                            </Link>
                        )
                    })}
                </nav>
            </div>

            {/* Bottom Footer Info */}
            <div className="p-4 border-t border-lucrix-border flex flex-col gap-1">
                <div className="flex items-center gap-2">
                    <span className="text-[10px] uppercase font-bold text-textMuted tracking-wider">Data Freshness</span>
                </div>
                <div className="text-brand-success font-mono text-xs font-medium">
                    ODDS · {freshness?.odds_last_updated ? formatDistanceToNow(new Date(freshness.odds_last_updated), { addSuffix: true }).replace('about ', '') : 'Scanning...'}
                </div>
                <div className="text-textMuted font-mono text-[10px] mt-2">
                    v2.1.0
                </div>
            </div>
        </aside>
    );
}
