"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Calendar, Zap, ArrowRightLeft, Target, BarChart3 } from "lucide-react";

export function MobileNav() {
    const pathname = usePathname();
    const [mounted, setMounted] = useState(false);
    const [activePath, setActivePath] = useState("");

    useEffect(() => {
        setMounted(true);
        setActivePath(pathname);
    }, [pathname]);

    const navItems = [
        { label: "Today", href: "/slate", icon: Calendar },
        { label: "Edges", href: "/top-edges", icon: Zap },
        { label: "Arbs", href: "/arbitrage", icon: ArrowRightLeft },
        { label: "Props", href: "/props", icon: Target },
        { label: "Hit Rate", href: "/hit-rate", icon: BarChart3 },
    ];

    return (
        <div className="fixed bottom-0 w-full bg-[#0f1117]/80 backdrop-blur-xl border-t border-white/5 pb-safe md:hidden z-50">
            <div className="flex justify-around items-center h-16">
                {navItems.map((item) => {
                    const isActive = mounted && activePath === item.href;
                    const Icon = item.icon;
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={`flex flex-col items-center justify-center w-full h-full space-y-1 transition-all ${isActive ? "text-[#F5C518]" : "text-slate-500"
                                }`}
                        >
                            <div className={isActive ? "scale-110" : ""}>
                                <Icon size={20} strokeWidth={isActive ? 2.5 : 2} />
                            </div>
                            <span className={`text-[10px] font-bold tracking-tighter uppercase ${isActive ? "opacity-100" : "opacity-60"}`}>{item.label}</span>
                        </Link>
                    );
                })}
            </div>
        </div>
    );
}
