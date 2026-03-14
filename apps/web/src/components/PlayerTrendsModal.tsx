"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, TrendingUp, Activity, Crosshair, Brain } from "lucide-react";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts";
import { api, isApiError } from "@/lib/api";

export default function PlayerTrendsModal({ isOpen, onClose, propData }: any) {
    const [trendData, setTrendData] = useState<any[]>([]);
    const [aiConfidence, setAiConfidence] = useState<number | null>(null);
    const [loading, setLoading] = useState(false);

    const currentLine = parseFloat(propData?.line_value || propData?.line || 0);

    useEffect(() => {
        if (!isOpen || !propData) return;

        const fetchData = async () => {
            setLoading(true);
            try {
                const playerName = propData.player?.name || propData.player_name;
                const statType = propData.market?.stat_type || propData.stat_type;

                // Fetch real historical trends
                const res = await api.playerTrends(playerName, statType);
                const history = res?.history || [];
                setTrendData(history);

                // Fetch AI Prediction
                const mlData = await api.mlPredict({
                    player_name: playerName,
                    stat_type: statType,
                    line: currentLine,
                    recent_performance: history.map((h: any) => h.value)
                });

                if (!isApiError(mlData) && mlData.ai_confidence_score) {
                    setAiConfidence(mlData.ai_confidence_score);
                }
            } catch (err) {
                console.error("Trends Fetch Failed:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [isOpen, propData, currentLine]);

    if (!isOpen || !propData) return null;

    const hasEdge = (propData.edge || 0) > 0;

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-md"
                onClick={onClose}
            >
                <motion.div
                    initial={{ scale: 0.95, y: 20 }}
                    animate={{ scale: 1, y: 0 }}
                    exit={{ scale: 0.95, y: 20 }}
                    onClick={(e) => e.stopPropagation()}
                    className="w-full max-w-2xl bg-[#0D0D14] border border-white/5 rounded-3xl shadow-2xl overflow-hidden"
                >
                    {/* Header */}
                    <div className="p-6 border-b border-white/[0.05] flex justify-between items-start">
                        <div className="flex items-center gap-4">
                            <div className="w-16 h-16 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center font-black text-slate-700 text-2xl overflow-hidden relative">
                                {propData.player_image ? (
                                    <img src={propData.player_image} className="w-full h-full object-cover" alt="" />
                                ) : (
                                    (propData.player?.name || propData.player_name || 'P').split(' ').map((n: string) => n[0]).join('')
                                )}
                            </div>
                            <div>
                                <h2 className="text-2xl font-black text-white italic tracking-tighter uppercase">{propData.player?.name || propData.player_name || 'Player'}</h2>
                                <p className="text-[10px] font-black text-[#6B7280] uppercase tracking-widest mt-0.5">
                                    {propData.player?.team || propData.team} vs {propData.matchup?.opponent || propData.opponent}
                                </p>
                            </div>
                        </div>
                        <button onClick={onClose} className="p-2 hover:bg-white/5 rounded-full transition-colors text-[#6B7280] hover:text-white">
                            <X size={20} />
                        </button>
                    </div>

                    {/* Stats Row */}
                    <div className="grid grid-cols-3 divide-x divide-white/[0.05] border-b border-white/[0.05] bg-black/20">
                        <div className="p-6 text-center">
                            <p className="text-[9px] font-black text-[#6B7280] uppercase tracking-widest mb-1 flex items-center justify-center gap-1 leading-none"><Crosshair size={12} /> Target</p>
                            <p className="text-xl font-black text-white italic tracking-tighter leading-tight">{propData.side?.toUpperCase() || 'OVER'} {currentLine}</p>
                            <p className="text-[10px] font-bold text-[#6B7280] uppercase leading-tight">{propData.market?.stat_type || propData.stat_type}</p>
                        </div>
                        <div className="p-6 text-center">
                            <p className="text-[9px] font-black text-[#6B7280] uppercase tracking-widest mb-1 flex items-center justify-center gap-1 leading-none"><Brain size={12} className="text-primary" /> AI Conf.</p>
                            <p className="text-xl font-black text-primary italic tracking-tighter leading-tight">{aiConfidence ? `${aiConfidence}%` : '---'}</p>
                            <p className="text-[10px] font-bold text-[#6B7280] uppercase leading-tight">Monte Carlo</p>
                        </div>
                        <div className="p-6 text-center">
                            <p className="text-[9px] font-black text-[#6B7280] uppercase tracking-widest mb-1 flex items-center justify-center gap-1 leading-none"><TrendingUp size={12} /> Edge</p>
                            <p className="text-xl font-black text-white italic tracking-tighter leading-tight">{((propData.ev_percentage || propData.edge || 0)).toFixed(1)}%</p>
                            <p className="text-[10px] font-bold text-[#6B7280] uppercase leading-tight">EV Delta</p>
                        </div>
                    </div>

                    {/* Chart Area */}
                    <div className="p-8">
                        <div className="flex items-center justify-between mb-6">
                            <h3 className="text-[10px] font-black text-[#6B7280] uppercase tracking-[0.2em] italic">Historical Performance vs Market</h3>
                            {loading && <div className="animate-pulse flex items-center gap-2 text-[10px] font-black text-primary italic uppercase">
                                <Activity size={12} /> Syncing...
                            </div>}
                        </div>
                        <div className="h-64 w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={trendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                    <defs>
                                        <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#0df233" stopOpacity={0.2} />
                                            <stop offset="95%" stopColor="#0df233" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <XAxis dataKey="game" stroke="#1f2937" fontSize={9} tickLine={false} axisLine={false} />
                                    <YAxis stroke="#1f2937" fontSize={9} tickLine={false} axisLine={false} />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#0D0D14', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '12px', fontSize: '10px', color: '#fff' }}
                                        labelStyle={{ color: '#6B7280', fontWeight: 'bold', marginBottom: '4px' }}
                                    />
                                    <ReferenceLine y={currentLine} stroke="#f59e0b" strokeDasharray="3 3" />
                                    <Area
                                        type="monotone"
                                        dataKey="value"
                                        stroke="#0df233"
                                        strokeWidth={3}
                                        fillOpacity={1}
                                        fill="url(#colorValue)"
                                    />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                        <p className="text-[9px] font-black text-[#6B7280] uppercase tracking-widest text-center mt-6">Data audited via SportsDataIO Performance API</p>
                    </div>
                </motion.div>
            </motion.div>
        </AnimatePresence>
    );
}
