"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Trophy, Medal, Star, TrendingUp, Users, Loader2, Search, ArrowRight } from "lucide-react";

import { API_ENDPOINTS } from "@/lib/apiConfig";

export default function Leaderboard() {
    const [leaderboard, setLeaderboard] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchLeaderboard = async () => {
            try {
                const res = await fetch(API_ENDPOINTS.LEADERBOARD);
                const data = await res.json();
                setLeaderboard(data.leaderboard);
            } catch (err) {
                console.error("Failed to load leaderboard:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchLeaderboard();
    }, []);

    if (loading) {
        return (
            <div className="h-[60vh] flex flex-col items-center justify-center gap-4 text-primary text-center">
                <Loader2 size={40} className="animate-spin" />
                <p className="text-sm font-bold uppercase tracking-widest text-slate-400">Verifying Sharp Status...</p>
            </div>
        );
    }

    const top3 = leaderboard.slice(0, 3);
    const others = leaderboard.slice(3);

    return (
        <div className="max-w-6xl mx-auto pb-24 px-4 sm:px-6">
            <header className="mb-12">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-500 text-[10px] font-black uppercase tracking-widest mb-3">
                    <Trophy size={12} /> Global Rankings
                </div>
                <h1 className="text-4xl font-black text-white tracking-tight">The Sharpest 100</h1>
                <p className="text-slate-400 mt-2 max-w-2xl text-sm leading-relaxed">
                    Ranked by verified 30-day ROI. Only the most consistent institutional-grade bettors make the global leaderboard.
                </p>
            </header>

            {/* Podium */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-20 items-end">
                {/* 2nd Place */}
                <div className="order-2 md:order-1">
                    <PodiumCard user={top3[1]} rank={2} color="text-slate-300" border="border-slate-300/20" />
                </div>
                {/* 1st Place */}
                <div className="order-1 md:order-2">
                    <PodiumCard user={top3[0]} rank={1} color="text-amber-400" border="border-amber-400/30" scale />
                </div>
                {/* 3rd Place */}
                <div className="order-3">
                    <PodiumCard user={top3[2]} rank={3} color="text-amber-700" border="border-amber-700/20" />
                </div>
            </div>

            {/* Table */}
            <div className="glass-premium rounded-3xl border-white/5 overflow-hidden shadow-2xl shadow-black/50">
                <div className="px-8 py-6 border-b border-white/5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white/[0.01]">
                    <h3 className="text-sm font-bold text-white uppercase tracking-widest flex items-center gap-2">
                        <TrendingUp size={16} className="text-emerald-500" /> Rolling Performance
                    </h3>
                    <div className="relative">
                        <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                        <input
                            placeholder="Find bettor..."
                            className="w-full sm:w-64 bg-black/40 border border-white/5 rounded-full pl-9 pr-4 py-2 text-xs text-white placeholder:text-slate-600 focus:outline-none focus:border-emerald-500/50 transition-colors"
                        />
                    </div>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead>
                            <tr className="text-[10px] uppercase tracking-widest text-slate-500 font-black border-b border-white/5 bg-white/[0.01]">
                                <th className="px-8 py-5">Rank</th>
                                <th className="px-8 py-5">Bettor</th>
                                <th className="px-8 py-5">Verified ROI</th>
                                <th className="px-8 py-5 text-right">Win Rate</th>
                                <th className="px-8 py-5 text-right">Volume</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/[0.03]">
                            {others.map((user) => (
                                <tr key={user.username} className="hover:bg-white/[0.02] transition-colors group">
                                    <td className="px-8 py-5 font-black text-slate-500">#{user.rank}</td>
                                    <td className="px-8 py-5">
                                        <div className="flex items-center gap-3">
                                            <div className="size-9 rounded-xl bg-surface border border-white/5 shadow-inner flex items-center justify-center text-[11px] font-black text-emerald-500">
                                                {user.username.slice(0, 2).toUpperCase()}
                                            </div>
                                            <span className="font-bold text-white group-hover:text-emerald-400 transition-colors">{user.username}</span>
                                        </div>
                                    </td>
                                    <td className="px-8 py-5 font-mono font-black text-emerald-500">+{user.roi}%</td>
                                    <td className="px-8 py-5 text-right">
                                        <span className="px-2.5 py-1.5 rounded-lg bg-white/5 text-[10px] font-black text-slate-300 border border-white/10">{user.win_rate}%</span>
                                    </td>
                                    <td className="px-8 py-5 text-right text-xs text-slate-500 font-bold tracking-tight">{user.volume} Picks</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}

function PodiumCard({ user, rank, color, border, scale = false }: any) {
    if (!user) return null;
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            whileHover={{ y: scale ? -10 : -5, scale: scale ? 1.07 : 1.02 }}
            className={`glass-premium p-10 rounded-[2.5rem] text-center relative ${border} transition-shadow ${scale ? 'md:-translate-y-8 shadow-[0_40px_80px_-20px_rgba(16,185,129,0.2)]' : 'shadow-xl'}`}
        >
            <div className={`absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 size-14 rounded-full glass-premium border-inherit flex items-center justify-center font-black text-xl shadow-lg shadow-black/20 ${color}`}>
                {rank === 1 ? <Star size={24} fill="currentColor" /> : rank}
            </div>

            <div className="relative mx-auto size-24 mb-6">
                <div className="absolute inset-0 bg-emerald-500/10 blur-2xl rounded-full" />
                <div className="relative size-24 rounded-3xl bg-[#0a0a0a] border border-white/10 flex items-center justify-center text-3xl font-black text-white shadow-2xl">
                    {user.username.slice(0, 1)}
                </div>
                {rank === 1 && (
                    <div className="absolute -top-2 -right-2 size-8 bg-amber-400 text-black rounded-full flex items-center justify-center shadow-lg transform rotate-12">
                        <Trophy size={16} />
                    </div>
                )}
            </div>

            <p className="text-xl font-black text-white mb-2">{user.username}</p>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-[10px] font-black uppercase tracking-widest text-slate-400 mb-8">
                Sharp Level: <span className={rank === 1 ? 'text-amber-400' : 'text-emerald-500'}>ELITE</span>
            </div>

            <div className="space-y-3">
                <div className="p-5 rounded-3xl bg-black/40 border border-white/5 flex items-center justify-between">
                    <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">30D ROI</span>
                    <span className={`font-mono font-black text-2xl ${color}`}>+{user.roi}%</span>
                </div>
                <div className="flex gap-3">
                    <div className="flex-1 p-3 rounded-2xl bg-white/[0.02] border border-white/5">
                        <p className="text-[8px] font-black text-slate-500 uppercase tracking-widest mb-1">Win Rate</p>
                        <p className="text-xs font-black text-white">{user.win_rate}%</p>
                    </div>
                    <div className="flex-1 p-3 rounded-2xl bg-white/[0.02] border border-white/5">
                        <p className="text-[8px] font-black text-slate-500 uppercase tracking-widest mb-1">Volume</p>
                        <p className="text-xs font-black text-white">{user.volume}</p>
                    </div>
                </div>
            </div>
        </motion.div>
    );
}
