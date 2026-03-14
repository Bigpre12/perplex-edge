"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { KalshiPortfolio } from "@/types/kalshi";
import { Skeleton } from "@/components/ui/Skeleton";
import { Button } from "@/components/ui/Button";
import { toast } from "react-hot-toast";

export function KalshiPortfolioView() {
    const queryClient = useQueryClient();
    const { data: portfolio, isLoading } = useQuery<KalshiPortfolio>({
        queryKey: ["kalshi-portfolio"],
        queryFn: async () => {
            const res = await fetch("/api/kalshi/portfolio");
            if (!res.ok) throw new Error("Failed to fetch portfolio");
            return res.json();
        },
        refetchInterval: 30000,
    });

    const cancelMutation = useMutation({
        mutationFn: async (orderId: string) => {
            const res = await fetch(`/api/kalshi/orders/${orderId}`, { method: "DELETE" });
            if (!res.ok) throw new Error("Cancellation failed");
            return res.json();
        },
        onSuccess: () => {
            toast.success("Order cancelled");
            queryClient.invalidateQueries({ queryKey: ["kalshi-portfolio"] });
        }
    });

    if (isLoading) {
        return <Skeleton className="h-40 w-full" />;
    }

    return (
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6 h-full flex flex-col">
            <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-bold flex items-center gap-2">
                    <span className="text-purple-400">⚡</span> Kalshi Portfolio
                </h3>
                <div className="text-right">
                    <div className="text-[10px] text-white/40 uppercase">Total Balance</div>
                    <div className="text-lg font-mono text-white">${portfolio?.balance.toLocaleString() || "0.00"}</div>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto max-h-[300px]">
                {portfolio?.positions && portfolio.positions.length > 0 ? (
                    <div className="space-y-4">
                        {portfolio.positions.map((pos, idx) => (
                            <div key={`${pos.ticker}-${idx}`} className="bg-white/5 rounded-xl p-4 border border-white/5 hover:border-white/10 transition-all group">
                                <div className="flex justify-between items-start mb-2">
                                    <div>
                                        <div className="text-xs font-bold text-white mb-1">{pos.title || pos.ticker}</div>
                                        <div className="flex items-center gap-2">
                                            <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded uppercase ${pos.side === 'yes' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                                                {pos.side}
                                            </span>
                                            <span className="text-[10px] text-white/40">{pos.count} contracts @ {pos.avg_cost}¢</span>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <div className={`text-sm font-bold ${pos.pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                            {pos.pnl >= 0 ? '+' : ''}${pos.pnl.toFixed(2)}
                                        </div>
                                        <div className="text-[10px] text-white/40">Value: ${pos.current_value.toFixed(2)}</div>
                                    </div>
                                </div>
                                <div className="opacity-0 group-hover:opacity-100 transition-opacity pt-2">
                                    <Button
                                        size="sm"
                                        variant="ghost"
                                        className="h-7 w-full text-[10px] text-red-400/60 hover:text-red-400 hover:bg-red-500/10"
                                        onClick={() => cancelMutation.mutate(pos.ticker)}
                                    >
                                        Sell Position
                                    </Button>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="h-32 flex flex-col items-center justify-center text-white/20 gap-2">
                        <div className="w-10 h-10 border-2 border-dashed border-white/10 rounded-full flex items-center justify-center">
                            <span className="text-lg">💰</span>
                        </div>
                        <p className="text-xs">No active positions</p>
                    </div>
                )}
            </div>
        </div>
    );
}
