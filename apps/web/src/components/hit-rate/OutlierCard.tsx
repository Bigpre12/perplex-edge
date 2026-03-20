"use client";
import { motion } from "framer-motion";
import { Zap, Flame, TrendingUp, TrendingDown, Minus, Award } from "lucide-react";

interface OutlierCardProps {
    data: {
        player_name: string;
        team: string;
        sport: string;
        market: string;
        line: number;
        hit_rate: number;
        hits: number;
        total: number;
        streak: number;
        trend: "up" | "down" | "stable";
        results: boolean[];
        confidence: "limited" | "early" | "reliable" | "high";
        book_line?: number;
    };
}

export function OutlierCard({ data }: OutlierCardProps) {
    const isElite = data.hit_rate >= 90;
    const isHigh = data.hit_rate >= 80;

    const trendIcon = {
        up: <TrendingUp size={14} className="text-brand-success" />,
        down: <TrendingDown size={14} className="text-brand-warning" />,
        stable: <Minus size={14} className="text-textMuted" />
    }[data.trend];

    const confidenceStyles = {
        high: "bg-brand-success/10 text-brand-success border-brand-success/30",
        reliable: "bg-brand-cyan/10 text-brand-cyan border-brand-cyan/30",
        early: "bg-brand-warning/10 text-brand-warning border-brand-warning/30",
        limited: "bg-white/5 text-textMuted border-white/10"
    }[data.confidence];

    return (
        <motion.div
            whileHover={{ y: -4, scale: 1.02 }}
            className={`relative p-5 rounded-2xl border transition-all duration-300 group
                ${isElite ? 'bg-gradient-to-br from-yellow-500/10 to-transparent border-yellow-500/40 shadow-lg shadow-yellow-500/5' : 
                  isHigh ? 'bg-gradient-to-br from-brand-success/10 to-transparent border-brand-success/30' : 
                  'bg-lucrix-surface border-lucrix-border hover:border-lucrix-borderBright'}`}
        >
            {/* Elite Badge */}
            {isElite && (
                <div className="absolute -top-3 -right-3 bg-yellow-500 text-black px-2 py-1 rounded-lg text-[10px] font-black uppercase flex items-center gap-1 shadow-xl">
                    <Award size={12} /> Elite Outlier
                </div>
            )}

            <div className="flex justify-between items-start mb-4">
                <div className="space-y-0.5">
                    <div className="flex items-center gap-2">
                        <span className="text-[10px] font-black uppercase tracking-widest text-textMuted bg-white/5 px-1.5 py-0.5 rounded-sm">
                            {data.sport.replace('_', ' ')}
                        </span>
                        <span className="text-xs text-textSecondary font-bold">{data.team}</span>
                    </div>
                    <h3 className="text-xl font-display font-black text-white group-hover:text-brand-cyan transition-colors truncate max-w-[180px]">
                        {data.player_name}
                    </h3>
                </div>
                <div className="text-right">
                    <div className={`text-3xl font-black italic font-display leading-none ${isElite ? 'text-yellow-400' : isHigh ? 'text-brand-success' : 'text-brand-cyan'}`}>
                        {data.hit_rate}%
                    </div>
                    <div className="text-[10px] text-textMuted uppercase font-black mt-1">
                        {data.hits} OF LAST {data.total}
                    </div>
                </div>
            </div>

            <div className="space-y-4">
                <div className="flex items-center justify-between">
                    <div className="text-sm font-bold text-gray-300">
                        {data.market} <span className="text-white">O{data.line}</span>
                    </div>
                    <div className="flex gap-1">
                        {data.results.slice(0, 10).map((hit, i) => (
                            <div 
                                key={i}
                                className={`size-1.5 rounded-full ${hit ? 'bg-brand-success shadow-glow-sm shadow-brand-success' : 'bg-brand-danger/40'}`}
                            />
                        )).reverse()}
                    </div>
                </div>

                <div className="pt-4 border-t border-white/5 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-1.5">
                            {trendIcon}
                            <span className="text-[10px] font-black uppercase text-textMuted tracking-wider">{data.trend}</span>
                        </div>
                        {data.streak >= 3 && (
                            <div className="flex items-center gap-1 text-orange-500">
                                <Flame size={14} />
                                <span className="text-[10px] font-black uppercase tracking-wider">{data.streak} STREAK</span>
                            </div>
                        )}
                    </div>
                    <span className={`px-2 py-0.5 rounded-sm border text-[9px] font-black uppercase tracking-widest ${confidenceStyles}`}>
                        {data.confidence}
                    </span>
                </div>
            </div>

            {/* Background Accent */}
            <div className={`absolute bottom-0 right-0 p-1 opacity-10 transition-opacity group-hover:opacity-20`}>
                <Zap size={64} className={isElite ? 'text-yellow-500' : 'text-brand-cyan'} />
            </div>
        </motion.div>
    );
}
