"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    Terminal,
    Key,
    Share2,
    MessageSquare,
    Send,
    RefreshCw,
    ShieldCheck,
    AlertCircle,
    Activity,
    Code,
    Plus,
    Trash2,
    Copy,
    Check,
    Webhook,
    Bot
} from "lucide-react";
import { getAuthToken } from "@/lib/auth";
import { API_BASE_URL } from "@/lib/apiConfig";

export default function ExecutionHub() {
    const [apiKeys, setApiKeys] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [newKeyLabel, setNewKeyLabel] = useState("");
    const [justGeneratedKey, setJustGeneratedKey] = useState<string | null>(null);
    const [copiedId, setCopiedId] = useState<string | null>(null);
    const [logs, setLogs] = useState<any[]>([]);
    const [error, setError] = useState<string | null>(null);

    // Webhook States
    const [discordUrl, setDiscordUrl] = useState("");
    const [tgToken, setTgToken] = useState("");
    const [tgChatId, setTgChatId] = useState("");
    const [saving, setSaving] = useState(false);

    const fetchKeys = async () => {
        const token = getAuthToken();
        try {
            const res = await fetch(`${API_BASE_URL}/auth/keys`, {
                headers: { "Authorization": `Bearer ${token}` }
            });
            if (res.ok) setApiKeys(await res.json());
        } catch (err) {
            console.error("Failed to fetch keys:", err);
        } finally {
            setLoading(false);
        }
    };

    const generateKey = async () => {
        if (!newKeyLabel) {
            setError("Please enter a label for your API key.");
            return;
        }
        setError(null);
        const token = getAuthToken();
        if (!token) {
            setError("Authentication required. Please login first.");
            return;
        }
        try {
            const res = await fetch(`${API_BASE_URL}/auth/keys/generate?label=` + encodeURIComponent(newKeyLabel), {
                method: 'POST',
                headers: { "Authorization": `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                setJustGeneratedKey(data.api_key);
                fetchKeys();
                setNewKeyLabel("");
                setError(null);
            } else if (res.status === 401) {
                setError("Session expired. Please login again.");
            } else {
                setError(`Key generation failed (${res.status}).`);
            }
        } catch (err) {
            setError("Cannot connect to backend. Check that server is running.");
            console.error("Failed to generate key:", err);
        }
    };

    const saveWebhooks = async () => {
        setSaving(true);
        const token = getAuthToken();
        try {
            await fetch(`${API_BASE_URL}/auth/profile/update-webhooks`, {
                method: 'POST',
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    discord_webhook_url: discordUrl,
                    telegram_bot_token: tgToken,
                    telegram_chat_id: tgChatId
                })
            });
            alert("Institutional configurations saved successfully.");
        } catch (err) {
            console.error("Save failed:", err);
        } finally {
            setSaving(false);
        }
    };

    useEffect(() => {
        fetchKeys();
        // Mock Logs
        setLogs([
            { id: 1, type: 'SIGNAL', target: 'Discord', status: 'SUCCESS', details: 'Lebron James Over 24.5 Pts', time: '2 mins ago' },
            { id: 2, type: 'BOT', target: 'ExecutionNode-01', status: 'POLL', details: 'Relay Active - 14 Props Scanned', time: '5 mins ago' },
            { id: 3, type: 'SIGNAL', target: 'Telegram', status: 'FAILED', details: 'Invalid Token Configuration', time: '12 mins ago' }
        ]);
    }, []);

    const copyToClipboard = (text: string, id: string) => {
        navigator.clipboard.writeText(text);
        setCopiedId(id);
        setTimeout(() => setCopiedId(null), 2000);
    };

    return (
        <div className="space-y-8 pb-12">
            {/* Header */}
            <div>
                <div className="flex items-center gap-3 mb-2">
                    <div className="p-2 bg-primary/20 rounded-lg text-primary shadow-[0_0_15px_rgba(13,242,51,0.2)]">
                        <Terminal size={24} />
                    </div>
                    <h1 className="text-3xl font-black text-white tracking-tighter uppercase italic">Algorithmic Execution Hub</h1>
                </div>
                <p className="text-secondary text-sm font-medium">Manage bot connections, signal dispatchers, and institutional API keys.</p>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
                {/* Developer Keys Section */}
                <div className="xl:col-span-2 space-y-6">
                    <div className="glass-panel p-8 rounded-3xl border-white/[0.05]">
                        <div className="flex items-center justify-between mb-8">
                            <h3 className="text-sm font-black text-white flex items-center gap-2 uppercase tracking-widest italic">
                                <Key size={18} className="text-primary" /> API Key Management
                            </h3>
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    placeholder="Label (e.g. Python Bot)"
                                    value={newKeyLabel}
                                    onChange={(e) => setNewKeyLabel(e.target.value)}
                                    className="bg-white/5 border border-white/10 rounded-xl px-4 py-2 text-xs text-white focus:outline-none focus:border-primary/50"
                                />
                                <button
                                    onClick={generateKey}
                                    className="px-4 py-2 bg-primary text-background-dark font-black text-xs rounded-xl hover:scale-105 active:scale-95 transition-all flex items-center gap-2"
                                >
                                    <Plus size={16} /> GENERATE
                                </button>
                            </div>
                        </div>

                        {error && (
                            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-2xl text-xs text-red-400 font-bold">
                                ⚠️ {error}
                            </div>
                        )}

                        {justGeneratedKey && (
                            <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="mb-6 p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl flex items-center justify-between"
                            >
                                <div className="flex items-center gap-3">
                                    <ShieldCheck className="text-emerald-500" size={20} />
                                    <div>
                                        <p className="text-[10px] font-black text-emerald-500 uppercase">New Key Generated</p>
                                        <p className="text-xs font-mono text-white mt-1">{justGeneratedKey}</p>
                                    </div>
                                </div>
                                <button
                                    onClick={() => copyToClipboard(justGeneratedKey, 'new')}
                                    className="p-2 hover:bg-white/10 rounded-lg transition-all"
                                >
                                    {copiedId === 'new' ? <Check size={18} className="text-emerald-500" /> : <Copy size={18} className="text-slate-400" />}
                                </button>
                            </motion.div>
                        )}

                        <div className="space-y-3">
                            {apiKeys.map((key) => (
                                <div key={key.id} className="flex items-center justify-between p-4 bg-white/[0.03] border border-white/[0.05] rounded-2xl hover:bg-white/[0.05] transition-all group">
                                    <div className="flex items-center gap-4">
                                        <div className="size-8 rounded-lg bg-surface border border-white/5 flex items-center justify-center text-slate-500">
                                            <Code size={16} />
                                        </div>
                                        <div>
                                            <p className="text-xs font-black text-white tracking-tight">{key.label}</p>
                                            <p className="text-[10px] text-slate-500 font-mono mt-0.5">Hash: ...{key.key_hash.slice(-8)} • Requests: {key.requests_count}</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                        <button className="p-2 hover:bg-white/10 rounded-lg text-slate-400 hover:text-white transition-all">
                                            <Activity size={16} />
                                        </button>
                                        <button className="p-2 hover:bg-red-500/10 rounded-lg text-slate-400 hover:text-red-500 transition-all">
                                            <Trash2 size={16} />
                                        </button>
                                    </div>
                                </div>
                            ))}
                            {apiKeys.length === 0 && !loading && (
                                <div className="text-center py-12">
                                    <div className="size-12 rounded-full bg-white/5 mx-auto mb-4 flex items-center justify-center text-slate-600">
                                        <Key size={24} />
                                    </div>
                                    <p className="text-sm text-slate-500 italic">No developer keys identified. Generate one to initiate bot connectivity.</p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Signal Logs */}
                    <div className="glass-panel p-8 rounded-3xl border-white/[0.05]">
                        <h3 className="text-sm font-black text-white mb-8 flex items-center justify-between uppercase tracking-widest italic">
                            <span className="flex items-center gap-2"><Send size={18} className="text-primary" /> Live Dispatch Logs</span>
                            <RefreshCw size={14} className="text-slate-600 animate-spin-slow cursor-pointer" />
                        </h3>
                        <div className="space-y-2">
                            {logs.map((log) => (
                                <div key={log.id} className="flex items-center justify-between py-3 border-b border-white/[0.03] last:border-0 overflow-hidden">
                                    <div className="flex items-center gap-4">
                                        <span className={`text-[9px] font-black px-1.5 py-0.5 rounded ${log.status === 'SUCCESS' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-red-500/10 text-red-500'}`}>
                                            {log.status}
                                        </span>
                                        <div>
                                            <p className="text-[11px] font-bold text-white">{log.details}</p>
                                            <p className="text-[9px] text-slate-500 uppercase font-black">{log.type} // TARGET: {log.target}</p>
                                        </div>
                                    </div>
                                    <span className="text-[9px] font-bold text-slate-600 whitespace-nowrap">{log.time}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Webhook Settings Sidebar */}
                <div className="space-y-6">
                    <div className="glass-panel p-6 rounded-3xl border-white/[0.05] bg-gradient-to-br from-[#0c1416]/50 to-transparent">
                        <h3 className="text-sm font-black text-white mb-6 flex items-center gap-2 italic">
                            <Webhook size={18} className="text-primary" /> Webhook Integrations
                        </h3>
                        <div className="space-y-6">
                            <WebhookInput
                                label="Discord Webhook"
                                icon={<Share2 size={16} />}
                                placeholder="https://discord.com/api/webhooks/..."
                                value={discordUrl}
                                onChange={(val: string) => setDiscordUrl(val)}
                            />
                            <WebhookInput
                                label="Telegram Bot Token"
                                icon={<MessageSquare size={16} />}
                                placeholder="123456:ABC-DEF1234..."
                                value={tgToken}
                                onChange={(val: string) => setTgToken(val)}
                            />
                            <WebhookInput
                                label="Telegram Chat ID"
                                icon={<Terminal size={16} />}
                                placeholder="-100123456789"
                                value={tgChatId}
                                onChange={(val: string) => setTgChatId(val)}
                            />
                            <button
                                onClick={saveWebhooks}
                                disabled={saving}
                                className="w-full py-3 bg-white/5 border border-white/10 rounded-xl text-xs font-black text-white hover:bg-white/10 transition-all uppercase tracking-widest disabled:opacity-50"
                            >
                                {saving ? "Saving..." : "Save Configurations"}
                            </button>
                        </div>
                    </div>

                    <div className="glass-panel p-6 rounded-3xl border-white/[0.05]">
                        <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-6">Execution Infrastructure</h3>
                        <div className="space-y-4">
                            <ExecutionHealth label="Main API Gateway" status="Active" latency="12ms" />
                            <ExecutionHealth label="Webhook Relay" status="Idle" latency="-" />
                            <ExecutionHealth label="Bot Connect Hub" status="Healthy" latency="48ms" />
                        </div>
                    </div>

                    <div className="p-6 rounded-3xl bg-primary/10 border border-primary/20 relative overflow-hidden group">
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:rotate-12 transition-transform">
                            <Bot size={60} />
                        </div>
                        <h4 className="text-xs font-black text-primary uppercase tracking-widest mb-2">Bot Connect Active</h4>
                        <p className="text-[10px] text-slate-400 font-medium leading-relaxed">
                            Your institutional API is live at <code className="text-primary">/execution/bot-connect</code>.
                            Use Header <code className="text-white">X-API-Key</code> for authenticated requests.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

function WebhookInput({ label, icon, placeholder, value, onChange }: any) {
    return (
        <div className="space-y-2">
            <p className="text-[10px] font-black text-slate-500 uppercase tracking-tighter flex items-center gap-2">
                {icon} {label}
            </p>
            <input
                type="text"
                value={value}
                onChange={(e) => onChange(e.target.value)}
                placeholder={placeholder}
                className="w-full bg-black/20 border border-white/5 rounded-xl px-4 py-3 text-xs text-white font-mono focus:outline-none focus:border-primary/50 placeholder:text-slate-700"
            />
        </div>
    );
}

function ExecutionHealth({ label, status, latency }: any) {
    return (
        <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
                <div className={`size-1.5 rounded-full ${status === 'Active' || status === 'Healthy' ? 'bg-primary' : 'bg-slate-700'}`}></div>
                <span className="text-xs font-black text-slate-400">{label}</span>
            </div>
            <div className="flex items-center gap-3">
                <span className="text-[9px] font-bold text-slate-600">{latency}</span>
                <span className="text-[10px] font-black text-white italic uppercase">{status}</span>
            </div>
        </div>
    );
}
