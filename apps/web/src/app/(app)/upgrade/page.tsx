"use client";

import { Check, Zap, Brain, Shield, ArrowRight } from "lucide-react";
import { useRouter } from "next/navigation";

export default function UpgradePage() {
    const router = useRouter();

    const handleUpgrade = (tier: string) => {
        // Implement Stripe checkout routing
        router.push(`/checkout?tier=${tier}`);
    };

    return (
        <div className="min-h-screen py-12 px-4 flex flex-col items-center">
            <div className="text-center mb-12 max-w-3xl mx-auto">
                <div className="inline-flex items-center gap-2 bg-[#F5C518]/10 text-[#F5C518] px-3 py-1 rounded-full text-xs font-black uppercase tracking-widest mb-6 border border-[#F5C518]/20">
                    <Zap size={14} className="animate-pulse" />
                    Unlock Institutional Grade Intel
                </div>
                <h1 className="text-4xl md:text-5xl font-black text-white italic uppercase tracking-tighter mb-4">
                    Stop Guessing. <span className="text-[#F5C518]">Start Knowing.</span>
                </h1>
                <p className="text-[#6B7280] text-lg font-medium">
                    Upgrade to Pro and get real-time market steam alerts, precise Kelly sizing, and unrestricted access to the Antigravity Quantum Model.
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl w-full">
                {/* Free Tier */}
                <div className="bg-[#141424] border border-[#1E1E35] rounded-3xl p-8 flex flex-col relative overflow-hidden h-full">
                    <div className="mb-8">
                        <h3 className="text-xl font-bold text-white mb-2">Free</h3>
                        <div className="flex items-baseline gap-2 mb-2">
                            <span className="text-4xl font-black text-white">$0</span>
                            <span className="text-[#6B7280] text-sm">/ forever</span>
                        </div>
                        <p className="text-[#6B7280] text-sm">Basic analytics for casual users.</p>
                    </div>

                    <div className="space-y-4 mb-8 flex-1">
                        <Feature icon={<Check size={16} className="text-[#6B7280]" />} text="3 Player Props per day" dim />
                        <Feature icon={<Check size={16} className="text-[#6B7280]" />} text="Basic Hit Rates" dim />
                        <Feature icon={<Check size={16} className="text-[#6B7280]" />} text="Standard Dashboard" dim />
                    </div>

                    <button
                        onClick={() => router.push('/')}
                        className="w-full py-3.5 bg-[#1E1E35] hover:bg-[#2A2A45] text-white rounded-xl font-bold transition-all"
                    >
                        Current Plan
                    </button>
                </div>

                {/* Pro Tier */}
                <div className="bg-[#1A1A2E] border-2 border-[#F5C518] rounded-3xl p-8 flex flex-col relative overflow-hidden h-full shadow-[0_0_40px_rgba(245,197,24,0.1)]">
                    <div className="absolute top-0 right-0 bg-[#F5C518] text-black text-[10px] font-black uppercase tracking-widest px-4 py-1.5 rounded-bl-xl z-10">
                        Most Popular
                    </div>
                    <div className="absolute -top-32 -right-32 w-64 h-64 bg-[#F5C518]/10 rounded-full blur-3xl z-0" />

                    <div className="mb-8 relative z-10">
                        <h3 className="text-xl font-bold text-[#F5C518] mb-2">Quantum Pro</h3>
                        <div className="flex items-baseline gap-2 mb-2">
                            <span className="text-4xl font-black text-white">$49</span>
                            <span className="text-[#6B7280] text-sm">/ month</span>
                        </div>
                        <p className="text-[#6B7280] text-sm">Full API access to sharp consensus and algorithm edges.</p>
                    </div>

                    <div className="space-y-4 mb-8 flex-1 relative z-10">
                        <Feature icon={<Brain size={16} className="text-[#F5C518]" />} text="Unlimited Quantum Player Props" />
                        <Feature icon={<Zap size={16} className="text-[#F5C518]" />} text="Real-time Whale Steam Alerts" />
                        <Feature icon={<Check size={16} className="text-[#F5C518]" />} text="Antigravity True Line & Kelly Sizing" />
                        <Feature icon={<Shield size={16} className="text-[#F5C518]" />} text="Risk / Exposure Calculator" />
                    </div>

                    <button
                        onClick={() => handleUpgrade('pro')}
                        className="relative z-10 w-full py-3.5 bg-[#F5C518] hover:bg-[#E5B508] text-black rounded-xl font-black text-sm uppercase tracking-wider transition-all shadow-[0_4px_14px_rgba(245,197,24,0.4)] flex items-center justify-center gap-2 group"
                    >
                        Unlock Pro Access
                        <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
                    </button>
                </div>
            </div>
        </div>
    );
}

function Feature({ icon, text, dim = false }: { icon: React.ReactNode, text: string, dim?: boolean }) {
    return (
        <div className={`flex items-start gap-3 ${dim ? 'text-[#6B7280]' : 'text-white'}`}>
            <div className="mt-0.5">{icon}</div>
            <p className="text-sm font-medium">{text}</p>
        </div>
    );
}
