"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Zap, TrendingDown, TrendingUp, Info, AlertTriangle, ArrowRight } from "lucide-react";
import { API, isApiError } from "@/lib/api";
import { useBackendStatus } from "@/hooks/useBackendStatus";
import { useFreshness } from '@/hooks/useFreshness';
import { FreshnessBadge } from './FreshnessBadge';
import { useSport } from "@/context/SportContext";

export function WhaleTracker({ sport: requestedSport }: { sport?: string }) {
    const { selectedSport } = useSport();
    const sport = requestedSport || selectedSport;
    const { data: freshness, isLoading: freshnessLoading } = useFreshness(sport);
    const [moves, setMoves] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const { isDown } = useBackendStatus();

    const fetchMoves = async () => {
        if (isDown) return;
        const result = await API.activeMoves(sport);

        if (!isApiError(result)) {
            const resultData = result as any;
            const data = Array.isArray(resultData) ? resultData : (resultData.data || resultData.items || []);
            
            const mappedMoves = data.map((m: any) => ({
                id: m.id || m.event_id || Math.random().toString(),
                player: m.player_name || m.home_team || 'N/A',
                stat: m.market_key || 'N/A',
                line: m.line,
                move_type: m.alert_type || "WHALE",
                delta: m.confidence || 0,
                severity: (m.confidence > 0.8) ? 'High' : 'Medium',
                books_involved: m.book ? [m.book] : ["Institutional"],
                whale_label: (m.confidence > 0.05) ? "MAX VALUE" : "SHARP MONEY",
                confidence: m.confidence || 0
            }));
            
            setMoves(mappedMoves);
        } else {
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
        <div className="bg-lucrix-surface/40 backdrop-blur-xl border border-white/10 rounded-3xl p-8 h-full flex flex-col shadow-2xl relative overflow-hidden group">
            {/* Background Decorator */}
            <div className="absolute top-0 right-0 w-64 h-64 -mr-32 -mt-32 bg-brand-orange/5 rounded-full blur-[100px] pointer-events-none" />
            
            <div className="flex items-center justify-between mb-8 relative z-10">
                <div className="flex items-center gap-4">
                    <div className="p-2.5 bg-brand-orange/20 rounded-xl border border-brand-orange/30 shadow-glow shadow-brand-orange/10">
                        <Zap className="text-brand-orange fill-brand-orange/20 animate-pulse" size={24} />
                    </div>
                    <div>
                        <h3 className="text-lg font-black italic tracking-tighter text-white uppercase leading-none mb-1">Whale Intel</h3>
                        <p className="text-[10px] text-textMuted font-black uppercase tracking-widest italic">Anomalous Volume Analytics</p>
                    </div>
                </div>
                <div className="hidden sm:flex flex-col items-end gap-1">
                    <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-brand-orange/10 border border-brand-orange/20">
                        <span className="flex h-1.5 w-1.5 rounded-full bg-brand-orange animate-pulse" />
                        <span className="text-[9px] font-black text-brand-orange uppercase tracking-widest">Live Monitor</span>
                    </div>
                    <div className="flex items-center gap-4">
                    <FreshnessBadge 
                        oddsTs={freshness?.last_odds_update || null} 
                        evTs={freshness?.last_ev_update || null}
                        isLoading={freshnessLoading}
                    />
                </div>
            </div>

            <div className="flex-1 space-y-4 overflow-y-auto pr-1 scrollbar-none relative z-10">
                <AnimatePresence mode="popLayout">
                    {loading ? (
                        <div className="h-full flex flex-col items-center justify-center gap-4 py-20">
                            <motion.div 
                                animate={{ rotate: 360 }}
                                transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
                                className="size-10 rounded-full border-t-2 border-brand-orange" 
                            />
                            <span className="text-[10px] text-textMuted font-black uppercase tracking-[0.2em] italic">Scanning Markets...</span>
                        </div>
                    ) : (moves || []).length > 0 ? (
                        moves.map((move, i) => (
                            <motion.div
                                key={move.id}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: i * 0.05 }}
                                className="p-5 bg-white/5 border border-white/5 rounded-2xl hover:border-brand-orange/30 hover:bg-white/10 transition-all group/item cursor-pointer relative overflow-hidden"
                            >
                                <div className="flex justify-between items-start mb-3 relative z-10">
                                    <div className="flex items-center gap-2">
                                        <div className={`px-2 py-0.5 rounded-md text-[8px] font-black tracking-widest uppercase border ${move.severity === 'High' ? 'bg-brand-danger/20 border-brand-danger/30 text-brand-danger' : 'bg-brand-orange/20 border-brand-orange/30 text-brand-orange'}`}>
                                            {move.move_type}
                                        </div>
                                        {move.confidence !== undefined && (
                                            <div className="px-2 py-0.5 rounded-md text-[8px] font-black tracking-widest uppercase border border-white/10 bg-white/5 text-textMuted">
                                                {move.confidence != null ? `${(Number(move.confidence) * 100).toFixed(1)}%` : "0.0%"} TRUST LEVEL
                                            </div>
                                        )}
                                    </div>
                                    <div className="text-[9px] font-black text-brand-orange italic uppercase tracking-widest bg-brand-orange/10 px-2 py-0.5 rounded-full">
                                        {move.whale_label}
                                    </div>
                                </div>

                                <div className="flex items-end justify-between relative z-10">
                                    <div className="space-y-1">
                                        <h4 className="text-base font-black text-white tracking-widest uppercase italic group-hover/item:text-brand-orange transition-colors">{move.player}</h4>
                                        <div className="flex items-center gap-2 text-[10px] text-textMuted font-black uppercase tracking-widest italic font-display">
                                            <span>{(move.stat || "N/A").replace('player_', '').replace('_', ' ')}</span>
                                            {move.line ? (
                                                <>
                                                    <ArrowRight size={10} className="text-white/20" />
                                                    <span className="text-white">@ {move.line}</span>
                                                </>
                                            ) : (
                                                <>
                                                    <ArrowRight size={10} className="text-white/20" />
                                                    <span className="text-white">N/A</span>
                                                </>
                                            )}
                                        </div>
                                    </div>
                                    <div className="flex -space-x-2">
                                        {(move.books_involved || []).slice(0, 3).map((book: string, idx: number) => (
                                            <div 
                                                key={idx} 
                                                className="size-7 rounded-full bg-lucrix-dark border border-white/10 flex items-center justify-center text-[8px] font-black text-white ring-2 ring-lucrix-surface uppercase shadow-2xl relative z-10"
                                            >
                                                {book[0]}
                                            </div>
                                        ))}
                                        {move.books_involved?.length > 3 && (
                                            <div className="size-7 rounded-full bg-brand-orange/20 border border-brand-orange/30 flex items-center justify-center text-[8px] font-black text-brand-orange ring-2 ring-lucrix-surface uppercase z-0">
                                                +{move.books_involved.length - 3}
                                            </div>
                                        )}
                                    </div>
                                </div>

                                {/* Item Glow */}
                                <div className="absolute inset-y-0 left-0 w-1 bg-brand-orange opacity-0 group-hover/item:opacity-100 transition-opacity" />
                            </motion.div>
                        ))
                    ) : (
                        <div className="flex flex-col items-center justify-center py-20 text-center gap-4 opacity-50 grayscale hover:grayscale-0 transition-all duration-500">
                            <div className="p-4 bg-white/5 rounded-full">
                                <TrendingUp size={32} className="text-textMuted" />
                            </div>
                            <p className="text-[10px] font-black text-textSecondary uppercase tracking-[0.3em] italic">Awaiting Whale Signals...</p>
                        </div>
                    )}
                </AnimatePresence>
            </div>

            <div className="mt-8 pt-6 border-t border-white/5 flex items-center justify-between relative z-10">
                <div className="flex items-center gap-3">
                    <div className="p-1.5 bg-brand-orange/10 rounded-lg">
                        <AlertTriangle size={14} className="text-brand-orange" />
                    </div>
                    <span className="text-[9px] text-textMuted font-black uppercase tracking-widest italic max-w-[200px] leading-tight">
                        Pinnacle split detected in {sport.split('_').pop()?.toUpperCase()} — <span className="text-white">High Variance Expected</span>
                    </span>
                </div>
                <div className="text-[8px] text-white/20 font-black uppercase tracking-[0.2em]">Institutional-Grade Feed</div>
            </div>
        </div>
    );
}
