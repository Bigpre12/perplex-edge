"use client";
import { TrendingUp, DollarSign, Activity, Zap } from "lucide-react";
import { motion } from "framer-motion";

interface SummaryProps {
    winRate: number;
    roi: number;
    gradedPicks: number;
    streak: string;
    loading?: boolean;
}

export function PerformanceSummary({ winRate, roi, gradedPicks, streak, loading }: SummaryProps) {
    const cards = [
        {
            label: "Win Rate",
            value: `${winRate}%`,
            icon: <TrendingUp className="text-emerald-400" size={20} />,
            trend: "accuracy",
            color: "emerald"
        },
        {
            label: "ROI",
            value: `${roi > 0 ? '+' : ''}${roi}%`,
            icon: <DollarSign className="text-blue-400" size={20} />,
            trend: "efficiency",
            color: "blue"
        },
        {
            label: "Graded Picks",
            value: String(gradedPicks),
            icon: <Activity className="text-purple-400" size={20} />,
            trend: "volume",
            color: "purple"
        },
        {
            label: "Current Streak",
            value: streak,
            icon: <Zap className="text-orange-400" size={20} />,
            trend: "momentum",
            color: "orange"
        }
    ];

    return (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {cards.map((card, i) => (
                <motion.div
                    key={card.label}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.1 }}
                    className="bg-lucrix-surface border border-lucrix-border p-5 rounded-2xl relative overflow-hidden group hover:border-white/20 transition-all shadow-card"
                >
                    <div className="flex justify-between items-start mb-4">
                        <div className={`p-2 bg-${card.color}-500/10 rounded-lg border border-${card.color}-500/20`}>
                            {card.icon}
                        </div>
                        <span className="text-[10px] font-black text-textMuted uppercase tracking-widest">{card.trend}</span>
                    </div>
                    
                    <div className="space-y-1">
                        <p className="text-xs text-textSecondary font-bold uppercase tracking-tight">{card.label}</p>
                        <h3 className={`text-2xl font-black text-white font-display ${loading ? 'animate-pulse opacity-40' : ''}`}>
                            {loading ? "—" : card.value}
                        </h3>
                    </div>

                    {/* Subtle Glow */}
                    <div className={`absolute -right-4 -bottom-4 w-16 h-16 bg-${card.color}-500/5 blur-2xl rounded-full group-hover:bg-${card.color}-500/10 transition-all`} />
                </motion.div>
            ))}
        </div>
    );
}
