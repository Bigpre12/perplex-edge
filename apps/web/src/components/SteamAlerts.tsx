"use client";

import React from 'react';
import { API } from '@/lib/api';
import { SportKey } from '@/lib/sports.config';
import { useLiveData } from '@/hooks/useLiveData';
import { TrendingUp, Flame, Clock, Radio, Activity, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { clsx } from 'clsx';
import { formatDistanceToNow } from 'date-fns';

export function SteamAlerts({ sport }: { sport: SportKey }) {
    const { data: alertsData, loading } = useLiveData(
        () => API.steamAlerts(sport),
        [sport],
        { refreshInterval: 15000 }
    );

    const alerts = Array.isArray(alertsData) ? alertsData : (alertsData as any)?.alerts || [];

    if (loading && alerts.length === 0) {
        return (
            <div className="space-y-4">
                {[...Array(3)].map((_, i) => (
                    <div key={i} className="h-24 bg-white/5 rounded-2xl animate-pulse border border-white/5" />
                ))}
            </div>
        );
    }

    return (
        <div className="bg-lucrix-surface/40 backdrop-blur-xl border border-white/10 rounded-2xl overflow-hidden shadow-2xl flex flex-col h-full min-h-[500px]">
            {/* High-Voltage Header */}
            <div className="bg-gradient-to-r from-orange-600/20 to-transparent p-5 border-b border-white/10 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-orange-500 rounded-lg shadow-glow shadow-orange-500/20">
                        <Flame size={20} className="text-white fill-white" />
                    </div>
                    <div>
                        <h3 className="font-black text-white uppercase italic tracking-tighter text-lg leading-tight">Live Steam</h3>
                        <div className="flex items-center gap-1.5 mt-0.5">
                            <span className="flex h-2 w-2 rounded-full bg-orange-500 animate-pulse" />
                            <p className="text-[10px] font-black text-orange-400 uppercase tracking-widest">Market Pressure Detect</p>
                        </div>
                    </div>
                </div>
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10">
                    <Radio size={12} className="text-brand-success animate-pulse" />
                    <span className="text-[9px] font-black text-white uppercase tracking-widest">Real-Time</span>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto custom-scrollbar p-1">
                <AnimatePresence mode="popLayout">
                    {alerts.length === 0 ? (
                        <motion.div 
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="p-12 text-center"
                        >
                            <AlertCircle size={32} className="mx-auto text-white/10 mb-4" />
                            <p className="text-[10px] text-textMuted font-black uppercase tracking-widest leading-relaxed">
                                Scanning Global Markets...<br />No Volatility Spikes Found
                            </p>
                        </motion.div>
                    ) : (
                        <div className="p-3 space-y-3">
                            {alerts.map((alert: any, idx: number) => (
                                <motion.div 
                                    key={alert.id || idx}
                                    initial={{ opacity: 0, x: -10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, scale: 0.95 }}
                                    transition={{ duration: 0.3 }}
                                    className="relative group p-4 rounded-xl bg-lucrix-dark/40 border border-white/5 hover:border-orange-500/30 hover:bg-white/5 transition-all cursor-crosshair"
                                >
                                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-orange-500 to-transparent rounded-l-xl opacity-50 group-hover:opacity-100 transition-opacity" />
                                    
                                    <div className="flex justify-between items-start mb-2">
                                        <span className="text-[9px] font-black uppercase tracking-widest px-2 py-0.5 rounded-md bg-orange-500/10 text-orange-400 border border-orange-500/20">
                                            {alert.severity || 'LINE STEAM'}
                                        </span>
                                        <div className="flex items-center gap-1.5 text-[9px] font-bold text-textMuted uppercase">
                                            <Clock size={10} />
                                            {alert.time_ago || 'JUST NOW'}
                                        </div>
                                    </div>
                                    
                                    <div className="text-sm font-black text-white italic uppercase tracking-tight mb-2 group-hover:text-orange-400 transition-colors">
                                        {alert.message || `${alert.player_name}: Moved ${alert.line_start} → ${alert.line_current}`}
                                    </div>
                                    
                                    <div className="flex items-center justify-between mt-3">
                                        <div className="flex items-center gap-2 bg-white/5 px-2 py-1 rounded-md">
                                            <Activity size={10} className="text-brand-success" />
                                            <span className="text-[10px] text-white/50 font-black uppercase tracking-widest">
                                                {alert.books_count || 12} SHARP BOOKS IN SYNC
                                            </span>
                                        </div>
                                        <div className="text-[9px] font-black text-orange-400 uppercase tracking-widest animate-pulse">
                                            🔥 HEAVY DEPTH
                                        </div>
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    )}
                </AnimatePresence>
            </div>

            {/* Visual Pressure Meter */}
            <div className="p-4 bg-lucrix-dark/60 backdrop-blur-md border-t border-white/10 flex flex-col gap-3">
                <div className="flex justify-between items-center">
                    <p className="text-[10px] text-textMuted font-black uppercase tracking-widest">Market Convergence</p>
                    <span className="text-[10px] font-black text-orange-400 uppercase tracking-widest italic">Critical Level</span>
                </div>
                <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden flex gap-1">
                    {[1, 2, 3, 4, 5, 6, 7, 8].map(i => (
                        <motion.div 
                            key={i} 
                            animate={{ opacity: [0.3, 1, 0.3] }}
                            transition={{ duration: 1.5, delay: i * 0.1, repeat: Infinity }}
                            className={clsx(
                                "h-full flex-1 rounded-full",
                                i <= 6 ? 'bg-orange-500 shadow-glow shadow-orange-500/40' : 'bg-white/10'
                            )}
                        />
                    ))}
                </div>
            </div>
        </div>
    );
}
