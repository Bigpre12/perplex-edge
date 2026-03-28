"use client";
import React from "react";
import { Lock, Zap, ArrowRight, Check } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { FeatureKey, getRequiredTier } from "@/lib/featureAccess";
import { checkTierAccess, Tier } from "@/lib/tier";

interface Props {
    children: React.ReactNode;
    feature?: FeatureKey;
    tierRequired?: Tier;
}

/**
 * UpgradeGate - A high-visibility paywall component.
 * Can be triggered either by a specific 'feature' key or a minimum 'tierRequired'.
 */
export function UpgradeGate({ children, feature, tierRequired }: Props) {
    const { tier, loading, checkAccess } = useAuth();
    const isDevMode = process.env.NEXT_PUBLIC_DEV_MODE === "true";

    if (loading) {
        return (
            <div className="w-full h-64 flex items-center justify-center animate-pulse text-gray-500 uppercase font-black tracking-widest text-xs">
                Verifying Access Level...
            </div>
        );
    }

    // Determine if user has access
    let hasAccess = false;
    let required: Tier = "pro";

    if (feature) {
        hasAccess = checkAccess(feature);
        required = getRequiredTier(feature);
    } else if (tierRequired) {
        hasAccess = checkTierAccess(tier, tierRequired);
        required = tierRequired;
    } else {
        // Default to pro if nothing specified
        hasAccess = checkTierAccess(tier, "pro");
        required = "pro";
    }

    if (isDevMode || hasAccess) {
        return <>{children}</>;
    }

    // Not upgraded, show paywall
    return (
        <div className="flex flex-col items-center justify-center min-h-[60vh] p-4 text-center space-y-6">
            <div className="bg-yellow-500/10 text-yellow-400 p-4 rounded-full border border-yellow-500/20 shadow-[0_0_20px_rgba(234,179,8,0.1)]">
                <Lock size={48} />
            </div>

            <div className="max-w-md space-y-4">
                <h2 className="text-3xl font-black text-white tracking-tight">Unlock the Oracle</h2>
                <p className="text-gray-400 text-lg leading-relaxed">
                    You need <span className="text-white font-bold">{required.toUpperCase()}</span> access to view this advanced data. Stop guessing and start investing with real-time edges.
                </p>
            </div>

            <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 w-full max-w-sm text-left space-y-4 shadow-xl relative overflow-hidden">
                <div className="absolute top-0 right-0 w-32 h-32 bg-blue-600/5 blur-3xl -mr-16 -mt-16 pointer-events-none" />
                
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                    <Zap className="text-blue-400" size={20} /> {required.charAt(0).toUpperCase() + required.slice(1)} Features
                </h3>
                <ul className="space-y-3">
                    {[
                        "Live Line Movement Alerts", 
                        "+EV Prop Screener", 
                        "Personal Analytics Track", 
                        "Institutional Data Feeds"
                    ].map(f => (
                        <li key={f} className="flex gap-3 text-sm text-gray-400">
                            <Check size={18} className="text-green-500/80 flex-shrink-0" />
                            {f}
                        </li>
                    ))}
                </ul>
                <button
                    onClick={() => window.location.href = "/pricing"}
                    className="w-full mt-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-black py-4 rounded-xl transition-all hover:scale-[1.02] active:scale-[0.98] shadow-lg shadow-blue-600/20 flex items-center justify-center gap-2"
                >
                    Upgrade Now <ArrowRight size={18} />
                </button>
            </div>
        </div>
    );
}
