"use client";

import { useQuery } from "@tanstack/react-query";
import { KalshiMarket } from "@/types/kalshi";
import { Skeleton } from "@/components/ui/Skeleton";
import { Input } from "@/components/ui/Input";
import { useState } from "react";

interface KalshiMarketsProps {
    sport: string;
    onSelect: (ticker: string) => void;
}

export function KalshiMarkets({ sport, onSelect }: KalshiMarketsProps) {
    const [filter, setFilter] = useState("");
    const { data: markets, isLoading } = useQuery<KalshiMarket[]>({
        queryKey: ["kalshi-markets", sport],
        queryFn: async () => {
            const res = await fetch(`/api/kalshi/markets?sport=${sport}`);
            if (!res.ok) throw new Error("Failed to fetch markets");
            return res.json();
        },
        refetchInterval: 30000,
    });

    const filteredMarkets = markets?.filter(m =>
        m.title.toLowerCase().includes(filter.toLowerCase()) ||
        m.ticker.toLowerCase().includes(filter.toLowerCase())
    );

    if (isLoading) {
        return <div className="space-y-2"><Skeleton className="h-40 w-full" /></div>;
    }

    return (
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6 h-full flex flex-col">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-bold flex items-center gap-2">
                    <span className="text-purple-400">⚡</span> Kalshi Markets
                </h3>
                <Input
                    placeholder="Filter markets..."
                    className="w-48 bg-white/5 border-white/10 text-xs"
                    value={filter}
                    onChange={(e) => setFilter(e.target.value)}
                />
            </div>
            <div className="flex-1 overflow-y-auto max-h-[400px]">
                <table className="w-full text-left">
                    <thead className="sticky top-0 bg-[#0a0a0a] z-10">
                        <tr className="text-white/40 border-b border-white/10 text-xs">
                            <th className="pb-3">Title</th>
                            <th className="pb-3">YES Bid/Ask</th>
                            <th className="pb-3">Volume</th>
                            <th className="pb-3">Closes</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {filteredMarkets?.map((market) => (
                            <tr
                                key={market.ticker}
                                className="hover:bg-white/5 cursor-pointer transition-colors"
                                onClick={() => onSelect(market.ticker)}
                            >
                                <td className="py-4 w-1/2">
                                    <div className="font-medium text-sm line-clamp-2">{market.title}</div>
                                    <div className="text-[10px] text-white/30 uppercase tracking-tighter">{market.ticker}</div>
                                </td>
                                <td className="py-4 text-xs">
                                    <span className="text-green-400">{market.yes_bid || '-'}¢</span>
                                    <span className="mx-1 text-white/20">/</span>
                                    <span className="text-red-400">{market.yes_ask || '-'}¢</span>
                                </td>
                                <td className="py-4 text-xs text-white/60">{market.volume.toLocaleString()}</td>
                                <td className="py-4 text-[10px] text-white/40">
                                    {new Date(market.close_time).toLocaleDateString()}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
