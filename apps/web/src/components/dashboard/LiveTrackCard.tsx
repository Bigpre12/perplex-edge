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
            className="bg-lucrix-surface p-5 rounded-xl border border-lucrix-border relative overflow-hidden group hover:border-brand-purple/30 transition-colors shadow-card"
        >
            <div className="absolute top-0 right-0 p-3">
                <div className="flex items-center gap-1.5 bg-brand-purple/10 px-2 py-1 rounded-sm border border-brand-purple/20">
                    <div className="size-1.5 bg-brand-purple rounded-full animate-pulse shadow-glow shadow-brand-purple" />
                    <span className="text-[10px] font-black text-brand-purple uppercase">{gameStatus}</span>
                </div>
            </div>

            <div className="space-y-4">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-lucrix-elevated rounded-lg border border-lucrix-border">
                        <Target className="text-brand-purple" size={20} />
                    </div>
                    <div>
                        <h4 className="text-sm font-black text-white tracking-tight uppercase italic">{player}</h4>
                        <p className="text-[10px] text-textMuted font-bold uppercase tracking-wider">{statType} • {side.toUpperCase()} {line}</p>
                    </div>
                </div>

                <div className="space-y-2">
                    <div className="flex items-center justify-between text-[10px] font-black uppercase tracking-widest text-textSecondary">
                        <span>Progress</span>
                        <span className={isHit ? "text-brand-purple" : "text-white"}>{currentValue} / {line}</span>
                    </div>
                    <div className="h-2 w-full bg-lucrix-dark rounded-full overflow-hidden border border-lucrix-border">
                        <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${progress}%` }}
                            className={`h-full transition-all duration-1000 ${isHit ? 'bg-brand-purple' : 'bg-brand-cyan'}`}
                            style={{ boxShadow: isHit ? '0 0 10px rgba(168, 85, 247, 0.5)' : 'none' }}
                        />
                    </div>
                </div>

                {hedgeRecommendation && (
                    <div className="mt-4 p-3 bg-brand-warning/10 border border-brand-warning/20 rounded-lg flex items-center gap-3 group-hover:bg-brand-warning/15 transition-all">
                        <ShieldAlert size={16} className="text-brand-warning" />
                        <div>
                            <p className="text-[10px] font-black text-brand-warning uppercase tracking-tighter leading-none mb-1">Hedge Alert</p>
                            <p className="text-[10px] text-textSecondary font-medium leading-none">{hedgeRecommendation}</p>
                        </div>
                    </div>
                )}

                <div className="flex items-center justify-between pt-2">
                    <div className="flex items-center gap-2">
                        <Activity size={12} className="text-textMuted" />
                        <span className="text-[9px] text-textMuted font-black uppercase tracking-widest">Confidence: {Math.round(progress)}%</span>
                    </div>
                    <button className="text-[9px] font-black text-brand-purple hover:text-white transition-colors uppercase tracking-widest px-2 py-1 bg-brand-purple/10 border border-brand-purple/20 rounded-sm">
                        Detailed View →
                    </button>
                </div>
            </div>
        </motion.div>
    );
}
