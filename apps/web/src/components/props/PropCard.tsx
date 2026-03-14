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
        S: '#00ff88',
        A: '#88ff00',
        B: '#ffcc00',
        C: '#ff8800',
        Elite: '#00ff88',
        Good: '#88ff00'
    };

    const getGradeLabel = (g: string) => (g === 'S' || g === 'Elite') ? 'S' : (g === 'A' || g === 'Good') ? 'A' : g;

    return (
        <div className={`group relative bg-[#12121e] border border-[#2a2a3a] rounded-xl p-4 transition-all duration-300 hover:border-[#7c3aed]/50 hover:shadow-[0_0_20px_rgba(124,58,237,0.1)] ${prop.is_sharp ? 'ring-1 ring-cyan-500/30' : ''}`}>
            {/* Header: Player & Grade */}
            <div className="flex justify-between items-start mb-3">
                <div className="flex gap-3">
                    <div className="w-10 h-10 rounded-full bg-[#1e1e2d] flex items-center justify-center font-bold text-[#f0f0ff] border border-[#2a2a3a]">
                        {prop.player_name[0]}
                    </div>
                    <div>
                        <h3 className="font-bold text-[#f0f0ff] text-sm leading-tight">{prop.player_name}</h3>
                        <p className="text-[#9090aa] text-xs mt-0.5">{prop.team} · {prop.stat_type.replace(/_/g, ' ')}</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <div
                        className="text-2xl font-black italic tracking-tighter"
                        style={{ color: gradeColors[prop.grade] || '#9090aa', textShadow: `0 0 10px ${gradeColors[prop.grade]}40` }}
                    >
                        {getGradeLabel(prop.grade)}
                    </div>
                    <button
                        onClick={() => toggleFavProp(prop.id)}
                        className={`text-lg transition-colors ${isFav ? 'text-yellow-400' : 'text-[#44445a] hover:text-[#66667a]'}`}
                    >
                        {isFav ? '★' : '☆'}
                    </button>
                </div>
            </div>

            {/* Main Prop Line */}
            <div className="bg-[#0a0a0f] rounded-lg p-3 flex justify-between items-center mb-3 border border-[#1e1e2d]">
                <div>
                    <span className="text-2xl font-mono font-bold text-white">{prop.line}</span>
                    <span className={`ml-2 text-xs font-black uppercase tracking-widest ${prop.side === 'over' ? 'text-[#00ff88]' : 'text-[#ff4466]'}`}>
                        {prop.side}
                    </span>
                </div>
                <div className="text-right">
                    <div className="text-[10px] text-[#55556a] uppercase font-bold">Best Odds</div>
                    <div className="text-lg font-mono font-bold text-[#f0f0ff]">{prop.odds > 0 ? '+' : ''}{prop.odds}</div>
                </div>
            </div>

            {/* Intelligence Row */}
            <div className="flex gap-2 mb-4 overflow-x-auto pb-1 no-scrollbar">
                {prop.is_sharp && (
                    <span className="bg-cyan-500/10 text-cyan-400 text-[10px] font-black px-2 py-0.5 rounded border border-cyan-500/20 whitespace-nowrap">🐋 SHARP</span>
                )}
                {prop.steam_score > 0 && (
                    <span className="bg-orange-500/10 text-orange-400 text-[10px] font-black px-2 py-0.5 rounded border border-orange-500/20 whitespace-nowrap">🔥 STEAM {prop.steam_score}</span>
                )}
                {prop.ev_percent > 0 && (
                    <span className="bg-green-500/10 text-green-400 text-[10px] font-black px-2 py-0.5 rounded border border-green-500/20 whitespace-nowrap">🎯 +{prop.ev_percent}% EV</span>
                )}
            </div>

            {/* Hit Rates (L5/L10/L20) */}
            <div className="grid grid-cols-3 gap-2 mb-4">
                <div className="bg-[#1e1e2d] rounded-lg p-2 text-center border border-[#2a2a3a]">
                    <div className="text-[9px] text-[#70708a] uppercase font-bold mb-1">Last 5</div>
                    <div className="text-sm font-bold text-[#f0f0ff]">{Math.round(prop.hit_rates.l5)}%</div>
                </div>
                <div className="bg-[#1e1e2d] rounded-lg p-2 text-center border border-[#2a2a3a]">
                    <div className="text-[9px] text-[#70708a] uppercase font-bold mb-1">Last 10</div>
                    <div className="text-sm font-bold text-[#f0f0ff]">{Math.round(prop.hit_rates.l10)}%</div>
                </div>
                <div className="bg-[#1e1e2d] rounded-lg p-2 text-center border border-[#2a2a3a]">
                    <div className="text-[9px] text-[#70708a] uppercase font-bold mb-1">Last 20</div>
                    <div className="text-sm font-bold text-[#f0f0ff]">{Math.round(prop.hit_rates.l20)}%</div>
                </div>
            </div>

            {/* Line Shopping */}
            <div className="space-y-1.5 mb-4">
                <div className="text-[10px] text-[#55556a] uppercase font-bold px-1">Market Shopping</div>
                <div className="grid grid-cols-2 gap-2">
                    {Object.entries(prop.books).slice(0, 4).map(([id, odds]) => {
                        const book = SPORTSBOOKS[id as keyof typeof SPORTSBOOKS];
                        return (
                            <div key={id} className="flex justify-between items-center bg-[#161625] px-2 py-1.5 rounded border border-[#2a2a3a]/50">
                                <span className="text-[11px] text-[#9090aa]">{book?.label || id}</span>
                                <span className="text-[11px] font-mono font-bold text-[#00ff88]">{odds.over > 0 ? '+' : ''}{odds.over}</span>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* CTA */}
            <button
                onClick={() => addLeg({ ...prop, label: `${prop.player_name} ${prop.stat_type} ${prop.line}` })}
                className="w-full bg-[#7c3aed] hover:bg-[#6d28d9] text-white py-2 rounded-lg text-sm font-bold transition-all shadow-lg shadow-purple-900/20 active:scale-[0.98]"
            >
                Add to Slate
            </button>
        </div>
    );
}
