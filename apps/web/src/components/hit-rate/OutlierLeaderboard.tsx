"use client";
import { TrendingUp, Flame, Award, ChevronRight } from "lucide-react";

interface LeaderboardProps {
    outliers: any[];
}

export function OutlierLeaderboard({ outliers }: LeaderboardProps) {
    return (
        <div className="bg-lucrix-surface border border-lucrix-border rounded-2xl overflow-hidden shadow-2xl">
            <div className="p-6 border-b border-white/5 flex items-center justify-between">
                <h3 className="text-xl font-black uppercase italic font-display text-white flex items-center gap-2">
                    <Award size={20} className="text-yellow-500" />
                    Top 20 Outliers Today
                </h3>
                <span className="text-[10px] text-textMuted font-black uppercase tracking-widest">Sort: Hit Rate DESC</span>
            </div>

            <div className="overflow-x-auto">
                <table className="w-full text-left">
                    <thead>
                        <tr className="bg-white/[0.02] text-[10px] uppercase font-black text-textMuted tracking-widest">
                            <th className="px-6 py-4">Player</th>
                            <th className="px-6 py-4">Market</th>
                            <th className="px-6 py-4">Hit Rate</th>
                            <th className="px-6 py-4">Sample</th>
                            <th className="px-6 py-4">Streak</th>
                            <th className="px-6 py-4">Trend</th>
                            <th className="px-6 py-4 pr-10">Confidence</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {outliers.slice(0, 20).map((p, i) => (
                            <tr key={i} className="hover:bg-white/[0.03] transition-colors group">
                                <td className="px-6 py-4">
                                    <div className="flex flex-col">
                                        <span className="text-sm font-bold text-white group-hover:text-brand-cyan transition-colors">{p.player_name}</span>
                                        <span className="text-[10px] font-medium text-textMuted uppercase">{p.team} • {p.sport.replace('_', ' ')}</span>
                                    </div>
                                </td>
                                <td className="px-6 py-4">
                                    <div className="text-sm font-bold text-gray-300">
                                        {p.market} <span className="text-white font-mono">O{p.line}</span>
                                    </div>
                                </td>
                                <td className="px-6 py-4">
                                    <span className={`text-lg font-black italic font-display ${p.hit_rate >= 90 ? 'text-yellow-400' : p.hit_rate >= 80 ? 'text-brand-success' : 'text-brand-cyan'}`}>
                                        {p.hit_rate}%
                                    </span>
                                </td>
                                <td className="px-6 py-4">
                                    <span className="text-xs font-bold text-textSecondary uppercase tracking-tighter">
                                        {p.hits}/{p.total} <span className="text-textMuted text-[10px]">Games</span>
                                    </span>
                                </td>
                                <td className="px-6 py-4">
                                    {p.streak >= 3 ? (
                                        <div className="flex items-center gap-1 text-orange-500">
                                            <Flame size={14} />
                                            <span className="text-xs font-black uppercase italic font-display">{p.streak}L</span>
                                        </div>
                                    ) : (
                                        <span className="text-textMuted text-xs">-</span>
                                    )}
                                </td>
                                <td className="px-6 py-4">
                                    {p.trend === "up" ? (
                                        <TrendingUp size={16} className="text-brand-success" />
                                    ) : (
                                        <span className="text-textMuted">--</span>
                                    )}
                                </td>
                                <td className="px-6 py-4 pr-10">
                                    <span className={`px-2 py-0.5 rounded-sm border text-[9px] font-black uppercase tracking-widest
                                        ${p.confidence === 'high' ? 'bg-brand-success/10 text-brand-success border-brand-success/30' : 
                                          p.confidence === 'reliable' ? 'bg-brand-cyan/10 text-brand-cyan border-brand-cyan/30' : 
                                          'bg-white/5 text-textMuted border-white/10'}`}>
                                        {p.confidence}
                                    </span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {outliers.length === 0 && (
                <div className="p-20 text-center space-y-4">
                    <div className="mx-auto size-16 bg-white/5 rounded-full flex items-center justify-center text-textMuted">
                        <TrendingUp size={32} />
                    </div>
                    <div>
                        <h4 className="text-xl font-bold text-white">Searching for Outliers...</h4>
                        <p className="text-textMuted">Lower your threshold or expand the sample window.</p>
                    </div>
                </div>
            )}
        </div>
    );
}
