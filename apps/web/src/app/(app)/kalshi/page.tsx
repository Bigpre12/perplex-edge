"use client";

import { useState } from "react";
import { KalshiEVSignals } from "@/components/kalshi/KalshiEVSignals";
import { KalshiArbAlerts } from "@/components/kalshi/KalshiArbAlerts";
import { KalshiMarkets } from "@/components/kalshi/KalshiMarkets";
import { KalshiOrderBook } from "@/components/kalshi/KalshiOrderBook";
import { KalshiTrader } from "@/components/kalshi/KalshiTrader";
import { KalshiPortfolioView } from "@/components/kalshi/KalshiPortfolio";
import { KalshiEventsTab } from "@/components/kalshi/KalshiEventsTab";
import GateLock from "@/components/GateLock";
import { Button } from "@/components/ui/Button";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue
} from "@/components/ui/Select";

export default function KalshiElitePage() {
    const [activeSport, setActiveSport] = useState("NBA");
    const [selectedTicker, setSelectedTicker] = useState<string>("");

    return (
        <GateLock feature="kalshi_elite">
            <div className="min-h-screen bg-black text-white p-6 space-y-8 max-w-[1600px] mx-auto">
                {/* Top Bar */}
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white/5 border border-white/10 rounded-2xl p-6">
                    <div>
                        <h1 className="text-3xl font-black tracking-tighter flex items-center gap-3">
                            <span className="text-purple-500">KΛLSHI</span> ELITE
                            <span className="text-[10px] bg-purple-500/20 text-purple-400 px-2 py-0.5 rounded-full border border-purple-500/30 font-bold uppercase tracking-widest animate-pulse">
                                Live
                            </span>
                        </h1>
                        <p className="text-white/40 text-sm mt-1">Institutional-grade predictive market intelligence & arbitrage tools</p>
                    </div>

                    <div className="flex items-center gap-3 w-full md:w-auto">
                        <Select value={activeSport} onValueChange={setActiveSport}>
                            <SelectTrigger className="w-full md:w-40 bg-white/5 border-white/10">
                                <SelectValue placeholder="Sport" />
                            </SelectTrigger>
                            <SelectContent className="bg-[#0f0f0f] border-white/10">
                                <SelectItem value="NBA">NBA Basketball</SelectItem>
                                <SelectItem value="NFL">NFL Football</SelectItem>
                                <SelectItem value="MLB">MLB Baseball</SelectItem>
                                <SelectItem value="NHL">NHL Hockey</SelectItem>
                                <SelectItem value="All">All Markets</SelectItem>
                            </SelectContent>
                        </Select>
                        <Button variant="outline" size="icon" className="bg-white/5 border-white/10 hover:bg-white/10" onClick={() => window.location.reload()}>
                            <span className="text-xs">🔄</span>
                        </Button>
                    </div>
                </div>

                {/* Core Intelligence Grid */}
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
                    <KalshiEVSignals sport={activeSport} onTrade={(t) => setSelectedTicker(t)} />
                    <KalshiArbAlerts />
                </div>

                {/* Market Analysis & Execution */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    <div className="lg:col-span-1 h-full">
                        <KalshiMarkets sport={activeSport} onSelect={(t) => setSelectedTicker(t)} />
                    </div>
                    <div className="lg:col-span-1 h-full">
                        <KalshiOrderBook ticker={selectedTicker} />
                    </div>
                    <div className="lg:col-span-1 h-full flex flex-col gap-8">
                        <KalshiTrader initialTicker={selectedTicker} />
                        <KalshiPortfolioView />
                    </div>
                </div>

                {/* Events Explorer */}
                <div className="w-full">
                    <KalshiEventsTab onSelect={(t) => setSelectedTicker(t)} />
                </div>

                {/* Footer Credit */}
                <div className="text-center py-8 text-white/10 text-[10px] uppercase tracking-[0.2em] font-medium">
                    Powered by Kalshi Trading API v2 ⚡ LUCRIX Institutional Engine
                </div>
            </div>
        </GateLock>
    );
}
