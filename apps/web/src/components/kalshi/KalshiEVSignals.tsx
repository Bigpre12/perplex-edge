"use client";

import { useQuery } from "@tanstack/react-query";
import { KalshiEVSignal } from "@/types/kalshi";
import { useKalshiPrices } from "@/hooks/useKalshiPrices";
import { Skeleton } from "@/components/ui/Skeleton";
import { Button } from "@/components/ui/Button";

interface KalshiEVSignalsProps {
    sport: string;
    onTrade: (ticker: string) => void;
}

export function KalshiEVSignals({ sport, onTrade }: KalshiEVSignalsProps) {
    const { data: signals, isLoading } = useQuery<KalshiEVSignal[]>({
        queryKey: ["kalshi-ev", sport],
        queryFn: async () => {
            const res = await fetch(`/api/kalshi/ev?sport=${sport}`);
            if (!res.ok) throw new Error("Failed to fetch EV signals");
            return res.json();
        },
        refetchInterval: 20000,
    });

    const tickers = signals?.map((s) => s.ticker) || [];
    const livePrices = useKalshiPrices(tickers);

    if (isLoading) {
        return <div className="space-y-2"><Skeleton className="h-40 w-full" /></div>;
    }

    return (
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6 overflow-hidden">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                <span className="text-purple-400">⚡</span> Kalshi EV Signals
            </h3>
            <div className="overflow-x-auto">
                <table className="w-full text-left">
                    <thead>
                        <tr className="text-white/40 border-b border-white/10 text-xs">
                            <th className="pb-3">Player</th>
                            <th className="pb-3">Prop</th>
                            <th className="pb-3">Kalshi %</th>
                            <th className="pb-3">Book %</th>
                            <th className="pb-3">Edge</th>
                            <th className="pb-3">Action</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {signals?.map((signal) => {
                            const liveData = livePrices[signal.ticker];
                            const displayProb = liveData ? (liveData.last_price || signal.kalshi_prob) : signal.kalshi_prob;

                            return (
                                <tr key={signal.ticker} className="hover:bg-white/5 transition-colors group">
                                    <td className="py-4 font-medium">{signal.player_name}</td>
                                    <td className="py-4 text-white/60">{signal.prop_label}</td>
                                    <td className="py-4 text-purple-400">{displayProb}%</td>
                                    <td className="py-4 text-white/60">{signal.book_prob}%</td>
                                    <td className={`py-4 font-bold ${signal.edge > 5 ? 'text-green-400' : signal.edge > 3 ? 'text-yellow-400' : 'text-white/30'}`}>
                                        {signal.edge > 0 ? '+' : ''}{signal.edge}%
                                    </td>
                                    <td className="py-4">
                                        <Button
                                            size="sm"
                                            className="bg-purple-600 hover:bg-purple-500 text-white font-bold"
                                            onClick={() => onTrade(signal.ticker)}
                                        >
                                            {signal.recommendation === "BUY NO" ? "BUY NO" : "BUY YES"}
                                        </Button>
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
