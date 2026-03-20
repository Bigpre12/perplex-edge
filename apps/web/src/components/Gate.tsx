"use client";
import { useSubscription } from "@/hooks/useSubscription";
import { FeatureKey, getRequiredTier } from "@/lib/permissions";
import Link from "next/link";
import { clsx } from "clsx";

interface GateProps {
    feature: FeatureKey;
    children: React.ReactNode;
    quiet?: boolean;   // just hide — no upgrade prompt
}

export default function Gate({ feature, children, quiet = false }: GateProps) {
    const { can, loading } = useSubscription();
    const isDevMode = process.env.NEXT_PUBLIC_DEV_MODE === "true";

    if (loading) return null;
    const hasAccess = can(feature); // Define hasAccess here

    if (isDevMode || hasAccess) {
        return <>{children}</>;
    }
    if (quiet) return null;

    const required = getRequiredTier(feature);

    return (
        <div className={clsx(
            "bg-lucrix-surface rounded-[14px] p-8 text-center relative overflow-hidden border",
            required === "elite" ? "border-[#f59e0b30]" : "border-[#6366f130]"
        )}>
            {/* Blurred preview bg */}
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,_rgba(99,102,241,0.05),_transparent_70%)] pointer-events-none" />

            <div className="text-[36px] mb-3">
                {required === "elite" ? "👑" : "⚡"}
            </div>
            <div className="font-black text-[18px] mb-2 text-white">
                {required === "elite" ? "Elite" : "Pro"} Feature
            </div>
            <div className="text-textSecondary text-[13px] mb-5 max-w-[280px] mx-auto text-center">
                Upgrade to <strong className={required === "elite" ? "text-[#f59e0b]" : "text-[#818cf8]"}>
                    {required === "elite" ? "Elite ($39.99/mo)" : "Pro ($19.99/mo)"}
                </strong> to unlock this feature.
            </div>
            <Link href="/pricing" className={clsx(
                "inline-block px-7 py-2.5 rounded-xl font-black text-sm transition-all",
                required === "elite" 
                    ? "bg-gradient-to-br from-[#f59e0b] to-[#d97706] shadow-glow shadow-orange-500/20 hover:scale-105" 
                    : "bg-gradient-to-br from-[#6366f1] to-[#8b5cf6] shadow-glow shadow-indigo-500/20 hover:scale-105"
            )}>
                Upgrade Now →
            </Link>
        </div>
    );
}
