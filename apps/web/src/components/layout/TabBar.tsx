"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const TABS = [
    { id: 'home', label: 'Home', icon: '⌂', href: '/' },
    { id: 'props', label: 'Props', icon: '🎯', href: '/player-props' },
    { id: 'ev', label: 'EV+', icon: '📈', href: '/ev' },
    { id: 'sharp', label: 'Sharp', icon: '⚡', href: '/sharp' },
    { id: 'trends', label: 'Hit Rate', icon: '🔥', href: '/hit-rate' },
    { id: 'parlay', label: 'Parlay', icon: '🔗', href: '/parlays' },
    { id: 'live', label: 'Live', icon: '🔴', href: '/live' },
    { id: 'movement', label: 'Move', icon: '📉', href: '/line-movement' },
    { id: 'settings', label: 'Settings', icon: '⚙️', href: '/settings' },
];

export function TabBar() {
    const pathname = usePathname();
    const [mounted, setMounted] = useState(false);
    const [activePath, setActivePath] = useState("");

    useEffect(() => {
        setMounted(true);
        setActivePath(pathname);
    }, [pathname]);

    const isActive = (href: string) => {
        if (!mounted) return false;
        return activePath === href;
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
