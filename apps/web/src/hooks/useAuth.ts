"use client";

import { useCallback } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/lib/supabaseClient";
import { clearUser } from "@/lib/auth";
import { api, isApiError } from "@/lib/api";
import { Tier } from "@/lib/tier";

interface UserProfile {
    id: string;
    email: string;
    username: string;
    tier: Tier;
    stripe_customer_id?: string;
    created_at?: string;
}

export function useAuth() {
    const queryClient = useQueryClient();

    // Fetch fresh user profile from backend via React Query
    const {
        data: user,
        isLoading,
        error
    } = useQuery<UserProfile | null>({
        queryKey: ["auth", "me"],
        queryFn: async () => {
            const { data: { session } } = await supabase.auth.getSession();
            if (!session) return null;

            const data = await api.get<UserProfile>("/auth/me");
            if (isApiError(data)) {
                if (data.status === 401) return null;
                throw new Error(data.message);
            }
            return data;
        },
        staleTime: 30000,
        refetchOnWindowFocus: true, // Refresh when user returns to tab
    });

    const refreshUser = useCallback(() => {
        queryClient.invalidateQueries({ queryKey: ["auth", "me"] });
    }, [queryClient]);

    const signOut = async () => {
        await supabase.auth.signOut();
        clearUser();
        localStorage.removeItem("perplex_edge_token");
        queryClient.setQueryData(["auth", "me"], null);
        window.location.href = "/login";
    };

    return {
        user,
        loading: isLoading,
        isSignedIn: !!user,
        signOut,
        refreshUser,
        error
    };
}
