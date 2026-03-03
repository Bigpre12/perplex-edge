"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const TABS = [
    { id: 'props', label: 'Props', icon: '🎯', href: '/player-props' },
    { id: 'trends', label: 'Hit Rate', icon: '🔥', href: '/trend-hunter' },
    { id: 'parlay', label: 'Parlay', icon: '🔗', href: '/parlays' },
    { id: 'live', label: 'Live', icon: '🔴', href: '/arbitrage' },
    { id: 'clv', label: 'CLV', icon: '📈', href: '/leaderboard' },
];

export function TabBar() {
    const pathname = usePathname();

    const isActive = (href: string) => {
        if (pathname === href) return true;
        return false;
    };

    return (
        <div className="sticky top-14 z-40 bg-[#080810]/90 backdrop-blur-xl
                    border-b border-[#1E1E35] px-4">
            <div className="flex gap-0 overflow-x-auto scrollbar-none">
                {TABS.map(tab => (
                    <Link
                        href={tab.href}
                        key={tab.id}
                        scroll={false}
                        className={`px-4 py-3 text-sm font-semibold whitespace-nowrap
                        border-b-2 transition-all flex items-center gap-2
                        ${isActive(tab.href)
                                ? 'border-[#F5C518] text-[#F5C518]'
                                : 'border-transparent text-[#6B7280] hover:text-white'
                            }`}>
                        {tab.icon} {tab.label}
                    </Link>
                ))}
            </div>
        </div>
    )
}
