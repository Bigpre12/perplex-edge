'use client';

import { useState, useEffect } from 'react';
import { api, isApiError } from '@/lib/api';
import {
    TrendingUp,
    Target,
    ShieldCheck,
    BarChart3,
    Calendar,
    CheckCircle2,
    XCircle,
    ExternalLink,
    ArrowUpRight
} from 'lucide-react';

interface Metric {
    total_picks: number;
    wins: number;
    win_rate: number;
    avg_ev: number;
    avg_clv: number;
    total_profit_units: number;
    timestamp: string;
}

interface PerformanceData {
    metrics_30d: Metric;
    metrics_all_time: Metric;
}

interface RecentPick {
    player: string;
    stat: string;
    line: number;
    odds: number;
    result: 'WIN' | 'LOSS';
    actual: number;
    clv: number;
    date: string;
}

export default function ResultsPage() {
    const [performance, setPerformance] = useState<PerformanceData | null>(null);
    const [recentPicks, setRecentPicks] = useState<RecentPick[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchData() {
            try {
                const [perfData, recentData] = await Promise.all([
                    api.trackRecordSummary(),
                    api.trackRecordRecent(20)
                ]);

                if (!isApiError(perfData)) setPerformance(perfData);
                if (!isApiError(recentData)) setRecentPicks(recentData.recent_picks || []);
            } catch (err) {
                console.error('Failed to fetch results:', err);
            } finally {
                setLoading(false);
            }
        }
        fetchData();
    }, []);

    if (loading) {
        return (
            <div className="min-h-screen bg-[#080810] flex items-center justify-center">
                <div className="w-12 h-12 border-4 border-[#F5C518]/20 border-t-[#F5C518] rounded-full animate-spin"></div>
            </div>
        );
    }

    const stats = performance?.metrics_all_time || performance?.metrics_30d;

    return (
        <div className="min-h-screen bg-[#080810] text-[#f1f5f9] font-sans section-padding">
            <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">

                {/* Header */}
                <div className="text-center mb-16 relative">
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-64 h-64 bg-[#F5C518]/10 rounded-full blur-[100px] -z-10"></div>
                    <h1 className="text-5xl font-extrabold tracking-tight mb-4 text-transparent bg-clip-text bg-gradient-to-b from-white to-white/70">
                        Transparent Track Record
                    </h1>
                    <p className="text-xl text-[#94a3b8] max-w-2xl mx-auto">
                        Real-time performance metrics and every pick we've ever made. No hidden losses, no deleted posts—just math.
                    </p>
                    <div className="mt-8 flex items-center justify-center gap-4">
                        <span className="flex items-center gap-2 px-4 py-2 bg-[#F5C518]/10 border border-[#F5C518]/20 rounded-full text-[#F5C518] text-sm font-medium">
                            <ShieldCheck className="w-4 h-4" />
                            Verifiable Blockchain Hashing (Coming Soon)
                        </span>
                    </div>
                </div>

                {/* Global Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
                    <StatCard
                        label="Win Rate"
                        value={`${stats?.win_rate}%`}
                        icon={<Target className="w-6 h-6 text-[#F5C518]" />}
                        subtext={`${stats?.wins}/${stats?.total_picks} Graded`}
                    />
                    <StatCard
                        label="Avg. CLV"
                        value={`+${stats?.avg_clv}%`}
                        icon={<TrendingUp className="w-6 h-6 text-[#22C55E]" />}
                        subtext="Beating the Market"
                    />
                    <StatCard
                        label="ROI (30d)"
                        value={`${performance?.metrics_30d.total_profit_units} Units`}
                        icon={<BarChart3 className="w-6 h-6 text-[#F5C518]" />}
                        subtext="Standard 1U Staking"
                    />
                    <StatCard
                        label="Avg. Edge"
                        value={`+${stats?.avg_ev}%`}
                        icon={<ArrowUpRight className="w-6 h-6 text-[#F5C518]" />}
                        subtext="Mathematical Advantage"
                    />
                </div>

                {/* Recent Picks Table */}
                <div className="bg-[#0F0F1A] border border-[#1E1E35] rounded-3xl overflow-hidden glass-morphism">
                    <div className="px-8 py-6 border-b border-[#1E1E35] flex items-center justify-between">
                        <h2 className="text-2xl font-bold flex items-center gap-3">
                            <Calendar className="w-6 h-6 text-[#F5C518]" />
                            Recent Graded Picks
                        </h2>
                        <div className="text-sm text-[#94a3b8]">
                            Last Update: {stats ? new Date(stats.timestamp).toLocaleTimeString() : 'Just now'}
                        </div>
                    </div>

                    <div className="overflow-x-auto">
                        <table className="w-full text-left">
                            <thead>
                                <tr className="bg-[#141424]/50 text-[#94a3b8] text-sm font-medium">
                                    <th className="px-8 py-4">Player / Market</th>
                                    <th className="px-4 py-4 text-center">Result</th>
                                    <th className="px-4 py-4">Line / Odds</th>
                                    <th className="px-4 py-4">Actual</th>
                                    <th className="px-4 py-4">CLV Beats</th>
                                    <th className="px-8 py-4 text-right">Date</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-[#1E1E35]">
                                {recentPicks.map((pick, i) => (
                                    <tr key={i} className="hover:bg-[#1E1E35]/30 transition-colors group">
                                        <td className="px-8 py-6">
                                            <div className="font-bold text-white group-hover:text-[#F5C518] transition-colors">
                                                {pick.player}
                                            </div>
                                            <div className="text-xs text-[#94a3b8] uppercase tracking-wider mt-1">
                                                {pick.stat.replace('_', ' ')}
                                            </div>
                                        </td>
                                        <td className="px-4 py-6">
                                            <div className="flex justify-center">
                                                {pick.result === 'WIN' ? (
                                                    <div className="flex items-center gap-1.5 px-3 py-1 bg-[#22C55E]/10 border border-[#22C55E]/20 text-[#22C55E] rounded-full text-xs font-bold">
                                                        <CheckCircle2 className="w-3.5 h-3.5" />
                                                        WIN
                                                    </div>
                                                ) : (
                                                    <div className="flex items-center gap-1.5 px-3 py-1 bg-[#EF4444]/10 border border-[#EF4444]/20 text-[#EF4444] rounded-full text-xs font-bold">
                                                        <XCircle className="w-3.5 h-3.5" />
                                                        LOSS
                                                    </div>
                                                )}
                                            </div>
                                        </td>
                                        <td className="px-4 py-6">
                                            <div className="text-white font-mono">{pick.line}</div>
                                            <div className="text-xs text-[#94a3b8]">{pick.odds}</div>
                                        </td>
                                        <td className="px-4 py-6">
                                            <div className="text-white font-mono font-bold">{pick.actual}</div>
                                        </td>
                                        <td className="px-4 py-6">
                                            <div className={`text-sm font-medium ${pick.clv > 0 ? 'text-[#22C55E]' : 'text-[#94a3b8]'}`}>
                                                {pick.clv > 0 ? `+${pick.clv}%` : '0%'}
                                            </div>
                                        </td>
                                        <td className="px-8 py-6 text-right text-[#94a3b8] text-sm font-mono">
                                            {new Date(pick.date).toLocaleDateString()}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Audit Disclaimer */}
                <div className="mt-12 text-center text-sm text-[#94a3b8] max-w-2xl mx-auto bg-[#141424] p-6 border border-[#1E1E35] rounded-2xl">
                    <p>
                        <strong>AUDIT POLICY:</strong> Every pick displayed here was sent to users via push notification or dashboard update
                        <em> before</em> the event start time. We use primary score feeds from ESPN and official league APIs to grade results automatically
                        within 60 minutes of game completion.
                    </p>
                </div>
            </div>
        </div>
    );
}

function StatCard({ label, value, icon, subtext }: { label: string, value: string, icon: React.ReactNode, subtext: string }) {
    return (
        <div className="bg-[#0F0F1A] border border-[#1E1E35] p-6 rounded-3xl relative overflow-hidden group hover:border-[#F5C518]/30 transition-all">
            <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition-opacity">
                {icon}
            </div>
            <div className="text-[#94a3b8] text-sm font-medium mb-1">{label}</div>
            <div className="text-3xl font-extrabold text-[#F5C518] mb-2">{value}</div>
            <div className="text-xs text-[#64748b]">{subtext}</div>
        </div>
    );
}
