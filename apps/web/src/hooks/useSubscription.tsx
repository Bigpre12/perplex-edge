"use client";
import { useState, useEffect, createContext, useContext, useCallback, ReactNode } from "react";
import { supabase } from "@/lib/supabaseClient";
import { canAccess, FeatureKey, Tier } from "@/lib/permissions";
import { api, isApiError } from "@/lib/api";
import { useLucrixStore } from "@/store";

const BYPASS = process.env.NEXT_PUBLIC_BYPASS_AUTH === "true";

const BYPASS_SUBSCRIPTION = {
    tier: "elite" as Tier,
    status: "active",
    loading: false,
    can: (_feature: FeatureKey) => true,
    isPro: true,
    isElite: true,
    refresh: () => { },
};

interface SubContext {
    tier: Tier;
    status: string;
    loading: boolean;
    can: (feature: FeatureKey) => boolean;
    isPro: boolean;
    isElite: boolean;
    refresh: () => void;
}

const SubscriptionContext = createContext<SubContext>({
    tier: "free", status: "active", loading: true,
    can: () => false, isPro: false, isElite: false,
    refresh: () => { },
});

export function SubscriptionProvider({ children }: { children: ReactNode }): JSX.Element {
    const tier = useLucrixStore((state: any) => state.userTier);
    const setStoreTier = useLucrixStore((state: any) => state.setUserTier);
    const [status, setStatus] = useState("active");
    const [loading, setLoading] = useState(true);
    const [mounted, setMounted] = useState(false);

    const fetchTier = useCallback(async () => {
        // GUARD: don't even try if there's no token
        const token = typeof window !== 'undefined' ? localStorage.getItem("accessToken") : null;
        if (!token) {
            setStoreTier("free");        // default unauthenticated tier
            setLoading(false);
            return;
        }

        try {
            const data = await api.authMe();
            if (isApiError(data)) {
                setStoreTier("free");
                return;
            }
            const normalizedTier = ((data as any).tier || "free").toLowerCase() as Tier;
            setStoreTier(normalizedTier);
            setStatus((data as any).status || "active");
        } catch (err) {
            console.error("Fetch tier error:", err);
            setStoreTier("free");
        } finally {
            setLoading(false);
        }
    }, [setStoreTier]);

    useEffect(() => {
        setMounted(true);
        fetchTier();
    }, [fetchTier]);

    const isDev = typeof window !== 'undefined' && 
                 (window.location.hostname === 'localhost' || 
                  window.location.hostname === '127.0.0.1' || 
                  window.location.hostname.startsWith('192.168.') || 
                  window.location.hostname.startsWith('172.'));

    const effectiveTier = mounted ? (isDev ? "elite" : tier) : "free";
    const effectiveLoading = mounted ? (isDev ? false : loading) : true;

    return (
        <SubscriptionContext.Provider value={{
            tier: effectiveTier as any,
            status: isDev ? "active" : status,
            loading: effectiveLoading,
            can: (f: FeatureKey) => isDev ? true : canAccess(effectiveTier as any, f),
            isPro: isDev ? true : canAccess(effectiveTier as any, "parlay_builder"),
            isElite: isDev ? true : canAccess(effectiveTier as any, "oracle_ai"),
            refresh: fetchTier,
        }}>
            {children}
        </SubscriptionContext.Provider>
    );
}

export const useSubscription = () => {
    const context = useContext(SubscriptionContext);
    if (BYPASS) return BYPASS_SUBSCRIPTION;
    return context;
};
