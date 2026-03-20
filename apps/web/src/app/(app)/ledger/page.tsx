"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    TrendingUp,
    Target,
    ShieldCheck,
    Clock,
    ArrowUpRight,
    ArrowDownRight,
    ChevronRight,
    Filter,
    Download,
    Share2,
    Loader2,
    Brain,
    Plus
} from "lucide-react";
import { getAuthToken } from "@/lib/auth";
import { api, isApiError } from "@/lib/api";

export default function LedgerPage() {
    const [bets, setBets] = useState<any[]>([]);
    const [stats, setStats] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [selectedSlip, setSelectedSlip] = useState<any>(null);
    const [shareText, setShareText] = useState("");
    const [isSharing, setIsSharing] = useState(false);
    const [showShareModal, setShowShareModal] = useState(false);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const [betsRes, statsRes] = await Promise.all([
                    api.ledgerMyBets(),
                    api.ledgerStats()
                ]);

                if (!isApiError(betsRes)) setBets(betsRes);
                if (!isApiError(statsRes)) setStats(statsRes);
            } catch (err) {
                console.error("Failed to fetch ledger data:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    const generateShareText = (bet: any) => {
        if (!bet) return "";
        const statusEmoji = bet.status === 'won' ? '✅' : bet.status === 'lost' ? '❌' : '⏳';
        const oddsSign = bet.total_odds > 0 ? '+' : '';
        return `My latest bet: ${bet.slip_type} at ${oddsSign}${bet.total_odds} on ${bet.sportsbook}. Status: ${statusEmoji} ${bet.status.toUpperCase()}! #BettingAnalytics #SportsBetting`;
    };

    const handleShare = async () => {
        if (!selectedSlip) return;
        setIsSharing(true);
        try {
            const token = getAuthToken();
            const data = await api.socialShare({
                title: `Locked in: ${selectedSlip.slip_type} @ ${selectedSlip.total_odds}`,
                content: shareText,
                slip_id: selectedSlip.id
            }, token as string);

            if (!isApiError(data)) {
                setShowShareModal(false);
                setShareText("");
                alert("Shared successfully to community feed!");
            }
        } catch (err) {
            console.error(err);
        } finally {
            setIsSharing(false);
        }
    };

    if (loading) {
        return (
            <div className="h-[60vh] flex items-center justify-center">
                <Loader2 className="animate-spin text-primary" size={40} />
            </div>
        );
    }

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-black text-white tracking-tight">Intelligence Ledger</h1>
                    <p className="text-secondary text-sm mt-1 italic">Real-time ROI & Performance Analytics</p>
                </div>
                <div className="flex gap-2">
                    <button className="flex items-center gap-2 px-4 py-2 bg-surface border border-slate-800 rounded-lg text-sm text-slate-300 hover:text-white transition-colors">
                        <Filter size={16} /> Filters
                    </button>
                    <button className="flex items-center gap-2 px-4 py-2 bg-surface border border-slate-800 rounded-lg text-sm text-slate-300 hover:text-white transition-colors">
                        <Download size={16} /> Export
                    </button>
                    <button
                        onClick={() => setShowShareModal(true)}
                        className="flex items-center gap-2 px-4 py-2 bg-primary text-background-dark font-bold rounded-lg text-sm hover:bg-primary/90 transition-all"
                    >
                        <Share2 size={16} /> Share
                    </button>
                </div>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard
                    label="Total Return"
                    value={`$${stats?.profit_loss || '0.00'}`}
                    trend={stats?.profit_loss >= 0 ? "Positive" : "Negative"}
                    color={stats?.profit_loss >= 0 ? "emerald" : "red"}
                    icon={stats?.profit_loss >= 0 ? <ArrowUpRight size={20} /> : <ArrowDownRight size={20} />}
                />
                <StatCard
                    label="Win Rate"
                    value={`${stats?.win_rate?.toFixed(1) || '0.0'}%`}
                    trend="Overall"
                    color="primary"
                    icon={<ShieldCheck size={20} />}
                />
                <StatCard
                    label="Total Tracked"
                    value={stats?.total_bets || '0'}
                    trend="Lifetime"
                    color="slate"
                    icon={<Clock size={20} />}
                />
                <StatCard
                    label="Avg CLV Edge"
                    value={`${stats?.clv_avg || '0.0'}%`}
                    trend="Positive"
                    color="amber"
                    icon={<TrendingUp size={20} />}
                />
            </div>

            {/* Main Grid */}
            <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
                {/* Recent Bets List */}
                <div className="xl:col-span-2 space-y-4">
                    <div className="glass-panel rounded-2xl overflow-hidden border-white/[0.05]">
                        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
                            <h3 className="text-sm font-bold text-white flex items-center gap-2 uppercase tracking-widest">
                                <Brain size={16} className="text-primary" /> Recent Placement Log
                            </h3>
                            <button onClick={() => window.location.href = '/player-props'} className="flex items-center gap-1 px-3 py-1 bg-primary text-background-dark font-bold rounded-lg text-xs hover:bg-primary/90 transition-all">
                                <Plus size={14} /> Add Bet
                            </button>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="w-full text-left">
                                <thead className="text-[10px] text-slate-500 font-bold uppercase tracking-widest bg-white/[0.02]">
                                    <tr>
                                        <th className="px-6 py-4">Date / Time</th>
                                        <th className="px-6 py-4">Market</th>
                                        <th className="px-6 py-4">Book</th>
                                        <th className="px-6 py-4">Odds</th>
                                        <th className="px-6 py-4 text-right">Status</th>
                                        <th className="px-6 py-4 text-right">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-800/50">
                                    {bets.length > 0 ? (
                                        bets.map((bet, i) => (
                                            <tr key={i} className="hover:bg-white/[0.02] transition-colors group">
                                                <td className="px-6 py-4">
                                                    <p className="text-xs text-white font-medium">{new Date(bet.placed_at).toLocaleDateString()}</p>
                                                    <p className="text-[10px] text-slate-500">{new Date(bet.placed_at).toLocaleTimeString()}</p>
                                                </td>
                                                <td className="px-6 py-4">
                                                    <p className="text-xs font-bold text-slate-200 uppercase">{bet.slip_type}</p>
                                                    <p className="text-[10px] text-slate-500">ID: #{bet.id}</p>
                                                </td>
                                                <td className="px-6 py-4 text-xs text-slate-300 italic">{bet.sportsbook}</td>
                                                <td className="px-6 py-4 font-mono text-xs text-primary">{bet.total_odds > 0 ? `+${bet.total_odds}` : bet.total_odds}</td>
                                                <td className="px-6 py-4 text-right">
                                                    <span className={`px-2 py-0.5 rounded text-[10px] font-black uppercase ${bet.status === 'won' ? 'bg-emerald-500/20 text-emerald-500' :
                                                        bet.status === 'lost' ? 'bg-red-500/20 text-red-500' :
                                                            'bg-slate-800 text-slate-400'
                                                        }`}>
                                                        {bet.status}
                                                    </span>
                                                </td>
                                                <td className="px-6 py-4 text-right">
                                                    <div className="flex items-center justify-end gap-2">
                                                        <button
                                                            onClick={() => {
                                                                setSelectedSlip(bet);
                                                                setShowShareModal(true);
                                                            }}
                                                            title="Share Insight"
                                                            className="p-2 hover:bg-white/5 rounded-lg text-slate-500 hover:text-primary transition-all"
                                                        >
                                                            <Share2 size={16} />
                                                        </button>
                                                        <button 
                                                            title="View Details"
                                                            className="p-2 hover:bg-white/5 rounded-lg text-slate-500 hover:text-white transition-all"
                                                        >
                                                            <ChevronRight size={16} />
                                                        </button>
                                                    </div>
                                                </td>
                                            </tr>
                                        ))
                                    ) : (
                                        <tr>
                                            <td colSpan={6} className="py-12 text-center text-slate-500 italic text-sm">
                                                No bets recorded in the intelligence ledger yet.
                                            </td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                {/* Analytics Sidebar */}
                <div className="space-y-6">
                    <div className="glass-panel p-6 rounded-2xl border-white/[0.05]">
                        <h3 className="text-sm font-bold text-white mb-6 flex items-center gap-2">
                            <Brain size={16} className="text-primary" /> Market Exposure
                        </h3>
                        <div className="space-y-4">
                            <ExposureBar label="NBA Basketball" percent={65} color="bg-blue-500" />
                            <ExposureBar label="NFL Football" percent={25} color="bg-orange-500" />
                            <ExposureBar label="NHL Hockey" percent={10} color="bg-primary" />
                        </div>
                    </div>

                    <div className="glass-panel p-6 rounded-2xl border-white/[0.05] bg-gradient-to-br from-[#0c1416] to-[#0a0a0a]">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="p-2 bg-primary/20 rounded-lg text-primary">
                                <TrendingUp size={20} />
                            </div>
                            <h3 className="text-sm font-bold text-white uppercase tracking-tight">Intelligence Quotient</h3>
                        </div>
                        <p className="text-xs text-slate-400 leading-relaxed italic">
                            "You are currently beating the closing line on 74% of your NBA props. Strategy suggests increasing unit size on highly correlated markets."
                        </p>
                    </div>
                </div>
            </div>

            {/* Share Modal */}
            <AnimatePresence>
                {showShareModal && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            onClick={() => setShowShareModal(false)}
                            className="absolute inset-0 bg-background-dark/80 backdrop-blur-sm"
                        ></motion.div>
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95, y: 20 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.95, y: 20 }}
                            className="relative w-full max-w-lg glass-premium p-8 rounded-3xl border-white/[0.08] shadow-2xl"
                        >
                            <div className="flex items-center gap-3 mb-6">
                                <div className="p-2 bg-primary/20 rounded-lg text-primary">
                                    <Share2 size={24} />
                                </div>
                                <div>
                                    <h2 className="text-xl font-black text-white">Share to Community</h2>
                                    <p className="text-[10px] text-secondary font-bold uppercase tracking-widest">Public Insight</p>
                                </div>
                            </div>

                            <div className="space-y-4">
                                <div className="p-4 rounded-xl bg-white/[0.03] border border-white/[0.08]">
                                    <p className="text-[10px] text-slate-500 font-bold uppercase mb-1">Attached Slip</p>
                                    <p className="text-sm font-bold text-white">ID: #{selectedSlip?.id} - {selectedSlip?.sportsbook} ({selectedSlip?.total_odds})</p>
                                </div>

                                <textarea
                                    placeholder="Tell the community why you're locking this in..."
                                    rows={4}
                                    value={shareText}
                                    onChange={(e) => setShareText(e.target.value)}
                                    className="w-full bg-white/[0.03] border border-white/[0.08] rounded-xl px-4 py-3 text-white focus:outline-none focus:border-primary/50 transition-colors resize-none"
                                />

                                <button
                                    onClick={handleShare}
                                    disabled={isSharing}
                                    className="w-full py-4 bg-primary text-background-dark font-black rounded-xl hover:bg-primary/90 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                                >
                                    {isSharing ? <Loader2 className="animate-spin" /> : <>PUBLISH TO FEED <TrendingUp size={18} /></>}
                                </button>
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </div>
    );
}

function StatCard({ label, value, trend, color, icon }: any) {
    const colors: any = {
        emerald: "text-emerald-500 border-emerald-500/20 bg-emerald-500/5",
        primary: "text-primary border-primary/20 bg-primary/5",
        slate: "text-slate-400 border-slate-700 bg-slate-800/20",
        amber: "text-amber-500 border-amber-500/20 bg-amber-500/5"
    };

    return (
        <motion.div
            whileHover={{ y: -4 }}
            className={`p-6 rounded-2xl border ${colors[color]} backdrop-blur-sm transition-all`}
        >
            <div className="flex justify-between items-start mb-4">
                <span className="text-[10px] font-black uppercase tracking-[0.2em] opacity-60">{label}</span>
                <div className="opacity-40">{icon}</div>
            </div>
            <div className="flex flex-col">
                <span className="text-2xl font-black tracking-tight">{value}</span>
                <span className="text-[10px] font-bold mt-1 opacity-60 flex items-center gap-1">
                    {trend}
                </span>
            </div>
        </motion.div>
    );
}

function ExposureBar({ label, percent, color }: any) {
    return (
        <div className="space-y-2">
            <div className="flex justify-between text-[10px] font-bold uppercase">
                <span className="text-slate-400">{label}</span>
                <span className="text-white">{percent}%</span>
            </div>
            <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${percent}%` }}
                    className={`h-full ${color} rounded-full`}
                />
            </div>
        </div>
    );
}
