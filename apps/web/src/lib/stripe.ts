// apps/web/src/lib/stripe.ts
import { loadStripe, Stripe } from "@stripe/stripe-js";
import { api, isApiError } from "./api";
import { PRICING } from "@/constants/pricing";

// Lazy load — only loads when actually needed, prevents crash on missing key
let stripeInstance: Promise<Stripe | null> | null = null;
export const getStripe = () => {
    const key = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY;
    if (!key) return null;
    if (!stripeInstance) {
        stripeInstance = loadStripe(key);
    }
    return stripeInstance;
};

export const PLANS = {
    free: {
        name: "Free",
        monthlyPrice: PRICING.FREE.monthly,
        annualPrice: PRICING.FREE.annual,
        monthlyPriceId: null,
        annualPriceId: null,
        color: "#6b7280",
        badge: null,
        description: PRICING.FREE.description,
        features: PRICING.FREE.features,
        cta: "Get Started Free",
        href: "/sign-up",
    },
    pro: {
        name: "Pro",
        monthlyPrice: PRICING.PRO.monthly,
        annualPrice: PRICING.PRO.annual,
        monthlyPriceId: process.env.NEXT_PUBLIC_STRIPE_PRO_MONTHLY,
        annualPriceId: process.env.NEXT_PUBLIC_STRIPE_PRO_ANNUAL,
        color: "#6366f1",
        badge: "Most Popular",
        description: PRICING.PRO.description,
        features: PRICING.PRO.features,
        cta: "Start 7-Day Free Trial",
        href: null,
    },
    elite: {
        name: "Elite",
        monthlyPrice: PRICING.ELITE.monthly,
        annualPrice: PRICING.ELITE.annual,
        monthlyPriceId: process.env.NEXT_PUBLIC_STRIPE_ELITE_MONTHLY,
        annualPriceId: process.env.NEXT_PUBLIC_STRIPE_ELITE_ANNUAL,
        color: "#f59e0b",
        badge: "Best Value",
        description: PRICING.ELITE.description,
        features: PRICING.ELITE.features,
        cta: "Start 7-Day Free Trial",
        href: null,
    },
} as const;

export type PlanKey = keyof typeof PLANS;

// Checkout helper — calls your FastAPI backend
export async function startCheckout(priceId: string) {
    const data = await api.stripeCheckout(priceId);

    if (isApiError(data)) {
        throw new Error(data.message || "Failed to create checkout session");
    }

    if (data.checkout_url) {
        window.location.href = data.checkout_url;
    }
}

// Portal helper — manage existing subscription
export async function openBillingPortal() {
    const data = await api.billingPortal();

    if (isApiError(data)) {
        throw new Error(data.message || "Failed to open billing portal");
    }

    if (data.portal_url) {
        window.location.href = data.portal_url;
    }
}
