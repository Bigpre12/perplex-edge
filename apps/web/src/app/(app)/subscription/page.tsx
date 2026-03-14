"use client";

import { useCallback } from "react";
import { Check, ShieldCheck, Zap, Star, ShieldAlert, CreditCard, Sparkles } from "lucide-react";
import { useLiveData } from "@/hooks/useLiveData";
import { api } from "@/lib/api";
import LiveStatusBar from "@/components/LiveStatusBar";
import PageStates from "@/components/PageStates";

const TIERS = [
    {
        name: "Free",
        price: "$0",
        desc: "Essential tracking for casual bettors.",
        features: ["Standard Prop Feed", "Delayed Injury Alerts", "Basic Bankroll Tracking", "1 Model Signal / day"],
        cta: "Current Plan",
        highlight: false
    },
    {
        name: "Pro",
        price: "$49",
        desc: "Our most popular tier for serious growth.",
        features: ["Live +EV Scanner", "Sharp Money Discrepancies", "Instant Steam Move Alerts", "Full Hit Rate Analytics", "Kelly Criterion Sizing"],
        cta: "Upgrade to Pro",
        highlight: true
    },
    {
        name: "Elite",
        price: "$149",
        desc: "Institutional tools for the top 1%.",
        features: ["Priority API Access", "Private Syndicate Slack", "Automated Bet Placement", "1-on-1 Strategy Calls", "Custom Model Parameters"],
        cta: "Join Elite",
        highlight: false
    }
];

export default function SubscriptionPage() {
    const { data: user, loading, error, lastUpdated, isStale, refresh } = useLiveData<any>(
        () => api.fetch(`/api/user/profile`),
        [],
        { refreshInterval: 600000 } // 10 minutes
    );

    return (
        <div className="p-4 sm:p-6 max-w-7xl mx-auto space-y-12 pb-24 text-white">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <div className="bg-[#F5C518]/20 p-2 rounded-lg border border-[#F5C518]/30">
                            <Sparkles size={24} className="text-[#F5C518]" />
                        </div>
                        <h1 className="text-3xl font-black italic tracking-tighter uppercase text-white">Alpha Access</h1>
                    </div>
                    <p className="text-[#6B7280] text-sm font-medium">Institutional data, zero latency. Choose your intelligence tier.</p>
                </div>

                <div className="flex items-center gap-4">
                    <div className="bg-[#0D0D14] border border-white/5 rounded-xl px-4 py-2 flex items-center gap-3 shadow-2xl">
                        <div className="flex flex-col">
                            <span className="text-[9px] font-black text-[#6B7280] uppercase tracking-widest leading-none mb-1">Current Tier</span>
                            <span className="text-xs font-black text-primary italic uppercase tracking-tighter leading-none">{user?.subscription_tier || 'PRO'}</span>
                        </div>
                    </div>
                    <LiveStatusBar
                        lastUpdated={lastUpdated}
                        isStale={isStale}
                        loading={loading}
                        error={error}
                        onRefresh={refresh}
                        refreshInterval={600}
                    />
                </div>
            </div>

            <PageStates
                loading={loading && !user}
                error={error}
                empty={false}
            >
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {TIERS.map((tier) => (
                        <div key={tier.name} className={`p-8 rounded-3xl border flex flex-col relative overflow-hidden transition-all group shadow-2xl ${tier.highlight
                            ? "bg-[#0D0D14] border-primary/30 scale-105 z-10"
                            : "bg-[#0D0D14] border-white/5"
                            }`}>
                            {tier.highlight && (
                                <div className="absolute top-0 right-8 bg-primary text-black font-black uppercase tracking-widest text-[9px] px-4 py-1.5 rounded-b-lg shadow-xl italic">
                                    MOST POPULAR
                                </div>
                            )}

                            <div className="mb-8">
                                <h3 className="text-xl font-black italic uppercase tracking-tight mb-1">{tier.name}</h3>
                                <p className="text-[10px] font-bold text-[#6B7280] uppercase tracking-widest">{tier.desc}</p>
                            </div>

                            <div className="flex items-baseline gap-2 mb-10">
                                <span className="text-5xl font-black font-mono tracking-tighter">{tier.price}</span>
                                <span className="text-[#6B7280] font-black uppercase text-[10px] tracking-widest">/ month</span>
                            </div>

                            <div className="space-y-4 mb-12 flex-1">
                                {tier.features.map((f, i) => (
                                    <div key={i} className="flex items-start gap-3">
                                        <div className={`h-4 w-4 rounded-md flex items-center justify-center shrink-0 mt-0.5 ${tier.highlight ? "bg-primary" : "bg-white/5"
                                            }`}>
                                            <Check size={10} className={tier.highlight ? "text-black" : "text-[#6B7280]"} />
                                        </div>
                                        <span className="text-[10px] font-medium text-[#6B7280] uppercase tracking-tight group-hover:text-white transition-colors">{f}</span>
                                    </div>
                                ))}
                            </div>

                            <button className={`w-full py-4 rounded-xl font-black uppercase tracking-widest text-xs transition-all shadow-xl ${tier.highlight
                                ? "bg-primary text-black hover:scale-[1.02] active:scale-95 italic"
                                : "bg-white/5 text-[#6B7280] hover:bg-white/10"
                                }`}>
                                {tier.cta}
                            </button>
                        </div>
                    ))}
                </div>

                <div className="bg-[#0D0D14] border border-white/5 rounded-3xl p-12 flex flex-col items-center text-center max-w-4xl mx-auto shadow-2xl relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-primary/20 to-transparent"></div>
                    <ShieldCheck size={48} className="text-primary mb-6 animate-pulse" />
                    <h4 className="text-2xl font-black italic uppercase tracking-tighter">Institutional Edge Guarantee</h4>
                    <p className="text-[10px] text-[#6B7280] font-medium max-w-lg mt-4 leading-relaxed uppercase tracking-[0.15em]">
                        All data is sourced directly from private model syndicates and institutional bookmaker feeds. We protect our users with audited settlement verification and zero-latency line reporting.
                    </p>
                    <div className="flex flex-wrap justify-center gap-6 mt-10">
                        <div className="flex items-center gap-2 text-[9px] font-black uppercase tracking-widest text-white/40 border border-white/5 px-4 py-2 rounded-full">
                            <CreditCard size={12} className="text-primary" /> SECURE BILLING
                        </div>
                        <div className="flex items-center gap-2 text-[9px] font-black uppercase tracking-widest text-white/40 border border-white/5 px-4 py-2 rounded-full">
                            <ShieldAlert size={12} className="text-primary" /> FRAUD PROTECTED
                        </div>
                    </div>
                </div>
            </PageStates>
        </div>
    );
}
