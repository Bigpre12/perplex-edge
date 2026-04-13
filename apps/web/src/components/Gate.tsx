"use client";
import React from "react";

// PAYWALLS DISABLED — All features unlocked for authenticated users
interface GateProps {
    feature?: string;
    children: React.ReactNode;
    quiet?: boolean;
}

export default function Gate({ children }: GateProps) {
    return <>{children}</>;
}
