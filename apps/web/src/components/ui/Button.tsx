"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

export interface ButtonProps
    extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: "default" | "outline" | "ghost";
    size?: "default" | "sm" | "lg" | "icon";
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant = "default", size = "default", ...props }, ref) => {
        const variants = {
            default: "bg-primary text-white hover:bg-primary/90",
            outline: "border border-white/10 bg-transparent hover:bg-white/5",
            ghost: "hover:bg-white/5 hover:text-white",
        };

        const sizes = {
            default: "h-10 px-4 py-2",
            sm: "h-8 px-3 text-xs",
            lg: "h-12 px-8",
            icon: "h-9 w-9",
        };

        return (
            <button
                className={cn(
                    "inline-flex items-center justify-center rounded-xl text-sm font-medium transition-colors focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50",
                    variants[variant],
                    sizes[size],
                    className
                )}
                ref={ref}
                {...props}
            />
        );
    }
);
Button.displayName = "Button";

export { Button };
