"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Sparkles, ShieldCheck, Zap, ArrowRight, Check } from "lucide-react";
import { getUser } from "@/lib/auth";

import { API_ENDPOINTS } from "@/lib/apiConfig";

export default function CheckoutPage() {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleUpgrade = async () => {
        setLoading(true);
        setError("");

        try {
            const user = getUser();

            if (!user) {
                window.location.href = "/login";
                return;
            }

            const res = await fetch(`${API_ENDPOINTS.STRIPE}/create-checkout-session`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    user_email: user.email,
                    user_id: String(user.id)
                })
            });

            if (!res.ok) {
                const data = await res.json();
                throw new Error(data.detail || "Failed to initialize secure checkout");
            }

            const { session_url } = await res.json();

            // Redirect to Stripe Hosted Checkout
            window.location.href = session_url;

        } catch (err: any) {
            setError(err.message);
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#050505] flex items-center justify-center p-4 relative overflow-hidden">
            {/* Ambient Background */}
            <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
                <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/10 blur-[120px] rounded-full" />
                <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/10 blur-[120px] rounded-full" />
            </div>

            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="w-full max-w-5xl z-10 grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-0"
            >
                {/* Left Panel: The Pitch */}
                <div className="lg:pr-12 flex flex-col justify-center">
                    <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-primary text-xs font-black uppercase tracking-widest w-fit mb-6 shadow-[0_0_15px_rgba(13,242,51,0.2)]">
                        <Sparkles size={14} /> Pro Clearance Required
                    </div>

                    <h1 className="text-4xl lg:text-5xl font-black text-white tracking-tight mb-6 leading-tight">
                        Unlock the <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-emerald-400">Institutional</span> Edge Engine
                    </h1>

                    <p className="text-slate-400 text-lg mb-8 leading-relaxed">
                        You have entered a restricted zone. Upgrade your clearance to access real-time Sharp Models, automated Arbitrage detection, and Live Web Push alerts.
                    </p>

                    <div className="space-y-4">
                        {[
                            "Live Arbitrage & Middle Betting Scanner",
                            "Dynamic Player Trends Data Visualization",
                            "Instant Push Notification Alerts",
                            "Custom AI Minimum EV% Sliders"
                        ].map((feature, i) => (
                            <div key={i} className="flex items-center gap-3">
                                <div className="flex-shrink-0 size-6 rounded-full bg-primary/20 flex items-center justify-center border border-primary/30">
                                    <Check size={12} className="text-primary" />
                                </div>
                                <span className="text-slate-300 font-medium">{feature}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Right Panel: The Pricing Card */}
                <div className="bg-[#0c1416]/90 backdrop-blur-2xl border border-white/10 p-8 lg:p-12 rounded-[2rem] shadow-2xl relative">
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-3/4 h-1 bg-gradient-to-r from-transparent via-primary to-transparent opacity-50" />

                    <div className="text-center mb-8">
                        <h2 className="text-2xl font-black text-white mb-2">Pro Membership</h2>
                        <div className="flex items-center justify-center gap-1">
                            <span className="text-5xl font-black text-white">$49</span>
                            <span className="text-slate-500 font-medium mt-3">/mo</span>
                        </div>
                    </div>

                    {error && (
                        <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm text-center font-medium">
                            {error}
                        </div>
                    )}

                    <button
                        onClick={handleUpgrade}
                        disabled={loading}
                        className="w-full bg-gradient-to-r from-primary to-emerald-500 hover:from-primary/90 hover:to-emerald-400 text-black font-black py-4 rounded-xl shadow-[0_0_20px_rgba(13,242,51,0.3)] flex items-center justify-center gap-3 transition-all active:scale-[0.98]"
                    >
                        {loading ? (
                            <div className="w-5 h-5 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                        ) : (
                            <>
                                <Zap size={18} /> Initialize Secure Checkout <ArrowRight size={18} />
                            </>
                        )}
                    </button>

                    <p className="text-center text-xs text-slate-500 font-medium mt-6 flex items-center justify-center gap-1.5">
                        <ShieldCheck size={14} className="text-slate-400" />
                        Payments securely processed by Stripe
                    </p>
                </div>
            </motion.div>
        </div>
    );
}
