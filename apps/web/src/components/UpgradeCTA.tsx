"use client";
import React from "react";

// PAYWALLS DISABLED — All features unlocked for authenticated users
interface Props {
    feature?: string;
    children: React.ReactNode;
    description?: string;
}

export default function UpgradeCTA({ children }: Props) {
    return <>{children}</>;
}
