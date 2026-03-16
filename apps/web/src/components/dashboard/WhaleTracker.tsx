"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Zap, TrendingDown, TrendingUp, Info, AlertTriangle } from "lucide-react";
import { API, isApiError } from "@/lib/api";
import { useBackendStatus } from "@/hooks/useBackendStatus";
import { SportKey } from "@/lib/sports.config";

interface WhaleMove {
    id: string;
    player: string;
    stat: string;
    line: number;
    move_type: string;
    delta: number;
    severity: string;
    books_involved: string[];
    whale_label?: string;
    confidence?: number;
}

import { useFreshness } from '@/hooks/useFreshness';
import { FreshnessBadge } from './FreshnessBadge';

export function WhaleTracker({ sport = "basketball_nba" }: { sport?: string }) {
    const freshness = useFreshness(sport);
    const [moves, setMoves] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const { isDown } = useBackendStatus();

    const fetchMoves = async () => {
        if (isDown) return;
        const result = await API.activeMoves(sport);

        if (!isApiError(result)) {
            const resultData = result as any;
            // Handle both object with data/items and raw array
            const data = Array.isArray(resultData) ? resultData : (resultData.data || resultData.items || []);
            
            // Map legacy/model fields to WhaleMove schema if needed
            const mappedMoves = data.map((m: any) => ({
                id: m.id || m.event_id || Math.random().toString(),
                player: m.player_name || m.player || "Unknown",
                stat: m.stat_type || "Market",
                line: m.line || 0,
                move_type: m.side || m.move_type || "WHALE",
                delta: m.delta || m.ev_percentage || 0,
                severity: m.severity || (m.confidence_score > 80 ? 'High' : 'Medium'),
                books_involved: m.books_involved || [m.book || "Institutional"],
                whale_label: m.whale_label || (m.expected_value > 5 ? "MAX VALUE" : "SHARP MONEY"),
                confidence: m.confidence_score || m.confidence || 0
            }));
            
            setMoves(mappedMoves);
        } else {
            console.warn('Whale tracker unavailable:', result.message);
            setMoves([]);
        }
        setLoading(false);
    };

    useEffect(() => {
        fetchMoves();
        const interval = setInterval(() => {
            if (!isDown) fetchMoves();
        }, 60000);
        return () => clearInterval(interval);
    }, [isDown, sport]);

    return (
        <div className="bg-lucrix-surface p-5 rounded-xl border border-lucrix-border h-full flex flex-col shadow-card">
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-brand-orange/10 rounded-lg border border-brand-orange/20">
                        <Zap className="text-brand-orange fill-brand-orange/20" size={20} />
                    </div>
                    <div className="flex flex-col">
                        <h3 className="text-lg font-bold tracking-tight text-white/90 font-display uppercase italic">Whale Intel</h3>
                        <p className="text-[10px] text-textMuted font-bold uppercase tracking-widest leading-none mb-1">Sharp Money Detection</p>
                        <FreshnessBadge 
                            oddsTs={freshness?.odds_last_updated || null} 
                            evTs={freshness?.ev_last_updated || null} 
                        />
                    </div>
                </div>
                <div className="flex items-center gap-1.5 bg-brand-orange/10 px-2 py-1 rounded-sm border border-brand-orange/20">
                    <div className="size-1.5 bg-brand-orange rounded-full animate-pulse shadow-glow shadow-brand-orange" />
                    <span className="text-[10px] font-black text-brand-orange uppercase tracking-tighter">LIVE MONITOR</span>
                </div>
            </div>

            <div className="flex-1 space-y-3 overflow-y-auto pr-1 scrollbar-none">
                {loading ? (
                    <div className="h-full flex flex-col items-center justify-center gap-3 py-10">
                        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-brand-orange" />
                        <span className="text-[10px] text-textMuted font-black uppercase tracking-widest">Scanning Markets...</span>
                    </div>
                ) : (moves || []).length > 0 ? (
                    moves.map((move, i) => (
                        <motion.div
                            key={move.id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: i * 0.1 }}
                            className="p-4 bg-lucrix-dark/50 border border-lucrix-border rounded-lg hover:border-brand-orange/30 hover:bg-lucrix-dark transition-all group cursor-pointer relative overflow-hidden"
                        >
                            <div className="flex justify-between items-start mb-2 relative z-10">
                                <div className="flex items-center gap-2">
                                    <span className={`text-[9px] font-black px-1.5 py-0.5 rounded-sm tracking-tighter uppercase ${move.severity === 'High' ? 'bg-brand-danger/10 text-brand-danger border border-brand-danger/20' : 'bg-brand-orange/10 text-brand-orange border border-brand-orange/20'}`}>
                                        {move.move_type}
                                    </span>
                                    {move.confidence && (
                                        <span className="text-[9px] text-textSecondary font-black border border-lucrix-border bg-lucrix-dark px-1.5 rounded-sm">
                                            {move.confidence}% CONF
                                        </span>
                                    )}
                                </div>
                                <div className="text-[9px] font-black text-brand-orange italic uppercase">
                                    {move.whale_label}
                                </div>
                            </div>

                            <div className="flex items-end justify-between relative z-10">
                                <div className="space-y-0.5">
                                    <h4 className="text-sm font-black text-white tracking-tight uppercase italic">{move.player}</h4>
                                    <p className="text-[10px] text-textMuted font-bold uppercase tracking-tight font-display">
                                        {move.stat.replace('player_', '').replace('_', ' ')} <span className="text-textSecondary">@{move.line}</span>
                                    </p>
                                </div>
                                <div className="flex -space-x-1.5">
                                    {(move.books_involved || []).slice(0, 3).map((book: string, idx: number) => (
                                        <div key={idx} className="size-5 rounded-full bg-lucrix-elevated border border-lucrix-border flex items-center justify-center text-[7px] font-black text-textSecondary ring-2 ring-lucrix-surface uppercase shadow-sm">
                                            {book[0]}
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {move.severity === 'High' && (
                                <div className="absolute -right-2 -bottom-2 w-12 h-12 bg-brand-danger/5 blur-xl rounded-full" />
                            )}
                        </motion.div>
                    ))
                ) : (
                    <div className="flex flex-col items-center justify-center py-12 text-center gap-2 opacity-80">
                        <TrendingUp size={24} className="text-textMuted" />
                        <p className="text-[10px] font-black text-textSecondary uppercase tracking-[0.2em]">Monitoring Sharp Books</p>
                    </div>
                )}
            </div>

            <div className="mt-4 pt-4 border-t border-lucrix-border flex items-center gap-2 text-[10px] text-textMuted font-black uppercase tracking-tight">
                <AlertTriangle size={12} className="text-brand-orange" />
                <span>Pinnacle split detected in {sport.split('_').pop()?.toUpperCase()}</span>
            </div>
        </div>
    );
}
