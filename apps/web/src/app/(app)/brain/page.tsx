"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Zap, Activity, BrainCircuit, Target, Scale } from "lucide-react";
import GateLock from "@/components/GateLock";
import { useLucrixStore } from "@/store";
import { api } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";

export default function BrainPage() {
    const userTier = useLucrixStore((state: any) => state.userTier);
    const activeSport = useLucrixStore((state: any) => state.activeSport);
    const [activeTab, setActiveTab] = useState("scorer");

    return (
        <div className="w-full max-w-7xl mx-auto p-4 md:p-6 pb-24 md:pb-6 space-y-6 text-slate-200">
            {/* Header */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-black italic tracking-tighter uppercase flex items-center gap-2">
                        <Zap className="w-8 h-8 text-emerald-primary" />
                        Neural Engine
                    </h1>
                    <p className="text-sm text-slate-400 font-mono mt-1">
                        AI-powered predictive modeling and quantitative analysis.
                    </p>
                </div>
            </div>

            {/* Tabs */}
            <div className="flex bg-slate-800/50 p-1 rounded-xl w-fit">
                <button
                    onClick={() => setActiveTab("scorer")}
                    className={`px-4 py-2 rounded-lg font-bold text-sm transition-colors ${activeTab === 'scorer' ? 'bg-indigo-500/20 text-indigo-400' : 'text-slate-400 hover:text-slate-200'}`}
                >
                    Prop Scorer
                </button>
                <button
                    onClick={() => setActiveTab("heatmap")}
                    className={`px-4 py-2 rounded-lg font-bold text-sm transition-colors ${activeTab === 'heatmap' ? 'bg-indigo-500/20 text-indigo-400' : 'text-slate-400 hover:text-slate-200'}`}
                >
                    Confidence Heatmap
                </button>
                <button
                    onClick={() => setActiveTab("reasoning")}
                    className={`px-4 py-2 rounded-lg font-bold text-sm transition-colors ${activeTab === 'reasoning' ? 'bg-indigo-500/20 text-indigo-400' : 'text-slate-400 hover:text-slate-200'}`}
                >
                    Reasoning Feed
                </button>
            </div>

            {/* Content Gate */}
            <GateLock
                feature="Neural Engine Analytics"
            >
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 min-h-[400px]">
                    {activeTab === "scorer" && <NeuralPropScorer />}
                    {activeTab === "heatmap" && <ConfidenceHeatmap />}
                    {activeTab === "reasoning" && <ReasoningFeed />}
                </div>
            </GateLock>
        </div>
    );
}

function ConfidenceHeatmap() {
    const { data: heatmap, isLoading } = useQuery({
        queryKey: ["brain_heatmap"],
        queryFn: () => api.brain.heatmap()
    });

    if (isLoading) return <LoadingBrain />;
    if (!heatmap) return <EmptyBrain message="No heatmap data available" />;

    return (
        <div className="space-y-4">
            <h3 className="text-xl font-bold font-mono text-slate-200 uppercase tracking-widest">Market Edge Heatmap</h3>
            <p className="text-sm text-slate-400">Darker red indicates stronger model conviction relative to market pricing.</p>
            <div className="overflow-x-auto mt-6">
                <div className="min-w-max">
                    {/* Header Row */}
                    <div className="flex">
                        <div className="w-24 shrink-0 bg-transparent"></div>
                        {heatmap.x_axis?.map((x: string, i: number) => (
                            <div key={i} className="w-24 shrink-0 text-center font-bold text-xs text-slate-500 uppercase pb-2">{x}</div>
                        ))}
                    </div>
                    {/* Data Rows */}
                    {heatmap.y_axis?.map((y: string, rowIndex: number) => (
                        <div key={rowIndex} className="flex mb-1">
                            <div className="w-24 shrink-0 font-black text-sm text-slate-300 pr-4 flex items-center justify-end">{y}</div>
                            {heatmap.matrix?.[rowIndex]?.map((val: number, colIndex: number) => {
                                // interpolate color based on value 0-100
                                const intensity = val / 100;
                                const bgColor = `rgba(225, 29, 72, ${intensity})`; // rose-600 with alpha
                                return (
                                    <div key={colIndex} className="w-24 h-12 shrink-0 border border-slate-900 flex items-center justify-center font-mono text-xs font-bold" style={{ backgroundColor: bgColor }}>
                                        <span className={intensity > 0.5 ? "text-white" : "text-slate-400"}>{val}</span>
                                    </div>
                                );
                            })}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

function ReasoningFeed() {
    const { data: feed, isLoading } = useQuery({
        queryKey: ["brain_reasoning_feed"],
        queryFn: () => api.brain.reasoningFeed()
    });

    if (isLoading) return <LoadingBrain />;

    const displayFeed = feed?.length ? feed : [];

    if (displayFeed.length === 0) {
        return <EmptyBrain message="No reasoning insights available for this slate." />;
    }

    return (
        <div className="space-y-6">
            <h3 className="text-xl font-bold font-mono text-slate-200 uppercase tracking-widest">Neural Reasoning Timeline</h3>
            <div className="space-y-4 border-l border-slate-700 ml-4 pl-6 relative">
                {displayFeed.map((item: any, i: number) => (
                    <div key={item.id || i} className="relative">
                        <div className="absolute -left-[30px] top-1.5 w-3 h-3 bg-indigo-500 rounded-full shadow-[0_0_10px_rgba(99,102,241,0.5)]" />
                        <div className="bg-slate-800/40 border border-slate-700 rounded-xl p-4">
                            <div className="flex justify-between items-start mb-2">
                                <div>
                                    <span className="font-bold text-white">{item.player}</span>
                                    <span className="mx-2 text-slate-500 text-xs">|</span>
                                    <span className="text-slate-400 text-xs uppercase">{item.stat_type}</span>
                                </div>
                                <span className="text-[10px] text-slate-500">{new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                            </div>
                            <p className="text-sm text-slate-300 italic mb-3 leading-relaxed">"{item.reason}"</p>
                            <div className="flex items-center gap-3">
                                <span className={`text-[10px] font-black px-2 py-0.5 rounded uppercase tracking-widest ${item.signal === 'OVER' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}`}>{item.signal}</span>
                                <span className="text-[10px] bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 px-2 py-0.5 rounded uppercase font-mono font-bold">Score: {item.brain_score}/100</span>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

function LoadingBrain() {
    return (
        <div className="flex flex-col items-center justify-center py-12 space-y-4">
            <BrainCircuit className="w-12 h-12 text-indigo-500/50 animate-pulse" />
            <p className="font-mono text-slate-400 text-sm">Querying neural predictive models...</p>
        </div>
    );
}

function EmptyBrain({ message }: { message: string }) {
    return (
        <div className="text-center py-12">
            <p className="text-slate-500 font-mono">{message}</p>
        </div>
    );
}

function NeuralPropScorer() {
    const { data: props, isLoading } = useQuery({
        queryKey: ["brain_prop_score"],
        queryFn: () => api.brain.propScore()
    });

    if (isLoading) {
        return (
            <div className="flex flex-col items-center justify-center py-12 space-y-4">
                <BrainCircuit className="w-12 h-12 text-indigo-500/50 animate-pulse" />
                <p className="font-mono text-slate-400 text-sm">Querying neural predictive models...</p>
            </div>
        );
    }

    if (!props || props.length === 0) {
        return (
            <div className="text-center py-12">
                <p className="text-slate-500 font-mono">No high-confidence edges detected for current slate.</p>
            </div>
        );
    }

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {props.map((p: any, i: number) => (
                <div key={i} className="bg-slate-800/40 border border-slate-700/50 rounded-xl p-4 hover:border-indigo-500/30 transition-colors">
                    <div className="flex justify-between items-start mb-3">
                        <div>
                            <h3 className="font-bold text-slate-200">{p.player}</h3>
                            <p className="text-xs text-slate-400">{p.stat_type.toUpperCase()} • Line: {p.line}</p>
                        </div>
                        <div className={`px-2 py-1 rounded text-xs font-black ${p.signal === 'OVER' ? 'bg-emerald-500/20 text-emerald-400' :
                            p.signal === 'UNDER' ? 'bg-rose-500/20 text-rose-400' :
                                'bg-slate-500/20 text-slate-400'
                            }`}>
                            {p.signal}
                        </div>
                    </div>

                    <div className="mb-4">
                        <div className="flex justify-between text-xs mb-1">
                            <span className="text-slate-400">Brain Score</span>
                            <span className="font-mono font-bold text-indigo-400">{p.brain_score}/100</span>
                        </div>
                        <div className="w-full bg-slate-700/50 rounded-full h-1.5">
                            <div
                                className={`h-1.5 rounded-full ${p.brain_score >= 70 ? 'bg-emerald-500' : p.brain_score >= 40 ? 'bg-yellow-500' : 'bg-rose-500'}`}
                                style={{ width: `${p.brain_score}%` }}
                            />
                        </div>
                    </div>

                    <div className="bg-slate-900/50 rounded p-3">
                        <p className="text-xs text-slate-300 leading-relaxed italic border-l-2 border-indigo-500/50 pl-2">
                            "{p.reason}"
                        </p>
                    </div>
                </div>
            ))}
        </div>
    );
}
