"use client";
import { useState } from "react";
import { useOnboarding } from "@/hooks/useOnboarding";
import { OnboardingModal } from "./OnboardingModal";

export function OnboardingProvider({ children }: { children: React.ReactNode }) {
    const { needsOnboarding } = useOnboarding();
    const [onboarded, setOnboarded] = useState(false);

    return (
        <>
            {needsOnboarding && !onboarded && (
                <OnboardingModal onComplete={() => setOnboarded(true)} />
            )}
            {children}
        </>
    );
}
