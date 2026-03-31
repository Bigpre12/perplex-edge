"use client";

import { motion } from "framer-motion";

export function UpgradeWall({ onDismiss }: { onDismiss?: () => void }) {
    return (
        <div className="fixed inset-0 bg-[#080810]/95 backdrop-blur-2xl 
                    z-[100] flex items-end justify-center pb-8 px-4 sm:items-center sm:pb-0">
            <motion.div
                initial={{ y: 100, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                exit={{ y: 100, opacity: 0 }}
                className="bg-[#141424] border border-[#1E1E35] rounded-[2rem] 
                      p-6 w-full max-w-sm shadow-[0_20px_50px_rgba(0,0,0,0.5)]"
            >
                <div className="text-center mb-6">
                    <div className="text-5xl mb-4">⚡</div>
                    <h2 className="text-white font-bold text-2xl mb-2">
                        Unlock Sharp Intelligence
                    </h2>
                    <p className="text-[#6B7280] text-sm leading-relaxed px-4">
                        Kelly units, Steam alerts, and CLV tracking
                        are <span className="text-[#F5C518] font-bold">Lucrix Pro</span> features.
                    </p>
                </div>

                {/* Tiers */}
                <div className="space-y-2.5 mb-8">
                    {[
                        { name: 'Free', price: '$0', perks: ['Full props feed', 'Basic slates'] },
                        { name: 'Pro', price: '$19.99', perks: ['Kelly units', '🔥 Steam score', 'Real-time Intel'], highlight: true },
                        { name: 'Elite', price: '$39.99', perks: ['Everything', 'Oracle AI+', 'Whale Tracker'] },
                    ].map(tier => (
                        <div key={tier.name}
                            className={`p-4 rounded-2xl border transition-all cursor-pointer
                ${tier.highlight
                                    ? 'border-[#F5C518] bg-[#F5C518]/5 shadow-[0_0_20px_rgba(245,197,24,0.05)]'
                                    : 'border-[#1E1E35] bg-[#0F0F1A] hover:bg-[#1E1E35]'}`}>
                            <div className="flex items-center justify-between mb-1.5">
                                <span className={`font-bold text-sm flex items-center gap-2
                  ${tier.highlight ? 'text-[#F5C518]' : 'text-white'}`}>
                                    {tier.name}
                                    {tier.highlight && <span className="text-[9px] bg-[#F5C518] text-black px-2 py-0.5 rounded-full font-black tracking-tighter">POPULAR</span>}
                                </span>
                                <span className="text-white font-mono font-bold">{tier.price}<span className="text-[#6B7280] text-[10px] ml-0.5 uppercase">/mo</span></span>
                            </div>
                            <p className="text-[#6B7280] text-[11px] leading-tight">{tier.perks.join(' · ')}</p>
                        </div>
                    ))}
                </div>

                <button className="w-full bg-[#F5C518] text-black font-black uppercase tracking-wider
                           py-4 rounded-2xl text-sm hover:bg-[#C49A12] 
                           transition-all shadow-[0_4px_15px_rgba(245,197,24,0.2)] active:scale-95">
                    Get Pro & Win More
                </button>
                <button
                    onClick={onDismiss}
                    className="w-full text-[#6B7280] text-xs mt-4 font-semibold hover:text-white transition-colors">
                    Continue with Free Tier
                </button>
            </motion.div>
        </div>
    )
}
