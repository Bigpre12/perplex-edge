import { Shield, Activity, TrendingUp } from 'lucide-react';

interface MatchupProps {
    oppRank: number;
    paceFactor: 'High' | 'Low' | 'Avg';
    trend: string;
}

export default function MatchupIntelligence({ oppRank, paceFactor, trend }: MatchupProps) {
    const getRankColor = (rank: number) => {
        if (rank <= 10) return 'text-emerald-primary'; // Easy matchup (offense favored)
        if (rank >= 22) return 'text-accent-red'; // Hard matchup (defense favored)
        return 'text-slate-400';
    };


    return (
        <div className="flex items-center gap-3 py-2 px-3 bg-white/[0.02] rounded-lg border border-white/[0.05]">
            <div className="flex flex-col gap-0.5">
                <div className="flex items-center gap-1">
                    <Shield size={10} className={getRankColor(oppRank)} />
                    <span className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">DEF RANK</span>
                </div>
                <span className={`text-xs font-bold ${getRankColor(oppRank)}`}>{oppRank}th</span>
            </div>

            <div className="w-[1px] h-6 bg-slate-800"></div>

            <div className="flex flex-col gap-0.5">
                <div className="flex items-center gap-1">
                    <Activity size={10} className="text-secondary" />
                    <span className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">PACE</span>
                </div>
                <span className="text-xs font-bold text-white">{paceFactor}</span>
            </div>

            <div className="w-[1px] h-6 bg-slate-800"></div>

            <div className="flex flex-col gap-0.5">
                <div className="flex items-center gap-1">
                    <TrendingUp size={10} className="text-emerald-primary" />
                    <span className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">L5 HIT %</span>
                </div>
                <span className="text-xs font-bold text-white tracking-tighter">{trend}</span>
            </div>
        </div>
    );
}
