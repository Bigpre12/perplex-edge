"use client";
import { Filter, ChevronDown, Activity, Calendar, Target } from "lucide-react";

interface FilterBarProps {
    filters: {
        window: number;
        min_hit_rate: number;
        market: string;
    };
    onChange: (key: string, value: any) => void;
}

export function OutlierFilterBar({ filters, onChange }: FilterBarProps) {
    return (
        <div className="flex flex-wrap items-center gap-4 bg-lucrix-surface/50 p-4 rounded-2xl border border-lucrix-border backdrop-blur-sm">
            <div className="flex items-center gap-2 text-textMuted uppercase font-black tracking-widest text-[10px] pr-4 border-r border-lucrix-border">
                <Filter size={14} />
                <span>Filters</span>
            </div>

            {/* Window Selector */}
            <div className="flex items-center gap-2">
                <Calendar size={14} className="text-brand-cyan" />
                <select 
                    value={filters.window}
                    onChange={(e) => onChange("window", Number(e.target.value))}
                    className="bg-transparent text-sm font-bold text-white outline-none cursor-pointer hover:text-brand-cyan transition-colors"
                    title="Select game window"
                >
                    <option value={5}>Last 5 Games</option>
                    <option value={10}>Last 10 Games</option>
                    <option value={20}>Last 20 Games</option>
                    <option value={82}>Full Season</option>
                </select>
            </div>

            {/* Hit Rate Threshold */}
            <div className="flex items-center gap-2 px-4 border-l border-lucrix-border">
                <Activity size={14} className="text-brand-success" />
                <select 
                    value={filters.min_hit_rate}
                    onChange={(e) => onChange("min_hit_rate", Number(e.target.value))}
                    className="bg-transparent text-sm font-bold text-white outline-none cursor-pointer hover:text-brand-success transition-colors"
                    title="Select minimum hit rate"
                >
                    <option value={0.70}>70%+ Hit Rate</option>
                    <option value={0.75}>75%+ Hit Rate</option>
                    <option value={0.80}>80%+ Hit Rate</option>
                    <option value={0.90}>90%+ Hit Rate</option>
                </select>
            </div>

            {/* Market Selector */}
            <div className="flex items-center gap-2 px-4 border-l border-lucrix-border">
                <Target size={14} className="text-brand-purple" />
                <select 
                    value={filters.market}
                    onChange={(e) => onChange("market", e.target.value)}
                    className="bg-transparent text-sm font-bold text-white outline-none cursor-pointer hover:text-brand-purple transition-colors"
                    title="Select market type"
                >
                    <option value="all">All Markets</option>
                    <option value="points">Points</option>
                    <option value="rebounds">Rebounds</option>
                    <option value="assists">Assists</option>
                    <option value="threes">3PM</option>
                    <option value="blocks">Blocks</option>
                    <option value="steals">Steals</option>
                </select>
            </div>
        </div>
    );
}
