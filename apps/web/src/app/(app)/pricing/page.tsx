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
        const href = billing === "annual" ? (plan as any).annualHref : plan.href;
        if (href) { window.location.href = href; return; }

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
        <div className="pricing-container">

            {/* Header */}
            <div className="pricing-header">
                <div className="pricing-badge">
                    PRICING
                </div>
                <h1 className="pricing-title">
                    The Edge Has a Price.<br />Losing Costs More.
                </h1>
                <p className="pricing-desc">
                    Professional-grade betting intelligence. No fluff, no filler — just data that wins.
                </p>

                {/* Billing toggle */}
                <div className="pricing-toggle-wrap">
                    {(["monthly", "annual"] as const).map(b => (
                        <button
                            key={b}
                            onClick={() => setBilling(b)}
                            className={`pricing-toggle-btn ${billing === b ? 'pricing-toggle-btn-active' : ''}`}
                        >
                            {b.charAt(0).toUpperCase() + b.slice(1)}
                            {b === "annual" && (
                                <span className="pricing-free-tag">
                                    2 months free
                                </span>
                            )}
                        </button>
                    ))}
                </div>
            </div>

            {/* Plan Cards */}
            <div className="pricing-grid">
                {(Object.entries(PLANS) as [PlanKey, typeof PLANS[PlanKey]][]).map(([key, plan]) => {
                    const isCurrent = currentTier === key;
                    const price = billing === "annual" ? plan.annualPrice : plan.monthlyPrice;
                    const isPopular = plan.badge === "Most Popular";
                    const isBest = plan.badge === "Best Value";

                    return (
                        <div key={key} className={`pricing-card ${isPopular ? 'pricing-card-popular' : isBest ? 'pricing-card-value' : ''}`}>

                             {/* Badge */}
                             {plan.badge && (
                                 <div className={`pricing-card-badge ${key === 'pro' ? 'pricing-bg-pro' : 'pricing-bg-elite'}`}>
                                     {plan.badge}
                                 </div>
                             )}

                            {/* Plan name */}
                            <div className={`pricing-plan-name pricing-color-${key}`}>
                                {plan.name.toUpperCase()}
                            </div>

                            {/* Price */}
                            <div className="pricing-price-wrap">
                                <span className="pricing-price-val">
                                    {price === 0 ? "Free" : `$${price}`}
                                </span>
                                {price > 0 && (
                                    <span className="pricing-price-unit">
                                        /{billing === "annual" ? "yr" : "mo"}
                                    </span>
                                )}
                            </div>

                            {/* Annual savings */}
                            {billing === "annual" && price > 0 && (
                                <div className="pricing-savings">
                                    Save ${annualSavings(plan.monthlyPrice)}/year
                                </div>
                            )}

                            {/* Description */}
                            <p className="pricing-plan-desc">
                                {plan.description}
                            </p>

                            {/* CTA Button */}
                            <button
                                onClick={() => handleCheckout(key)}
                                disabled={isCurrent || loading === key}
                                 className={`pricing-cta-btn ${isCurrent
                                    ? 'pricing-cta-current'
                                    : isPopular
                                        ? 'pricing-cta-popular'
                                        : isBest
                                            ? 'pricing-cta-value'
                                            : 'pricing-cta-default'
                                    } ${loading === key ? 'pricing-cta-loading' : ''}`}
                            >
                                {loading === key
                                    ? "Redirecting..."
                                    : isCurrent
                                        ? "✓ Current Plan"
                                        : plan.cta}
                            </button>

                            {/* Features */}
                            <div className="pricing-features-list">
                                {plan.features.map((f, i) => (
                                    <div key={i} className="pricing-feature-item">
                                        <span className={`pricing-feature-icon pricing-color-${key}`}>✓</span>
                                        <span className={f.startsWith("Everything") ? "pricing-feature-bold" : "pricing-feature-text"}>
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
            <div className="discord-section">
                <div className="discord-header">
                    <div className="discord-icon">💬</div>
                    <h2 className="discord-title">
                        VIP Discord Picks Community
                    </h2>
                    <p className="discord-desc">
                        Daily pick slips, +EV breakdowns, and a community of sharp bettors.
                    </p>
                </div>

                <div className="discord-grid">
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
                            colorClass: "pricing-color-elite",
                            bgClass: "pricing-bg-elite",
                            borderClass: "discord-border-elite",
                            badge: "Best Value",
                            features: ["Everything in Monthly", "Elite strategy channel", "Quarterly 1:1 review", "Early feature access"],
                            href: "https://whop.com/your-annual-link",
                        },
                    ].map(tier => {
                        const tierColorClass = tier.label === "Weekly" ? "pricing-color-free" : tier.label === "Monthly" ? "pricing-color-pro" : "pricing-color-elite";
                        const tierBgClass = tier.label === "Weekly" ? "pricing-bg-free" : tier.label === "Monthly" ? "pricing-bg-pro" : "pricing-bg-elite";
                        const tierBorderClass = tier.label === "Weekly" ? "discord-border-free" : tier.label === "Monthly" ? "discord-border-pro" : "discord-border-elite";

                        return (
                            <div key={tier.label} className={`discord-card ${tierBorderClass}`}>
                                {tier.badge && (
                                    <div className={`discord-card-badge ${tierBgClass}`}>{tier.badge}</div>
                                )}
                                <div className={`discord-tier-name ${tierColorClass}`}>
                                    {tier.label.toUpperCase()}
                                </div>
                                <div className="discord-price-wrap">
                                    <span className="discord-price-val">{tier.price}</span>
                                    <span className="discord-price-per">{tier.per}</span>
                                </div>
                                <div className="discord-feat-list">
                                    {tier.features.map((f, i) => (
                                        <div key={i} className="discord-feat-item">
                                            <span className={tierColorClass}>✓</span>{f}
                                        </div>
                                    ))}
                                </div>
                                <a href={tier.href} target="_blank" rel="noopener noreferrer" className={`discord-cta ${tierBgClass}`}>
                                    Join on Whop →
                                </a>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Competitor callout */}
            <div className="comparison-banner">
                <div className="comparison-text">
                    <span className="comparison-text-muted">Outlier Pro charges </span>
                    <span className="comparison-bad">$79.99/month</span>
                    <span className="comparison-text-muted"> for arb + sharp money tools. </span>
                    <span className="comparison-highlight">Lucrix Elite gives you all of that — plus Oracle AI — for $39.99.</span>
                    <span className="comparison-text-muted"> Half the price. More features. Better data.</span>
                </div>
            </div>

            {/* FAQ */}
            <div className="faq-wrap">
                <h3 className="faq-title">Common Questions</h3>
                {[
                    ["Is there a free trial?", "Yes — Pro and Elite both come with a 7-day free trial. Cancel anytime before it ends and you won't be charged."],
                    ["Can I switch plans?", "Yes. Upgrade or downgrade anytime from your account settings. Prorated credits apply automatically."],
                    ["What sportsbooks are supported?", "FanDuel, DraftKings, BetMGM, Caesars, Bet365, BetOnline, Bovada, and more — all in one place."],
                    ["Do you guarantee wins?", "No one can. We give you the mathematical edge. Results depend on volume, discipline, and bankroll management."],
                    ["What is the Oracle AI?", "An AI assistant with live access to today's full +EV slate. Ask it for parlays, best edges, steam moves, or whale signals — it answers with real live data."],
                ].map(([q, a], i) => (
                    <div key={i} className="faq-item">
                        <div className="faq-q">{q}</div>
                        <div className="faq-a">{a}</div>
                    </div>
                ))}
            </div>
        </div>
    );
}
