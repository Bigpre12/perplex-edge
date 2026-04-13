"use client";
import { useState, useEffect } from "react";
import { supabase } from "@/lib/supabase";

export function useOnboarding() {
    const [needsOnboarding, setNeedsOnboarding] = useState(false);

    useEffect(() => {
        supabase.auth.getUser().then(({ data }) => {
            if (data.user && !data.user.user_metadata?.onboarded) {
                setNeedsOnboarding(true);
            }
        });
    }, []);

    return { needsOnboarding };
}
