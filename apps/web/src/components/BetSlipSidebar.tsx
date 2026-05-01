"use client";

import React, { useState } from 'react';

interface Leg {
    id: string;
    player: string;
    stat: string;
    line: number;
    odds: number;
}

export const BetSlipSidebar: React.FC = () => {
    const [legs, setLegs] = useState<Leg[]>([]);

    const americanToDecimal = (odds: any): number => {
        const n = Number(odds);
        if (!odds || isNaN(n) || n === 0) return 1.909; // default -110
        if (n > 0) return (n / 100) + 1;
        return (100 / Math.abs(n)) + 1;
    };

    const calculateParlayOdds = (legs: Leg[]) => {
        const multiplier = legs.reduce((acc, leg) => acc * americanToDecimal(leg.odds), 1);
        const raw = Math.round((multiplier - 1) * 100);
        return Number.isFinite(raw) ? raw : 0;
    };

    const removeLeg = (id: string) => {
        setLegs(legs.filter(l => l.id !== id));
    };

    return (
        <div className="bet-slip-sidebar fixed right-0 top-0 w-80 h-screen bg-lucrix-surface border-l border-lucrix-border p-5 text-white flex flex-col z-[100] shadow-2xl">
            <h3 className="border-b border-lucrix-border pb-2 text-lg font-black uppercase italic tracking-tighter">Bet Slip</h3>

            <div className="flex-1 overflow-y-auto my-4 space-y-3 pr-2 custom-scrollbar">
                {legs.length === 0 ? (
                    <p className="text-textMuted text-center text-sm font-bold uppercase tracking-widest mt-8">Your slip is empty.</p>
                ) : (
                    legs.map(leg => (
                        <div key={leg.id} className="bg-lucrix-dark p-3.5 rounded-xl relative border border-lucrix-border/50 hover:border-lucrix-border transition-colors">
                            <button 
                                onClick={() => removeLeg(leg.id)} 
                                className="absolute right-3 top-3 bg-transparent border-none text-textMuted hover:text-brand-danger transition-colors cursor-pointer"
                            >
                                ✕
                            </button>
                            <div className="text-sm font-black uppercase italic tracking-tight">{leg.player}</div>
                            <div className="text-xs font-bold text-textMuted uppercase tracking-widest mt-0.5">{leg.stat} {leg.line}</div>
                            <div className="text-brand-success font-mono font-black mt-2 text-base">
                                {leg.odds > 0 ? '+' : ''}{leg.odds}
                            </div>
                        </div>
                    ))
                )}
            </div>

            {legs.length > 0 && (
                <div className="border-t border-lucrix-border pt-5">
                    <div className="flex justify-between items-center mb-4">
                        <span className="text-xs font-black uppercase text-textMuted tracking-widest">Parlay Odds:</span>
                        <span className="text-brand-success font-display font-black text-2xl">
                            {(() => { const v = calculateParlayOdds(legs); return Number.isFinite(v) && v !== 0 ? (v > 0 ? `+${v}` : v) : "—"; })()}
                        </span>
                    </div>
                    <button className="w-full py-4 bg-brand-success hover:bg-brand-success/90 text-lucrix-dark rounded-xl font-black uppercase tracking-widest text-sm transition-all shadow-glow shadow-brand-success/20">
                        Place Bet on DraftKings
                    </button>
                    <p className="text-[9px] text-textMuted mt-4 text-center uppercase tracking-widest font-bold opacity-70">
                        * Affiliate link triggers on click
                    </p>
                </div>
            )}
        </div>
    );
};
