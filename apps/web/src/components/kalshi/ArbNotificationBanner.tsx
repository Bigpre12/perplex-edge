"use client";

import { useState, useEffect } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Button } from "@/components/ui/Button";
import Link from "next/link";

export function ArbNotificationBanner() {
    const [show, setShow] = useState(false);
    const [currentArb, setCurrentArb] = useState<{ player: string; margin: number } | null>(null);

    // Mock interval for demonstration — in production this would be triggered by useKalshiArb or a global store
    useEffect(() => {
        const timer = setInterval(() => {
            // setShow(true);
            // setCurrentArb({ player: "LeBron James", margin: 5.4 });
        }, 45000);
        return () => clearInterval(timer);
    }, []);

    if (!show || !currentArb) return null;

    return (
        <AnimatePresence>
            <motion.div
                initial={{ y: -100, opacity: 0 }}
                animate={{ y: 20, opacity: 1 }}
                exit={{ y: -100, opacity: 0 }}
                className="fixed top-0 left-1/2 -translate-x-1/2 z-[100] w-full max-w-md px-4"
            >
                <div className="bg-[#0f0f0f] border-2 border-green-500/50 rounded-2xl p-4 shadow-2xl shadow-green-500/20 backdrop-blur-xl flex items-center justify-between gap-4">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-green-500/20 rounded-full flex items-center justify-center animate-pulse">
                            <span className="text-xl">⚡</span>
                        </div>
                        <div>
                            <div className="text-[10px] text-green-500 font-black uppercase tracking-widest">Arb Detected</div>
                            <div className="text-sm font-bold text-white leading-none mt-0.5">{currentArb.player}</div>
                            <div className="text-[10px] text-white/40 mt-1">Profit Margin: <span className="text-green-400 font-bold">+{currentArb.margin}%</span></div>
                        </div>
                    </div>

                    <div className="flex items-center gap-2">
                        <Link href="/kalshi">
                            <Button size="sm" className="bg-green-600 hover:bg-green-500 text-white font-bold h-8 text-[11px]">
                                Trade Now
                            </Button>
                        </Link>
                        <button
                            onClick={() => setShow(false)}
                            className="w-8 h-8 flex items-center justify-center text-white/20 hover:text-white transition-colors"
                        >
                            ✕
                        </button>
                    </div>
                </div>
            </motion.div>
        </AnimatePresence>
    );
}
