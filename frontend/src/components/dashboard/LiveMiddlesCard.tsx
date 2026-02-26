"use client";

import { motion } from "framer-motion";
import { Zap, Scale, Target } from "lucide-react";

interface LiveMiddle {
    id: string;
    match: string;
    book_a: { name: string; odds: string; line: string };
    book_b: { name: string; odds: string; line: string };
    middle_width: number;
    ev_percent: number;
    status: string;
}

interface LiveMiddlesCardProps {
    middle: LiveMiddle;
    index: number;
}

export default function LiveMiddlesCard({ middle, index }: LiveMiddlesCardProps) {
    const isPro = middle.ev_percent > 0;

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="flex flex-col justify-between p-4 rounded-xl bg-gradient-to-br from-surface to-surface-highlight border border-slate-700/50 hover:border-primary/50 transition-all duration-300 shadow-lg group relative overflow-hidden"
        >
            {/* Background Glow Effect */}
            <div className="absolute -inset-1 bg-gradient-to-r from-primary/10 via-transparent to-accent-blue/10 rounded-xl blur-lg group-hover:blur-xl transition-all opacity-0 group-hover:opacity-100 mix-blend-overlay"></div>

            {/* Header / Match Title */}
            <div className="flex justify-between items-start mb-4 relative z-10">
                <div className="flex items-center gap-2">
                    <div className="p-1.5 rounded-lg bg-surface border border-slate-700">
                        <Scale size={16} className={isPro ? "text-primary" : "text-accent-orange"} />
                    </div>
                    <div>
                        <h4 className="text-sm font-bold text-white truncate max-w-[200px]">{middle.match}</h4>
                        <span className="text-[10px] text-slate-400 font-mono tracking-wider">{middle.status}</span>
                    </div>
                </div>
                <div className={`px-2 py-1 rounded text-xs font-bold font-mono tracking-wide flex items-center gap-1 ${isPro ? "bg-primary/10 text-primary border border-primary/20" : "bg-accent-orange/10 text-accent-orange border border-accent-orange/20"}`}>
                    <Zap size={12} className={isPro ? "animate-pulse" : ""} />
                    {isPro ? "+" : ""}{middle.ev_percent}% EV
                </div>
            </div>

            {/* Middle Configuration */}
            <div className="grid grid-cols-2 gap-2 relative z-10">
                <div className="bg-black/30 rounded-lg p-2 border border-white/5 flex flex-col items-center justify-center text-center group-hover:bg-black/40 transition-colors">
                    <span className="text-[10px] text-slate-500 uppercase font-black tracking-widest leading-tight">{middle.book_a.name}</span>
                    <span className="text-sm font-bold text-white">{middle.book_a.line}</span>
                    <span className="text-xs text-primary font-mono">{middle.book_a.odds}</span>
                </div>
                <div className="bg-black/30 rounded-lg p-2 border border-white/5 flex flex-col items-center justify-center text-center group-hover:bg-black/40 transition-colors">
                    <span className="text-[10px] text-slate-500 uppercase font-black tracking-widest leading-tight">{middle.book_b.name}</span>
                    <span className="text-sm font-bold text-white">{middle.book_b.line}</span>
                    <span className="text-xs text-accent-blue font-mono">{middle.book_b.odds}</span>
                </div>
            </div>

            {/* Middle Width Footer */}
            <div className="mt-4 pt-3 border-t border-slate-700/50 flex justify-between items-center relative z-10">
                <span className="text-[10px] text-slate-400 tracking-wider">MIDDLE WINDOW</span>
                <span className="text-sm font-black text-white flex items-center gap-1">
                    <Target size={14} className="text-accent-blue" />
                    {middle.middle_width} Points
                </span>
            </div>
        </motion.div>
    );
}
