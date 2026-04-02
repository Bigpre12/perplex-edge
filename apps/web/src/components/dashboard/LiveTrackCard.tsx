"use client";

import { motion } from "framer-motion";
import { Activity, Target, ShieldAlert, TrendingUp, CheckCircle2, Clock } from "lucide-react";

interface LiveTrackCardProps {
    player: string;
    statType: string;
    currentValue: number;
    line: number;
    side: 'over' | 'under';
    gameStatus: string;
    hedgeRecommendation?: string;
    confidence?: number;
}

export default function LiveTrackCard({ 
    player, 
    statType, 
    currentValue, 
    line, 
    side, 
    gameStatus, 
    hedgeRecommendation,
    confidence 
}: LiveTrackCardProps) {
    const progress = Math.min((currentValue / line) * 100, 100);
    const isHit = (side === 'over' && currentValue >= line) || (side === 'under' && currentValue < line);

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            whileHover={{ y: -4 }}
            className="bg-lucrix-surface/40 backdrop-blur-xl border border-white/10 rounded-2xl p-6 relative overflow-hidden group shadow-2xl transition-all"
        >
            <div className="absolute top-0 right-0 p-4 relative z-10">
                <div className="flex items-center gap-2 bg-brand-purple/10 px-3 py-1 rounded-full border border-brand-purple/20 shadow-glow shadow-brand-purple/5">
                    <div className="size-1.5 bg-brand-purple rounded-full animate-pulse" />
                    <span className="text-[9px] font-black text-brand-purple uppercase tracking-widest">{gameStatus}</span>
                </div>
            </div>

            <div className="space-y-6 relative z-10">
                <div className="flex items-center gap-4">
                    <div className="p-3 bg-brand-purple/20 rounded-xl border border-brand-purple/30 shadow-glow shadow-brand-purple/10">
                        <Target className="text-brand-purple" size={24} />
                    </div>
                    <div>
                        <h4 className="text-base font-black text-white tracking-widest uppercase italic leading-tight mb-1">{player}</h4>
                        <div className="flex items-center gap-2 text-[10px] text-textMuted font-black uppercase tracking-widest italic">
                            <span>{statType}</span>
                            <span className="text-white/20">•</span>
                            <span className={side === 'over' ? "text-brand-success" : "text-brand-danger"}>{side.toUpperCase()} {line}</span>
                        </div>
                    </div>
                </div>

                <div className="space-y-3">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <Activity size={12} className="text-textMuted" />
                            <span className="text-[10px] font-black uppercase tracking-widest text-textSecondary italic">Quantum Track</span>
                        </div>
                        <div className="flex items-baseline gap-1">
                            <span className={`text-sm font-black italic ${isHit ? "text-brand-purple" : "text-white"}`}>{currentValue}</span>
                            <span className="text-[10px] text-textMuted font-black uppercase italic">/ {line}</span>
                        </div>
                    </div>
                    
                    <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden p-[1px] border border-white/5">
                        <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${progress}%` }}
                            transition={{ duration: 1.5, ease: "easeOut" }}
                            className={`h-full rounded-full transition-all relative ${isHit ? 'bg-brand-purple' : 'bg-brand-cyan'}`}
                        >
                            <div className="absolute inset-0 bg-gradient-to-r from-transparent to-white/30 animate-pulse" />
                        </motion.div>
                    </div>
                    
                    <div className="flex justify-between items-center text-[8px] font-black text-textMuted uppercase tracking-[0.2em] italic">
                        <span>Pace: {progress > 100 ? 'EXCEEDED' : 'TRACKING'}</span>
                        <span className={isHit ? "text-brand-success" : "text-brand-purple"}>
                            {isHit ? "HIT DETECTED" : `${Math.round(progress)}% COMPLETE`}
                        </span>
                    </div>
                </div>

                {hedgeRecommendation && (
                    <motion.div 
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="p-4 bg-brand-warning/10 border border-brand-warning/20 rounded-2xl flex items-center gap-4 group-hover:bg-brand-warning/15 transition-all shadow-glow shadow-brand-warning/5"
                    >
                        <div className="p-2 bg-brand-warning/20 rounded-lg">
                            <ShieldAlert size={18} className="text-brand-warning" />
                        </div>
                        <div>
                            <p className="text-[9px] font-black text-brand-warning uppercase tracking-widest leading-none mb-1 italic">Vulnerability Alert</p>
                            <p className="text-[10px] text-textSecondary font-black uppercase italic leading-tight">{hedgeRecommendation}</p>
                        </div>
                    </motion.div>
                )}

                <div className="flex items-center justify-between pt-2 border-t border-white/5">
                    <div className="flex items-center gap-3">
                        <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-white/5 border border-white/5">
                            <Clock size={10} className="text-textMuted" />
                            <span className="text-[8px] text-textMuted font-black uppercase tracking-widest">
                                Conf: {confidence != null ? Math.round(confidence * 100) : Math.round(progress)}%
                            </span>
                        </div>
                        {isHit && (
                            <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-brand-success/10 border border-brand-success/20">
                                <CheckCircle2 size={10} className="text-brand-success" />
                                <span className="text-[8px] text-brand-success font-black uppercase tracking-widest">In Range</span>
                            </div>
                        )}
                    </div>
                    <button className="text-[9px] font-black text-brand-purple hover:text-white transition-all uppercase tracking-widest px-3 py-1.5 bg-brand-purple/10 border border-brand-purple/20 rounded-lg hover:bg-brand-purple hover:shadow-glow hover:shadow-brand-purple/20 italic">
                        Core Stats →
                    </button>
                </div>
            </div>

            {/* Background Glow */}
            <div className={`absolute -right-10 -bottom-10 size-40 blur-[60px] rounded-full transition-colors duration-1000 ${isHit ? 'bg-brand-purple/10' : 'bg-brand-cyan/5'}`} />
        </motion.div>
    );
}
