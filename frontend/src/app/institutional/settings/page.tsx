"use client";

import { useState, useEffect } from "react";
import { Settings, Cpu, ShieldAlert, Save, TrendingUp, Loader2, Zap } from "lucide-react";
import { motion } from "framer-motion";

export default function EdgeSettingsPage() {
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [config, setConfig] = useState({
        active_edge_model: "baseline",
        min_edge_percent: 8.0,
        max_edge_percent: 40.0,
        min_games_sample: 10,
        min_bets_volume: 50,
        max_juice: -120.0,
        include_main_lines: true,
        discord_webhook_url: ""
    });
    const [statusBlock, setStatusBlock] = useState<{ msg: string, isError: boolean } | null>(null);

    useEffect(() => {
        async function fetchConfig() {
            try {
                const res = await fetch("http://localhost:8000/api/config");
                if (res.ok) {
                    const data = await res.json();
                    setConfig(data);
                }
            } catch (err) {
                console.error("Failed to load config:", err);
            } finally {
                setLoading(false);
            }
        }
        fetchConfig();
    }, []);

    const saveSettings = async () => {
        setSaving(true);
        setStatusBlock(null);
        try {
            const res = await fetch("http://localhost:8000/api/config", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(config)
            });
            if (res.ok) {
                setStatusBlock({ msg: "Settings saved and deployed to AI Edge Engine.", isError: false });
            } else {
                throw new Error("Server rejected settings payload");
            }
        } catch (err) {
            setStatusBlock({ msg: "Failed to save configuration settings.", isError: true });
        } finally {
            setSaving(false);
            setTimeout(() => setStatusBlock(null), 4000);
        }
    };

    if (loading) return <div className="p-12 flex items-center gap-4 text-secondary"><Loader2 className="animate-spin" /> Loading Core Connectors...</div>;

    return (
        <div className="space-y-8 pb-12">
            <div className="flex items-center justify-between">
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <div className="p-2 bg-primary/20 rounded-lg text-primary shadow-[0_0_15px_rgba(13,242,51,0.2)]">
                            <Settings size={28} />
                        </div>
                        <h1 className="text-3xl font-black text-white tracking-tighter uppercase italic">Control Architecture</h1>
                    </div>
                    <p className="text-secondary text-sm font-medium">Mutate the active Edge Engine filtering thresholds in real-time.</p>
                </div>
                <button
                    onClick={saveSettings}
                    disabled={saving}
                    className="px-8 py-3 bg-gradient-to-r from-primary to-emerald-400 text-background-dark font-black rounded-2xl hover:scale-105 active:scale-95 transition-all flex items-center gap-2 shadow-[0_0_20px_rgba(13,242,51,0.3)] disabled:opacity-50"
                >
                    {saving ? <Loader2 size={20} className="animate-spin" /> : <Save size={20} />}
                    {saving ? "DEPLOYING..." : "DEPLOY CONFIG"}
                </button>
            </div>

            {statusBlock && (
                <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className={`p-4 rounded-xl font-bold text-sm border flex items-center gap-3 ${statusBlock.isError ? "bg-accent-orange/10 text-accent-orange border-accent-orange/20" : "bg-primary/10 text-primary border-primary/20"}`}>
                    <Cpu size={18} />
                    {statusBlock.msg}
                </motion.div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Engine Parameters */}
                <div className="glass-panel p-8 rounded-3xl border-white/[0.05] bg-[#0c1416]/90 relative overflow-hidden group hover:border-white/10 transition-colors">
                    <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:rotate-12 transition-transform text-white">
                        <Cpu size={80} />
                    </div>
                    <h3 className="text-sm font-black text-white flex items-center gap-2 uppercase italic tracking-widest mb-8 border-b border-white/[0.05] pb-4">
                        <TrendingUp size={18} className="text-primary" /> Algorithmic Thresholds
                    </h3>

                    <div className="space-y-8 relative z-10">
                        <div>
                            <div className="flex justify-between mb-2">
                                <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Minimum Edge Requirement</label>
                                <span className="text-sm text-primary font-bold">{config.min_edge_percent.toFixed(1)}%</span>
                            </div>
                            <input
                                type="range"
                                min="1" max="15" step="0.5"
                                value={config.min_edge_percent}
                                onChange={e => setConfig({ ...config, min_edge_percent: parseFloat(e.target.value) })}
                                className="w-full accent-primary bg-slate-800 rounded-lg cursor-pointer"
                            />
                            <p className="text-[10px] text-slate-500 mt-2 font-medium">Blocks props with an EV return lower than {config.min_edge_percent}%.</p>
                        </div>

                        <div>
                            <div className="flex justify-between mb-2">
                                <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Maximum Outlier Ceiling</label>
                                <span className="text-sm text-accent-orange font-bold">{config.max_edge_percent.toFixed(1)}%</span>
                            </div>
                            <input
                                type="range"
                                min="20" max="60" step="1.0"
                                value={config.max_edge_percent}
                                onChange={e => setConfig({ ...config, max_edge_percent: parseFloat(e.target.value) })}
                                className="w-full accent-accent-orange bg-slate-800 rounded-lg cursor-pointer"
                            />
                            <p className="text-[10px] text-slate-500 mt-2 font-medium">Caps the EV scale to avoid corrupted data-points (e.g., glitch lines showing {config.max_edge_percent}%+).</p>
                        </div>

                        <div>
                            <div className="flex justify-between mb-2">
                                <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Maximum Allowed Juice</label>
                                <span className="text-sm text-white font-bold">{config.max_juice}</span>
                            </div>
                            <input
                                type="range"
                                min="-180" max="-105" step="5"
                                value={config.max_juice}
                                onChange={e => setConfig({ ...config, max_juice: parseFloat(e.target.value) })}
                                className="w-full accent-white bg-slate-800 rounded-lg cursor-pointer"
                            />
                            <p className="text-[10px] text-slate-500 mt-2 font-medium">Filters out heavily juiced outcomes past {config.max_juice}.</p>
                        </div>
                    </div>
                </div>

                {/* Model Selectors & Toggles */}
                <div className="space-y-8">
                    <div className="glass-panel p-8 rounded-3xl border-white/[0.05] bg-[#0c1416]/90 relative overflow-hidden group hover:border-white/10 transition-colors">
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:-rotate-12 transition-transform text-accent-blue">
                            <ShieldAlert size={80} />
                        </div>
                        <h3 className="text-sm font-black text-white flex items-center gap-2 uppercase italic tracking-widest mb-6 border-b border-white/[0.05] pb-4">
                            Model Selection
                        </h3>

                        <div className="grid grid-cols-2 gap-4 relative z-10">
                            <button
                                onClick={() => setConfig({ ...config, active_edge_model: "baseline" })}
                                className={`p-4 rounded-xl border text-left transition-all ${config.active_edge_model === "baseline" ? "bg-primary/10 border-primary text-primary shadow-[0_0_15px_rgba(13,242,51,0.15)]" : "bg-black/30 border-white/5 text-slate-400 hover:bg-black/50"}`}
                            >
                                <p className="text-[10px] uppercase font-black tracking-widest mb-1.5 opacity-80">v1.2 Stable</p>
                                <h4 className="font-bold text-sm text-white">Baseline Engine</h4>
                            </button>
                            <button
                                onClick={() => setConfig({ ...config, active_edge_model: "sharp_v2" })}
                                className={`p-4 rounded-xl border text-left transition-all ${config.active_edge_model === "sharp_v2" ? "bg-accent-blue/10 border-accent-blue text-accent-blue shadow-[0_0_15px_rgba(13,204,242,0.15)]" : "bg-black/30 border-white/5 text-slate-400 hover:bg-black/50"}`}
                            >
                                <p className="text-[10px] uppercase font-black tracking-widest mb-1.5 opacity-80">Beta v2</p>
                                <h4 className="font-bold text-sm text-white">Sharp Aggregation</h4>
                            </button>
                        </div>
                    </div>

                    <div className="glass-panel p-8 rounded-3xl border-white/[0.05] bg-[#0c1416]/90 flex items-center justify-between group hover:border-white/10 transition-colors">
                        <div>
                            <h4 className="text-sm font-bold text-white tracking-wide">Include Main Betting Lines</h4>
                            <p className="text-[10px] font-medium text-slate-500 mt-1">If disabled, the AI strictly prioritizes alternate lines.</p>
                        </div>
                        <button
                            onClick={() => setConfig({ ...config, include_main_lines: !config.include_main_lines })}
                            className={`w-14 h-7 rounded-full transition-colors relative ${config.include_main_lines ? 'bg-primary' : 'bg-slate-700'}`}
                        >
                            <div className={`w-5 h-5 bg-white rounded-full absolute top-1 transition-transform ${config.include_main_lines ? 'translate-x-8' : 'translate-x-1'}`}></div>
                        </button>
                    </div>
                </div>

                {/* Institutional Integrations */}
                <div className="glass-panel p-8 rounded-3xl border-white/[0.05] bg-[#0c1416]/90 relative overflow-hidden group hover:border-white/10 transition-colors lg:col-span-2">
                    <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:rotate-12 transition-transform text-white">
                        <Zap size={80} />
                    </div>
                    <h3 className="text-sm font-black text-white flex items-center gap-2 uppercase italic tracking-widest mb-8 border-b border-white/[0.05] pb-4">
                        <Zap size={18} className="text-primary" /> External API & Webhooks
                    </h3>

                    <div className="space-y-6 relative z-10 max-w-2xl">
                        <div>
                            <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest block mb-2 tracking-[0.2em]">Discord Webhook URL</label>
                            <input
                                type="text"
                                placeholder="https://discord.com/api/webhooks/..."
                                value={config.discord_webhook_url}
                                onChange={e => setConfig({ ...config, discord_webhook_url: e.target.value })}
                                className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder:text-slate-700 focus:outline-none focus:border-primary/50 transition-colors font-mono"
                            />
                            <p className="text-[10px] text-slate-500 mt-3 font-medium flex items-center gap-2">
                                <span className="size-1 rounded-full bg-primary" /> Instantly pipes +EV alerts and whale movements into your private community.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
