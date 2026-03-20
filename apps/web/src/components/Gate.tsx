"use client";
import { useSubscription } from "@/hooks/useSubscription";
import { FeatureKey, getRequiredTier } from "@/lib/permissions";
import Link from "next/link";

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
        <div style={{
            background: "#0f1117",
            borderRadius: "14px",
            padding: "32px",
            textAlign: "center",
            border: `1px solid ${required === "elite" ? "#f59e0b30" : "#6366f130"}`,
            position: "relative",
            overflow: "hidden",
        }}>
            {/* Blurred preview bg */}
            <div style={{
                position: "absolute", inset: 0,
                background: "radial-gradient(circle at 50% 0%, rgba(99,102,241,0.05), transparent 70%)",
                pointerEvents: "none",
            }} />

            <div style={{ fontSize: "36px", marginBottom: "12px" }}>
                {required === "elite" ? "👑" : "⚡"}
            </div>
            <div style={{ fontWeight: 900, fontSize: "18px", marginBottom: "8px", color: "#fff" }}>
                {required === "elite" ? "Elite" : "Pro"} Feature
            </div>
            <div style={{ color: "#6b7280", fontSize: "13px", marginBottom: "20px", maxWidth: "280px", margin: "0 auto 20px" }}>
                Upgrade to <strong style={{ color: required === "elite" ? "#f59e0b" : "#818cf8" }}>
                    {required === "elite" ? "Elite ($39.99/mo)" : "Pro ($19.99/mo)"}
                </strong> to unlock this feature.
            </div>
            <Link href="/pricing" style={{
                display: "inline-block",
                padding: "10px 28px",
                background: required === "elite"
                    ? "linear-gradient(135deg, #f59e0b, #d97706)"
                    : "linear-gradient(135deg, #6366f1, #8b5cf6)",
                color: "#fff", borderRadius: "10px",
                fontWeight: 800, fontSize: "14px",
                textDecoration: "none",
            }}>
                Upgrade Now →
            </Link>
        </div>
    );
}
