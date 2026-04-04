"use client";
import React from "react";

// PAYWALLS DISABLED — All features unlocked for authenticated users
interface Props {
    children: React.ReactNode;
    feature?: string;
    tierRequired?: string;
}

export function UpgradeGate({ children }: Props) {
    return <>{children}</>;
}
