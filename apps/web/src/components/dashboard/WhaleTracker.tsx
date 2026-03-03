"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Zap, TrendingDown, TrendingUp, Info, AlertTriangle } from "lucide-react";

interface WhaleMove {
    id: number;
    player: string;
    stat: string;
    line: number;
    move_type: string;
    delta: number;
    severity: string;
    books_involved: string[];
}

import { API_BASE_URL } from "@/lib/apiConfig";

export default function WhaleTracker() {
    const [moves, setMoves] = useState<WhaleMove[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchMoves = async () => {
            try {
                const res = await fetch(`${API_BASE_URL}/api/whale/active-moves`);
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                const json = await res.json();
                setMoves(json.data || []);
            } catch (err) {
                console.warn('Whale tracker unavailable:', err);
                setMoves([]); // Fail silently
            } finally {
                setLoading(false);
            }
        };
        fetchMoves();
        const interval = setInterval(fetchMoves, 30000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="glass-panel p-5 rounded-2xl border-white/[0.05] h-full flex flex-col">
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-accent-orange/10 rounded-xl border border-accent-orange/20">
                        <Zap className="text-accent-orange fill-accent-orange/20" size={20} />
                    </div>
                    <div>
                        <h3 className="text-sm font-black text-white uppercase tracking-tight">Whale Intelligence</h3>
                        <p className="text-[10px] text-slate-500 font-bold">Sharp Market Steam Detection</p>
                    </div>
                </div>
                <div className="flex items-center gap-1.5 bg-accent-orange/10 px-2 py-1 rounded-lg border border-accent-orange/20">
                    <div className="size-1.5 bg-accent-orange rounded-full animate-ping" />
                    <span className="text-[10px] font-black text-accent-orange uppercase tracking-tighter">LIVE FEED</span>
                </div>
            </div>

            <div className="flex-1 space-y-3 overflow-y-auto pr-1 scrollbar-hide">
                {loading ? (
                    <div className="h-full flex items-center justify-center">
                        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-accent-orange" />
                    </div>
                ) : (moves || []).map((move, i) => (
                    <motion.div
                        key={move.id}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.1 }}
                        className="p-3 bg-white/[0.02] border border-white/[0.05] rounded-xl hover:border-accent-orange/30 hover:bg-white/[0.04] transition-all group cursor-pointer"
                    >
                        <div className="flex justify-between items-start mb-2">
                            <div className="flex items-center gap-2">
                                <span className={`text-[10px] font-black px-1.5 py-0.5 rounded ${move.severity === 'High' ? 'bg-red-500/20 text-red-500' : 'bg-accent-orange/20 text-accent-orange'} uppercase tracking-tighter`}>
                                    {move.move_type}
                                </span>
                                <span className="text-[10px] text-slate-500 font-mono">14s ago</span>
                            </div>
                            <div className="flex items-center gap-1 text-[10px] font-black">
                                {move.delta < 0 ? <TrendingDown size={14} className="text-red-500" /> : <TrendingUp size={14} className="text-primary" />}
                                <span className={move.delta < 0 ? "text-red-500" : "text-primary"}>{move.delta > 0 ? '+' : ''}{move.delta}</span>
                            </div>
                        </div>

                        <div className="flex items-end justify-between">
                            <div>
                                <h4 className="text-xs font-bold text-white tracking-tight">{move.player}</h4>
                                <p className="text-[10px] text-slate-500 font-medium">{move.stat} • {move.line}</p>
                            </div>
                            <div className="flex -space-x-1.5">
                                {(move.books_involved || []).slice(0, 3).map((book, idx) => (
                                    <div key={idx} className="size-4 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-[6px] font-black text-slate-300 ring-2 ring-background-dark">
                                        {book[0]}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </motion.div>
                ))}
            </div>

            <div className="mt-4 pt-4 border-t border-white/[0.05] flex items-center gap-2 text-[10px] text-slate-500 font-medium">
                <AlertTriangle size={12} className="text-accent-orange" />
                <span>High volatility detected in NBA markets</span>
            </div>
        </div>
    );
}
