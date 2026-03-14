"use client";
import { useState, useEffect } from "react";
import { TrendingUp, Calendar, ChevronRight } from "lucide-react";
import api from "@/lib/api";

export default function MarketsPage() {
    const [slate, setSlate] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchSlate = async () => {
            setLoading(true);
            const res = await api.get("/api/props/slate/today?sport=basketball_nba");
            setSlate(Array.isArray(res) ? res : []);
            setLoading(false);
        };
        fetchSlate();
    }, []);

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-bold flex items-center gap-3">
                        <TrendingUp className="w-8 h-8 text-[#F5C518]" />
                        Full Market Odds
                    </h1>
                    <p className="text-slate-400 mt-1">Deep liquidity views and cross-book comparison.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {loading ? (
                    <p className="text-slate-500">Loading today's slate...</p>
                ) : slate.length === 0 ? (
                    <p className="text-slate-500">No games scheduled for today.</p>
                ) : slate.map((game, i) => (
                    <div key={i} className="bg-[#12121e] border border-white/5 p-6 rounded-2xl hover:border-white/10 transition-all group">
                        <div className="flex justify-between items-start mb-4">
                            <div className="flex items-center gap-2 text-xs font-bold text-[#F5C518] uppercase">
                                <Calendar className="w-3 h-3" />
                                {new Date(game.commence_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </div>
                            <span className="text-[10px] bg-white/5 text-slate-500 px-2 py-0.5 rounded-full">{game.status}</span>
                        </div>

                        <div className="flex justify-between items-center mb-6">
                            <div className="text-center flex-1">
                                <p className="font-bold text-lg">{game.away_team}</p>
                                <p className="text-xs text-slate-500 mt-1">AWAY</p>
                            </div>
                            <div className="px-4 text-slate-700 font-bold italic">VS</div>
                            <div className="text-center flex-1">
                                <p className="font-bold text-lg">{game.home_team}</p>
                                <p className="text-xs text-slate-500 mt-1">HOME</p>
                            </div>
                        </div>

                        <button className="w-full bg-white/5 hover:bg-[#F5C518] hover:text-black py-3 rounded-xl font-bold text-sm transition-all flex items-center justify-center gap-2 group-hover:translate-y-[-2px]">
                            View All Markets
                            <ChevronRight className="w-4 h-4" />
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
}
