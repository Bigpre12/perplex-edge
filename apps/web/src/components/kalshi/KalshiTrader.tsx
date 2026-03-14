"use client";

import { useState, useMemo } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/Tabs";
import { toast } from "react-hot-toast";

interface KalshiTraderProps {
    initialTicker?: string;
}

export function KalshiTrader({ initialTicker }: KalshiTraderProps) {
    const [ticker, setTicker] = useState(initialTicker || "");
    const [side, setSide] = useState<"yes" | "no">("yes");
    const [count, setCount] = useState(1);
    const [price, setPrice] = useState(50);
    const [type, setType] = useState<"limit" | "market">("limit");
    const [showConfirm, setShowConfirm] = useState(false);

    const queryClient = useQueryClient();

    const totalCost = useMemo(() => (count * price) / 100, [count, price]);

    const mutation = useMutation({
        mutationFn: async (order: any) => {
            const res = await fetch("/api/kalshi/orders", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(order),
            });
            if (!res.ok) throw new Error("Order placement failed");
            return res.json();
        },
        onSuccess: () => {
            toast.success("Order placed successfully!");
            setShowConfirm(false);
            queryClient.invalidateQueries({ queryKey: ["kalshi-portfolio"] });
        },
        onError: (err: any) => {
            toast.error(`Error: ${err.message}`);
        },
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setShowConfirm(true);
    };

    const confirmOrder = () => {
        mutation.mutate({ ticker, side, count, price, type });
    };

    return (
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6 h-full flex flex-col">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                <span className="text-purple-400">⚡</span> Kalshi Trader
            </h3>

            <form onSubmit={handleSubmit} className="space-y-4 flex-1">
                <div>
                    <Label className="text-xs text-white/40">Ticker</Label>
                    <Input
                        value={ticker}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setTicker(e.target.value)}
                        className="bg-white/5 border-white/10"
                        placeholder="e.g. NBA-2024-LEBRON-PTS-OVER-24.5"
                    />
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <Label className="text-xs text-white/40">Side</Label>
                        <Tabs value={side} onValueChange={(v) => setSide(v as any)} className="w-full">
                            <TabsList className="grid w-full grid-cols-2 bg-white/5 border border-white/10">
                                <TabsTrigger value="yes" className="data-[state=active]:bg-green-500/20 data-[state=active]:text-green-400">YES</TabsTrigger>
                                <TabsTrigger value="no" className="data-[state=active]:bg-red-500/20 data-[state=active]:text-red-400">NO</TabsTrigger>
                            </TabsList>
                        </Tabs>
                    </div>
                    <div>
                        <Label className="text-xs text-white/40">Order Type</Label>
                        <Tabs value={type} onValueChange={(v) => setType(v as any)} className="w-full">
                            <TabsList className="grid w-full grid-cols-2 bg-white/5 border border-white/10">
                                <TabsTrigger value="limit">LIMIT</TabsTrigger>
                                <TabsTrigger value="market">MARKET</TabsTrigger>
                            </TabsList>
                        </Tabs>
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <Label className="text-xs text-white/40">Contracts</Label>
                        <Input
                            type="number"
                            value={count}
                            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setCount(parseInt(e.target.value) || 0)}
                            className="bg-white/5 border-white/10 text-center font-bold"
                        />
                    </div>
                    <div>
                        <Label className="text-xs text-white/40">Price (¢)</Label>
                        <div className="relative">
                            <Input
                                type="number"
                                value={price}
                                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPrice(parseInt(e.target.value) || 0)}
                                className="bg-white/5 border-white/10 pr-6 text-center font-bold text-purple-400"
                                max={99}
                                min={1}
                            />
                            <span className="absolute right-3 top-2.5 text-xs text-white/20">¢</span>
                        </div>
                    </div>
                </div>

                <div className="pt-4 border-t border-white/10">
                    <div className="flex justify-between text-xs mb-2">
                        <span className="text-white/40">Total Cost</span>
                        <span className="text-white font-mono">${totalCost.toFixed(2)}</span>
                    </div>
                    <Button
                        className="w-full bg-purple-600 hover:bg-purple-500 h-10 font-bold"
                        disabled={!ticker || count <= 0 || mutation.isPending}
                        type="submit"
                    >
                        {mutation.isPending ? "Placing Order..." : `PLACE ${side.toUpperCase()} ORDER`}
                    </Button>
                </div>
            </form>

            {showConfirm && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div className="bg-[#0f0f0f] border border-white/10 rounded-2xl p-6 max-w-sm w-full shadow-2xl">
                        <h4 className="text-lg font-bold mb-2">Confirm Order</h4>
                        <div className="text-sm text-white/60 mb-6 space-y-2">
                            <p>You are about to place a <span className="text-white font-bold">{side.toUpperCase()}</span> order for:</p>
                            <div className="bg-white/5 rounded-lg p-3 text-xs">
                                <p><span className="text-white/40">Ticker:</span> {ticker}</p>
                                <p><span className="text-white/40">Contracts:</span> {count}</p>
                                <p><span className="text-white/40">Price:</span> {price}¢</p>
                                <p><span className="text-white/40">Total:</span> <span className="text-white font-mono">${totalCost.toFixed(2)}</span></p>
                            </div>
                            <p className="text-[10px] text-red-500/60 uppercase font-bold text-center pt-2">Warning: Real Money Trade</p>
                        </div>
                        <div className="flex gap-3">
                            <Button variant="outline" className="flex-1 bg-white/5 hover:bg-white/10 border-white/10" onClick={() => setShowConfirm(false)}>Cancel</Button>
                            <Button className="flex-1 bg-purple-600 hover:bg-purple-500" onClick={confirmOrder}>Confirm</Button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
