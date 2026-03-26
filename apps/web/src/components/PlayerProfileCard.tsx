"use client";

import { useQuery } from "@tanstack/react-query";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ReferenceLine, ResponsiveContainer } from "recharts";

interface Props {
    playerId: string;
    propType: string;
    line: number;
}

const fetchInsight = (id: string, prop: string, line: number) =>
    fetch(`/api/insights/player/${id}/${prop}?line=${line}`).then(r => r.json());

const fetchDvp = (id: string) =>
    fetch(`/api/dvp/player/${id}`).then(r => r.json());

// Mocking history fetch for visualization until history API is fully exposed
const fetchHistory = (id: string, prop: string) =>
    Promise.resolve([
        { game_date: "2024-02-20", actual_value: 28, line: 24.5 },
        { game_date: "2024-02-22", actual_value: 22, line: 24.5 },
        { game_date: "2024-02-24", actual_value: 31, line: 24.5 },
        { game_date: "2024-02-26", actual_value: 25, line: 24.5 },
        { game_date: "2024-02-28", actual_value: 19, line: 24.5 },
    ]);

export function PlayerProfileCard({ playerId, propType, line }: Props) {
    const { data: insight } = useQuery({
        queryKey: ["insight", playerId, propType, line],
        queryFn: () => fetchInsight(playerId, propType, line),
    });

    const { data: dvp } = useQuery({
        queryKey: ["dvp", playerId],
        queryFn: () => fetchDvp(playerId),
    });

    const { data: history } = useQuery({
        queryKey: ["history", playerId, propType],
        queryFn: () => fetchHistory(playerId, propType),
    });

    const trendIcon =
        insight?.trend === "heating_up" ? <TrendingUp className="text-green-400" size={16} /> :
            insight?.trend === "cooling_down" ? <TrendingDown className="text-red-400" size={16} /> :
                <Minus className="text-gray-400" size={16} />;

    const chartData = history?.map((h: any) => ({
        date: new Date(h.game_date).toLocaleDateString("en-US", { month: "short", day: "numeric" }),
        actual: h.actual_value,
        line: h.line,
    })) ?? [];

    return (
        <div className="bg-gray-900 border border-gray-700 rounded-2xl p-5 space-y-5 shadow-xl">
            <div className="flex justify-between items-center">
                <h3 className="text-white font-bold text-sm uppercase tracking-wider">Performance Insights</h3>
                <span className="text-xs text-gray-500">Last 15 Games</span>
            </div>

            {/* Hit Rate Badges */}
            <div className="flex gap-3 flex-wrap">
                {[["L5 Rate", insight?.recent_rate], ["Total Rate", insight?.hit_rate]].map(([label, val]) => (
                    <div key={label as string} className="flex flex-col items-center bg-gray-800 border border-gray-700 rounded-xl px-4 py-2 min-w-[80px]">
                        <span className="text-[10px] text-gray-400 uppercase font-semibold">{label}</span>
                        <span className={`text-lg font-bold ${Number(val) >= 0.7 ? "text-green-400" :
                                Number(val) >= 0.5 ? "text-yellow-400" : "text-red-400"
                            }`}>
                            {val != null && !isNaN(Number(val)) ? `${(Number(val) * 100).toFixed(0)}%` : "—"}
                        </span>
                    </div>
                ))}
                <div className="flex flex-col items-center justify-center gap-1 bg-gray-800 border border-gray-700 rounded-xl px-4 py-2">
                    <span className="text-[10px] text-gray-400 uppercase font-semibold">Momentum</span>
                    <div className="flex items-center gap-1">
                        {trendIcon}
                        <span className="text-xs text-white font-medium capitalize">{insight?.trend?.replace("_", " ") ?? "Stable"}</span>
                    </div>
                </div>
            </div>

            {/* Trend Chart */}
            {chartData.length > 0 && (
                <div className="h-40 w-full bg-gray-950/50 rounded-xl p-2 border border-gray-800/50" style={{ minWidth: 0 }}>
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={chartData}>
                            <XAxis dataKey="date" tick={{ fontSize: 10, fill: "#6b7280" }} axisLine={false} tickLine={false} />
                            <YAxis tick={{ fontSize: 10, fill: "#6b7280" }} axisLine={false} tickLine={false} hide />
                            <Tooltip
                                contentStyle={{ background: "#111827", border: "1px solid #374151", borderRadius: 8 }}
                                labelStyle={{ color: "#9ca3af", fontSize: 10 }}
                                itemStyle={{ color: "#fff", fontSize: 12, fontWeight: "bold" }}
                            />
                            <ReferenceLine y={line} stroke="#6366f1" strokeDasharray="3 3" label={{ value: `Line ${line}`, fill: "#818cf8", fontSize: 9, position: 'insideLeft' }} />
                            <Line
                                type="monotone"
                                dataKey="actual"
                                stroke="#10b981"
                                strokeWidth={3}
                                dot={{ r: 4, fill: "#10b981", strokeWidth: 2, stroke: "#111827" }}
                                activeDot={{ r: 6, strokeWidth: 0 }}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            )}

            {/* DvP Matchup */}
            {dvp?.dvp && (
                <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-4">
                    <div className="flex items-center gap-2 mb-3">
                        <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse" />
                        <p className="text-[10px] text-gray-400 uppercase font-bold tracking-widest">Matchup vs {dvp.opponent}</p>
                    </div>
                    <div className="grid grid-cols-1 gap-2">
                        {Object.entries(dvp.dvp).map(([pt, data]: [string, any]) => (
                            <div key={pt} className="flex justify-between items-center text-sm bg-gray-900/40 rounded-lg px-3 py-2 border border-gray-700/30">
                                <span className="text-gray-300 capitalize text-xs">{pt.replace("player_", "").replace("_", " ")}</span>
                                <span className={`text-[11px] font-bold px-2 py-0.5 rounded-full ${data.rank === "favorable" ? "bg-green-500/10 text-green-400 border border-green-500/20" :
                                        data.rank === "neutral" ? "bg-yellow-500/10 text-yellow-400 border border-yellow-500/20" :
                                            "bg-red-500/10 text-red-400 border border-red-500/20"
                                    }`}>{data.label ?? "—"}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
