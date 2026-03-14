"use client";

import React from 'react';
import { useSubscription } from '@/hooks/useSubscription';
import { checkTierAccess, Tier } from '@/lib/tier';
import Link from 'next/link';

interface TierGateProps {
    feature: string;
    description: string;
    requiredTier: 'pro' | 'elite';
    children: React.ReactNode;
    mode?: 'blur' | 'hide' | 'lock';
}

/**
 * TierGate - Wraps sensitive features and provides a premium "locked" experience 
 * if the user's subscription doesn't meet requirements.
 */
export default function TierGate({
    feature,
    description,
    requiredTier,
    children,
    mode = 'blur',
}: TierGateProps) {
    const { tier, loading } = useSubscription();

    // Show children while loading — avoids flash of lock screen
    if (loading) return <>{children}</>;

    const hasAccess = checkTierAccess(
        tier as Tier,
        requiredTier
    );

    // Unlocked — show full feature
    if (hasAccess) return <>{children}</>;

    // Hidden lock
    if (mode === 'hide') return null;

    const isElite = requiredTier === 'elite';
    const color = isElite ? '#06b6d4' : '#F5C518';
    const label = isElite ? 'ELITE' : 'PRO';

    return (
        <div className="relative rounded-2xl overflow-hidden border border-white/5 bg-black/40">
            {mode === 'blur' && (
                <div className="blur-md pointer-events-none select-none opacity-30">
                    {children}
                </div>
            )}

            <div className="absolute inset-0 flex items-center justify-center bg-[#080810]/80 backdrop-blur-[2px] z-10 p-8 border border-white/10 rounded-2xl">
                <div className="text-center max-w-[280px] animate-in fade-in zoom-in duration-500">
                    <div className="text-3xl mb-4 grayscale opacity-80">🔒</div>

                    <h3 className="text-[#f1f5f9] text-base font-black tracking-tight mb-2 uppercase">
                        {feature}
                    </h3>

                    <p className="text-[#6B7280] text-[11px] leading-relaxed font-bold uppercase tracking-wider mb-6">
                        {description}
                    </p>

                    <div className={`inline-block px-3 py-1 rounded-full text-[9px] font-black mb-6 tracking-widest ${isElite ? 'bg-cyan-500/10 text-cyan-400' : 'bg-[#F5C518]/10 text-[#F5C518]'}`}>
                        {label} FEATURE
                    </div>

                    <Link
                        href="/pricing"
                        className="block w-full py-3 rounded-xl font-black text-[11px] tracking-widest uppercase transition-all hover:scale-[1.02] active:scale-[0.98] shadow-lg shadow-[#F5C518]/5"
                        style={{
                            background: isElite ? 'linear-gradient(135deg, #06b6d4, #3b82f6)' : 'linear-gradient(135deg, #F5C518, #FF8C00)',
                            color: '#000'
                        }}
                    >
                        Upgrade to {label}
                    </Link>
                </div>
            </div>
        </div>
    );
}
