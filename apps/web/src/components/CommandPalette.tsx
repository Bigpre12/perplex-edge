"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Search, Compass, Rocket, Sparkles, Settings, Users, ArrowRight, ShieldCheck } from "lucide-react";

type Action = {
    id: string;
    label: string;
    icon: React.ReactNode;
    route?: string;
    action?: () => void;
    category: "Navigation" | "Command" | "System";
};

export default function CommandPalette() {
    const [isOpen, setIsOpen] = useState(false);
    const [query, setQuery] = useState("");
    const [activeIndex, setActiveIndex] = useState(0);
    const router = useRouter();

    // The Global Action Dictionary
    const actions: Action[] = [
        { id: '1', label: "Go to Live Engine Screener", icon: <Compass size={16} />, route: "/institutional/strategy-lab", category: "Navigation" },
        { id: '2', label: "Go to Player Props Grid", icon: <Users size={16} />, route: "/player-props", category: "Navigation" },
        { id: '3', label: "Go to Affiliate Dashboard", icon: <Sparkles size={16} />, route: "/institutional/affiliate", category: "Navigation" },
        { id: '4', label: "Go to Engine Settings", icon: <Settings size={16} />, route: "/institutional/settings", category: "Navigation" },
        { id: '5', label: "Go to Admin Command Center", icon: <ShieldCheck size={16} />, route: "/admin", category: "System" },
        {
            id: '6',
            label: "Force Manual EV Sync",
            icon: <Rocket size={16} />,
            action: () => {
                alert("Triggering backend Arbitrage engine sweep...");
                setIsOpen(false);
            },
            category: "Command"
        },
    ];

    // Filter logic
    const filteredActions = query === ""
        ? actions
        : actions.filter(a => a.label.toLowerCase().includes(query.toLowerCase()) || a.category.toLowerCase().includes(query.toLowerCase()));

    // Listen for Cmd+K globally
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if ((e.metaKey || e.ctrlKey) && e.key === "k") {
                e.preventDefault();
                setIsOpen(open => !open);
            }
            if (e.key === "Escape") {
                setIsOpen(false);
            }
        };

        window.addEventListener("keydown", handleKeyDown);
        return () => window.removeEventListener("keydown", handleKeyDown);
    }, []);

    // Listen for up/down/enter when modal is open
    const handleModalKeys = useCallback((e: React.KeyboardEvent) => {
        if (!isOpen) return;

        if (e.key === "ArrowDown") {
            e.preventDefault();
            setActiveIndex(prev => (prev + 1) % filteredActions.length);
        } else if (e.key === "ArrowUp") {
            e.preventDefault();
            setActiveIndex(prev => (prev - 1 + filteredActions.length) % filteredActions.length);
        } else if (e.key === "Enter") {
            e.preventDefault();
            const action = filteredActions[activeIndex];
            if (action) {
                if (action.route) {
                    router.push(action.route);
                    setIsOpen(false);
                } else if (action.action) {
                    action.action();
                }
            }
        }
    }, [isOpen, filteredActions, activeIndex, router]);

    // Reset index on search
    useEffect(() => {
        setActiveIndex(0);
    }, [query]);

    // Grouping logic for rendering
    const groupedActions = filteredActions.reduce((acc, action) => {
        if (!acc[action.category]) acc[action.category] = [];
        acc[action.category].push(action);
        return acc;
    }, {} as Record<string, Action[]>);

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={() => setIsOpen(false)}
                        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[100]"
                    />

                    {/* Palette Modal */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: -20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: -20 }}
                        transition={{ duration: 0.2, ease: "easeOut" }}
                        className="fixed top-[15%] left-1/2 -translate-x-1/2 w-full max-w-2xl bg-[#0c1416]/95 border border-white/10 rounded-2xl shadow-[0_0_50px_rgba(0,0,0,0.5)] z-[101] overflow-hidden flex flex-col"
                        onKeyDown={handleModalKeys}
                    >
                        {/* Search Input Header */}
                        <div className="flex items-center px-4 py-4 border-b border-white/10 bg-white/[0.02]">
                            <Search size={20} className="text-slate-400 mr-3" />
                            <input
                                autoFocus
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                placeholder="Search apps, commands, or documentation..."
                                className="flex-1 bg-transparent border-none outline-none text-white text-lg placeholder:text-slate-500 font-medium font-display"
                            />
                            <div className="hidden sm:flex items-center gap-1.5 px-2 py-1 rounded-md bg-white/5 border border-white/10 text-[10px] text-slate-400 font-bold uppercase tracking-widest shrink-0">
                                <span>ESC</span> to close
                            </div>
                        </div>

                        {/* Results Body */}
                        <div className="max-h-[60vh] overflow-y-auto custom-scrollbar p-2">
                            {filteredActions.length === 0 ? (
                                <div className="p-8 text-center text-slate-500 text-sm">
                                    No commands found. Try searching for "Screener" or "Sync".
                                </div>
                            ) : (
                                Object.entries(groupedActions).map(([category, items]) => (
                                    <div key={category} className="mb-4 last:mb-0">
                                        <div className="px-3 py-2 text-[10px] font-black uppercase tracking-widest text-slate-500">
                                            {category}
                                        </div>
                                        <div className="space-y-1">
                                            {items.map((action) => {
                                                // Find the actual index of this UI item inside the flat filtered array
                                                const globalIndex = filteredActions.findIndex(a => a.id === action.id);
                                                const isActive = globalIndex === activeIndex;

                                                return (
                                                    <div
                                                        key={action.id}
                                                        onMouseEnter={() => setActiveIndex(globalIndex)}
                                                        onClick={() => {
                                                            if (action.route) {
                                                                router.push(action.route);
                                                                setIsOpen(false);
                                                            } else if (action.action) {
                                                                action.action();
                                                            }
                                                        }}
                                                        className={`flex items-center gap-3 px-3 py-3 rounded-xl cursor-pointer transition-colors ${isActive ? 'bg-primary/10 border-l-2 border-primary' : 'hover:bg-white/[0.02] border-l-2 border-transparent'
                                                            }`}
                                                    >
                                                        <div className={`p-2 rounded-lg ${isActive ? 'bg-primary/20 text-primary' : 'bg-white/5 text-slate-400'}`}>
                                                            {action.icon}
                                                        </div>
                                                        <span className={`text-sm font-medium ${isActive ? 'text-white' : 'text-slate-300'}`}>
                                                            {action.label}
                                                        </span>
                                                        {isActive && (
                                                            <ArrowRight size={14} className="ml-auto text-primary opacity-50" />
                                                        )}
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>

                        {/* Footer Hints */}
                        <div className="px-4 py-3 border-t border-white/5 bg-[#050505] flex items-center gap-4 text-[10px] font-bold uppercase tracking-widest text-slate-500">
                            <span className="flex items-center gap-1.5">
                                <span className="px-1.5 py-0.5 rounded border border-slate-700 bg-slate-800 text-slate-300 shadow-sm leading-none">↑</span>
                                <span className="px-1.5 py-0.5 rounded border border-slate-700 bg-slate-800 text-slate-300 shadow-sm leading-none">↓</span>
                                Navigate
                            </span>
                            <span className="flex items-center gap-1.5">
                                <span className="px-1.5 py-0.5 rounded border border-slate-700 bg-slate-800 text-slate-300 shadow-sm leading-none">↵</span>
                                Select
                            </span>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
}
