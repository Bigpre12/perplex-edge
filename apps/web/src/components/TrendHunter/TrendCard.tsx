"use client";

import { motion } from 'framer-motion';
import { ArrowRight, Trophy, Zap, Info } from 'lucide-react';

interface TrendCardProps {
    trend: {
        id: string;
        player_name: string;
        player_image: string;
        stat_type: string;
        line: number;
        side: string;
        odds: number;
        edge: number;
        hit_rate: number;
        hits: number;
        total_games: number;
        avg_value: number;
        last_10_values: number[];
        matchup: {
            opponent: string;
            time: string;
        };
        sportsbook: string;
    };
}

export function TrendCard({ trend }: TrendCardProps) {
    const isHighEdge = trend.edge >= 8;
    const isFade = trend.hit_rate < 50;

    return (
        <motion.div
            layout
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="group bg-[#181B21] rounded-2xl shadow-xl border border-gray-800/50 overflow-hidden hover:border-gray-600 transition-all duration-300"
        >
            <div className="p-5">
                {/* Player Info & Edge Badge */}
                <div className="flex justify-between items-start mb-5">
                    <div className="flex items-center gap-3">
                        <div className="relative">
                            <img
                                src={trend.player_image}
                                alt={trend.player_name}
                                className="w-14 h-14 rounded-full object-cover border-2 border-gray-700 group-hover:border-primary transition-colors"
                            />
                            <div className="absolute -bottom-1 -right-1 bg-[#1F2937] rounded-full p-1 shadow-md border border-gray-800">
                                <Zap size={10} className="text-primary fill-primary" />
                            </div>
                        </div>
                        <div>
                            <h3 className="font-bold text-white text-lg leading-tight group-hover:text-primary transition-colors">
                                {trend.player_name}
                            </h3>
                            <p className="text-[11px] text-gray-500 font-bold uppercase tracking-wider mt-0.5">
                                vs {trend.matchup.opponent} • {trend.matchup.time}
                            </p>
                        </div>
                    </div>

                    <div className={`px-2.5 py-1 rounded-lg text-[10px] font-black uppercase tracking-tighter ${isFade
                            ? 'bg-red-500/10 text-red-500 border border-red-500/20'
                            : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shadow-[0_0_10px_rgba(16,185,129,0.1)]'
                        }`}>
                        {isFade ? 'Fade Rec' : `+${trend.edge}% Edge`}
                    </div>
                </div>

                {/* Market Summary & Hit Rate */}
                <div className="flex justify-between items-end mb-6">
                    <div>
                        <p className="text-[10px] text-gray-400 font-black uppercase tracking-widest mb-1.5 opacity-60">
                            {trend.stat_type}
                        </p>
                        <div className="flex items-baseline gap-2">
                            <span className="text-2xl font-black text-white italic tracking-tighter capitalize">
                                {trend.side} {trend.line}
                            </span>
                            <span className="text-sm font-bold text-gray-500">
                                {trend.odds > 0 ? `+${trend.odds}` : trend.odds}
                            </span>
                        </div>
                    </div>
                    <div className="text-right">
                        <div className={`text-4xl font-black italic tracking-tighter leading-none ${isFade ? 'text-red-500' : 'text-primary'
                            }`}>
                            {Math.round(trend.hit_rate)}%
                        </div>
                        <div className="text-[9px] text-gray-500 uppercase font-black tracking-widest mt-1">
                            Hit Rate ({trend.hits}/{trend.total_games})
                        </div>
                    </div>
                </div>

                {/* Bar Chart Visualization */}
                <div className="space-y-3">
                    <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-wider text-gray-500">
                        <span>Last 10 Performance</span>
                        <span className="text-gray-300">Avg: {trend.avg_value}</span>
                    </div>

                    <div className="flex items-end justify-between h-14 gap-1 px-1">
                        {trend.last_10_values.map((val, idx) => {
                            const isHit = val > trend.line;
                            // Calculate height percentage based on value relative to line
                            const height = Math.min(100, Math.max(20, (val / (trend.line * 1.5)) * 100));

                            return (
                                <div
                                    key={idx}
                                    className="flex-1 group/bar relative"
                                >
                                    <div
                                        style={{ height: `${height}%` }}
                                        className={`w-full rounded-t-sm transition-all duration-300 ${isHit
                                                ? 'bg-primary shadow-[0_0_5px_rgba(16,185,129,0.4)] group-hover/bar:brightness-125'
                                                : 'bg-gray-700/50 group-hover/bar:bg-gray-600'
                                            }`}
                                    />
                                    {/* Tooltip on hover */}
                                    <div className="absolute -top-6 left-1/2 -translate-x-1/2 bg-white text-black text-[8px] px-1 rounded opacity-0 group-hover/bar:opacity-100 font-bold transition-opacity whitespace-nowrap pointer-events-none">
                                        {val}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>

            {/* Footer with Bookie and Analyze */}
            <div className="px-5 py-3.5 bg-gray-900/40 border-t border-gray-800/50 flex justify-between items-center group-hover:bg-gray-900/60 transition-colors">
                <div className="flex items-center gap-3">
                    <span className="text-[9px] font-black uppercase tracking-widest text-gray-600 mr-1">Best At</span>
                    <div className="flex gap-2">
                        {trend.sportsbook.toLowerCase().includes('fanduel') ? (
                            <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuCn7EoY-gYbR7KO4udQSGkbU86LwpidUFHlxWiI-fGmrSNv33nEaJmHThEHFrqFMc2zbepxRF71_2_oO2cv7poIRGJ1uys4p1bLBw1aUuPToQ5eXnvA1sFPIeYtgs4GG40-agkqdIu8TjmqtSZ484sG3gWZVS8VM3N8OuW723Bz90g2pc7BDzRjYFfR-IOpCtSbpe552qUy5pyj94091zQbHt7JLOVW3pQsR5CUTKPlAxuR8tfEhYctrF2ZwWj5G0sdNKLQ8CAU6zbn" className="h-3 grayscale opacity-40 group-hover:grayscale-0 group-hover:opacity-100 transition-all" alt="FanDuel" />
                        ) : (
                            <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuBwp4I7AM4GKnYBRU5--iIEec98-SX5RrU5WlPv8h1MaBzII3SF2ZEJnHviywkEsts4n5w1G5Xi4Gsb7npxgDfSVsJbusjMOkpMuNvk-UMsei6i1_xPFe46X3vSCRgfM8EKBZT7ZGXmSTrQCYHBt5xPpZi-8Fd8AArfrqfsTPE-2wRXziwk_tKTHj2CHR-otuLK1jWU__eX5x71MWAMgEz1E_MPb6E04FANuy6UeK2MFg7zBubf9In231WufITmbXtaEDJDJRqu8TUM" className="h-3 grayscale opacity-40 group-hover:grayscale-0 group-hover:opacity-100 transition-all" alt="DraftKings" />
                        )}
                    </div>
                </div>

                <button className="flex items-center gap-1.5 text-primary text-[11px] font-black uppercase tracking-widest hover:gap-2.5 transition-all">
                    Analyze <ArrowRight size={12} />
                </button>
            </div>
        </motion.div>
    );
}
