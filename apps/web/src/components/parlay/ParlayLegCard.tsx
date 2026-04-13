"use client";

import React from "react";
import { motion } from "framer-motion";
import { Trash2, AlertCircle, TrendingUp, Zap, PlusCircle } from "lucide-react";
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
    onAiAdd?: () => void;
    aiLoading?: boolean;
    index: number;
}

export const ParlayLegCard: React.FC<ParlayLegCardProps> = ({ leg, onRemove, onAiAdd, aiLoading, index }) => {
    return (
        <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            className="group relative bg-white/5 border border-white/5 rounded-xl p-3 hover:bg-white/10 hover:border-white/10 transition-all mb-3 last:mb-0"
        >
            <div className="flex justify-between items-start">
                <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                        <span className="text-[10px] font-black text-brand-primary uppercase tracking-widest leading-none">
                            {(leg.stat_category || "Prop").replace(/_/g, " ")}
                        </span>
                    </div>
                    <h4 className="text-xs font-black text-white uppercase italic tracking-tight mb-1">
                        {leg.player_name || "Unknown Player"}
                    </h4>
                    <div className="flex items-center gap-2">
                        <span className={clsx(
                            "text-[10px] font-bold px-1.5 py-0.5 rounded uppercase leading-none",
                            (leg.side || "Over").toLowerCase() === "over" ? "bg-brand-success/10 text-brand-success" : "bg-brand-danger/10 text-brand-danger"
                        )}>
                            {leg.side || "Over"} {leg.line || 0}
                        </span>
                        <span className="text-[10px] font-mono text-textMuted font-bold leading-none">
                            {leg.odds > 0 ? `+${leg.odds}` : leg.odds}
                        </span>
                    </div>
                </div>
                
                <div className="flex items-center gap-1">
                    {onAiAdd && (
                        <button
                            onClick={onAiAdd}
                            disabled={aiLoading}
                            className="p-2 text-brand-primary/40 hover:text-brand-primary transition-colors rounded-lg hover:bg-brand-primary/10"
                            title="Add AI Suggested Leg"
                        >
                            <PlusCircle size={12} className={aiLoading ? "animate-spin" : ""} />
                        </button>
                    )}
                    <button
                        onClick={() => onRemove(leg.prop_id)}
                        className="p-2 text-textMuted hover:text-brand-danger transition-colors rounded-lg hover:bg-brand-danger/10"
                        aria-label="Remove leg"
                    >
                        <Trash2 size={12} />
                    </button>
                </div>
            </div>
            
            {/* Hover Decorator */}
            <div className="absolute left-0 top-0 bottom-0 w-1 bg-brand-primary rounded-l-xl opacity-0 group-hover:opacity-100 transition-opacity" />
        </motion.div>
    );
};
