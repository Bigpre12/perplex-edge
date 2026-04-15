"use client";
import { useQuery } from "@tanstack/react-query";
import { CircleDollarSign, Plus, CheckCircle, XCircle, MinusCircle } from "lucide-react";
import { useState } from "react";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import API, { isApiError } from "@/lib/api";

export default function BetTracker() {
    const { data, refetch } = useQuery({
        queryKey: ["bets"],
        queryFn: async () => {
            const res = await API.bets();
            return isApiError(res) ? { bets: [], stats: {} } : res;
        },
    });

    const [isAdding, setIsAdding] = useState(false);

    async function settleBet(id: number, result: string) {
        const res = await API.settleBet(id, result);
        if (!isApiError(res)) {
            refetch();
        }
    }

    return (
        <ErrorBoundary label="Failed to load bet tracker">
            <div className="space-y-6 p-4 pb-24">
                <div className="flex items-center justify-between">
                    <h1 className="text-2xl font-black text-white flex items-center gap-2">
                        <CircleDollarSign className="text-green-400" /> Action Tracker
                    </h1>
                    <button onClick={() => setIsAdding(!isAdding)} className="bg-green-500 text-black px-3 py-1.5 rounded-lg font-bold text-sm flex items-center gap-1">
                        <Plus size={16} /> Log Bet
                    </button>
                </div>

                {/* Stats Banner */}
                <div className="grid grid-cols-3 gap-2">
                    <StatCard label="P&L" value={`${data?.stats?.profit_loss > 0 ? '+' : ''}${data?.stats?.profit_loss || 0}u`} color={data?.stats?.profit_loss >= 0 ? "text-green-400" : "text-red-400"} />
                    <StatCard label="Win Rate" value={`${data?.stats?.win_rate || 0}%`} color="text-white" />
                    <StatCard label="Pending" value={data?.stats?.pending || 0} color="text-yellow-400" />
                </div>

                {/* Bets List */}
                <div className="space-y-3">
                    <h2 className="text-gray-400 font-bold uppercase tracking-wider text-sm">Recent Action</h2>
                    {data?.bets?.map((bet: any) => (
                        <div key={bet.id} className="bg-gray-900 border border-gray-800 rounded-xl p-4 flex justify-between items-center">
                            <div>
                                <div className="flex gap-2 items-center">
                                    <span className="font-bold text-white">{bet.player_name}</span>
                                    <span className={`text-[10px] uppercase font-bold px-1.5 py-0.5 rounded ${bet.result === 'pending' ? 'bg-yellow-500/20 text-yellow-400' :
                                        bet.result === 'win' ? 'bg-green-500/20 text-green-400' :
                                            bet.result === 'loss' ? 'bg-red-500/20 text-red-400' : 'bg-gray-500/20 text-gray-400'
                                        }`}>{bet.result}</span>
                                </div>
                                <div className="text-sm text-gray-400">
                                    {bet.pick.toUpperCase()} {bet.line} {bet.prop_type.replace("player_", "")} ({bet.odds})
                                </div>
                                <div className="text-xs text-gray-600 mt-1">{bet.bookmaker} • {bet.stake}u stake</div>
                            </div>

                            {bet.result === 'pending' && (
                                <div className="flex gap-2">
                                    <button onClick={() => settleBet(bet.id, "win")} className="p-2 bg-gray-800 rounded hover:text-green-400"><CheckCircle size={18} /></button>
                                    <button onClick={() => settleBet(bet.id, "loss")} className="p-2 bg-gray-800 rounded hover:text-red-400"><XCircle size={18} /></button>
                                    <button onClick={() => settleBet(bet.id, "push")} className="p-2 bg-gray-800 rounded hover:text-gray-400"><MinusCircle size={18} /></button>
                                </div>
                            )}
                            {bet.result !== 'pending' && (
                                <div className={`font-mono font-bold ${bet.profit_loss > 0 ? "text-green-400" : bet.profit_loss < 0 ? "text-red-400" : "text-gray-400"}`}>
                                    {bet.profit_loss > 0 ? "+" : ""}{bet.profit_loss}u
                                </div>
                            )}
                        </div>
                    ))}
                    {(!data?.bets || data.bets.length === 0) && (
                        <div className="text-center p-8 text-gray-500">No action logged yet. Get in the game!</div>
                    )}
                </div>
            </div>
        </ErrorBoundary>
    );
}

function StatCard({ label, value, color }: { label: string, value: string | number, color: string }) {
    return (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-3 text-center">
            <div className="text-xs text-gray-500 font-bold uppercase tracking-wider">{label}</div>
            <div className={`text-xl font-black ${color} mt-1`}>{value}</div>
        </div>
    );
}
