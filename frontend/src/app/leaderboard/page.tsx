"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Trophy, TrendingUp, Medal, Search, Filter, ArrowUpRight, Crown, Zap } from "lucide-react";

interface LeaderboardEntry {
    rank: number;
    username: string;
    roi: number;
    win_rate: number;
    streak: number;
    tier: string;
}

export default function LeaderboardPage() {
    const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchLeaderboard = async () => {
            try {
                const res = await fetch("http://localhost:8000/api/contests/global-leaderboard");
                const json = await res.json();
                setEntries(json.leaderboard);
            } catch (err) {
                console.error("Leaderboard fetch failed", err);
            } finally {
                setLoading(false);
            }
        };
        fetchLeaderboard();
    }, []);

    return (
        <div className="space-y-8 max-w-6xl mx-auto">
            {/* Header section */}
            <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-[#102023] to-[#0a1517] border border-white/[0.05] p-10">
                <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-8">
                    <div className="space-y-4">
                        <div className="flex items-center gap-3">
                            <div className="p-3 bg-primary/10 rounded-2xl border border-primary/20">
                                <Trophy className="text-primary" size={32} />
                            </div>
                            <div>
                                <h1 className="text-3xl font-black text-white uppercase tracking-tighter">Community Elite</h1>
                                <p className="text-slate-500 font-bold uppercase text-xs tracking-widest">Global verified ROI rankings</p>
                            </div>
                        </div>
                        <p className="text-slate-400 max-w-lg font-medium leading-relaxed">
                            Welcome to the Perplex Elite. These rankings are calculated based on verified virtual unit ROI across all active slates and contests.
                        </p>
                    </div>

                    <div className="flex gap-4">
                        <div className="glass-premium p-6 rounded-2xl border-white/[0.08] text-center min-w-[140px]">
                            <p className="text-[10px] text-slate-500 font-black uppercase mb-1">Total Prize POOL</p>
                            <p className="text-2xl font-black text-primary tracking-tighter">$25,000</p>
                        </div>
                        <div className="glass-premium p-6 rounded-2xl border-white/[0.08] text-center min-w-[140px]">
                            <p className="text-[10px] text-slate-500 font-black uppercase mb-1">Active Competing</p>
                            <p className="text-2xl font-black text-white tracking-tighter">1,242</p>
                        </div>
                    </div>
                </div>

                {/* Background blobs */}
                <div className="absolute -right-20 -top-20 w-96 h-96 bg-primary/5 rounded-full blur-[100px]" />
                <div className="absolute -left-20 -bottom-20 w-80 h-80 bg-cyan-500/5 rounded-full blur-[80px]" />
            </div>

            {/* Podium for top 3 */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {entries.slice(0, 3).map((entry, i) => (
                    <PodiumCard key={entry.username} entry={entry} place={i + 1} />
                ))}
            </div>

            {/* Main Table */}
            <div className="glass-panel rounded-3xl border-white/[0.05] overflow-hidden">
                <div className="p-6 border-b border-white/[0.05] flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white/[0.01]">
                    <div className="flex items-center gap-4">
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={16} />
                            <input
                                type="text"
                                placeholder="SEARCH ANALYSTS..."
                                className="bg-background-dark/50 border border-white/[0.08] rounded-xl pl-10 pr-4 py-2 text-xs font-bold text-white focus:outline-none focus:border-primary/50 transition-all w-64 uppercase tracking-wider"
                            />
                        </div>
                        <button className="flex items-center gap-2 p-2 px-4 bg-white/[0.03] border border-white/[0.08] rounded-xl text-[10px] font-black text-slate-400 hover:text-white transition-all uppercase tracking-widest">
                            <Filter size={14} /> FILTER: 30D ROI
                        </button>
                    </div>
                    <p className="text-[10px] text-slate-500 font-black uppercase tracking-widest">LAST UPDATED: JUST NOW</p>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-white/[0.01]">
                                <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest">RANK</th>
                                <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest">ANALYST</th>
                                <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest text-right">LIFETIME ROI</th>
                                <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest text-right">WIN RATE</th>
                                <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest text-right">STREAK</th>
                                <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest text-right">CLEARANCE</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/[0.03]">
                            {entries.slice(3).map((entry) => (
                                <tr key={entry.username} className="hover:bg-white/[0.02] transition-colors group cursor-pointer">
                                    <td className="px-6 py-5">
                                        <span className="text-sm font-black text-slate-400 group-hover:text-primary transition-colors">#{entry.rank}</span>
                                    </td>
                                    <td className="px-6 py-5">
                                        <div className="flex items-center gap-3">
                                            <div className="size-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center overflow-hidden">
                                                <img src={`https://ui-avatars.com/api/?name=${entry.username}&background=random`} alt={entry.username} />
                                            </div>
                                            <span className="text-sm font-bold text-white tracking-tight">{entry.username}</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-5 text-right">
                                        <span className="text-sm font-black text-primary">+{entry.roi}%</span>
                                    </td>
                                    <td className="px-6 py-5 text-right">
                                        <span className="text-sm font-bold text-slate-300">{entry.win_rate}%</span>
                                    </td>
                                    <td className="px-6 py-5 text-right">
                                        <div className="flex items-center justify-end gap-1 text-accent-orange font-black text-xs">
                                            {entry.streak > 0 && Array.from({ length: entry.streak }).map((_, idx) => <Zap key={idx} size={12} fill="currentColor" />)}
                                            {entry.streak === 0 && <span className="text-slate-600">—</span>}
                                        </div>
                                    </td>
                                    <td className="px-6 py-5 text-right">
                                        <span className="text-[10px] font-black text-slate-500 uppercase tracking-tighter px-2 py-1 bg-white/[0.03] rounded-lg border border-white/[0.08]">
                                            {entry.tier}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}

function PodiumCard({ entry, place }: { entry: LeaderboardEntry; place: number }) {
    const isFirst = place === 1;
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: place * 0.1 }}
            className={`relative p-6 rounded-3xl border ${isFirst ? 'border-primary/30 bg-primary/[0.03]' : 'border-white/[0.05] bg-white/[0.01]'} overflow-hidden group`}
        >
            <div className="absolute top-4 right-4 text-4xl font-black text-white/5 tracking-tighter leading-none select-none">
                0{place}
            </div>

            <div className="space-y-6 relative z-10">
                <div className="flex items-center gap-4">
                    <div className={`relative ${isFirst ? 'size-20' : 'size-16'}`}>
                        <div className={`size-full rounded-2xl overflow-hidden border-2 transition-transform group-hover:scale-105 ${isFirst ? 'border-primary shadow-[0_0_20px_rgba(13,242,51,0.2)]' : 'border-slate-700'}`}>
                            <img src={`https://ui-avatars.com/api/?name=${entry.username}&background=random`} alt={entry.username} className="w-full h-full object-cover" />
                        </div>
                        {isFirst && (
                            <div className="absolute -top-3 -right-3 p-1.5 bg-yellow-500 rounded-lg shadow-lg rotate-12">
                                <Crown size={18} className="text-black" />
                            </div>
                        )}
                    </div>
                    <div>
                        <h3 className="text-xl font-black text-white tracking-tighter uppercase">{entry.username}</h3>
                        <div className="flex items-center gap-2">
                            <span className="text-[10px] font-black text-primary uppercase">VERIFIED ELITE</span>
                            <div className="size-1 bg-slate-600 rounded-full" />
                            <span className="text-[10px] font-bold text-slate-500 uppercase">{entry.tier}</span>
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                    <div className="p-3 rounded-2xl bg-white/[0.03] border border-white/[0.05]">
                        <p className="text-[10px] text-slate-500 font-black uppercase mb-1">ROI</p>
                        <div className="flex items-center gap-1.5 font-black text-primary">
                            <ArrowUpRight size={16} />
                            <span className="text-lg">+{entry.roi}%</span>
                        </div>
                    </div>
                    <div className="p-3 rounded-2xl bg-white/[0.03] border border-white/[0.05]">
                        <p className="text-[10px] text-slate-500 font-black uppercase mb-1">Win Rate</p>
                        <div className="flex items-center gap-1.5 font-black text-white">
                            <TrendingUp size={16} className="text-slate-400" />
                            <span className="text-lg">{entry.win_rate}%</span>
                        </div>
                    </div>
                </div>

                <button className={`w-full py-3 rounded-xl font-black text-[10px] uppercase tracking-widest transition-all ${isFirst ? 'bg-primary text-background-dark hover:scale-[1.02] shadow-lg shadow-primary/20' : 'bg-white/[0.05] text-white hover:bg-white/[0.1]'}`}>
                    View Detailed Analytics
                </button>
            </div>
        </motion.div>
    );
}
