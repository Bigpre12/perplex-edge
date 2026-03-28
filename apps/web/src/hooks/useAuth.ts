"use client";

import { useCallback } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/lib/supabase";
import { clearUser } from "@/lib/auth";
import { TOKEN_STORAGE_KEY } from "@/lib/authStorage";
import API from "@/lib/api";
import { Tier } from "@/lib/tier";

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

    // Fetch fresh user profile from backend via React Query
    const {
        data: profile,
        isLoading,
        error
    } = useQuery<UserProfile | null>({
        queryKey: ["auth", "me"],
        queryFn: async () => {
            const { data: { session } } = await supabase.auth.getSession();
            if (!session) return null;

            try {
                const data = await API.authMe() as UserProfile;
                return data;
            } catch (err: any) {
                if (err?.message?.startsWith("401")) return null;
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
        await supabase.auth.signOut();
        clearUser();
        localStorage.removeItem(TOKEN_STORAGE_KEY);
        queryClient.setQueryData(["auth", "me"], null);
        window.location.href = "/login";
    };

    // Helper to get token from localStorage/Supabase
    const getToken = () => {
        if (typeof window === 'undefined') return null;
        return localStorage.getItem("accessToken") || localStorage.getItem(TOKEN_STORAGE_KEY);
    };

    return {
        user: profile,
        token: getToken(),
        tier: profile?.tier || 'free',
        loading: isLoading,
        isSignedIn: !!profile,
        signOut,
        refreshUser,
        error
    };
}
