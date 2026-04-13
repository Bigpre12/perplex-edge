"use client";

import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Activity, Users, DollarSign, ShieldAlert, Cpu, Database, RefreshCw, Send } from "lucide-react";
import { getUser } from "@/lib/auth";

import API, { isApiError } from "@/lib/api";

export default function AdminCommandCenter() {
    const [stats, setStats] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [isAdmin, setIsAdmin] = useState(false);

    useEffect(() => {
        const fetchAdminData = async () => {
            try {
                const user = getUser();
                if (!user) {
                    window.location.href = "/login";
                    return;
                }

                const data = await API.adminStats(user.email);

                if (isApiError(data)) {
                    if (data.status === 403) {
                        setIsAdmin(false);
                        setError("ACCESS DENIED: Insufficient Security Clearance");
                    } else {
                        throw new Error(data.message || "Failed to fetch command center metrics");
                    }
                    return;
                }

                setStats(data);
                setIsAdmin(true);

            } catch (err: any) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchAdminData();
    }, []);

    const triggerManualSync = async () => {
        alert("Manually dispatching the NFL Player Props Engine Sync...");
        // This would post to an internal /sync route in production
    };

    if (loading) {
        return (
            <div className="h-full flex items-center justify-center">
                <div className="flex flex-col items-center gap-4 text-emerald-500">
                    <RefreshCw size={40} className="animate-spin" />
                    <p className="font-black uppercase tracking-widest text-sm">Authenticating Command Clearance...</p>
                </div>
            </div>
        );
    }

    if (!isAdmin) {
        return (
            <div className="h-full flex items-center justify-center p-8">
                <div className="max-w-md w-full glass-premium border-red-500/20 p-8 rounded-2xl text-center shadow-[0_0_50px_rgba(239,68,68,0.1)]">
                    <div className="mx-auto size-16 rounded-full bg-red-500/10 flex items-center justify-center mb-6">
                        <ShieldAlert size={32} className="text-red-500" />
                    </div>
                    <h2 className="text-2xl font-black text-white mb-2 uppercase tracking-widest">Access Denied</h2>
                    <p className="text-slate-400 text-sm">{error}</p>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-6xl mx-auto space-y-8">
            <header className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-white/5 pb-6">
                <div>
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-500 text-[10px] font-black uppercase tracking-widest mb-3">
                        <ShieldAlert size={12} /> Master Command Center
                    </div>
                    <h1 className="text-3xl font-black text-white tracking-tight">System Overview</h1>
                    <p className="text-slate-400 mt-1">Global monitoring of SaaS subscriptions and Engine health.</p>
                </div>
                <div className="flex gap-3">
                    <button
                        onClick={triggerManualSync}
                        className="px-4 py-2 glass-premium border-white/10 rounded-xl text-xs font-bold text-white hover:bg-white/5 transition-colors flex items-center gap-2"
                    >
                        <RefreshCw size={14} /> Force Engine Sync
                    </button>
                    <button className="px-4 py-2 bg-primary text-black rounded-xl text-xs font-black uppercase tracking-wider hover:bg-primary/90 transition-colors flex items-center gap-2 shadow-[0_0_15px_rgba(13,242,51,0.2)]">
                        <Send size={14} /> Blast Push Alert
                    </button>
                </div>
            </header>

            {/* Top Level Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="glass-premium p-6 rounded-2xl border-white/5 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
                        <DollarSign size={64} className="text-primary" />
                    </div>
                    <p className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-2">Estimated MRR</p>
                    <h3 className="text-4xl font-black text-white">{stats.estimated_mrr}</h3>
                    <p className="text-[10px] text-primary mt-2 flex items-center gap-1 font-bold">
                        <Activity size={12} /> Based on active $49/mo tiers
                    </p>
                </motion.div>

                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="glass-premium p-6 rounded-2xl border-white/5 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
                        <Users size={64} className="text-blue-500" />
                    </div>
                    <p className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-2">Pro Subscribers</p>
                    <h3 className="text-4xl font-black text-white">{stats.pro_subscriptions}</h3>
                    <p className="text-[10px] text-slate-500 mt-2 flex items-center gap-1 font-bold">
                        <span className="text-blue-400">{(stats.pro_subscriptions / Math.max(stats.total_users, 1) * 100).toFixed(1)}%</span> Conversion Rate
                    </p>
                </motion.div>

                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="glass-premium p-6 rounded-2xl border-emerald-500/10 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
                        <Database size={64} className="text-emerald-500" />
                    </div>
                    <p className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-2">Total Edge Accounts</p>
                    <h3 className="text-4xl font-black text-white">{stats.total_users}</h3>
                    <p className="text-[10px] text-emerald-500 mt-2 flex items-center gap-1 font-bold">
                        <Cpu size={12} /> Database Healthy
                    </p>
                </motion.div>
            </div>

            {/* Active Services Matrix */}
            <div className="glass-premium rounded-2xl border border-white/5 overflow-hidden">
                <div className="p-6 border-b border-white/5 bg-white/[0.02]">
                    <h3 className="text-lg font-black text-white flex items-center gap-2">
                        <Cpu size={18} className="text-primary" /> Core Engine Microservices
                    </h3>
                </div>
                <div className="divide-y divide-white/5">
                    {stats.active_services.map((service: string, i: number) => (
                        <div key={i} className="p-4 flex items-center justify-between hover:bg-white/[0.02] transition-colors">
                            <div className="flex items-center gap-3">
                                <span className="relative flex h-3 w-3">
                                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                                    <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
                                </span>
                                <span className="text-sm font-bold text-slate-200">{service}</span>
                            </div>
                            <span className="text-[10px] uppercase tracking-widest text-emerald-500 font-black px-2 py-1 rounded bg-emerald-500/10 border border-emerald-500/20">Online</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
