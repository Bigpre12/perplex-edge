"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

// Mobile-first subset aligned with docs/PRODUCT_BLUEPRINT.md (Desk → Scanner → core → risk)
const TABS = [
    { id: 'desk', label: 'Desk', icon: '▣', href: '/dashboard' },
    { id: 'scanner', label: 'Scan', icon: '◎', href: '/scanner' },
    { id: 'props', label: 'Props', icon: '◆', href: '/player-props' },
    { id: 'ev', label: 'EV+', icon: '▲', href: '/ev' },
    { id: 'clv', label: 'CLV', icon: '◇', href: '/clv' },
    { id: 'trends', label: 'Hit', icon: '◉', href: '/hit-rate' },
    { id: 'signals', label: 'Sig', icon: '◈', href: '/signals' },
    { id: 'live', label: 'Live', icon: '●', href: '/live' },
    { id: 'movement', label: 'Move', icon: '→', href: '/line-movement' },
    { id: 'settings', label: 'Set', icon: '⚙', href: '/settings' },
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
        if (activePath === href) return true;
        if (href !== '/dashboard' && href !== '/settings' && activePath.startsWith(href)) return true;
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
