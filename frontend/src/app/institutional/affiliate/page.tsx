"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Copy, Users, Link2, DollarSign, Loader2, Sparkles, CheckCircle2 } from "lucide-react";
import { supabase } from "@/lib/supabaseClient";

export default function AffiliateDashboard() {
    const [referralData, setReferralData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [copied, setCopied] = useState(false);

    useEffect(() => {
        const fetchAffiliateData = async () => {
            try {
                const { data: { session } } = await supabase.auth.getSession();
                if (!session) return;

                const res = await fetch(`http://localhost:8000/api/affiliates/my-link/${session.user.id}`);
                const data = await res.json();
                setReferralData(data);
            } catch (err) {
                console.error("Failed to load affiliate data:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchAffiliateData();
    }, []);

    const handleCopy = () => {
        if (!referralData) return;
        const link = `https://perplexedge.com?ref=${referralData.referral_code}`;
        navigator.clipboard.writeText(link);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    if (loading) {
        return (
            <div className="h-[60vh] flex flex-col items-center justify-center gap-4 text-primary">
                <Loader2 size={40} className="animate-spin" />
                <p className="text-sm font-bold uppercase tracking-widest text-slate-400">Loading Partner Portal...</p>
            </div>
        );
    }

    // Calculate Estimated Payout (e.g., $15 bounty per paid conversion)
    const estimatedPayout = (referralData?.conversions || 0) * 15;

    return (
        <div className="max-w-5xl mx-auto space-y-8 pb-12">
            <header className="border-b border-white/5 pb-6">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary text-[10px] font-black uppercase tracking-widest mb-3">
                    <Sparkles size={12} /> Partner Program Active
                </div>
                <h1 className="text-3xl font-black text-white tracking-tight">Affiliate Hub</h1>
                <p className="text-slate-400 mt-1">Earn a $15 recurring bounty for every Pro user you refer to the Sharp Engine.</p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Main Link Generator Card */}
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="lg:col-span-2 glass-premium p-8 rounded-2xl border-white/5 relative overflow-hidden"
                >
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-primary to-transparent opacity-50" />
                    <h2 className="text-xl font-black text-white mb-6">Your Unique Sharp Link</h2>

                    <div className="flex flex-col sm:flex-row gap-4 mb-8">
                        <div className="flex-1 bg-black/40 border border-slate-700/50 rounded-xl px-4 py-3 flex items-center justify-between font-mono text-sm text-slate-300">
                            <span className="truncate mr-4 flex-1">
                                https://perplexedge.com?ref=<span className="text-primary font-bold">{referralData?.referral_code}</span>
                            </span>
                            <div className="size-2 rounded-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)] shrink-0" />
                        </div>
                        <button
                            onClick={handleCopy}
                            className={`px-8 py-3 rounded-xl font-black uppercase tracking-widest text-xs flex items-center justify-center gap-2 transition-all ${copied
                                    ? 'bg-emerald-500/20 text-emerald-500 border border-emerald-500/50'
                                    : 'bg-primary text-black shadow-[0_0_20px_rgba(13,242,51,0.2)] hover:bg-primary/90 active:scale-[0.98]'
                                }`}
                        >
                            {copied ? <><CheckCircle2 size={16} /> COPIED</> : <><Copy size={16} /> COPY LINK</>}
                        </button>
                    </div>

                    <div className="p-4 rounded-xl border border-white/[0.05] bg-white/[0.02] flex items-start gap-4">
                        <div className="p-2 bg-blue-500/10 rounded-lg text-blue-400 shrink-0">
                            <Users size={20} />
                        </div>
                        <div>
                            <h4 className="text-sm font-bold text-white mb-1">How it works</h4>
                            <p className="text-xs text-slate-400 leading-relaxed">
                                Share your link on Twitter, Discord, or with your betting syndicate. When a click successfully converts into an active Pro tier subscription, you'll receive a commission credit securely routed via Stripe Connect.
                            </p>
                        </div>
                    </div>
                </motion.div>

                {/* Tracking Metrics */}
                <div className="space-y-6">
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="glass-premium p-6 rounded-2xl border-white/5 text-center group"
                    >
                        <div className="mx-auto size-12 rounded-full bg-white/5 flex items-center justify-center text-slate-400 mb-4 group-hover:bg-primary/10 group-hover:text-primary transition-colors">
                            <Link2 size={24} />
                        </div>
                        <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mb-1">Total Link Clicks</p>
                        <h3 className="text-4xl font-black text-white">{referralData?.clicks || 0}</h3>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                        className="glass-premium p-6 rounded-2xl border-emerald-500/10 text-center relative overflow-hidden group"
                    >
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                            <DollarSign size={80} className="text-emerald-500" />
                        </div>
                        <p className="text-[10px] text-emerald-500 font-bold uppercase tracking-widest mb-1 relative z-10">Unpaid Bounties (Est)</p>
                        <h3 className="text-5xl font-black text-white relative z-10">${estimatedPayout}</h3>
                        <p className="text-[10px] text-slate-400 mt-2 font-medium relative z-10">From {referralData?.conversions || 0} Pro Conversions</p>
                    </motion.div>
                </div>
            </div>
        </div>
    );
}
