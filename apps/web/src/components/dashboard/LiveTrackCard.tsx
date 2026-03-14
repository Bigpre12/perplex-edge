"use client";

import { motion } from "framer-motion";
import { Activity, Target, ShieldAlert, TrendingUp } from "lucide-react";

interface LiveTrackCardProps {
    player: string;
    statType: string;
    currentValue: number;
    line: number;
    side: 'over' | 'under';
    gameStatus: string;
    hedgeRecommendation?: string;
}

export default function LiveTrackCard({ player, statType, currentValue, line, side, gameStatus, hedgeRecommendation }: LiveTrackCardProps) {
    const progress = Math.min((currentValue / line) * 100, 100);
    const isHit = (side === 'over' && currentValue >= line) || (side === 'under' && currentValue < line);

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-premium p-5 rounded-2xl border-white/[0.08] relative overflow-hidden group"
        >
            <div className="absolute top-0 right-0 p-3">
                <div className="flex items-center gap-1.5 bg-primary/10 px-2 py-1 rounded-full border border-primary/20">
                    <div className="size-1.5 bg-primary rounded-full animate-pulse" />
                    <span className="text-[10px] font-black text-primary uppercase">{gameStatus}</span>
                </div>
            </div>

            <div className="space-y-4">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-white/[0.03] rounded-xl border border-white/[0.08]">
                        <Target className="text-primary" size={20} />
                    </div>
                    <div>
                        <h4 className="text-sm font-bold text-white tracking-tight">{player}</h4>
                        <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">{statType} • {side.toUpperCase()} {line}</p>
                    </div>
                </div>

                <div className="space-y-2">
                    <div className="flex items-center justify-between text-[10px] font-black uppercase tracking-widest text-slate-400">
                        <span>Progress</span>
                        <span className={isHit ? "text-primary" : "text-slate-200"}>{currentValue} / {line}</span>
                    </div>
                    <div className="h-2 w-full bg-white/[0.03] rounded-full overflow-hidden border border-white/[0.05]">
                        <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${progress}%` }}
                            className={`h-full transition-all duration-1000 ${isHit ? 'bg-primary' : 'bg-slate-400'}`}
                            style={{ boxShadow: isHit ? '0 0 10px rgba(13, 242, 51, 0.5)' : 'none' }}
                        />
                    </div>
                </div>

                {hedgeRecommendation && (
                    <div className="mt-4 p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl flex items-center gap-3 group-hover:bg-amber-500/15 transition-all">
                        <ShieldAlert size={16} className="text-amber-500" />
                        <div>
                            <p className="text-[10px] font-black text-amber-500 uppercase tracking-tighter">Hedge Alert</p>
                            <p className="text-[10px] text-slate-300 font-medium">{hedgeRecommendation}</p>
                        </div>
                    </div>
                )}

                <div className="flex items-center justify-between pt-2">
                    <div className="flex items-center gap-2">
                        <Activity size={14} className="text-slate-500" />
                        <span className="text-[10px] text-slate-500 font-bold uppercase">Confidence: {Math.round(progress)}%</span>
                    </div>
                    <button className="text-[10px] font-black text-primary hover:text-white transition-colors uppercase tracking-widest px-2 py-1">
                        Detailed View →
                    </button>
                </div>
            </div>
        </motion.div>
    );
}
