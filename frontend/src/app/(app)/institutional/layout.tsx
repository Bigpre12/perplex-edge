"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getUser } from "@/lib/auth";
import { Loader2 } from "lucide-react";

export default function InstitutionalLayout({ children }: { children: React.ReactNode }) {
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const checkSession = () => {
            const user = getUser();
            if (!user) {
                router.replace("/login");
                return;
            }

            // Authorization Guard
            const tier = user.subscription_tier;
            // Temporarily allowing 'admin' or bypass during dev if needed, else strict 'pro'
            if (tier !== 'pro' && tier !== 'admin') {
                router.replace("/checkout");
            } else {
                setIsLoading(false);
            }
        };

        checkSession();
    }, [router]);

    if (isLoading) {
        return (
            <div className="h-[60vh] flex flex-col items-center justify-center gap-4 text-primary">
                <Loader2 size={40} className="animate-spin" />
                <p className="text-sm font-bold uppercase tracking-widest text-slate-400">Verifying Security Clearance...</p>
            </div>
        );
    }

    return <>{children}</>;
}
