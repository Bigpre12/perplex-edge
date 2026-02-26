"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabaseClient";
import { Loader2 } from "lucide-react";

export default function InstitutionalLayout({ children }: { children: React.ReactNode }) {
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const checkSession = async () => {
            const { data: { session } } = await supabase.auth.getSession();
            if (!session) {
                router.replace("/login");
            } else {
                setIsLoading(false);
            }
        };

        checkSession();

        const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
            if (!session) {
                router.replace("/login");
            }
        });

        return () => subscription.unsubscribe();
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
