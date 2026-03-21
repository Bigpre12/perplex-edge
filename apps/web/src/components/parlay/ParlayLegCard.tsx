"use client";

import React from "react";
import { motion } from "framer-motion";
import { Trash2, AlertCircle, TrendingUp, Zap } from "lucide-react";
import { clsx } from "clsx";

interface Leg {
    prop_id: string;
    player_name: string;
    side: string;
    line: number;
    stat_category: string;
    odds: number;
    game_id?: string;
}

interface ParlayLegCardProps {
    leg: Leg;
    onRemove: (id: string) => void;
    index: number;
}

export const ParlayLegCard: React.FC<ParlayLegCardProps> = ({ leg, onRemove, index }) => {
    const isHighOdds = leg.odds >= 150 || leg.odds <= -150;
    
    return (
        <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            className="group relative bg-white/5 border border-white/5 rounded-xl p-3 hover:bg-white/10 hover:border-white/10 transition-all"
        >
            <div className="flex justify-between items-start">
                <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                        <span className="text-[10px] font-black text-brand-primary uppercase tracking-widest">
                            {leg.stat_category.replace(/_/g, " ")}
                        </span>
                    </div>
                    <h4 className="text-xs font-black text-white uppercase italic tracking-tight">
                        {leg.player_name}
                    </h4>
                    <div className="flex items-center gap-2 mt-1">
                        <span className={clsx(
                            "text-[10px] font-bold px-1.5 py-0.5 rounded uppercase",
                            leg.side.toLowerCase() === "over" ? "bg-brand-success/10 text-brand-success" : "bg-brand-danger/10 text-brand-danger"
                        )}>
                            {leg.side} {leg.line}
                        </span>
                        <span className="text-[10px] font-mono text-textMuted font-bold">
                            {leg.odds > 0 ? `+${leg.odds}` : leg.odds}
                        </span>
                    </div>
                </div>
                
                <button
                    onClick={() => onRemove(leg.prop_id)}
                    className="p-2 text-textMuted hover:text-brand-danger transition-colors rounded-lg hover:bg-brand-danger/10"
                    aria-label="Remove leg"
                >
                    <Trash2 size={12} />
                </button>
            </div>
            
            {/* Hover Decorator */}
            <div className="absolute left-0 top-0 bottom-0 w-1 bg-brand-primary rounded-l-xl opacity-0 group-hover:opacity-100 transition-opacity" />
        </motion.div>
    );
};
