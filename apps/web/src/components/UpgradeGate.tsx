"use client";
import { useState, useEffect } from "react";
import { Lock, Zap, ArrowRight, Check } from "lucide-react";
import { useSubscription } from "@/hooks/useSubscription";
import { supabase } from "@/lib/supabaseClient";

interface Props {
    children: React.ReactNode;
    tierRequired?: string;
}

export function UpgradeGate({ children, tierRequired = "pro" }: Props) {
    const { tier, loading } = useSubscription();

    if (loading) {
        return (
            <div className="w-full h-64 flex items-center justify-center animate-pulse text-gray-500 uppercase font-black tracking-widest text-xs">
                Verifying Access Level...
            </div>
        );
    }

    const currentTier = tier.toLowerCase();
    const targetTier = tierRequired.toLowerCase();

    // Elite/Owner always has access. Pro has access if target is Pro.
    const hasAccess =
        currentTier === "elite" ||
        currentTier === "owner" ||
        (currentTier === "pro" && targetTier === "pro");

    if (hasAccess) {
        return <>{children}</>;
    }

    // Not upgraded, show paywall
    return (
        <div className="flex flex-col items-center justify-center min-h-[60vh] p-4 text-center space-y-6">
            <div className="bg-yellow-500/10 text-yellow-400 p-4 rounded-full border border-yellow-500/20">
                <Lock size={48} />
            </div>

            <div className="max-w-md space-y-4">
                <h2 className="text-3xl font-black text-white">Unlock the Oracle</h2>
                <p className="text-gray-400 text-lg">
                    You need {tierRequired} access to view this advanced data. Stop guessing and start investing with real-time edges.
                </p>
            </div>

            <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 w-full max-w-sm text-left space-y-4 shadow-xl">
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                    <Zap className="text-blue-400" /> Pro Features
                </h3>
                <ul className="space-y-3">
                    {["Live Line Movement Alerts", "+EV Prop Screener", "Personal Analytics Track", "Institutional Data Feeds"].map(f => (
                        <li key={f} className="flex gap-2 text-sm text-gray-300">
                            <Check size={18} className="text-green-400 flex-shrink-0" />
                            {f}
                        </li>
                    ))}
                </ul>
                <button
                    onClick={() => window.location.href = "/api/stripe/checkout"}
                    className="w-full mt-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold py-3 rounded-xl transition flex items-center justify-center gap-2"
                >
                    Upgrade Now <ArrowRight size={18} />
                </button>
            </div>
        </div>
    );
}
