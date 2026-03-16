"use client";

import { useQuery } from "@tanstack/react-query";
import { useKalshiPrices } from "@/hooks/useKalshiPrices";
import { Skeleton } from "@/components/ui/Skeleton";

interface KalshiOrderBookProps {
    ticker: string;
}

export function KalshiOrderBook({ ticker }: KalshiOrderBookProps) {
    const { data: orderbook, isLoading } = useQuery({
        queryKey: ["kalshi-orderbook", ticker],
        queryFn: async () => {
            const res = await fetch(`/api/kalshi/markets/${ticker}/orderbook`);
            if (!res.ok) throw new Error("Failed to fetch orderbook");
            return res.json();
        },
        refetchInterval: 5000,
        enabled: !!ticker,
    });

    const livePrices = useKalshiPrices([ticker]);
    const currentPrice = livePrices[ticker]?.last_price;

    if (isLoading) {
        return <Skeleton className="h-64 w-full" />;
    }

    const bids = orderbook?.bids || [];
    const asks = orderbook?.asks || [];

    return (
        <div className="kalshi-orderbook">
            <h3 className="text-xl font-bold mb-4 flex items-center justify-between">
                <span className="flex items-center gap-2">
                    <span className="text-purple-400">⚡</span> Order Book
                    {ticker && <span className="text-xs text-white/30 bg-white/5 py-1 px-2 rounded">{ticker}</span>}
                </span>
                {currentPrice && <span className="text-sm font-mono text-purple-400">{currentPrice}¢</span>}
            </h3>

            <div className="kalshi-row">
                {/* Asks (Sellers) */}
                <div className="flex flex-col-reverse justify-start overflow-y-auto pr-2">
                    {asks.slice(0, 10).map((ask: [number, number], i: number) => (
                        <div key={i} className="flex justify-between items-center text-xs py-1 hover:bg-red-500/10 rounded px-2 transition-colors">
                            <span className="text-red-400 font-bold">{ask[0]}¢</span>
                            <span className="text-white/40">{ask[1]} contracts</span>
                             <div className={`kalshi-depth-bar w-dp-${Math.min(Math.round(ask[1] / 10) * 10 || 10, 100)}`} />
                        </div>
                    ))}
                    <div className="text-[10px] text-red-500/40 uppercase mb-2">Asks / Sell</div>
                </div>

                {/* Bids (Buyers) */}
                <div className="flex flex-col justify-start overflow-y-auto pl-2">
                    <div className="text-[10px] text-green-500/40 uppercase mb-2">Bids / Buy</div>
                    {bids.slice(0, 10).map((bid: [number, number], i: number) => (
                        <div key={i} className="flex justify-between items-center text-xs py-1 hover:bg-green-500/10 rounded px-2 transition-colors">
                            <span className="text-green-400 font-bold">{bid[0]}¢</span>
                            <span className="text-white/40">{bid[1]} contracts</span>
                        </div>
                    ))}
                </div>
            </div>

            <div className="mt-4 pt-4 border-t border-white/10 flex justify-between text-[10px] text-white/30 italic">
                <span>Real-time via Kalshi Elite API</span>
                <span>Depth: 10 levels</span>
            </div>
        </div>
    );
}
