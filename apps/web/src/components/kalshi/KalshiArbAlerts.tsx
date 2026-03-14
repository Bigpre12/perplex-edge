"use client";

import { useQuery } from "@tanstack/react-query";
import { KalshiArbAlert } from "@/types/kalshi";
import { Skeleton } from "@/components/ui/Skeleton";
import { Button } from "@/components/ui/Button";
import { useEffect, useState } from "react";

export function KalshiArbAlerts() {
    const [lastArbCount, setLastArbCount] = useState(0);
    const { data: alerts, isLoading } = useQuery<KalshiArbAlert[]>({
        queryKey: ["kalshi-arb"],
        queryFn: async () => {
            const res = await fetch("/api/kalshi/arb");
            if (!res.ok) throw new Error("Failed to fetch arb alerts");
            return res.json();
        },
        refetchInterval: 15000,
    });

    useEffect(() => {
        if (alerts && alerts.length > lastArbCount) {
            setLastArbCount(alerts.length);
            // Flash animation could be triggered here via a state/ref
        }
    }, [alerts, lastArbCount]);

    if (isLoading) {
        return <div className="space-y-2"><Skeleton className="h-40 w-full" /></div>;
    }

    return (
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6 overflow-hidden">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                <span className="text-purple-400">⚡</span> Kalshi Arb Alerts
            </h3>
            {alerts && alerts.length > 0 ? (
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead>
                            <tr className="text-white/40 border-b border-white/10 text-xs">
                                <th className="pb-3">Player</th>
                                <th className="pb-3">Kalshi YES</th>
                                <th className="pb-3">Book NO</th>
                                <th className="pb-3">Margin</th>
                                <th className="pb-3">Action</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {alerts.map((alert, idx) => (
                                <tr key={`${alert.ticker}-${idx}`} className="hover:bg-white/5 transition-colors border-l-2 border-transparent hover:border-green-500 animate-pulse-border">
                                    <td className="py-4 font-medium">{alert.player_name}</td>
                                    <td className="py-4 text-white/60">{alert.kalshi_yes}¢</td>
                                    <td className="py-4 text-white/60">{alert.book_no_implied}%</td>
                                    <td className="py-4 text-green-400 font-bold">
                                        +{alert.profit_margin}%
                                    </td>
                                    <td className="py-4">
                                        <Button size="sm" variant="outline" className="border-green-500/50 text-green-400 hover:bg-green-500 hover:text-white">
                                            Trade Now
                                        </Button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            ) : (
                <div className="h-40 flex items-center justify-center text-white/30 text-sm">
                    No arbitrage detected — checking every 15s
                </div>
            )}
            <style jsx>{`
        @keyframes pulse-border {
          0% { border-color: transparent; }
          50% { border-color: rgb(34 197 94); }
          100% { border-color: transparent; }
        }
        .animate-pulse-border {
          animation: pulse-border 2s infinite;
        }
      `}</style>
        </div>
    );
}
