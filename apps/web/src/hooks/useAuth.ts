"use client";

import { useCallback } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { clearUser } from "@/lib/auth";
import { TOKEN_STORAGE_KEY } from "@/lib/authStorage";
import API from "@/lib/api";
import { Tier, checkTierAccess } from "@/lib/tier";
import { FeatureKey, getRequiredTier } from "@/lib/featureAccess";

interface UserProfile {
    id: string;
    email: string;
    username: string;
    tier: Tier;
    stripe_customer_id?: string;
    created_at?: string;
    user_metadata?: { full_name?: string; [key: string]: any };
}

export function useAuth() {
    const queryClient = useQueryClient();

    // Helper to get token from localStorage
    const getToken = () => {
        if (typeof window === 'undefined') return null;
        return localStorage.getItem(TOKEN_STORAGE_KEY) || localStorage.getItem("accessToken");
    };

    // Fetch fresh user profile from backend via React Query
    const {
        data: profile,
        isLoading,
        error
    } = useQuery<UserProfile | null>({
        queryKey: ["auth", "me"],
        queryFn: async () => {
            // Use custom backend JWT token (not Supabase)
            const token = getToken();
            if (!token) return null;
            try {
                const data = await API.authMe() as UserProfile;
                return data;
            } catch (err: any) {
                // 401 means token expired or invalid - clear it
                if (err?.response?.status === 401 || err?.message?.startsWith("401")) {
                    clearUser();
                    localStorage.removeItem(TOKEN_STORAGE_KEY);
                    localStorage.removeItem("accessToken");
                    return null;
                }
                throw err;
            }
        },
        staleTime: 30000,
        refetchOnWindowFocus: true,
    });

    const refreshUser = useCallback(() => {
        queryClient.invalidateQueries({ queryKey: ["auth", "me"] });
    }, [queryClient]);

    const signOut = async () => {
        clearUser();
        localStorage.removeItem(TOKEN_STORAGE_KEY);
        localStorage.removeItem("accessToken");
        queryClient.setQueryData(["auth", "me"], null);
        window.location.href = "/login";
    };

    const tier: Tier = 'elite'; // PAYWALLS DISABLED — treat all users as elite
    const isFree = false;
    const isPro = true;
    const isElite = true;
    const isAtLeastPro = true;

    /**
     * checkAccess - PAYWALLS DISABLED. Always returns true for all authenticated users.
     */
    const checkAccess = useCallback((_feature: FeatureKey): boolean => {
        return true;
    }, []);

    return {
        user: profile,
        token: getToken(),
        tier,
        isFree,
        isPro,
        isElite,
        isAtLeastPro,
        checkAccess,
        loading: isLoading,
        isSignedIn: !!profile,
        signOut,
        refreshUser,
        error
    };
}
