"use client";
import React from "react";

// PAYWALLS DISABLED — All features unlocked for authenticated users
interface Props {
    feature?: string;
    children: React.ReactNode;
    reason?: string;
}

export default function GateLock({ children }: Props) {
    return <>{children}</>;
}
