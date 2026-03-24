'use client';

import React from 'react';
import { useLucrixStore } from "@/store";
import { SPORTSBOOKS } from '@/lib/sportsbooks.config';
import Sparkline from '../Sparkline';
import { StreakBadge } from '../StreakBadge';

export interface PropData {
    id: string;
    player_name: string;
    team: string;
    stat_type: string;
    line: number;
    side: 'over' | 'under';
    odds: number;
    grade: 'S' | 'A' | 'B' | 'C' | 'Elite' | 'Good';
    hit_rates: {
        total: number;
        l5: number;
        l10: number;
        l20: number;
    };
    books: Record<string, { over: number; under: number }>;
    is_sharp: boolean;
    steam_score: number;
    ev_percent: number;
}

export function PropCard({ prop }: { prop: PropData }) {
    const { addLeg, favoriteProps, toggleFavProp } = useLucrixStore();
    const isFav = favoriteProps.includes(prop.id);

    const gradeColors: Record<string, string> = {
        S: '#00ff88', // brand-success
        A: '#88ff00',
        B: '#ffcc00', // brand-warning
        C: '#ff8800', // brand-orange
        Elite: '#00ff88',
        Good: '#88ff00'
    };

    const getGradeLabel = (g: string) => (g === 'S' || g === 'Elite') ? 'S' : (g === 'A' || g === 'Good') ? 'A' : g;

    return (
        <div className={`group relative prop-card ${prop.is_sharp ? 'ring-1 ring-brand-cyan/30' : ''}`}>
            {/* Header: Player & Grade */}
            <div className="flex justify-between items-start mb-3">
                <div className="flex gap-3">
                    <div className="w-10 h-10 rounded-full bg-lucrix-dark flex items-center justify-center font-bold text-white border border-lucrix-border font-display">
                        {(prop.player_name || prop.team || "?")[0]}
                    </div>
                    <div>
                        <h3 className="font-black text-white text-sm leading-tight uppercase tracking-tight italic font-display">
                            {prop.player_name || prop.team || "Full Match"}
                        </h3>
                        <p className="text-textMuted text-[10px] font-bold mt-0.5 uppercase tracking-widest">
                            {prop.player_name ? `${prop.team} · ` : ""}{prop.stat_type.replace(/_/g, ' ')}
                        </p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <div className={`prop-grade-display prop-grade-${getGradeLabel(prop.grade).toLowerCase()}`}>
                        {getGradeLabel(prop.grade)}
                    </div>
                    <button
                        onClick={() => toggleFavProp(prop.id)}
                        className={`text-lg transition-colors ${isFav ? 'text-brand-warning drop-shadow-[0_0_5px_rgba(255,204,0,0.5)]' : 'text-textSecondary hover:text-textMuted'}`}
                    >
                        {isFav ? '★' : '☆'}
                    </button>
                </div>
            </div>

            {/* Main Prop Line */}
            <div className="bg-lucrix-dark/50 rounded-xl p-3 flex justify-between items-center mb-3 border border-lucrix-border">
                <div>
                    <span className="text-2xl font-black text-white font-display leading-none">{prop.line}</span>
                    <span className={`ml-2 text-xs font-black uppercase tracking-widest ${prop.side === 'over' ? 'text-brand-success' : 'text-brand-danger'}`}>
                        {prop.side}
                    </span>
                </div>
                <div className="text-right">
                    <div className="text-[10px] text-textSecondary uppercase font-black tracking-widest leading-tight">Best Odds</div>
                    <div className="text-lg font-mono font-black text-white leading-none">{prop.odds > 0 ? '+' : ''}{prop.odds}</div>
                </div>
            </div>

            {/* Intelligence Row */}
            <div className="flex gap-2 mb-4 overflow-x-auto pb-1 no-scrollbar">
                {prop.is_sharp && (
                    <span className="bg-brand-cyan/10 text-brand-cyan text-[10px] font-black px-2 py-0.5 rounded-sm border border-brand-cyan/20 whitespace-nowrap uppercase tracking-widest">🐋 SHARP</span>
                )}
                {prop.steam_score > 0 && (
                    <span className="bg-brand-orange/10 text-brand-orange text-[10px] font-black px-2 py-0.5 rounded-sm border border-brand-orange/20 whitespace-nowrap uppercase tracking-widest">🔥 STEAM {prop.steam_score}</span>
                )}
                {prop.ev_percent > 0 && (
                    <span className="bg-brand-success/10 text-brand-success text-[10px] font-black px-2 py-0.5 rounded-sm border border-brand-success/20 whitespace-nowrap uppercase tracking-widest">🎯 +{prop.ev_percent}% EV</span>
                )}
            </div>

            {/* Hit Rates (L5/L10/L20) */}
            <div className="grid grid-cols-3 gap-2 mb-4">
                <div className="bg-lucrix-dark/50 rounded-lg p-2 text-center border border-lucrix-border/50">
                    <div className="text-[9px] text-textSecondary uppercase font-black tracking-widest mb-1">Last 5</div>
                    <div className="text-sm font-black text-white">{Math.round(prop.hit_rates.l5)}%</div>
                </div>
                <div className="bg-lucrix-dark/50 rounded-lg p-2 text-center border border-lucrix-border/50">
                    <div className="text-[9px] text-textSecondary uppercase font-black tracking-widest mb-1">Last 10</div>
                    <div className="text-sm font-black text-white">{Math.round(prop.hit_rates.l10)}%</div>
                </div>
                <div className="bg-lucrix-dark/50 rounded-lg p-2 text-center border border-lucrix-border/50">
                    <div className="text-[9px] text-textSecondary uppercase font-black tracking-widest mb-1">Last 20</div>
                    <div className="text-sm font-black text-white">{Math.round(prop.hit_rates.l20)}%</div>
                </div>
            </div>

            {/* Line Shopping */}
            <div className="space-y-1.5 mb-4">
                <div className="text-[10px] text-textSecondary uppercase font-black tracking-widest px-1">Market Shopping</div>
                <div className="grid grid-cols-2 gap-2">
                    {Object.entries(prop.books).slice(0, 4).map(([id, odds]) => {
                        const book = SPORTSBOOKS[id as keyof typeof SPORTSBOOKS];
                        return (
                            <div key={id} className="flex justify-between items-center bg-lucrix-dark px-2 py-1.5 rounded-md border border-lucrix-border/50">
                                <span className="text-[10px] font-bold text-textMuted uppercase tracking-wider truncate max-w-[50px]">{book?.label || id}</span>
                                <span className={`text-[11px] font-mono font-black ${prop.side === 'under' ? 'text-brand-danger' : 'text-brand-success'}`}>{odds.over > 0 ? '+' : ''}{odds.over}</span>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* CTA */}
            <button
                onClick={() => addLeg({ ...prop, label: `${prop.player_name} ${prop.stat_type} ${prop.line}` })}
                className="w-full bg-brand-purple/10 border border-brand-purple/30 hover:bg-brand-purple hover:text-white hover:border-brand-purple text-brand-purple py-2 rounded-xl text-xs font-black uppercase tracking-widest transition-all shadow-glow shadow-brand-purple/10 active:scale-[0.98]"
            >
                Add to Slate
            </button>
        </div>
    );
}
