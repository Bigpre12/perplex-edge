"use client";

import { useQuery } from "@tanstack/react-query";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/Tabs";
import { Skeleton } from "@/components/ui/Skeleton";
import { useState } from "react";

export function KalshiEventsTab({ onSelect }: { onSelect: (ticker: string) => void }) {
    const { data: events, isLoading } = useQuery({
        queryKey: ["kalshi-events"],
        queryFn: async () => {
            const res = await fetch("/api/kalshi/events");
            if (!res.ok) throw new Error("Failed to fetch events");
            return res.json();
        },
        refetchInterval: 60000,
    });

    if (isLoading) {
        return <Skeleton className="h-64 w-full" />;
    }

    const categories = ["Sports", "Politics", "Economics", "All"];

    return (
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6 w-full">
            <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
                <span className="text-purple-400">⚡</span> Kalshi Events
            </h3>

            <Tabs defaultValue="All" className="w-full">
                <TabsList className="bg-white/5 border border-white/10 mb-6 flex-wrap h-auto p-1">
                    {categories.map(cat => (
                        <TabsTrigger key={cat} value={cat} className="px-6 data-[state=active]:bg-purple-600 data-[state=active]:text-white">
                            {cat}
                        </TabsTrigger>
                    ))}
                </TabsList>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {events?.map((event: any, idx: number) => (
                        <div
                            key={`${event.event_ticker}-${idx}`}
                            className="bg-white/5 rounded-2xl p-5 border border-white/5 hover:border-purple-500/50 hover:bg-purple-500/5 transition-all cursor-pointer group flex flex-col justify-between"
                            onClick={() => onSelect(event.event_ticker)}
                        >
                            <div>
                                <div className="flex justify-between items-start mb-3">
                                    <span className="text-[10px] uppercase tracking-widest text-purple-400 font-bold bg-purple-400/10 px-2 py-0.5 rounded">
                                        {event.category || "General"}
                                    </span>
                                    <span className="text-[10px] text-white/30">{new Date(event.close_time).toLocaleDateString()}</span>
                                </div>
                                <h4 className="font-bold text-sm leading-snug mb-4 group-hover:text-purple-400 transition-colors">
                                    {event.title}
                                </h4>
                            </div>

                            <div className="flex justify-between items-end border-t border-white/5 pt-4">
                                <div className="text-xs">
                                    <div className="text-[10px] text-white/40 uppercase mb-1">Last Price</div>
                                    <div className="text-lg font-mono text-white">52¢</div>
                                </div>
                                <div className="text-right">
                                    <div className="text-[10px] text-white/40 uppercase mb-1">Volume</div>
                                    <div className="text-xs text-white/60">24.5k contracts</div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </Tabs>
        </div>
    );
}
