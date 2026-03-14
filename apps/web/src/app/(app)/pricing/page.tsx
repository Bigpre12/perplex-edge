"use client";
import { useState, useEffect } from "react";
// Removed Clerk useAuth, using Supabase auth instead since we migrated
import { supabase } from "@/lib/supabaseClient";
import { PLANS, startCheckout, PlanKey } from "@/lib/stripe";
import { useSubscription } from "@/hooks/useSubscription";

export default function PricingPage() {
    const { tier: currentTier } = useSubscription();
    const [billing, setBilling] = useState<"monthly" | "annual">("monthly");
    const [loading, setLoading] = useState<string | null>(null);
    const [isSignedIn, setIsSignedIn] = useState(false);

    useEffect(() => {
        supabase.auth.getSession().then(({ data: { session } }) => {
            setIsSignedIn(!!session);
        });
    }, []);

    const handleCheckout = async (planKey: PlanKey) => {
        const plan = PLANS[planKey];
        if (plan.href) { window.location.href = plan.href; return; }

        const priceId = billing === "annual"
            ? plan.annualPriceId
            : plan.monthlyPriceId;

        if (!priceId) return;

        setLoading(planKey);
        try {
            await startCheckout(priceId); // Supabase token handling is now built into startCheckout
        } catch (e) {
            alert("Something went wrong. Please try again.");
        } finally {
            setLoading(null);
        }
    };

    const annualSavings = (monthly: number) =>
        Math.round(monthly * 12 - (monthly === 19.99 ? 199 : 399));

    return (
        <div style={{
            background: "#0a0c12", minHeight: "100vh",
            padding: "60px 24px", color: "#fff",
        }}>

            {/* Header */}
            <div style={{ textAlign: "center", marginBottom: "48px" }}>
                <div style={{
                    display: "inline-block",
                    background: "#6366f120",
                    color: "#818cf8",
                    padding: "6px 16px", borderRadius: "20px",
                    fontSize: "12px", fontWeight: 700,
                    letterSpacing: "0.08em", marginBottom: "16px",
                }}>
                    PRICING
                </div>
                <h1 style={{
                    fontSize: "clamp(32px, 5vw, 52px)",
                    fontWeight: 900, margin: "0 0 16px",
                    background: "linear-gradient(135deg, #fff, #9ca3af)",
                    WebkitBackgroundClip: "text",
                    WebkitTextFillColor: "transparent",
                }}>
                    The Edge Has a Price.<br />Losing Costs More.
                </h1>
                <p style={{ color: "#6b7280", fontSize: "16px", maxWidth: "480px", margin: "0 auto 32px" }}>
                    Professional-grade betting intelligence. No fluff, no filler — just data that wins.
                </p>

                {/* Billing toggle */}
                <div style={{
                    display: "inline-flex",
                    background: "#1a1d2e",
                    borderRadius: "12px",
                    padding: "4px",
                    border: "1px solid #2d3748",
                }}>
                    {(["monthly", "annual"] as const).map(b => (
                        <button
                            key={b}
                            onClick={() => setBilling(b)}
                            style={{
                                padding: "8px 20px", borderRadius: "10px",
                                border: "none", cursor: "pointer",
                                fontWeight: 700, fontSize: "13px",
                                background: billing === b ? "#6366f1" : "transparent",
                                color: billing === b ? "#fff" : "#6b7280",
                                transition: "all 0.2s",
                            }}
                        >
                            {b.charAt(0).toUpperCase() + b.slice(1)}
                            {b === "annual" && (
                                <span style={{
                                    marginLeft: "6px", fontSize: "10px",
                                    background: "#10b98130", color: "#10b981",
                                    padding: "2px 6px", borderRadius: "10px",
                                }}>
                                    2 months free
                                </span>
                            )}
                        </button>
                    ))}
                </div>
            </div>

            {/* Plan Cards */}
            <div style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 300px), 1fr))",
                gap: "20px",
                maxWidth: "1000px",
                margin: "0 auto 60px",
            }}>
                {(Object.entries(PLANS) as [PlanKey, typeof PLANS[PlanKey]][]).map(([key, plan]) => {
                    const isCurrent = currentTier === key;
                    const price = billing === "annual" ? plan.annualPrice : plan.monthlyPrice;
                    const isPopular = plan.badge === "Most Popular";
                    const isBest = plan.badge === "Best Value";

                    return (
                        <div key={key} style={{
                            background: "#0f1117",
                            borderRadius: "20px",
                            padding: "32px",
                            border: `2px solid ${isPopular ? "#6366f1" : isBest ? "#f59e0b" : "#1f2937"}`,
                            position: "relative",
                            transform: isPopular ? "scale(1.02)" : "scale(1)",
                            boxShadow: isPopular
                                ? "0 0 40px rgba(99,102,241,0.2)"
                                : isBest
                                    ? "0 0 40px rgba(245,158,11,0.15)"
                                    : "none",
                        }}>

                            {/* Badge */}
                            {plan.badge && (
                                <div style={{
                                    position: "absolute", top: "-14px", left: "50%",
                                    transform: "translateX(-50%)",
                                    background: isPopular ? "#6366f1" : "#f59e0b",
                                    color: "#fff", fontSize: "11px", fontWeight: 800,
                                    padding: "4px 16px", borderRadius: "20px",
                                    letterSpacing: "0.05em", whiteSpace: "nowrap",
                                }}>
                                    {plan.badge}
                                </div>
                            )}

                            {/* Plan name */}
                            <div style={{
                                fontSize: "12px", fontWeight: 800,
                                color: plan.color, letterSpacing: "0.1em",
                                marginBottom: "8px",
                            }}>
                                {plan.name.toUpperCase()}
                            </div>

                            {/* Price */}
                            <div style={{ marginBottom: "8px" }}>
                                <span style={{ fontSize: "42px", fontWeight: 900, color: "#fff" }}>
                                    {price === 0 ? "Free" : `$${price}`}
                                </span>
                                {price > 0 && (
                                    <span style={{ color: "#6b7280", fontSize: "14px", marginLeft: "4px" }}>
                                        /{billing === "annual" ? "yr" : "mo"}
                                    </span>
                                )}
                            </div>

                            {/* Annual savings */}
                            {billing === "annual" && price > 0 && (
                                <div style={{
                                    fontSize: "12px", color: "#10b981", fontWeight: 700,
                                    marginBottom: "12px",
                                }}>
                                    Save ${annualSavings(plan.monthlyPrice)}/year
                                </div>
                            )}

                            {/* Description */}
                            <p style={{
                                fontSize: "13px", color: "#9ca3af",
                                lineHeight: "1.5", marginBottom: "24px",
                            }}>
                                {plan.description}
                            </p>

                            {/* CTA Button */}
                            <button
                                onClick={() => handleCheckout(key)}
                                disabled={isCurrent || loading === key}
                                style={{
                                    width: "100%", padding: "13px",
                                    borderRadius: "12px",
                                    fontWeight: 800, fontSize: "14px",
                                    cursor: isCurrent ? "default" : "pointer",
                                    marginBottom: "24px",
                                    background: isCurrent
                                        ? "#1f2937"
                                        : isPopular
                                            ? "linear-gradient(135deg, #6366f1, #8b5cf6)"
                                            : isBest
                                                ? "linear-gradient(135deg, #f59e0b, #d97706)"
                                                : "#1a1d2e",
                                    color: isCurrent ? "#6b7280" : "#fff",
                                    border: isCurrent
                                        ? "none"
                                        : key === "free"
                                            ? "1px solid #2d3748"
                                            : "none",
                                    transition: "opacity 0.2s",
                                    opacity: loading === key ? 0.7 : 1,
                                }}
                            >
                                {loading === key
                                    ? "Redirecting..."
                                    : isCurrent
                                        ? "✓ Current Plan"
                                        : plan.cta}
                            </button>

                            {/* Features */}
                            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                                {plan.features.map((f, i) => (
                                    <div key={i} style={{
                                        display: "flex", gap: "10px", alignItems: "flex-start",
                                        fontSize: "13px",
                                    }}>
                                        <span style={{ color: plan.color, flexShrink: 0, marginTop: "1px" }}>✓</span>
                                        <span style={{ color: f.startsWith("Everything") ? "#e5e7eb" : "#9ca3af", fontWeight: f.startsWith("Everything") ? 700 : 400 }}>
                                            {f}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Discord/Whop section */}
            <div style={{
                maxWidth: "1000px", margin: "0 auto 60px",
                background: "#0f1117", borderRadius: "20px",
                padding: "40px", border: "1px solid #1f2937",
            }}>
                <div style={{ textAlign: "center", marginBottom: "32px" }}>
                    <div style={{ fontSize: "28px", marginBottom: "8px" }}>💬</div>
                    <h2 style={{ fontWeight: 900, fontSize: "24px", margin: "0 0 8px" }}>
                        VIP Discord Picks Community
                    </h2>
                    <p style={{ color: "#6b7280", fontSize: "14px", margin: 0 }}>
                        Daily pick slips, +EV breakdowns, and a community of sharp bettors.
                    </p>
                </div>

                <div style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
                    gap: "16px",
                }}>
                    {[
                        {
                            label: "Weekly",
                            price: "$24.99",
                            per: "/week",
                            color: "#10b981",
                            features: ["VIP Discord access", "All daily pick slips", "+EV reasoning on every card", "Injury & lineup alerts"],
                            href: "https://whop.com/your-weekly-link",
                        },
                        {
                            label: "Monthly",
                            price: "$59.99",
                            per: "/month",
                            color: "#6366f1",
                            badge: "Popular",
                            features: ["Everything in Weekly", "Full Lucrix Pro included", "Priority alerts channel", "Exclusive members plays"],
                            href: "https://whop.com/your-monthly-link",
                        },
                        {
                            label: "Annual",
                            price: "$599",
                            per: "/year",
                            color: "#f59e0b",
                            badge: "Best Value",
                            features: ["Everything in Monthly", "Elite strategy channel", "Quarterly 1:1 review", "Early feature access"],
                            href: "https://whop.com/your-annual-link",
                        },
                    ].map(tier => (
                        <div key={tier.label} style={{
                            background: "#1a1d2e", borderRadius: "14px",
                            padding: "24px", border: `1px solid ${tier.color}30`,
                            position: "relative",
                        }}>
                            {tier.badge && (
                                <div style={{
                                    position: "absolute", top: "-11px", left: "50%",
                                    transform: "translateX(-50%)",
                                    background: tier.color, color: "#fff",
                                    fontSize: "10px", fontWeight: 800,
                                    padding: "3px 12px", borderRadius: "20px",
                                    whiteSpace: "nowrap",
                                }}>{tier.badge}</div>
                            )}
                            <div style={{ fontSize: "11px", fontWeight: 800, color: tier.color, letterSpacing: "0.1em", marginBottom: "8px" }}>
                                {tier.label.toUpperCase()}
                            </div>
                            <div style={{ marginBottom: "16px" }}>
                                <span style={{ fontSize: "28px", fontWeight: 900 }}>{tier.price}</span>
                                <span style={{ color: "#6b7280", fontSize: "13px" }}>{tier.per}</span>
                            </div>
                            <div style={{ display: "flex", flexDirection: "column", gap: "8px", marginBottom: "20px" }}>
                                {tier.features.map((f, i) => (
                                    <div key={i} style={{ fontSize: "12px", color: "#9ca3af", display: "flex", gap: "8px" }}>
                                        <span style={{ color: tier.color }}>✓</span>{f}
                                    </div>
                                ))}
                            </div>
                            <a href={tier.href} target="_blank" rel="noopener noreferrer" style={{
                                display: "block", width: "100%", padding: "10px",
                                background: tier.color, borderRadius: "10px",
                                color: "#fff", fontWeight: 800, fontSize: "13px",
                                textAlign: "center", textDecoration: "none",
                                boxSizing: "border-box",
                            }}>
                                Join on Whop →
                            </a>
                        </div>
                    ))}
                </div>
            </div>

            {/* Competitor callout */}
            <div style={{
                maxWidth: "1000px", margin: "0 auto 60px",
                background: "linear-gradient(135deg, #0f1117, #1a1d2e)",
                borderRadius: "16px", padding: "32px",
                border: "1px solid #6366f130", textAlign: "center",
            }}>
                <div style={{ fontSize: "13px", color: "#9ca3af", maxWidth: "600px", margin: "0 auto" }}>
                    <span style={{ color: "#6b7280" }}>Outlier Pro charges </span>
                    <span style={{ color: "#f87171", fontWeight: 700, textDecoration: "line-through" }}>$79.99/month</span>
                    <span style={{ color: "#9ca3af" }}> for arb + sharp money tools. </span>
                    <span style={{ color: "#fff", fontWeight: 800 }}>Lucrix Elite gives you all of that — plus Oracle AI — for $39.99.</span>
                    <span style={{ color: "#9ca3af" }}> Half the price. More features. Better data.</span>
                </div>
            </div>

            {/* FAQ */}
            <div style={{ maxWidth: "640px", margin: "0 auto" }}>
                <h3 style={{ fontWeight: 900, textAlign: "center", marginBottom: "24px" }}>Common Questions</h3>
                {[
                    ["Is there a free trial?", "Yes — Pro and Elite both come with a 7-day free trial. Cancel anytime before it ends and you won't be charged."],
                    ["Can I switch plans?", "Yes. Upgrade or downgrade anytime from your account settings. Prorated credits apply automatically."],
                    ["What sportsbooks are supported?", "FanDuel, DraftKings, BetMGM, Caesars, Bet365, BetOnline, Bovada, and more — all in one place."],
                    ["Do you guarantee wins?", "No one can. We give you the mathematical edge. Results depend on volume, discipline, and bankroll management."],
                    ["What is the Oracle AI?", "An AI assistant with live access to today's full +EV slate. Ask it for parlays, best edges, steam moves, or whale signals — it answers with real live data."],
                ].map(([q, a], i) => (
                    <div key={i} style={{
                        marginBottom: "16px", background: "#0f1117",
                        borderRadius: "12px", padding: "20px",
                        border: "1px solid #1f2937",
                    }}>
                        <div style={{ fontWeight: 700, marginBottom: "8px", fontSize: "14px" }}>{q}</div>
                        <div style={{ color: "#6b7280", fontSize: "13px", lineHeight: "1.6" }}>{a}</div>
                    </div>
                ))}
            </div>
        </div>
    );
}
