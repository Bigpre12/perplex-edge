"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
    Home, 
    Target, 
    Zap, 
    Link as LinkIcon, 
    MoreHorizontal, 
    X,
    TrendingUp,
    ArrowRightLeft,
    BarChart2,
    Diamond,
    Settings,
    Activity,
    History,
    TrendingDown
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { clsx } from "clsx";

export function MobileNav() {
    const pathname = usePathname();
    const [mounted, setMounted] = useState(false);
    const [isMoreOpen, setIsMoreOpen] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    useEffect(() => {
        setIsMoreOpen(false);
    }, [pathname]);

    const mainNav = [
        { label: "Home", href: "/", icon: Home },
        { label: "Props", href: "/player-props", icon: Target },
        { label: "EV+", href: "/ev", icon: Zap },
        { label: "Parlay", href: "/parlays", icon: LinkIcon },
    ];

    const moreNav = [
        { label: "Sharp Intel", href: "/sharp", icon: Activity },
        { label: "Hit Rate", href: "/hit-rate", icon: BarChart2 },
        { label: "Line Movement", href: "/line-movement", icon: TrendingUp },
        { label: "Arbitrage", href: "/arbitrage", icon: ArrowRightLeft },
        { label: "Whale Tracker", href: "/whale", icon: TrendingDown },
        { label: "Prop History", href: "/props-history", icon: History },
        { label: "Kalshi Term", href: "/kalshi", icon: Diamond, badge: "ELITE" },
        { label: "Settings", href: "/settings", icon: Settings },
    ];

    if (!mounted) return null;

    return (
        <>
            {/* Bottom Nav Bar */}
            <div className="fixed bottom-0 left-0 right-0 bg-lucrix-dark/95 backdrop-blur-xl border-t border-white/5 pb-safe md:hidden z-[100]">
                <div className="flex justify-around items-center h-16">
                    {mainNav.map((item) => {
                        const isActive = pathname === item.href;
                        const Icon = item.icon;
                        return (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={clsx(
                                    "flex flex-col items-center justify-center w-full h-full space-y-1 transition-all",
                                    isActive ? "text-brand-primary" : "text-textSecondary"
                                )}
                            >
                                <Icon size={20} className={isActive ? "scale-110" : "opacity-60"} strokeWidth={isActive ? 2.5 : 2} />
                                <span className={clsx(
                                    "text-[9px] font-black uppercase tracking-widest",
                                    isActive ? "opacity-100" : "opacity-40"
                                )}>
                                    {item.label}
                                </span>
                            </Link>
                        );
                    })}
                    
                    {/* More Toggle */}
                    <button
                        onClick={() => setIsMoreOpen(!isMoreOpen)}
                        className={clsx(
                            "flex flex-col items-center justify-center w-full h-full space-y-1 transition-all",
                            isMoreOpen ? "text-brand-primary" : "text-textSecondary"
                        )}
                    >
                        {isMoreOpen ? <X size={20} strokeWidth={2.5} /> : <MoreHorizontal size={20} strokeWidth={2} className="opacity-60" />}
                        <span className={clsx(
                            "text-[9px] font-black uppercase tracking-widest",
                            isMoreOpen ? "opacity-100" : "opacity-40"
                        )}>
                            More
                        </span>
                    </button>
                </div>
            </div>

            {/* More Drawer Overlay */}
            <AnimatePresence>
                {isMoreOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: 100 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 100 }}
                        className="fixed inset-0 bg-lucrix-dark/98 z-[90] md:hidden p-8 pt-20"
                    >
                        <div className="flex items-center justify-between mb-10">
                            <div>
                                <h2 className="text-3xl font-black italic uppercase tracking-tighter text-white font-display">Command</h2>
                                <p className="text-[10px] font-black text-brand-primary uppercase tracking-[0.2em] italic">Full Terminal Matrix</p>
                            </div>
                            <button onClick={() => setIsMoreOpen(false)} className="p-3 bg-white/5 rounded-2xl border border-white/10 text-white">
                                <X size={24} />
                            </button>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            {moreNav.map((item) => (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    className="flex items-center gap-4 p-4 rounded-2xl bg-white/5 border border-white/5 active:bg-white/10 active:border-white/10 transition-all"
                                >
                                    <div className="p-2.5 bg-lucrix-dark rounded-xl border border-white/10 text-brand-primary">
                                       <item.icon size={18} />
                                    </div>
                                    <div className="flex flex-col">
                                        <span className="text-[11px] font-black text-white uppercase tracking-tight">{item.label}</span>
                                        {item.badge && <span className="text-[8px] font-black text-brand-primary uppercase tracking-widest mt-0.5">{item.badge}</span>}
                                    </div>
                                </Link>
                            ))}
                        </div>

                        <div className="mt-12 p-6 rounded-3xl bg-brand-primary/5 border border-brand-primary/10 text-center">
                            <p className="text-[10px] font-black text-textMuted uppercase tracking-widest leading-relaxed">
                                v2.4.0 NEURAL CORE <br/>
                                <span className="text-brand-primary">SECURE CONNECTION ACTIVE</span>
                            </p>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
}
