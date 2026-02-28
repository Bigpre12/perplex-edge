"use client";

import { useRouter } from "next/navigation";

interface Prop {
    id: string;
    player: {
        name: string;
        position: string;
    };
    game?: {
        home: string;
        away: string;
    };
    matchup?: {
        opponent: string;
    };
    market: {
        stat_type: string;
    };
    line_value: number | string;
    side: 'over' | 'under';
    odds: number;
    display_edge: number;
    model_probability: number;
    confidence_score: number;
    sharp_money?: boolean;
    steam_score?: number;
    kelly_units: number;
}

export function PropCard({ prop, tier }: { prop: Prop, tier: string }) {
    const router = useRouter();

    return (
        <div className="bg-[#141424] border border-[#1E1E35] rounded-2xl p-4
                    hover:border-[#F5C518]/30 transition-all duration-200
                    hover:shadow-[0_0_20px_rgba(245,197,24,0.05)]">

            {/* Header Row */}
            <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                    {/* Player Avatar */}
                    <div className="w-9 h-9 rounded-full bg-[#1E1E35] 
                          flex items-center justify-center text-sm font-bold text-white">
                        {prop.player.name[0]}
                    </div>
                    <div>
                        <p className="text-white font-semibold text-sm leading-tight">
                            {prop.player.name}
                        </p>
                        <p className="text-[#6B7280] text-xs">
                            {prop.player.position} · {prop.game ? `${prop.game.away} @ ${prop.game.home}` : `vs ${prop.matchup?.opponent || 'Opponent'}`}
                        </p>
                    </div>
                </div>

                {/* Badges */}
                <div className="flex gap-1">
                    {prop.sharp_money && (
                        <span className="bg-[#F5C518]/10 text-[#F5C518] text-[10px] 
                             font-bold px-2 py-0.5 rounded-full border 
                             border-[#F5C518]/20">
                            ⚡ SHARP
                        </span>
                    )}
                    {prop.steam_score && prop.steam_score > 0 && (
                        <span className="bg-[#FF6B35]/10 text-[#FF6B35] text-[10px] 
                             font-bold px-2 py-0.5 rounded-full border 
                             border-[#FF6B35]/20">
                            🔥 {prop.steam_score.toFixed(1)}
                        </span>
                    )}
                </div>
            </div>

            {/* Prop Line — The Main Event */}
            <div className="bg-[#0F0F1A] rounded-xl p-3 mb-3">
                <div className="flex items-center justify-between">
                    <div>
                        <p className="text-[#6B7280] text-xs uppercase tracking-wider mb-0.5">
                            {prop.market.stat_type}
                        </p>
                        <div className="flex items-baseline gap-2">
                            <span className="text-white text-2xl font-bold font-mono">
                                {prop.line_value}
                            </span>
                            <span className={`text-sm font-bold uppercase
                ${prop.side === 'over' ? 'text-[#22C55E]' : 'text-[#EF4444]'}`}>
                                {prop.side}
                            </span>
                        </div>
                    </div>
                    <div className="text-right">
                        <p className="text-[#6B7280] text-xs mb-0.5">Odds</p>
                        <span className="text-white font-mono font-semibold">
                            {prop.odds > 0 ? `+${prop.odds}` : prop.odds}
                        </span>
                    </div>
                </div>
            </div>

            {/* Stats Row */}
            <div className="grid grid-cols-3 gap-2 mb-3">
                <StatChip label="EV" value={`+${(prop.display_edge * 100).toFixed(1)}%`} color="edge" />
                <StatChip label="Model" value={`${(prop.model_probability * 100).toFixed(0)}%`} color="neutral" />
                <StatChip label="Conf" value={`${(prop.confidence_score * 100).toFixed(0)}%`} color="neutral" />
            </div>

            {/* Kelly / Antigravity Rec */}
            {tier === 'free' ? (
                <div className="flex items-center justify-between p-2.5 
                        bg-[#1E1E35] rounded-xl cursor-pointer
                        hover:bg-[#2A2A45] transition-colors"
                    onClick={() => router.push('/upgrade')}>
                    <span className="text-[#6B7280] text-xs blur-sm select-none">
                        ANTIGRAVITY REC: 0.03u
                    </span>
                    <span className="text-[#F5C518] text-xs font-semibold">
                        🔒 Unlock Pro
                    </span>
                </div>
            ) : (
                <div className="flex items-center justify-between p-2.5 
                        bg-[#F5C518]/5 border border-[#F5C518]/10 rounded-xl">
                    <span className="text-[#F5C518] text-xs font-bold font-sans">
                        ANTIGRAVITY REC
                    </span>
                    <span className="text-white font-mono font-bold text-sm">
                        {prop.kelly_units.toFixed(2)}u
                    </span>
                </div>
            )}
        </div>
    )
}

function StatChip({ label, value, color }: { label: string, value: string, color: 'edge' | 'steam' | 'sharp' | 'neutral' }) {
    const colors = {
        edge: 'text-[#22C55E]',
        steam: 'text-[#FF6B35]',
        sharp: 'text-[#F5C518]',
        neutral: 'text-white',
    }
    return (
        <div className="bg-[#0F0F1A] rounded-lg p-2 text-center">
            <p className="text-[#6B7280] text-[10px] uppercase tracking-wider mb-0.5 font-sans">
                {label}
            </p>
            <p className={`font-mono font-bold text-sm ${colors[color]}`}>
                {value}
            </p>
        </div>
    )
}
