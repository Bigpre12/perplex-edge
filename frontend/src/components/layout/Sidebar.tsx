"use client";
/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import {
    LayoutDashboard,
    TrendingUp,
    Compass,
    Target,
    BarChart2,
    History,
    Settings,
    LogOut,
    User,
    ChevronRight,
    Search
} from 'lucide-react';
import { getUser, logoutUser } from '@/lib/auth';
import NotificationManager from '@/components/settings/NotificationManager';

function cn(...inputs: any[]) {
    return twMerge(clsx(inputs));
}

export default function Sidebar() {
    const [user, setLocalUser] = useState<any>(null);
    const pathname = usePathname();

    useEffect(() => {
        setLocalUser(getUser());
    }, []);

    const navItems = [
        { href: "/", icon: "dashboard", label: "Dashboard" },
        { href: "/arbitrage", icon: "analytics", label: "Market Analysis" },
        { href: "/player-props", icon: "bolt", label: "Player Props" },
        { href: "/parlays", icon: "check_circle", label: "Parlay Builder" },
        { href: "/ledger", icon: "account_balance_wallet", label: "Profit Ledger" },
        { href: "/ledger/analytics", icon: "insights", label: "Portfolio Deep-Dive" },
        { href: "/institutional/scanner", icon: "radar", label: "Institutional Scanner" },
        { href: "/institutional/strategy-lab", icon: "experiment", label: "Strategy Lab" },
        { href: "/institutional/execution", icon: "terminal", label: "Execution Hub" },
        { href: "/leaderboard", icon: "leaderboard", label: "ROI Leaderboard" },
        { href: "/shared-intel", icon: "hub", label: "Shared Intel" },
    ];

    return (
        <aside className="w-64 flex-shrink-0 border-r border-slate-800 bg-[#102023] flex flex-col justify-between z-20 h-full overflow-hidden">
            <div className="flex flex-col gap-8 p-4 flex-1 overflow-y-auto scrollbar-hide">
                <div className="flex items-center gap-3 px-2">
                    <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-primary to-cyan-700 flex items-center justify-center shadow-lg shadow-primary/20">
                        <span className="material-symbols-outlined text-white text-2xl">psychology</span>
                    </div>
                    <div className="flex flex-col">
                        <h1 className="text-white text-base font-bold leading-tight tracking-wide uppercase">LUCRIX</h1>
                        <p className="text-secondary text-xs font-normal">Engine Console</p>
                    </div>
                </div>

                <nav className="flex flex-col gap-2">
                    <p className="px-3 text-xs font-semibold text-secondary/50 uppercase tracking-wider mb-1">Main Menu</p>
                    {navItems.map((item) => (
                        <NavItem
                            key={item.href}
                            to={item.href}
                            icon={item.icon}
                            label={item.label}
                            active={pathname === item.href}
                        />
                    ))}
                </nav>
            </div>

            {/* User Profile Area */}
            <div className="p-4 border-t border-white/[0.05] bg-background-dark/30 space-y-4">
                {user && <NotificationManager />}

                <div className="flex items-center justify-between group">
                    <div className="flex items-center gap-3 px-1">
                        <div className="bg-center bg-no-repeat bg-cover rounded-full h-9 w-9 ring-2 ring-primary/20 flex items-center justify-center bg-slate-800 overflow-hidden"
                            style={{ backgroundImage: user ? `url(https://ui-avatars.com/api/?name=${encodeURIComponent(user.username)}&background=0df233&color=101f19)` : 'none' }}>
                            {!user && <span className="material-symbols-outlined text-slate-500 text-sm">person</span>}
                        </div>
                        <div className="flex flex-col overflow-hidden">
                            <span className="text-white text-sm font-medium truncate">{user?.username || 'Guest'}</span>
                            <span className="text-secondary text-[10px] truncate uppercase font-bold tracking-tighter">
                                {user ? user.subscription_tier : 'NO CLEARANCE'}
                            </span>
                        </div>
                    </div>
                    {user && (
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

function NavItem({ to, icon, label, active }: { to: string; icon: string; label: string, active: boolean }) {
    return (
        <Link
            href={to}
            className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all group",
                active
                    ? "glass-premium border border-primary/20 text-white"
                    : "text-secondary hover:bg-white/5 hover:text-white border border-transparent"
            )}
        >
            <span className={cn(
                "material-symbols-outlined group-hover:scale-110 transition-transform",
                active ? "text-primary" : "text-secondary"
            )}>
                {icon}
            </span>
            <span className="text-sm font-medium">{label}</span>
        </Link>
    );
}
