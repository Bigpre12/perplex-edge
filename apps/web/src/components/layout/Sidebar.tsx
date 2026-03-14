"use client";
import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { useSubscription } from '@/hooks/useSubscription';
import {
    LogOut,
    Zap,
    Crown,
    LayoutDashboard,
    TrendingUp,
    Compass,
    Target,
    BarChart2,
    History,
    Settings,
    User,
    ChevronRight,
    Search
} from 'lucide-react';
import { logoutUser } from '@/lib/auth';
import NotificationManager from '@/components/settings/NotificationManager';

import { cn } from '@/lib/utils';

export default function Sidebar() {
    const { tier, loading } = useSubscription();
    const pathname = usePathname();
    const [mounted, setMounted] = useState(false);
    const [activePath, setActivePath] = useState("");

    useEffect(() => {
        setMounted(true);
        setActivePath(pathname);
    }, [pathname]);

    const navItems = [
        { href: "/", icon: "dashboard", label: "Dashboard" },
        { href: "/slate", icon: "calendar_today", label: "Today's Slate" },
        { href: "/brain", icon: "bolt", label: "Neural Engine", tier: "pro" },
        { href: "/top-edges", icon: "bolt", label: "Top Edges", tier: "pro" },
        { href: "/arbitrage", icon: "currency_exchange", label: "Arbitrage Scanner", tier: "elite" },
        { href: "/middle-boost", icon: "calculate", label: "Middle & Boost", tier: "pro" },
        { href: "/whale", icon: "monitoring", label: "Whale Tracker", tier: "elite" },
        { href: "/clv", icon: "timeline", label: "CLV Tracker", tier: "elite" },
        { href: "/kalshi", icon: "diamond", label: "Kalshi Elite", tier: "elite" },
        { href: "/player-props", icon: "target", label: "Player Props" },
        { href: "/hit-rate", icon: "analytics", label: "Hit Rate Analytics", tier: "pro" },
        { href: "/parlays", icon: "link", label: "Parlay Builder", tier: "pro" },
        { href: "/live", icon: "radio_button_checked", label: "Live Odds" },
        { href: "/bankroll", icon: "account_balance_wallet", label: "Bankroll/P&L", tier: "pro" },
        { href: "/settings", icon: "settings", label: "Settings" },
    ];

    return (
        <aside className="w-64 flex-shrink-0 border-r border-slate-800 bg-[#102023] flex flex-col justify-between z-20 h-full overflow-hidden">
            <div className="flex flex-col gap-8 p-4 flex-1 overflow-y-auto scrollbar-hide">
                <Link href="/" className="flex items-center gap-3 px-2 hover:opacity-80 transition-opacity">
                    <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-primary to-cyan-700 flex items-center justify-center shadow-lg shadow-primary/20">
                        <span className="material-symbols-outlined text-white text-2xl">psychology</span>
                    </div>
                    <div className="flex flex-col">
                        <h1 className="text-white text-base font-bold leading-tight tracking-wide uppercase">LUCRIX</h1>
                        <p className="text-secondary text-xs font-normal">Engine Console</p>
                    </div>
                </Link>

                <nav className="flex flex-col gap-2">
                    <p className="px-3 text-xs font-semibold text-secondary/50 uppercase tracking-wider mb-1">Main Menu</p>
                    {navItems.map((item) => (
                        <NavItem
                            key={item.href}
                            to={item.href}
                            icon={item.icon}
                            label={item.label}
                            active={mounted && activePath === item.href}
                            requiredTier={item.tier}
                        />
                    ))}
                </nav>
            </div>

            {/* User Profile Area */}
            <div className="p-4 border-t border-white/[0.05] bg-background-dark/30 space-y-4">
                {!loading && tier !== "free" && <NotificationManager />}

                <div className="flex items-center justify-between group">
                    <div className="flex items-center gap-3 px-1">
                        <div className="bg-center bg-no-repeat bg-cover rounded-full h-9 w-9 ring-2 ring-primary/20 flex items-center justify-center bg-slate-800 overflow-hidden">
                            <span className="material-symbols-outlined text-slate-500 text-sm">person</span>
                        </div>
                        <div className="flex flex-col overflow-hidden">
                            <span className="text-white text-sm font-medium truncate uppercase tracking-tight">
                                {tier === "elite" || tier === "owner" ? "Elite Operator" : tier === "pro" ? "Pro Member" : "Free User"}
                            </span>
                            <span className={cn(
                                "text-[10px] truncate uppercase font-bold tracking-tighter flex items-center gap-1",
                                tier === "elite" || tier === "owner" ? "text-cyan-400" : tier === "pro" ? "text-[#F5C518]" : "text-slate-500"
                            )}>
                                {tier === "elite" || tier === "owner" ? <Crown size={10} /> : <Zap size={10} />}
                                {tier?.toUpperCase() || 'LOADING...'}
                            </span>
                        </div>
                    </div>
                    {tier !== "free" && (
                        <button
                            onClick={() => logoutUser()}
                            className="p-2 text-slate-500 hover:text-red-400 transition-colors"
                        >
                            <LogOut size={16} />
                        </button>
                    )}
                </div>
            </div>
        </aside>
    );
}

function NavItem({ to, icon, label, active, requiredTier }: {
    to: string;
    icon: string;
    label: string;
    active: boolean;
    requiredTier?: string;
}) {
    return (
        <Link
            href={to}
            className={cn(
                "flex items-center justify-between gap-3 px-3 py-2.5 rounded-xl transition-all group",
                active
                    ? "glass-premium border border-primary/20 text-white"
                    : "text-secondary hover:bg-white/5 hover:text-white border border-transparent"
            )}
        >
            <div className="flex items-center gap-3">
                <span className={cn(
                    "material-symbols-outlined group-hover:scale-110 transition-transform",
                    active ? "text-primary" : "text-secondary"
                )}>
                    {icon}
                </span>
                <span className="text-sm font-medium">{label}</span>
            </div>
            {requiredTier && (
                <span className={cn(
                    "text-[8px] font-black px-1.5 py-0.5 rounded-md",
                    requiredTier === 'elite' ? "bg-cyan-500/10 text-cyan-400" : "bg-[#F5C518]/10 text-[#F5C518]"
                )}>
                    {requiredTier.toUpperCase()}
                </span>
            )}
        </Link>
    );
}
