"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Trash2, TrendingUp, Filter, BarChart3, ChevronRight } from "lucide-react";

interface System {
    id: number;
    name: string;
    filters: Record<string, any>;
    total_bets: number;
    wins: number;
    roi: number;
    units_profit: number;
}

export function SavedSystems({ userId }: { userId: string }) {
    const qc = useQueryClient();

    const { data: systems = [], isLoading } = useQuery<System[]>({
        queryKey: ["systems", userId],
        queryFn: () => fetch(`/api/systems/user/${userId}`).then(r => r.json()),
    });

    const deleteMutation = useMutation({
        mutationFn: (id: number) => fetch(`/api/systems/${id}`, { method: "DELETE" }),
        onSuccess: () => qc.invalidateQueries({ queryKey: ["systems", userId] }),
    });

    if (isLoading) return <div className="space-y-4 animate-pulse">
        {[1, 2].map(i => <div key={i} className="h-24 bg-gray-900 border border-gray-800 rounded-xl" />)}
    </div>;

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <h2 className="text-white font-black text-xs uppercase tracking-[0.2em] flex items-center gap-2">
                    <TrendingUp size={14} className="text-blue-400" /> My Saved Systems
                </h2>
                <span className="text-[10px] text-gray-500 font-bold uppercase">{systems.length} Running</span>
            </div>

            {systems.length === 0 && (
                <div className="bg-gray-900/50 border border-gray-800 border-dashed rounded-2xl p-8 text-center">
                    <Filter size={24} className="mx-auto text-gray-700 mb-3" />
                    <p className="text-gray-500 text-sm font-medium">No saved systems yet.</p>
                    <p className="text-gray-600 text-[11px] mt-1 max-w-[200px] mx-auto uppercase tracking-wider font-bold">
                        Save a filter set from the dashboard to track its historical ROI.
                    </p>
                </div>
            )}

            {systems.map((s: System) => (
                <div key={s.id} className="group relative bg-gray-900 border border-gray-800 hover:border-blue-500/30 rounded-2xl p-5 flex justify-between items-center transition-all duration-300 shadow-lg hover:shadow-blue-500/5 overflow-hidden">
                    <div className="absolute top-0 left-0 w-1 h-full bg-blue-500 opacity-0 group-hover:opacity-100 transition-opacity" />

                    <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                            <p className="text-white font-black text-sm uppercase tracking-wider">{s.name}</p>
                            <div className="h-3 w-px bg-gray-800" />
                            <span className="text-[10px] text-gray-500 font-bold uppercase">{s.total_bets} Bets Tracked</span>
                        </div>

                        <div className="flex gap-4 mt-2">
                            <div className="flex flex-col">
                                <span className="text-[9px] text-gray-600 font-black uppercase tracking-widest">ROI</span>
                                <span className={`text-md font-black ${s.roi >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                                    {s.roi >= 0 ? "+" : ""}{s.roi.toFixed(1)}%
                                </span>
                            </div>
                            <div className="flex flex-col">
                                <span className="text-[9px] text-gray-600 font-black uppercase tracking-widest">PnL</span>
                                <span className={`text-md font-black ${s.units_profit >= 0 ? "text-blue-400" : "text-gray-400"}`}>
                                    {s.units_profit >= 0 ? "+" : ""}{s.units_profit.toFixed(2)}<span className="text-[10px] ml-0.5">u</span>
                                </span>
                            </div>
                            <div className="flex flex-col">
                                <span className="text-[9px] text-gray-600 font-black uppercase tracking-widest">Record</span>
                                <span className="text-md font-black text-gray-300">
                                    {s.wins}<span className="text-[10px] text-gray-600 mx-0.5">W</span> {s.total_bets - s.wins}<span className="text-[10px] text-gray-600 mx-0.5">L</span>
                                </span>
                            </div>
                        </div>
                    </div>

                    <div className="flex items-center gap-3">
                        <button
                            className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-gray-400 hover:text-white transition-all shadow-inner border border-gray-700/50"
                            title="View Detailed Analytics"
                        >
                            <BarChart3 size={16} />
                        </button>
                        <button
                            onClick={() => deleteMutation.mutate(s.id)}
                            className="p-2 bg-gray-800 hover:bg-rose-500/10 rounded-lg text-gray-600 hover:text-rose-400 transition-all border border-gray-700/50"
                        >
                            <Trash2 size={16} />
                        </button>
                        <ChevronRight size={16} className="text-gray-800 group-hover:text-blue-500 transition-colors" />
                    </div>
                </div>
            ))}
        </div>
    );
}
